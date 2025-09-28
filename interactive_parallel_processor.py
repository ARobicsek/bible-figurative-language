#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Parallel Flexible Tagging Processor
User-friendly interface with high-performance parallel processing
"""
import sys
import os
import logging
import traceback
import json
import time
import re
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier
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
    """Get book, chapter, and verse selection from user with parallel settings"""
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34
    }

    print("\n=== INTERACTIVE PARALLEL HEBREW FIGURATIVE LANGUAGE PROCESSOR ===")
    print("High-performance processing with interactive selection")
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
            return None

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
            return None

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
            return None

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
                return None

    # Get parallelization settings
    print(f"\nPARALLEL PROCESSING SETTINGS:")
    print(f"Recommended: 6-8 workers (balance of speed vs API limits)")
    print(f"Conservative: 2-4 workers (slower but more reliable)")
    print(f"Aggressive: 8-12 workers (faster but may hit rate limits)")

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
            return None

    # Get logging level preference
    debug_choice = input("\nEnable detailed debug logging? (y/N): ").strip().lower()
    enable_debug = debug_choice in ['y', 'yes']

    return {
        'book_name': book_name,
        'chapters': chapters,
        'verse_selection': verse_selection,
        'verse_input_str': verse_input_str,
        'max_workers': max_workers,
        'enable_debug': enable_debug
    }

def process_single_verse(verse_data, book_name, chapter, flexible_client, validator, divine_names_modifier, logger, worker_id):
    """Process a single verse for parallel execution"""
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        if logger.level <= logging.INFO:
            logger.info(f"Worker {worker_id}: Processing {verse_ref}")

        # Use flexible tagging analysis
        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter
        )

        # Handle truncation fallback
        truncation_occurred = metadata.get('truncation_detected', False)
        pro_model_used = False
        both_models_truncated = False
        tertiary_decomposed = False

        if truncation_occurred:
            if logger.level <= logging.WARNING:
                logger.warning(f"Worker {worker_id}: Truncation detected in {verse_ref}, retrying with Pro model")

            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book=book_name, chapter=chapter, model_override="gemini-2.5-pro"
            )
            pro_model_used = True

            # Check if Pro model also truncated
            pro_truncation_occurred = metadata.get('truncation_detected', False)
            both_models_truncated = pro_truncation_occurred
            if pro_truncation_occurred:
                if logger.level <= logging.WARNING:
                    logger.warning(f"Worker {worker_id}: Pro model also truncated for {verse_ref} - trying Claude Sonnet 4 fallback")

                # Claude Sonnet 4 fallback
                try:
                    result_text, error, metadata = flexible_client.analyze_with_claude_fallback(
                        heb_verse, eng_verse, book=book_name, chapter=chapter
                    )
                    tertiary_decomposed = True

                    claude_success = not error and metadata.get('instances_count', 0) >= 0
                    instances_found = metadata.get('instances_count', 0)

                    if logger.level <= logging.INFO:
                        logger.info(f"Worker {worker_id}: Claude fallback completed for {verse_ref} - "
                                   f"Success: {claude_success}, Instances: {instances_found}")

                    # Keep both_models_truncated as True since both Gemini models failed
                    # Don't overwrite - both Gemini models actually truncated regardless of Claude success

                except Exception as claude_error:
                    if logger.level <= logging.ERROR:
                        logger.error(f"Worker {worker_id}: Claude fallback failed for {verse_ref}: {claude_error}")
                    # both_models_truncated stays True - both Gemini models truncated

                # Keep truncation_occurred as True to indicate the verse had truncation issues
                truncation_occurred = True

        # Prepare verse data
        hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)
        hebrew_non_sacred = divine_names_modifier.modify_divine_names(heb_verse)
        english_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(eng_verse)
        instances_count = len(metadata.get('flexible_instances', []))
        figurative_detection = metadata.get('figurative_detection_deliberation', '')

        # Determine final model used
        final_model_used = metadata.get('model_used', 'gemini-2.5-flash')
        if tertiary_decomposed and metadata.get('claude_fallback_used'):
            final_model_used = 'claude-3-5-sonnet-20241022'
        elif pro_model_used:
            final_model_used = 'gemini-2.5-pro'

        verse_result = {
            'reference': verse_ref,
            'book': book_name,
            'chapter': chapter,
            'verse': int(verse_ref.split(':')[1]),
            'hebrew': heb_verse,
            'hebrew_stripped': hebrew_stripped,
            'hebrew_text_non_sacred': hebrew_non_sacred,
            'english': eng_verse,
            'english_text_non_sacred': english_non_sacred,
            'word_count': len(heb_verse.split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': figurative_detection,
            'instances_detected': instances_count,
            'instances_recovered': instances_count,
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'yes' if truncation_occurred else 'no',
            'both_models_truncated': 'yes' if both_models_truncated else 'no',
            'model_used': final_model_used,  # Add to verse-level tracking
            'worker_id': worker_id,
            'instances': metadata.get('flexible_instances', []),
            'tagging_analysis': metadata.get('tagging_analysis_deliberation', ''),
            'tertiary_decomposed': tertiary_decomposed
        }

        if logger.level <= logging.INFO:
            logger.info(f"Worker {worker_id}: Completed {verse_ref} - {instances_count} instances")

        return verse_result, None

    except Exception as e:
        error_msg = f"Worker {worker_id}: Error processing {verse_data.get('reference', 'unknown')}: {str(e)}"
        if logger.level <= logging.ERROR:
            logger.error(error_msg)
        return None, error_msg

def process_verses_parallel(verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers):
    """Process verses in parallel and store results"""

    logger.info(f"Starting parallel processing: {len(verses_to_process)} verses with {max_workers} workers")

    all_verse_results = []
    all_instance_results = []

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all verse processing tasks
        future_to_verse = {}
        for i, verse_data in enumerate(verses_to_process):
            worker_id = (i % max_workers) + 1
            future = executor.submit(
                process_single_verse, verse_data, book_name, chapter,
                flexible_client, validator, divine_names_modifier, logger, worker_id
            )
            future_to_verse[future] = verse_data

        # Collect results as they complete
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_verse):
            verse_data = future_to_verse[future]
            try:
                verse_result, error = future.result()
                completed_count += 1

                if verse_result:
                    all_verse_results.append(verse_result)

                    # Process instances for this verse
                    instances = verse_result.get('instances', [])
                    for j, instance in enumerate(instances):
                        if isinstance(instance, dict):
                            instance_result = {
                                'verse_ref': verse_result['reference'],
                                'instance_number': j + 1,
                                'instance_data': instance,
                                'tagging_analysis': verse_result.get('tagging_analysis', ''),
                                'model_used': verse_result.get('model_used', 'gemini-2.5-flash'),
                                'tertiary_decomposed': verse_result.get('tertiary_decomposed', False)
                            }
                            all_instance_results.append(instance_result)

                # Progress update
                if completed_count % 5 == 0 or completed_count == len(verses_to_process):
                    logger.info(f"Progress: {completed_count}/{len(verses_to_process)} verses completed")

            except Exception as e:
                logger.error(f"Failed to process verse {verse_data.get('reference', 'unknown')}: {e}")

    processing_time = time.time() - start_time

    # Store results in database
    logger.info("Storing results in database...")

    verses_stored = 0
    instances_stored = 0

    for verse_result in all_verse_results:
        try:
            # Store verse
            verse_data = {k: v for k, v in verse_result.items()
                         if k not in ['instances', 'tagging_analysis', 'worker_id', 'tertiary_decomposed']}
            verse_id = db_manager.insert_verse(verse_data)
            verses_stored += 1

            # Store instances for this verse
            verse_instances = [inst for inst in all_instance_results
                             if inst['verse_ref'] == verse_result['reference']]

            # Store instances first, then validate
            instances_with_db_ids = []

            for instance_result in verse_instances:
                instance_data = instance_result['instance_data']

                # Prepare instance data for database
                figurative_data = {
                    'figurative_language': instance_data.get('figurative_language', 'no'),
                    'simile': instance_data.get('simile', 'no'),
                    'metaphor': instance_data.get('metaphor', 'no'),
                    'personification': instance_data.get('personification', 'no'),
                    'idiom': instance_data.get('idiom', 'no'),
                    'hyperbole': instance_data.get('hyperbole', 'no'),
                    'metonymy': instance_data.get('metonymy', 'no'),
                    'other': instance_data.get('other', 'no'),
                    'confidence': instance_data.get('confidence', 0.5),
                    'figurative_text': instance_data.get('english_text', ''),
                    'figurative_text_in_hebrew': instance_data.get('hebrew_text', ''),
                    'figurative_text_in_hebrew_stripped': HebrewTextProcessor.strip_diacritics(instance_data.get('hebrew_text', '')),
                    'figurative_text_in_hebrew_non_sacred': divine_names_modifier.modify_divine_names(instance_data.get('hebrew_text', '')),
                    'explanation': instance_data.get('explanation', ''),
                    'speaker': instance_data.get('speaker', ''),
                    'purpose': instance_data.get('purpose', ''),
                    'target': json.dumps(instance_data.get('target', [])) if instance_data.get('target') else '[]',
                    'vehicle': json.dumps(instance_data.get('vehicle', [])) if instance_data.get('vehicle') else '[]',
                    'ground': json.dumps(instance_data.get('ground', [])) if instance_data.get('ground') else '[]',
                    'posture': json.dumps(instance_data.get('posture', [])) if instance_data.get('posture') else '[]',
                    'tagging_analysis_deliberation': instance_result.get('tagging_analysis', ''),
                    'model_used': instance_result.get('model_used', 'gemini-2.5-flash')
                }

                figurative_language_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                instances_stored += 1

                # Keep track of instance and its new DB ID for validation
                instance_data['db_id'] = figurative_language_id
                instances_with_db_ids.append(instance_data)

            # VALIDATION STEP - Add bulk validation for all instances in this verse
            if validator and instances_with_db_ids:
                try:
                    logger.debug(f"Starting validation for {len(instances_with_db_ids)} instances in {verse_result['reference']}")
                    bulk_validation_results = validator.validate_verse_instances(instances_with_db_ids, verse_result['hebrew'], verse_result['english'])

                    # Create a mapping from instance_id to db_id for easy lookup
                    instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                    # Process the bulk validation results
                    for validation_result in bulk_validation_results:
                        instance_id = validation_result.get('instance_id')
                        results = validation_result.get('validation_results', {})

                        db_id = instance_id_to_db_id.get(instance_id)

                        if not db_id:
                            logger.error(f"Could not find DB ID for validation result with instance_id {instance_id}")
                            continue

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
                                logger.debug(f"RECLASSIFIED: {fig_type} → {reclassified_type} - {reason}")
                            elif decision == 'VALID':
                                validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                validation_data[f'final_{fig_type}'] = 'yes'
                                any_valid = True
                                logger.debug(f"VALID: {fig_type} - {reason}")
                            else: # INVALID
                                validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                logger.debug(f"INVALID: {fig_type} - {reason}")

                        validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'

                        db_manager.update_validation_data(db_id, validation_data)
                        logger.debug(f"Validation data updated for ID: {db_id}")

                except Exception as e:
                    logger.error(f"Validation failed for {verse_result['reference']}: {e}")

        except Exception as e:
            logger.error(f"Error storing {verse_result['reference']}: {e}")

    return verses_stored, instances_stored, processing_time, len(verses_to_process)

def main():
    """Main execution function"""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    # Get user selection
    selection = get_user_selection()
    if not selection:
        return

    book_name = selection['book_name']
    chapters = selection['chapters']
    verse_selection = selection['verse_selection']
    verse_input_str = selection['verse_input_str']
    max_workers = selection['max_workers']
    enable_debug = selection['enable_debug']

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

    print(f"\nStarting parallel processing:")
    print(f"  Book: {book_name}")
    print(f"  Chapters: {chapter_part}")
    print(f"  Verses: {verse_part}")
    print(f"  Workers: {max_workers}")
    print(f"  Debug logging: {'enabled' if enable_debug else 'disabled'}")
    print(f"  Output files: {base_filename}.*")

    logger = setup_logging(log_file, enable_debug)

    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}")

    logger.info(f"=== INTERACTIVE PARALLEL PROCESSING: {book_name.upper()} ===")
    logger.info(f"Chapters: {chapters}, Verses: {verse_selection}, Workers: {max_workers}")

    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        logger.info("Initializing MetaphorValidator...")
        validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)

        logger.info("Initializing Flexible Tagging Gemini Client...")
        flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

        logger.info("Initializing Hebrew Divine Names Modifier...")
        divine_names_modifier = HebrewDivineNamesModifier(logger=logger)

        total_verses, total_instances, total_errors = 0, 0, 0
        all_results = []

        for chapter in chapters:
            logger.info(f"--- PROCESSING: {book_name} {chapter} ---")

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
            v, i, processing_time, total_attempted = process_verses_parallel(
                verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers
            )

            total_verses += v
            total_instances += i

            logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s")
            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

            db_manager.commit()

        total_time = time.time() - start_time
        db_manager.close()

        # Generate summary
        print(f"\n=== PROCESSING COMPLETE ===")
        print(f"Database: {db_name}")
        print(f"Log file: {log_file}")
        print(f"Total verses processed: {total_verses}")
        print(f"Total instances found: {total_instances}")
        print(f"Total processing time: {total_time:.1f} seconds")
        if total_verses > 0:
            print(f"Average time per verse: {total_time/total_verses:.2f} seconds")
            detection_rate = (total_instances / total_verses) * 100
            print(f"Figurative language detection rate: {detection_rate:.1f}%")
        else:
            print(f"Average time per verse: N/A (no verses processed)")
            print(f"Figurative language detection rate: N/A")
        print(f"Workers used: {max_workers}")

        # Save basic results summary
        summary = {
            'processing_info': {
                'book': book_name,
                'chapters': chapters,
                'verse_selection': verse_selection,
                'max_workers': max_workers,
                'timestamp': now.isoformat(),
                'total_verses': total_verses,
                'total_instances': total_instances,
                'processing_time_seconds': total_time,
                'avg_time_per_verse': total_time/total_verses if total_verses > 0 else 0
            },
            'usage_statistics': flexible_client.get_usage_info(),
            'validation_statistics': validator.get_validation_stats() if validator else {}
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Summary saved: {json_file}")

        logger.info(f"=== PROCESSING COMPLETE ===")
        logger.info(f"Final stats: {total_instances} instances from {total_verses} verses")

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
        print(f"An error occurred: {e}")
        print("Check the log file for detailed error information.")