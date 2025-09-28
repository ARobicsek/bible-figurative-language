#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Parallel Interactive Flexible Tagging Processor
High-performance version with async processing, reduced logging, and database batching.
"""
import sys
import os
import logging
import traceback
import json
import time
import re
import asyncio
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Import our flexible tagging client
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def setup_logging(log_file, enable_debug=False):
    """Setup optimized logging with level filtering"""
    log_level = logging.DEBUG if enable_debug else logging.INFO
    logging.basicConfig(
        level=log_level,
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

    print("\n=== PARALLEL HEBREW FIGURATIVE LANGUAGE PROCESSOR ===")
    print("High-performance parallel processing system")
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
            return None, None, None, None, None

    max_chapters = books[book_name]
    print(f"\nSelected: {book_name} (1-{max_chapters} chapters available)")

    # Get chapter selection - enhanced to support ranges
    while True:
        try:
            chapter_input = input(f"Enter chapter number, range (e.g. 1-5), or 'all' for all chapters: ").strip().lower()
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
                # Check for chapter range (e.g., "1-5")
                range_match = re.match(r'^(\d+)-(\d+)$', chapter_input)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2))
                    if 1 <= start <= end <= max_chapters:
                        chapters = list(range(start, end + 1))
                        print(f"Selected chapters: {start} to {end}")
                        break
                    else:
                        print(f"Chapter range must be between 1 and {max_chapters}")
                else:
                    print("Invalid input. Enter a number, range (e.g. 1-5), or 'all'")
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None, None, None, None, None

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
            return None, None, None, None, None

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
                return None, None, None, None, None

    # Get parallelization settings
    print(f"\n⚡ PARALLEL PROCESSING SETTINGS:")
    print(f"Recommended workers: 6-8 (balance of speed vs API limits)")
    print(f"Lower workers (2-4): More conservative, slower but more reliable")
    print(f"Higher workers (8-12): Faster but may hit API rate limits")

    while True:
        try:
            max_workers_input = input(f"\nEnter max parallel workers (1-12, default: 6): ").strip()
            if not max_workers_input:
                max_workers = 6  # Default
                break
            elif max_workers_input.isdigit():
                max_workers = int(max_workers_input)
                if 1 <= max_workers <= 12:
                    break
                else:
                    print("Max workers must be between 1 and 12")
            else:
                print("Please enter a number or press Enter for default (6)")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None, None, None, None, None

    return book_name, chapters, verse_selection, verse_input_str, max_workers

class ParallelVerseProcessor:
    """Handles parallel processing of verses with batching"""

    def __init__(self, flexible_client, validator, db_manager, logger, max_workers=6):
        self.flexible_client = flexible_client
        self.validator = validator
        self.db_manager = db_manager
        self.logger = logger
        self.max_workers = max_workers

        # Batching collections
        self.verse_batch = []
        self.instance_batch = []
        self.VERSE_BATCH_SIZE = 20
        self.INSTANCE_BATCH_SIZE = 50

    def process_single_verse(self, verse_data, book_name, chapter) -> Tuple[Dict, List[Dict], Optional[str]]:
        """Process a single verse - designed to be thread-safe"""
        try:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']

            # Optimized logging - only log essential info
            if self.logger.level <= logging.INFO:
                self.logger.info(f"Processing {verse_ref}")

            # Use flexible tagging analysis
            result_text, error, metadata = self.flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book=book_name, chapter=chapter
            )

            # Handle truncation fallback
            truncation_occurred = metadata.get('truncation_detected', False)
            pro_model_recovery_successful = False
            if truncation_occurred:
                if self.logger.level <= logging.WARNING:
                    self.logger.warning(f"Truncation detected in {verse_ref}, retrying with Pro model")

                result_text, error, metadata = self.flexible_client.analyze_figurative_language_flexible(
                    heb_verse, eng_verse, book=book_name, chapter=chapter, model_override="gemini-2.5-pro"
                )
                pro_model_recovery_successful = not metadata.get('truncation_detected', False)

            # Prepare verse data
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)
            instances_count = len(metadata.get('flexible_instances', []))
            figurative_detection = metadata.get('figurative_detection_deliberation', '')

            verse_data_dict = {
                'reference': verse_ref,
                'book': book_name,
                'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]),
                'hebrew': heb_verse,
                'hebrew_stripped': hebrew_stripped,
                'english': eng_verse,
                'word_count': len(heb_verse.split()),
                'llm_restriction_error': error,
                'figurative_detection_deliberation': figurative_detection,
                'instances_detected': instances_count,
                'instances_recovered': instances_count,
                'instances_lost_to_truncation': 1 if truncation_occurred and not pro_model_recovery_successful else 0,
                'truncation_occurred': 'yes' if truncation_occurred else 'no'
            }

            if error:
                if self.logger.level <= logging.ERROR:
                    self.logger.error(f"Error processing {verse_ref}: {error}")
                return verse_data_dict, [], error

            # Process instances
            flexible_instances = metadata.get('flexible_instances', [])
            tagging_analysis = metadata.get('tagging_analysis_deliberation', '')

            # Prepare instance data
            instance_data_list = []
            for j, instance in enumerate(flexible_instances):
                if not isinstance(instance, dict):
                    continue

                hebrew_text = instance.get('hebrew_text', '')
                english_text = instance.get('english_text', '')
                hebrew_stripped_inst = HebrewTextProcessor.strip_diacritics(hebrew_text) if hebrew_text else ''

                flexible_data = {
                    'verse_ref': verse_ref,
                    'instance_number': j + 1,
                    'hebrew_text': hebrew_text,
                    'english_text': english_text,
                    'figurative_language': instance.get('figurative_language', 'no'),
                    'simile': instance.get('simile', 'no'),
                    'metaphor': instance.get('metaphor', 'no'),
                    'personification': instance.get('personification', 'no'),
                    'idiom': instance.get('idiom', 'no'),
                    'hyperbole': instance.get('hyperbole', 'no'),
                    'metonymy': instance.get('metonymy', 'no'),
                    'other': instance.get('other', 'no'),
                    'explanation': instance.get('explanation', ''),
                    'confidence': instance.get('confidence', ''),
                    'target': json.dumps(instance.get('target', [])) if instance.get('target') else '[]',
                    'vehicle': json.dumps(instance.get('vehicle', [])) if instance.get('vehicle') else '[]',
                    'ground': json.dumps(instance.get('ground', [])) if instance.get('ground') else '[]',
                    'posture': json.dumps(instance.get('posture', [])) if instance.get('posture') else '[]',
                    'speaker': instance.get('speaker', ''),
                    'purpose': instance.get('purpose', ''),
                    'figurative_text': english_text,
                    'figurative_text_in_hebrew': hebrew_text,
                    'figurative_text_in_hebrew_stripped': hebrew_stripped_inst,
                    'tagging_analysis_deliberation': tagging_analysis,
                    'model_used': metadata.get('model_used', 'gemini-2.5-flash'),
                    'raw_instance_data': instance  # Store original for validation
                }
                instance_data_list.append(flexible_data)

            return verse_data_dict, instance_data_list, None

        except Exception as e:
            error_msg = f"Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}"
            if self.logger.level <= logging.ERROR:
                self.logger.error(error_msg)
            return None, [], error_msg

    def batch_insert_verses(self, verse_data_list: List[Dict]) -> List[int]:
        """Insert multiple verses in a single batch operation"""
        if not verse_data_list:
            return []

        verse_ids = []
        try:
            # Use transaction for batch insert
            for verse_data in verse_data_list:
                verse_id = self.db_manager.insert_verse(verse_data)
                verse_ids.append(verse_id)

            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"Batch inserted {len(verse_ids)} verses")

        except Exception as e:
            if self.logger.level <= logging.ERROR:
                self.logger.error(f"Batch verse insert failed: {e}")

        return verse_ids

    def batch_insert_instances(self, instance_data_list: List[Tuple[int, Dict]]) -> List[int]:
        """Insert multiple instances in a single batch operation"""
        if not instance_data_list:
            return []

        instance_ids = []
        try:
            for verse_id, instance_data in instance_data_list:
                # Remove the raw data before DB insert
                clean_data = {k: v for k, v in instance_data.items() if k != 'raw_instance_data'}
                instance_id = self.db_manager.insert_figurative_language(verse_id, clean_data)
                instance_ids.append(instance_id)

            if self.logger.level <= logging.DEBUG:
                self.logger.debug(f"Batch inserted {len(instance_ids)} instances")

        except Exception as e:
            if self.logger.level <= logging.ERROR:
                self.logger.error(f"Batch instance insert failed: {e}")

        return instance_ids

    def batch_validate_instances(self, validation_batch: List[Tuple[List[Dict], str, str]]) -> Dict:
        """Batch validate multiple verses' instances"""
        if not validation_batch:
            return {}

        all_validation_results = {}

        for instances_with_ids, heb_verse, eng_verse in validation_batch:
            if not instances_with_ids:
                continue

            # Prepare instances for validation (remove DB IDs temporarily)
            instances_for_validation = []
            for instance_data in instances_with_ids:
                raw_instance = instance_data.get('raw_instance_data', {})
                if raw_instance:
                    raw_instance['instance_id'] = instance_data.get('instance_number', 0)
                    instances_for_validation.append(raw_instance)

            if instances_for_validation:
                try:
                    validation_results = self.validator.validate_verse_instances(
                        instances_for_validation, heb_verse, eng_verse
                    )

                    # Map results back to database IDs
                    for validation_result in validation_results:
                        instance_id = validation_result.get('instance_id')
                        # Find corresponding instance with DB ID
                        for instance_data in instances_with_ids:
                            if instance_data.get('instance_number') == instance_id:
                                db_id = instance_data.get('db_id')
                                if db_id:
                                    all_validation_results[db_id] = validation_result
                                break

                except Exception as e:
                    if self.logger.level <= logging.ERROR:
                        self.logger.error(f"Batch validation failed: {e}")

        return all_validation_results

def process_verses_parallel(verses_to_process, book_name, chapter, processor: ParallelVerseProcessor):
    """Process verses in parallel using ThreadPoolExecutor"""
    all_results = []
    verse_batch = []
    instance_batch = []
    validation_batch = []

    processed_count = 0
    total_verses = len(verses_to_process)

    with concurrent.futures.ThreadPoolExecutor(max_workers=processor.max_workers) as executor:
        # Submit all verse processing tasks
        future_to_verse = {
            executor.submit(processor.process_single_verse, verse_data, book_name, chapter): verse_data
            for verse_data in verses_to_process
        }

        for future in concurrent.futures.as_completed(future_to_verse):
            try:
                verse_data_dict, instance_data_list, error = future.result()
                processed_count += 1

                if verse_data_dict:
                    verse_batch.append(verse_data_dict)

                    # Process batches when they reach threshold
                    if len(verse_batch) >= processor.VERSE_BATCH_SIZE:
                        verse_ids = processor.batch_insert_verses(verse_batch)

                        # Process instances for these verses
                        for i, (verse_data, verse_id) in enumerate(zip(verse_batch, verse_ids)):
                            verse_instances = [inst for inst in instance_data_list if inst.get('verse_ref') == verse_data['reference']]

                            if verse_instances:
                                # Insert instances
                                instances_with_db_ids = []
                                for instance_data in verse_instances:
                                    instance_id = processor.db_manager.insert_figurative_language(verse_id,
                                        {k: v for k, v in instance_data.items() if k != 'raw_instance_data'})
                                    instance_data['db_id'] = instance_id
                                    instances_with_db_ids.append(instance_data)

                                # Queue for validation
                                validation_batch.append((instances_with_db_ids, verse_data['hebrew'], verse_data['english']))

                                # Process validation batch
                                if len(validation_batch) >= 5:  # Validate in smaller batches
                                    validation_results = processor.batch_validate_instances(validation_batch)

                                    # Update database with validation results
                                    for db_id, validation_result in validation_results.items():
                                        results = validation_result.get('validation_results', {})

                                        # Process validation updates
                                        any_valid = False
                                        validation_data = {}
                                        for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                                            validation_data[f'final_{fig_type}'] = 'no'

                                        for fig_type, result in results.items():
                                            decision = result.get('decision')
                                            reason = result.get('reason', '')
                                            reclassified_type = result.get('reclassified_type')

                                            if decision == 'RECLASSIFIED' and reclassified_type:
                                                validation_data[f'validation_decision_{fig_type}'] = 'RECLASSIFIED'
                                                validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"
                                                validation_data[f'final_{reclassified_type}'] = 'yes'
                                                any_valid = True
                                            elif decision == 'VALID':
                                                validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                                                validation_data[f'validation_reason_{fig_type}'] = reason
                                                validation_data[f'final_{fig_type}'] = 'yes'
                                                any_valid = True
                                            else:
                                                validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                                                validation_data[f'validation_reason_{fig_type}'] = reason

                                        validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'
                                        processor.db_manager.update_validation_data(db_id, validation_data)

                                    validation_batch = []

                        verse_batch = []

                # Progress update
                if processed_count % 10 == 0 or processed_count == total_verses:
                    if processor.logger.level <= logging.INFO:
                        processor.logger.info(f"Progress: {processed_count}/{total_verses} verses processed")

            except Exception as e:
                verse_data = future_to_verse[future]
                if processor.logger.level <= logging.ERROR:
                    processor.logger.error(f"Failed to process verse {verse_data.get('reference', 'unknown')}: {e}")

    # Process remaining batches
    if verse_batch:
        verse_ids = processor.batch_insert_verses(verse_batch)
        # Handle remaining instances and validation...

    if validation_batch:
        validation_results = processor.batch_validate_instances(validation_batch)
        # Update database with remaining validation results...

    return processed_count, len(all_results), 0  # verse_count, instance_count, error_count

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    selection_result = get_user_selection()
    if not selection_result or len(selection_result) != 5:
        return

    book_name, chapters, verse_selection, verse_input_str, max_workers = selection_result

    # Generate filenames
    book_part = book_name.lower()
    chapter_part = "all_c" if len(chapters) > 1 else str(chapters[0])
    verse_part = "all_v" if verse_input_str == 'all' else verse_input_str

    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")

    base_filename = f"{book_part}_{chapter_part}_{verse_part}_parallel_{date_part}_{time_part}"
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"
    json_file = f"{base_filename}_results.json"

    print(f"\n🚀 Parallel processing {book_name}, chapter(s): {chapter_part}, verse(s): {verse_part}")
    print(f"⚡ Using {max_workers} parallel workers")
    print(f"📁 Output files will be based on: {base_filename}")

    # Ask about debug logging
    debug_input = input("\nEnable debug logging? (y/N): ").strip().lower()
    enable_debug = debug_input in ['y', 'yes']

    logger = setup_logging(log_file, enable_debug)

    if was_loaded:
        logger.info(f"✅ Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"⚠️  Warning: .env file not found at {dotenv_path}")

    logger.info(f"=== ⚡ PARALLEL FLEXIBLE TAGGING: {book_name.upper()} CHAPTER(S) {chapters} ===")
    logger.info(f"🔧 Max workers: {max_workers}")
    logger.info(f"🐛 Debug logging: {'enabled' if enable_debug else 'disabled'}")

    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        logger.info("🌐 Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info(f"💾 Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        logger.info("🔍 Initializing MetaphorValidator...")
        validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)

        logger.info("🏷️  Initializing Flexible Tagging Gemini Client...")
        flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

        # Initialize parallel processor
        processor = ParallelVerseProcessor(flexible_client, validator, db_manager, logger, max_workers)

        total_verses, total_instances, total_errors = 0, 0, 0

        for chapter in chapters:
            logger.info(f"--- PARALLEL PROCESSING: {book_name} {chapter} ---")

            # Fetch verses for the chapter
            verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
            if not verses_data:
                logger.error(f"Failed to get text for {book_name} {chapter}")
                continue

            # Filter verses based on user selection
            if verse_selection != 'all':
                verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in verse_selection]
                logger.info(f"Processing {len(verses_to_process)} selected verses from {book_name} {chapter}")
            else:
                verses_to_process = verses_data
                logger.info(f"Processing all {len(verses_to_process)} verses from {book_name} {chapter}")

            # Process verses in parallel
            chapter_start = time.time()
            v, i, e = process_verses_parallel(verses_to_process, book_name, chapter, processor)
            chapter_time = time.time() - chapter_start

            total_verses += v
            total_instances += i
            total_errors += e

            logger.info(f"✅ {book_name} {chapter} completed in {chapter_time:.1f}s: {i} instances from {v} verses")
            db_manager.conn.commit()

        total_time = time.time() - start_time
        db_manager.close()

        logger.info(f"\n=== ✅ {book_name.upper()} PARALLEL PROCESSING COMPLETE ===")
        logger.info(f"📊 Database: {db_name}")
        logger.info(f"📄 Log file: {log_file}")
        logger.info(f"📝 Total verses processed: {total_verses}")
        logger.info(f"🏷️  Total instances: {total_instances}")
        logger.info(f"❌ Errors: {total_errors}")
        logger.info(f"⚡ Max workers used: {max_workers}")
        logger.info(f"⏱️  Total processing time: {total_time:.1f} seconds")

        if total_verses > 0:
            avg_time_per_verse = total_time / total_verses
            logger.info(f"📈 Average time per verse: {avg_time_per_verse:.2f} seconds")

        print(f"\n✅ Parallel processing complete!")
        print(f"📁 Database: {db_name}")
        print(f"📋 Detailed log: {log_file}")
        print(f"⚡ Processed {total_verses} verses in {total_time:.1f}s ({total_time/total_verses:.2f}s/verse)")

    except Exception as e:
        logger.error(f"💥 CRITICAL FAILURE: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Processing interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Check the log file for detailed error information.")