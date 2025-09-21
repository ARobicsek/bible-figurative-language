#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive chapter processor using the Multi-Model Gemini API
Allows user to select any book, chapter, and verse(s) to process with context-aware analysis.
"""
import sys
import os
import logging
import traceback
import json
import time
import re
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from hebrew_figurative_db.database.db_manager import DatabaseManager

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

def parse_verse_selection(input_str, max_verses):
    """Parse user input for verse selection (e.g., '5', '10-15', 'all')."""
    input_str = input_str.strip().lower()
    if input_str == 'all':
        return list(range(1, max_verses + 1))

    # Range of verses (e.g., 10-15)
    range_match = re.match(r'^(\d+)-(\d+)$', input_str)
    if range_match:
        start = int(range_match.group(1))
        end = int(range_match.group(2))
        if 1 <= start <= end <= max_verses:
            return list(range(start, end + 1))

    # Single verse
    if input_str.isdigit():
        verse = int(input_str)
        if 1 <= verse <= max_verses:
            return [verse]

    return None # Invalid input

def get_user_selection():
    """Get book, chapter, and verse selection from user"""
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34
    }

    print("\n=== HEBREW FIGURATIVE LANGUAGE INTERACTIVE MULTI-MODEL PROCESSOR ===")
    print("\nAvailable books:")
    for i, (book, chapters) in enumerate(books.items(), 1):
        print(f"  {i}. {book} ({chapters} chapters)")

    # Get book selection
    while True:
        try:
            choice = input(f"\nSelect book (1-{len(books)}) or type book name: ").strip()
            if choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(books):
                    book_name = list(books.keys())[choice_num - 1]
                    break
            else:
                matched_book = next((b for b in books if b.lower() == choice.lower()), None)
                if matched_book:
                    book_name = matched_book
                    break
                else:
                    print("Invalid selection. Please try again.")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None, None, None

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
            return None, None, None

    # Get verse selection if a single chapter was chosen
    verse_selection = 'all'
    if len(chapters) == 1:
        chapter_num = chapters[0]
        print(f"\nFetching verse count for {book_name} {chapter_num}...")
        temp_sefaria = SefariaClient()
        verses_data, _ = temp_sefaria.extract_hebrew_text(f"{book_name}.{chapter_num}")
        max_verses = len(verses_data)

        if max_verses == 0:
            print(f"Could not retrieve verses for {book_name} {chapter_num}. Exiting.")
            return None, None, None

        while True:
            try:
                verse_input = input(f"Enter verse, range (e.g. 5-10), or 'all' for all {max_verses} verses: ").strip()
                selected_verses = parse_verse_selection(verse_input, max_verses)
                if selected_verses:
                    verse_selection = selected_verses
                    break
                else:
                    print(f"Invalid input. Please enter a valid verse, range (1-{max_verses}), or 'all'.")
            except KeyboardInterrupt:
                print("\nExiting...")
                return None, None, None

    return book_name, chapters, verse_selection

def process_chapter(book_name, chapter, verse_selection, sefaria, multi_model_api, db_manager, logger):
    """Process a single chapter"""
    logger.info(f"--- Processing {book_name} {chapter} ---")

    logger.info(f"Fetching text for {book_name} {chapter}...")
    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")

    if not verses_data:
        logger.error(f"Failed to get text for {book_name} {chapter}")
        return 0, 0, 1

    logger.info(f"Retrieved {len(verses_data)} verses for {book_name} {chapter}")

    # Filter verses based on user selection
    if verse_selection != 'all':
        verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in verse_selection]
        logger.info(f"Filtering to process {len(verses_to_process)} selected verse(s): {verse_selection}")
    else:
        verses_to_process = verses_data

    chapter_verses = 0
    chapter_instances = 0
    chapter_errors = 0

    for i, verse_data in enumerate(verses_to_process):
        try:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            chapter_verses += 1

            logger.info(f"  Processing {verse_ref} ({i+1}/{len(verses_to_process)})...")

            result_json, error, metadata = multi_model_api.analyze_figurative_language(
                heb_verse, eng_verse, book=book_name, chapter=chapter
            )
            logger.info(f"    API Metadata: {metadata}")

            verse_data_dict = {
                'reference': verse_ref, 'book': book_name, 'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]), 'hebrew': heb_verse,
                'english': eng_verse, 'word_count': len(heb_verse.split()),
                'llm_restriction_error': error
            }
            verse_id = db_manager.insert_verse(verse_data_dict)
            logger.debug(f"    Verse stored in database with ID: {verse_id}")

            if error:
                logger.error(f"API error for {verse_ref}: {error}")
                if "Failed after" not in error:
                    chapter_errors += 1
                continue

            if not result_json:
                logger.warning(f"Empty result for {verse_ref}")
                continue

            try:
                results = json.loads(result_json)
                if results:
                    chapter_instances += len(results)
                    logger.info(f"    FOUND: {len(results)} figurative instances")
                    for j, result in enumerate(results):
                        figurative_data = {k: result.get(k) for k in ['type', 'vehicle_level_1', 'vehicle_level_2', 'tenor_level_1', 'tenor_level_2', 'confidence', 'english_text', 'hebrew_text', 'explanation', 'speaker', 'purpose']}
                        figurative_data['figurative_text'] = result.get('english_text')
                        figurative_data['figurative_text_in_hebrew'] = result.get('hebrew_text')
                        db_manager.insert_figurative_language(verse_id, figurative_data)
                        logger.info(f"      Instance {j+1}: {result.get('type', 'unknown')} - '{result.get('english_text', 'N/A')}'")
                else:
                    logger.debug(f"    No figurative language detected")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for {verse_ref}: {str(e)}")
                logger.error(f"Problematic JSON: {result_json[:200]}")
                chapter_errors += 1
        except Exception as e:
            logger.error(f"Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            chapter_errors += 1

    logger.info(f"{book_name} {chapter} COMPLETED: {chapter_instances} figurative instances from {chapter_verses} verses")
    return chapter_verses, chapter_instances, chapter_errors

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    book_name, chapters, verse_selection = get_user_selection()
    if not book_name:
        return

    verse_info = f"verse(s) {verse_selection}" if verse_selection != 'all' else "all verses"
    print(f"\nProcessing {book_name} chapter(s): {chapters}, {verse_info}")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    chapter_str = str(chapters[0]) if len(chapters) == 1 else "multi"
    log_file = f"{book_name.lower()}_{chapter_str}_multi_model_log_{timestamp}.txt"
    db_name = f"{book_name.lower()}_{chapter_str}_multi_model_{timestamp}.db"

    logger = setup_logging(log_file)
    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}. Relying on system environment variables.")
    logger.info(f"=== PROCESSING {book_name.upper()} CHAPTER(S) {chapters} WITH MULTI-MODEL API ===")
    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please ensure a .env file with the key exists in the script's directory, or that the environment variable is set.")

        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()
        logger.info("Initializing Gemini multi-model API...")
        multi_model_api = MultiModelGeminiClient(api_key)

        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        total_verses, total_instances, total_errors = 0, 0, 0

        for chapter in chapters:
            v, i, e = process_chapter(book_name, chapter, verse_selection, sefaria, multi_model_api, db_manager, logger)
            total_verses += v
            total_instances += i
            total_errors += e
            db_manager.conn.commit()

        total_time = time.time() - start_time
        db_manager.close()

        logger.info(f"\n=== {book_name.upper()} PROCESSING COMPLETE ===")
        logger.info(f"Database: {db_name}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Total verses processed: {total_verses}")
        logger.info(f"Total figurative instances: {total_instances}")
        logger.info(f"Errors: {total_errors}")
        logger.info(f"Processing time: {total_time:.1f} seconds")

        logger.info("\n--- Multi-Model API Usage Statistics ---")
        usage_stats = multi_model_api.get_usage_info()
        for key, value in usage_stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")

        print(f"\n✅ Processing complete! See {log_file} for details.")
        print(f"📁 Database: {db_name}")

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
        print(f"\nAn error occurred: {e}")
        print("Check the log file for detailed error information.")
