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
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor

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

def parse_selection(input_str, max_value, selection_type="item"):
    """Parse user input for flexible selection (e.g., '5', '10-15', '1,3,5-7', 'all')."""
    input_str = input_str.strip().lower()
    if input_str == 'all':
        return list(range(1, max_value + 1))

    selected = set()

    # Split by commas for multiple selections
    parts = [part.strip() for part in input_str.split(',')]

    for part in parts:
        if not part:
            continue

        # Range (e.g., 10-15)
        range_match = re.match(r'^(\d+)-(\d+)$', part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if 1 <= start <= end <= max_value:
                selected.update(range(start, end + 1))
            else:
                print(f"Invalid range {part}: must be between 1 and {max_value}")
                return None
        # Single number
        elif part.isdigit():
            num = int(part)
            if 1 <= num <= max_value:
                selected.add(num)
            else:
                print(f"Invalid {selection_type} {num}: must be between 1 and {max_value}")
                return None
        else:
            print(f"Invalid format: {part}")
            return None

    return sorted(list(selected)) if selected else None

def get_user_selection():
    """Get flexible book, chapter, and verse selection from user"""
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34
    }

    print("\n=== HEBREW FIGURATIVE LANGUAGE INTERACTIVE MULTI-MODEL PROCESSOR ===")
    print("Enhanced version with flexible multi-book, multi-chapter, multi-verse selection")
    print("\nAvailable books:")
    for i, (book, chapters) in enumerate(books.items(), 1):
        print(f"  {i}. {book} ({chapters} chapters)")

    # Get book selection
    selected_books = []
    while True:
        try:
            print("\nBook Selection Examples:")
            print("  - Single: 'Genesis' or '1'")
            print("  - Multiple: 'Genesis,Exodus' or '1,2'")
            print("  - Range: '1-3' (Genesis through Leviticus)")
            print("  - Mixed: '1,3,5' (Genesis, Leviticus, Deuteronomy)")
            print("  - All: 'all'")

            choice = input(f"\nSelect books: ").strip()

            if choice.lower() == 'all':
                selected_books = list(books.keys())
                break

            # Parse book selection
            book_parts = [part.strip() for part in choice.split(',')]
            temp_books = []

            for part in book_parts:
                if not part:
                    continue

                # Range of book numbers (e.g., 1-3)
                range_match = re.match(r'^(\d+)-(\d+)$', part)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2))
                    if 1 <= start <= end <= len(books):
                        book_list = list(books.keys())
                        temp_books.extend(book_list[start-1:end])
                    else:
                        print(f"Invalid book range {part}: must be between 1 and {len(books)}")
                        temp_books = []
                        break
                # Single book number
                elif part.isdigit():
                    book_num = int(part)
                    if 1 <= book_num <= len(books):
                        temp_books.append(list(books.keys())[book_num - 1])
                    else:
                        print(f"Invalid book number {book_num}: must be between 1 and {len(books)}")
                        temp_books = []
                        break
                # Book name
                else:
                    matched_book = next((b for b in books if b.lower() == part.lower()), None)
                    if matched_book:
                        temp_books.append(matched_book)
                    else:
                        print(f"Invalid book name: {part}")
                        temp_books = []
                        break

            if temp_books:
                # Remove duplicates and maintain order
                seen = set()
                selected_books = []
                for book in temp_books:
                    if book not in seen:
                        selected_books.append(book)
                        seen.add(book)
                break
            else:
                print("Please try again with valid book selection.")

        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None

    print(f"\nSelected books: {', '.join(selected_books)}")

    # Get chapter and verse selections for each book
    book_selections = {}

    for book_name in selected_books:
        max_chapters = books[book_name]
        print(f"\n--- {book_name} ({max_chapters} chapters available) ---")

        # Get chapter selection for this book
        while True:
            try:
                print("Chapter Selection Examples:")
                print(f"  - Single: '5'")
                print(f"  - Multiple: '1,3,7'")
                print(f"  - Range: '5-10'")
                print(f"  - Mixed: '1,3,5-7,10'")
                print(f"  - All chapters: 'all'")
                print(f"  - ALL CHAPTERS & VERSES: 'full' (processes entire book)")

                chapter_input = input(f"Enter chapters for {book_name} (1-{max_chapters}): ").strip().lower()

                if chapter_input == 'full':
                    # Process entire book - all chapters, all verses
                    print(f"Selected: FULL BOOK ({book_name} - all chapters, all verses)")
                    print(f"  Will process all {max_chapters} chapters with all verses")

                    # Use special marker 'ALL' to indicate full book processing
                    book_selections[book_name] = 'FULL_BOOK'
                    break

                selected_chapters = parse_selection(chapter_input, max_chapters, "chapter")

                if selected_chapters is not None:
                    break
                else:
                    print(f"Please enter valid chapters (1-{max_chapters})")

            except KeyboardInterrupt:
                print("\nExiting...")
                return None

        # Skip individual chapter processing if 'full' was selected
        if chapter_input == 'full':
            continue

        print(f"Selected chapters for {book_name}: {selected_chapters}")

        # Get verse selection for each chapter
        chapter_verse_map = {}

        # Ask if user wants all verses for all selected chapters
        if len(selected_chapters) > 1:
            all_verses_choice = input(f"\nProcess ALL verses for all {len(selected_chapters)} chapters? (y/n): ").strip().lower()
            if all_verses_choice == 'y':
                # Use special marker for all chapters/all verses
                chapter_verse_map = {chapter: 'ALL_VERSES' for chapter in selected_chapters}
                print(f"  Will process all verses for all {len(selected_chapters)} chapters")
                book_selections[book_name] = chapter_verse_map
                continue

        for chapter in selected_chapters:
            print(f"\n  Chapter {chapter}:")

            # Fetch verse count for this chapter
            print(f"    Fetching verse count for {book_name} {chapter}...")
            temp_sefaria = SefariaClient()
            verses_data, _ = temp_sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
            max_verses = len(verses_data)

            if max_verses == 0:
                print(f"    Could not retrieve verses for {book_name} {chapter}. Skipping.")
                continue

            while True:
                try:
                    print("    Verse Selection Examples:")
                    print(f"      - Single: '5'")
                    print(f"      - Multiple: '1,3,7'")
                    print(f"      - Range: '5-10'")
                    print(f"      - Mixed: '1,3,5-7,10'")
                    print(f"      - All: 'all'")

                    verse_input = input(f"    Enter verses for {book_name} {chapter} (1-{max_verses}): ").strip()
                    selected_verses = parse_selection(verse_input, max_verses, "verse")

                    if selected_verses is not None:
                        chapter_verse_map[chapter] = selected_verses
                        print(f"    Selected verses for {book_name} {chapter}: {selected_verses}")
                        break
                    else:
                        print(f"    Please enter valid verses (1-{max_verses})")

                except KeyboardInterrupt:
                    print("\nExiting...")
                    return None

        book_selections[book_name] = chapter_verse_map

    return book_selections


def process_chapter(book_name, chapter, verse_selection, sefaria, multi_model_api, db_manager, logger):
    """Process a single chapter with selected verses"""
    logger.info(f"--- Processing {book_name} {chapter} ---")

    logger.info(f"Fetching text for {book_name} {chapter}...")
    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")

    if not verses_data:
        logger.error(f"Failed to get text for {book_name} {chapter}")
        return 0, 0, 1

    logger.info(f"Retrieved {len(verses_data)} verses for {book_name} {chapter}")

    # Handle verse selection
    if verse_selection == 'ALL_VERSES':
        verses_to_process = verses_data
        logger.info(f"Processing all {len(verses_to_process)} verses")
    else:
        verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in verse_selection]
        logger.info(f"Processing {len(verses_to_process)} selected verse(s): {verse_selection}")

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

            # Retry logic for verses with retryable errors
            max_verse_retries = 3
            verse_retry_count = 0
            final_error = None
            final_metadata = None
            result_json = None

            while verse_retry_count < max_verse_retries:
                result_json, error, metadata = multi_model_api.analyze_figurative_language(
                    heb_verse, eng_verse, book=book_name, chapter=chapter
                )

                # Check if this is a retryable error
                is_retryable = error and ("500" in error or "internal error" in error.lower() or "retry" in error.lower())

                if not error or not is_retryable:
                    # Success or non-retryable error - stop retrying
                    final_error = error
                    final_metadata = metadata
                    break
                else:
                    # Retryable error - log and retry
                    verse_retry_count += 1
                    logger.warning(f"    Retryable error on attempt {verse_retry_count}/{max_verse_retries}: {error}")
                    if verse_retry_count < max_verse_retries:
                        import time
                        time.sleep(2)  # Brief delay before retry
                    final_error = error  # Keep last error in case all retries fail
                    final_metadata = metadata

            logger.info(f"    API Metadata: {final_metadata}")
            if verse_retry_count > 0:
                if final_error:
                    logger.error(f"    Failed after {verse_retry_count} retries: {final_error}")
                else:
                    logger.info(f"    Succeeded after {verse_retry_count} retries")

            # Extract truncation info from metadata
            truncation_info = final_metadata.get('truncation_info', {}) if final_metadata else {}

            # Strip diacritics from Hebrew text
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)

            verse_data_dict = {
                'reference': verse_ref, 'book': book_name, 'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]), 'hebrew': heb_verse,
                'hebrew_stripped': hebrew_stripped,
                'english': eng_verse, 'word_count': len(heb_verse.split()),
                'llm_restriction_error': final_error,
                'llm_deliberation': final_metadata.get('llm_deliberation') if final_metadata else None,
                'instances_detected': truncation_info.get('instances_detected'),
                'instances_recovered': truncation_info.get('instances_recovered'),
                'instances_lost_to_truncation': truncation_info.get('instances_lost_to_truncation'),
                'truncation_occurred': truncation_info.get('truncation_occurred', 'no')
            }
            verse_id = db_manager.insert_verse(verse_data_dict)
            logger.debug(f"    Verse stored in database with ID: {verse_id}")

            if final_error:
                logger.error(f"API error for {verse_ref}: {final_error}")
                if "Failed after" not in final_error:
                    chapter_errors += 1
                continue

            # Use final_metadata instead of metadata for the rest of the processing
            metadata = final_metadata

            if not result_json:
                logger.warning(f"Empty result for {verse_ref}")
                continue

            try:
                results = json.loads(result_json)
                validated_count = len(results) if results else 0

                # Get all detected instances from metadata (including rejected ones)
                all_instances = metadata.get('all_detected_instances', [])
                total_detected = len(all_instances)

                if all_instances:
                    logger.info(f"    DETECTED: {total_detected} instances, VALIDATED: {validated_count} instances")

                    # Insert all instances (both valid and rejected) with validation data
                    valid_count = multi_model_api.insert_and_validate_instances(
                        verse_id, all_instances, heb_verse, eng_verse
                    )

                    chapter_instances += valid_count
                    logger.info(f"    FINAL: {valid_count} valid instances stored with validation decisions")

                    for j, instance in enumerate(all_instances[:3]):  # Show first 3 for brevity
                        logger.info(f"      Instance {j+1}: {instance.get('type', 'unknown')} - '{instance.get('english_text', 'N/A')}'")
                    if total_detected > 3:
                        logger.info(f"      ... and {total_detected - 3} more instances")
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

def generate_filename_from_selections(book_selections):
    """Generate filename from flexible book selections"""
    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")

    if len(book_selections) == 1:
        # Single book
        book_name = list(book_selections.keys())[0]
        book_part = book_name.lower()

        chapters = list(book_selections[book_name].keys())
        if len(chapters) == 1:
            chapter_part = str(chapters[0])
            verses = book_selections[book_name][chapters[0]]
            if len(verses) == 1:
                verse_part = str(verses[0])
            else:
                verse_part = f"v{len(verses)}"
        else:
            chapter_part = f"c{len(chapters)}"
            verse_part = "multi_v"
    else:
        # Multiple books
        book_part = f"{len(book_selections)}books"
        total_chapters = sum(len(chapters) for chapters in book_selections.values())
        chapter_part = f"c{total_chapters}"
        verse_part = "multi_v"

    base_filename = f"{book_part}_{chapter_part}_{verse_part}_{date_part}_{time_part}"
    return base_filename

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    book_selections = get_user_selection()
    if not book_selections:
        return

    # Generate filename from selections
    base_filename = generate_filename_from_selections(book_selections)
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"

    # Create summary of what will be processed
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34
    }

    total_tasks = 0
    summary_lines = []

    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            # Estimate verses for full book (approximate)
            verse_estimates = {
                "Genesis": 1533, "Exodus": 1213, "Leviticus": 859,
                "Numbers": 1288, "Deuteronomy": 959
            }
            estimated_verses = verse_estimates.get(book_name, 1000)  # Default estimate
            total_tasks += estimated_verses
            summary_lines.append(f"  {book_name}: FULL BOOK (~{estimated_verses} verses)")
        else:
            for chapter, verses in chapters.items():
                if verses == 'ALL_VERSES':
                    # Estimate verses per chapter (approximate)
                    estimated_verses = 25  # Average verses per chapter
                    total_tasks += estimated_verses
                    summary_lines.append(f"  {book_name} {chapter}: all verses (~{estimated_verses})")
                else:
                    total_tasks += len(verses)
                    summary_lines.append(f"  {book_name} {chapter}: verses {verses}")

    print(f"\n=== PROCESSING SUMMARY ===")
    print(f"Books: {len(book_selections)}")
    print(f"Estimated verses to process: ~{total_tasks}")
    for line in summary_lines[:10]:  # Show first 10 for brevity
        print(line)
    if len(summary_lines) > 10:
        print(f"  ... and {len(summary_lines) - 10} more chapter/verse combinations")
    print(f"\nOutput files: {base_filename}.*")
    print(f"\nNote: This script uses single-threaded processing.")
    print(f"For parallel processing with worker selection, use: interactive_parallel_processor.py")

    proceed = input("\nProceed with processing? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Processing cancelled.")
        return

    logger = setup_logging(log_file)
    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}. Relying on system environment variables.")

    # Log processing summary
    logger.info(f"=== MULTI-BOOK PROCESSING STARTED ===")
    logger.info(f"Total books: {len(book_selections)}")
    logger.info(f"Total verses: {total_tasks}")
    for book_name, chapters in book_selections.items():
        logger.info(f"Book: {book_name} - Chapters: {list(chapters.keys())}")

    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please ensure a .env file with the key exists in the script's directory, or that the environment variable is set.")

        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        logger.info("Initializing Metaphor Validator...")
        validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
        logger.info("Initializing Gemini multi-model API...")
        multi_model_api = MultiModelGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

        total_verses, total_instances, total_errors = 0, 0, 0

        # Process each book, chapter, and verse selection
        for book_name, chapters in book_selections.items():
            logger.info(f"\n=== PROCESSING BOOK: {book_name.upper()} ===")

            if chapters == 'FULL_BOOK':
                # Process entire book - all chapters, all verses
                books = {
                    "Genesis": 50, "Exodus": 40, "Leviticus": 27,
                    "Numbers": 36, "Deuteronomy": 34
                }
                max_chapters = books[book_name]
                logger.info(f"Processing full book: all {max_chapters} chapters with all verses")

                for chapter in range(1, max_chapters + 1):
                    v, i, e = process_chapter(book_name, chapter, 'ALL_VERSES', sefaria, multi_model_api, db_manager, logger)
                    total_verses += v
                    total_instances += i
                    total_errors += e
                    db_manager.conn.commit()
            else:
                # Process specific chapters and verses
                for chapter, verse_selection in chapters.items():
                    v, i, e = process_chapter(book_name, chapter, verse_selection, sefaria, multi_model_api, db_manager, logger)
                    total_verses += v
                    total_instances += i
                    total_errors += e
                    db_manager.conn.commit()

        total_time = time.time() - start_time
        db_manager.close()

        logger.info(f"\n=== MULTI-BOOK PROCESSING COMPLETE ===")
        logger.info(f"Database: {db_name}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Books processed: {len(book_selections)}")
        logger.info(f"Total verses processed: {total_verses}")
        logger.info(f"Total figurative instances: {total_instances}")
        logger.info(f"Errors: {total_errors}")
        logger.info(f"Processing time: {total_time:.1f} seconds")
        logger.info(f"Average time per verse: {total_time/total_verses:.2f} seconds")

        logger.info("\n--- Multi-Model API Usage Statistics ---")
        usage_stats = multi_model_api.get_usage_info()
        for key, value in usage_stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")

        print(f"\n✅ Processing complete! See {log_file} for details.")
        print(f"📁 Database: {db_name}")
        print(f"📊 Processed {total_verses} verses from {len(book_selections)} books")
        print(f"⏱️  Total time: {total_time:.1f} seconds")

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
