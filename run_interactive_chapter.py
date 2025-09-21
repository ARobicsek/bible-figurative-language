#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive chapter processor for Hebrew Figurative Language analysis
Allows user to select any book and chapter to process
"""
import sys
import os
import logging
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
import json
import time
from datetime import datetime

def setup_logging(log_file):
    """Setup comprehensive logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def get_user_selection():
    """Get book and chapter selection from user"""

    # Available books with chapter counts
    books = {
        "Genesis": 50,
        "Exodus": 40,
        "Leviticus": 27,
        "Numbers": 36,
        "Deuteronomy": 34
    }

    print("\n=== HEBREW FIGURATIVE LANGUAGE INTERACTIVE PROCESSOR ===")
    print("\nAvailable books:")
    for i, (book, chapters) in enumerate(books.items(), 1):
        print(f"  {i}. {book} ({chapters} chapters)")

    # Get book selection
    while True:
        try:
            choice = input(f"\nSelect book (1-{len(books)}) or type book name: ").strip()

            # Try numeric choice
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(books):
                    book_name = list(books.keys())[choice_num - 1]
                    break

            # Try book name
            for book in books:
                if choice.lower() == book.lower():
                    book_name = book
                    break
            else:
                print("Invalid selection. Please try again.")
                continue
            break

        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None, None

    max_chapters = books[book_name]
    print(f"\nSelected: {book_name} (1-{max_chapters} chapters available)")

    # Get chapter selection
    while True:
        try:
            chapter_input = input(f"Enter chapter number (1-{max_chapters}) or 'all' for all chapters: ").strip().lower()

            if chapter_input == 'all':
                chapters = list(range(1, max_chapters + 1))
                break
            elif chapter_input.isdigit():
                chapter = int(chapter_input)
                if 1 <= chapter <= max_chapters:
                    chapters = [chapter]
                    break
                else:
                    print(f"Chapter must be between 1 and {max_chapters}")
            else:
                print("Invalid input. Enter a number or 'all'")

        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None, None

    return book_name, chapters

def process_chapter(book_name, chapter, sefaria, conservative_api, db_manager, logger):
    """Process a single chapter"""

    logger.info(f"--- Processing {book_name} {chapter} ---")

    # Get text
    logger.info(f"Fetching text for {book_name} {chapter}...")
    verses_data, api_time = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")

    if not verses_data:
        logger.error(f"Failed to get text for {book_name} {chapter}")
        return 0, 0, 1

    logger.info(f"Retrieved {len(verses_data)} verses for {book_name} {chapter}")

    chapter_verses = 0
    chapter_instances = 0
    chapter_errors = 0

    # Process each verse
    for i, verse_data in enumerate(verses_data):
        try:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            chapter_verses += 1

            logger.info(f"  Processing {verse_ref} ({i+1}/{len(verses_data)})...")

            # Analyze with conservative API
            result_json, error = conservative_api.analyze_figurative_language(heb_verse, eng_verse)

            if error:
                logger.error(f"API error for {verse_ref}: {error}")
                chapter_errors += 1
                continue

            # First insert verse regardless of figurative language detection
            verse_data_dict = {
                'reference': verse_ref,
                'book': book_name,
                'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]),
                'hebrew': heb_verse,
                'english': eng_verse,
                'word_count': len(heb_verse.split())
            }
            verse_id = db_manager.insert_verse(verse_data_dict)
            logger.debug(f"    Verse stored in database with ID: {verse_id}")

            if not result_json:
                logger.warning(f"Empty result for {verse_ref}")
                continue

            try:
                # Clean up markdown formatting if present
                clean_json = result_json.strip()
                if clean_json.startswith('```json\n'):
                    clean_json = clean_json[8:]  # Remove ```json\n
                if clean_json.endswith('\n```'):
                    clean_json = clean_json[:-4]  # Remove \n```

                # Additional cleanup for analysis text after JSON
                if '\n```\n' in clean_json:
                    clean_json = clean_json.split('\n```\n')[0]
                elif '\n```' in clean_json:
                    clean_json = clean_json.split('\n```')[0]

                results = json.loads(clean_json)
                if results:  # Found figurative language
                    chapter_instances += len(results)
                    logger.info(f"    FOUND: {len(results)} figurative instances")

                    # Store each figurative language instance
                    for j, result in enumerate(results):
                        figurative_data = {
                            'type': result.get('type', 'unknown'),
                            'vehicle_level_1': result.get('vehicle_level_1', ''),
                            'vehicle_level_2': result.get('vehicle_level_2', ''),
                            'tenor_level_1': result.get('tenor_level_1', ''),
                            'tenor_level_2': result.get('tenor_level_2', ''),
                            'confidence': result.get('confidence', 0.0),
                            'figurative_text': result.get('english_text', ''),
                            'figurative_text_in_hebrew': result.get('hebrew_text', ''),
                            'explanation': result.get('explanation', ''),
                            'speaker': result.get('speaker', ''),
                            'purpose': result.get('purpose', '')
                        }

                        fig_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                        logger.info(f"      Instance {j+1}: {result.get('type', 'unknown')} - '{result.get('english_text', 'N/A')}'")
                else:
                    logger.debug(f"    No figurative language detected")

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for {verse_ref}: {str(e)}")
                try:
                    safe_output = result_json[:200] + "..." if len(result_json) > 200 else result_json
                    logger.error(f"Problematic JSON: {safe_output}")
                except:
                    logger.error("Could not log problematic JSON due to encoding issues")
                chapter_errors += 1

        except Exception as e:
            logger.error(f"Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            chapter_errors += 1

    logger.info(f"{book_name} {chapter} COMPLETED: {chapter_instances} figurative instances from {chapter_verses} verses")
    return chapter_verses, chapter_instances, chapter_errors

def main():
    """Main interactive processing function"""

    # Get user selection
    book_name, chapters = get_user_selection()
    if not book_name:
        return

    print(f"\nProcessing {book_name} chapter(s): {chapters}")

    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if len(chapters) == 1:
        log_file = f"{book_name.lower()}_{chapters[0]}_log_{timestamp}.txt"
        db_name = f"{book_name.lower()}_{chapters[0]}_fixed_{timestamp}.db"
    else:
        log_file = f"{book_name.lower()}_multiple_log_{timestamp}.txt"
        db_name = f"{book_name.lower()}_multiple_fixed_{timestamp}.db"

    logger = setup_logging(log_file)

    logger.info(f"=== PROCESSING {book_name.upper()} CHAPTER(S) {chapters} ===")
    start_time = time.time()

    try:
        # Initialize clients
        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info("Initializing Gemini conservative API...")
        conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

        # Create database
        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        total_verses = 0
        total_instances = 0
        total_errors = 0

        # Process each chapter
        for chapter in chapters:
            chapter_verses, chapter_instances, chapter_errors = process_chapter(
                book_name, chapter, sefaria, conservative_api, db_manager, logger
            )
            total_verses += chapter_verses
            total_instances += chapter_instances
            total_errors += chapter_errors

            # Commit after each chapter
            db_manager.conn.commit()

        total_time = time.time() - start_time

        # Final commit and close database
        db_manager.conn.commit()
        db_manager.conn.close()

        # Summary
        logger.info(f"\n=== {book_name.upper()} PROCESSING COMPLETE ===")
        logger.info(f"Database: {db_name}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Chapters processed: {len(chapters)}")
        logger.info(f"Total verses processed: {total_verses}")
        logger.info(f"Total figurative instances: {total_instances}")
        if total_verses > 0:
            logger.info(f"Instances per verse: {total_instances/total_verses:.3f}")
        logger.info(f"Errors: {total_errors}")
        logger.info(f"Processing time: {total_time:.1f} seconds")

        # Verify database contents
        import sqlite3
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM figurative_language")
        fig_count = cursor.fetchone()[0]
        logger.info(f"Database verification: {verse_count} verses, {fig_count} figurative instances stored")

        # Show figurative language summary if found
        if fig_count > 0:
            logger.info("\n=== FIGURATIVE LANGUAGE SUMMARY ===")
            cursor.execute("""
                SELECT v.reference, fl.type, fl.figurative_text, fl.confidence
                FROM figurative_language fl
                JOIN verses v ON fl.verse_id = v.id
                ORDER BY v.chapter, v.verse
            """)
            instances = cursor.fetchall()
            for ref, ftype, text, confidence in instances:
                logger.info(f"{ref}: {ftype} (confidence: {confidence:.2f}) - '{text}'")

        conn.close()

        print(f"\n✅ Processing complete!")
        print(f"📁 Database: {db_name}")
        print(f"📄 Log file: {log_file}")
        print(f"📊 Results: {verse_count} verses, {fig_count} figurative instances")

        return db_name, total_verses, total_instances

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Check the log file for detailed error information.")