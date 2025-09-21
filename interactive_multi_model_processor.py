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
            return None, None, None, None

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
            return None, None, None, None

    # Get verse selection if a single chapter was chosen
    verse_selection = 'all'
    verse_input_str = 'all'
    if len(chapters) == 1:
        chapter_num = chapters[0]
        print(f"\nFetching verse count for {book_name} {chapter_num}...")
        temp_sefaria = SefariaClient()
        verses_data, _ = temp_sefaria.extract_hebrew_text(f"{book_name}.{chapter_num}")
        max_verses = len(verses_data)

        if max_verses == 0:
            print(f"Could not retrieve verses for {book_name} {chapter_num}. Exiting.")
            return None, None, None, None

        while True:
            try:
                verse_input = input(f"Enter verse, range (e.g. 5-10), or 'all' for all {max_verses} verses: ").strip()
                selected_verses = parse_verse_selection(verse_input, max_verses)
                if selected_verses:
                    verse_selection = selected_verses
                    verse_input_str = verse_input.lower()
                    break
                else:
                    print(f"Invalid input. Please enter a valid verse, range (1-{max_verses}), or 'all'.")
            except KeyboardInterrupt:
                print("\nExiting...")
                return None, None, None, None

    return book_name, chapters, verse_selection, verse_input_str


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

            verse_data_dict = {
                'reference': verse_ref, 'book': book_name, 'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]), 'hebrew': heb_verse,
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

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    book_name, chapters, verse_selection, verse_input_str = get_user_selection()
    if not book_name:
        return

    # New filename generation
    book_part = book_name.lower()
    chapter_part = "all_c" if len(chapters) > 1 else str(chapters[0])
    verse_part = "all_v" if verse_input_str == 'all' else verse_input_str

    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")

    base_filename = f"{book_part}_{chapter_part}_{verse_part}_{date_part}_{time_part}"
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"

    print(f"\nProcessing {book_name}, chapter(s): {chapter_part}, verse(s): {verse_part}")
    print(f"Output files will be based on: {base_filename}")

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

        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        logger.info("Initializing Metaphor Validator...")
        validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
        logger.info("Initializing Gemini multi-model API...")
        multi_model_api = MultiModelGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

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
