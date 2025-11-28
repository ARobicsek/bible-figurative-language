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
    """Get flexible book, chapter, and verse selection from user with parallel settings"""
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
        "Proverbs": 31
    }

    print("\n=== INTERACTIVE PARALLEL HEBREW FIGURATIVE LANGUAGE PROCESSOR ===")
    print("Enhanced version with flexible multi-book, multi-chapter, multi-verse selection + parallel processing")
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
            print("    Verse Selection Examples:")
            print(f"      - Single: '5'")
            print(f"      - Multiple: '1,3,7'")
            print(f"      - Range: '5-10'")
            print(f"      - Mixed: '1,3,5-7,10'")
            print(f"      - All: 'all'")

            verse_input = input(f"    Enter verses for {book_name} {chapter}: ").strip()

            if verse_input.lower() == 'all':
                selected_verses = 'ALL_VERSES'
            else:
                # We'll validate actual verse ranges during processing
                # For now, just store the input for later processing
                selected_verses = verse_input

            chapter_verse_map[chapter] = selected_verses
            print(f"    Selected verses for {book_name} {chapter}: {selected_verses}")

        book_selections[book_name] = chapter_verse_map

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
        'book_selections': book_selections,
        'max_workers': max_workers,
        'enable_debug': enable_debug
    }

def process_single_verse(verse_data, book_name, chapter, flexible_client, validator, divine_names_modifier, logger, worker_id, chapter_context=None):
    """Process a single verse for parallel execution

    Args:
        verse_data: Dict with verse reference, hebrew, and english text
        book_name: Name of the book being processed
        chapter: Chapter number
        flexible_client: FlexibleTaggingGeminiClient instance
        validator: MetaphorValidator instance
        divine_names_modifier: HebrewDivineNamesModifier instance
        logger: Logger instance
        worker_id: Worker thread ID
        chapter_context: Optional full chapter text for context (used for Proverbs and other wisdom literature)
    """
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        if logger.level <= logging.INFO:
            logger.info(f"Worker {worker_id}: Processing {verse_ref}")

        # Use flexible tagging analysis (with chapter context for Proverbs)
        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter, chapter_context=chapter_context
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
                heb_verse, eng_verse, book=book_name, chapter=chapter, model_override="gemini-2.5-pro",
                chapter_context=chapter_context
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
                        heb_verse, eng_verse, book=book_name, chapter=chapter, chapter_context=chapter_context
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
        figurative_detection_non_sacred = divine_names_modifier.modify_divine_names(figurative_detection) if figurative_detection else ''

        # SAFEGUARD: Ensure we don't have truncated deliberation from fallback scenarios
        # If we used Pro model or Claude fallback, verify the deliberation is complete
        if (pro_model_used or tertiary_decomposed) and figurative_detection:
            # Check for known truncation patterns that indicate incomplete deliberation
            truncation_patterns = [
                'I have included this in the',
                'It is included in the',
                'marked it as such in the',
                'I have marked it as such in the',
                'included in the'
            ]

            if any(figurative_detection.endswith(pattern) for pattern in truncation_patterns):
                if logger.level <= logging.WARNING:
                    logger.warning(f"Worker {worker_id}: Detected truncated deliberation in {verse_ref} despite fallback model usage")
                    logger.warning(f"Worker {worker_id}: Deliberation ends with: '{figurative_detection[-100:]}'")

                # Mark as potentially incomplete
                figurative_detection += " [TRUNCATION DETECTED DESPITE FALLBACK]"

        # Determine final model used
        final_model_used = metadata.get('model_used', 'gemini-2.5-flash')
        if tertiary_decomposed and metadata.get('claude_fallback_used'):
            final_model_used = 'claude-sonnet-4-20250514'
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
            'figurative_detection_deliberation_non_sacred': figurative_detection_non_sacred,
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

def process_verses_parallel(verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context=None):
    """Process verses in parallel and store results

    Args:
        verses_to_process: List of verse data dicts
        book_name: Name of the book
        chapter: Chapter number
        flexible_client: FlexibleTaggingGeminiClient instance
        validator: MetaphorValidator instance
        divine_names_modifier: HebrewDivineNamesModifier instance
        db_manager: DatabaseManager instance
        logger: Logger instance
        max_workers: Number of parallel workers
        chapter_context: Optional full chapter text for context (used for Proverbs)
    """

    logger.info(f"Starting parallel processing: {len(verses_to_process)} verses with {max_workers} workers")
    if chapter_context:
        logger.info(f"Using chapter context for {book_name} {chapter} (wisdom literature mode)")

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
                flexible_client, validator, divine_names_modifier, logger, worker_id, chapter_context
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
    # Look for .env in parent directory (project root), not in private/
    project_root = os.path.dirname(os.path.dirname(__file__))
    dotenv_path = os.path.join(project_root, '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    # Get user selection
    selection = get_user_selection()
    if not selection:
        return

    book_selections = selection['book_selections']
    max_workers = selection['max_workers']
    enable_debug = selection['enable_debug']

    # Generate filename from selections (similar to the single-threaded version)
    def generate_filename_from_selections(book_selections):
        now = datetime.now()
        date_part = now.strftime("%Y%m%d")
        time_part = now.strftime("%H%M")

        if len(book_selections) == 1:
            # Single book
            book_name = list(book_selections.keys())[0]
            book_part = book_name.lower()

            if book_selections[book_name] == 'FULL_BOOK':
                chapter_part = "full"
                verse_part = "full"
            else:
                chapters = list(book_selections[book_name].keys())
                if len(chapters) == 1:
                    chapter_part = str(chapters[0])
                    verses = book_selections[book_name][chapters[0]]
                    if verses == 'ALL_VERSES':
                        verse_part = "all_v"
                    else:
                        verse_part = f"custom_v"
                else:
                    chapter_part = f"c{len(chapters)}"
                    verse_part = "multi_v"
        else:
            # Multiple books
            book_part = f"{len(book_selections)}books"
            total_chapters = 0
            for book_name, chapters in book_selections.items():
                if chapters == 'FULL_BOOK':
                    books_info = {
                        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
                        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
                        "Proverbs": 31
                    }
                    total_chapters += books_info.get(book_name, 25)
                else:
                    total_chapters += len(chapters)
            chapter_part = f"c{total_chapters}"
            verse_part = "multi_v"

        base_filename = f"{book_part}_{chapter_part}_{verse_part}_parallel_{date_part}_{time_part}"
        return base_filename

    base_filename = generate_filename_from_selections(book_selections)
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"
    json_file = f"{base_filename}_results.json"

    # Create summary of what will be processed
    books_info = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
        "Proverbs": 31
    }

    total_tasks = 0
    summary_lines = []

    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            # Estimate verses for full book (approximate)
            verse_estimates = {
                "Genesis": 1533, "Exodus": 1213, "Leviticus": 859,
                "Numbers": 1288, "Deuteronomy": 959, "Psalms": 2461,
                "Proverbs": 915
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
                    # For specific verse selections, we'll count during processing
                    total_tasks += 20  # Rough estimate
                    summary_lines.append(f"  {book_name} {chapter}: selected verses")

    print(f"\n=== PARALLEL PROCESSING SUMMARY ===")
    print(f"Books: {len(book_selections)}")
    print(f"Estimated verses to process: ~{total_tasks}")
    for line in summary_lines[:10]:  # Show first 10 for brevity
        print(line)
    if len(summary_lines) > 10:
        print(f"  ... and {len(summary_lines) - 10} more chapter/verse combinations")
    print(f"\nParallel workers: {max_workers}")
    print(f"Debug logging: {'enabled' if enable_debug else 'disabled'}")
    print(f"Output files: {base_filename}.*")

    proceed = input("\nProceed with parallel processing? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Processing cancelled.")
        return

    logger = setup_logging(log_file, enable_debug)

    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}")

    # Log processing summary
    logger.info(f"=== MULTI-BOOK PARALLEL PROCESSING STARTED ===")
    logger.info(f"Total books: {len(book_selections)}")
    logger.info(f"Estimated verses: ~{total_tasks}")
    logger.info(f"Workers: {max_workers}")
    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            logger.info(f"Book: {book_name} - FULL BOOK")
        else:
            logger.info(f"Book: {book_name} - Chapters: {list(chapters.keys())}")

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

        # Process each book, chapter, and verse selection
        for book_name, chapters in book_selections.items():
            logger.info(f"\n=== PROCESSING BOOK: {book_name.upper()} ===")

            if chapters == 'FULL_BOOK':
                # Process entire book - all chapters, all verses
                books_info = {
                    "Genesis": 50, "Exodus": 40, "Leviticus": 27,
                    "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
                    "Proverbs": 31
                }
                max_chapters = books_info[book_name]
                logger.info(f"Processing full book: all {max_chapters} chapters with all verses")

                for chapter in range(1, max_chapters + 1):
                    logger.info(f"--- PROCESSING: {book_name} {chapter} (FULL BOOK) ---")

                    # Fetch all verses for the chapter
                    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
                    if not verses_data:
                        logger.error(f"Failed to get text for {book_name} {chapter}")
                        continue

                    logger.info(f"Processing all {len(verses_data)} verses from {book_name} {chapter}")

                    # Generate chapter context for Proverbs (wisdom literature needs full chapter context)
                    chapter_context_text = None
                    if book_name == "Proverbs":
                        # Build full chapter text from all verses
                        hebrew_chapter = "\n".join([v['hebrew'] for v in verses_data])
                        english_chapter = "\n".join([v['english'] for v in verses_data])
                        chapter_context_text = f"=== {book_name} Chapter {chapter} ===\n\nHebrew:\n{hebrew_chapter}\n\nEnglish:\n{english_chapter}"
                        logger.info(f"Generated chapter context for Proverbs {chapter} ({len(chapter_context_text)} chars)")

                    # Process verses in parallel
                    v, i, processing_time, total_attempted = process_verses_parallel(
                        verses_data, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context_text
                    )

                    total_verses += v
                    total_instances += i

                    logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s")
                    if total_attempted > 0:
                        logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                    db_manager.commit()
            else:
                # Process specific chapters and verses
                for chapter, verse_selection in chapters.items():
                    logger.info(f"--- PROCESSING: {book_name} {chapter} ---")

                    # Fetch verses for the chapter
                    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
                    if not verses_data:
                        logger.error(f"Failed to get text for {book_name} {chapter}")
                        continue

                    # Filter verses based on user selection
                    if verse_selection == 'ALL_VERSES':
                        verses_to_process = verses_data
                        logger.info(f"Processing all {len(verses_to_process)} verses from {book_name} {chapter}")
                    else:
                        # Parse the verse selection string
                        max_verses = len(verses_data)
                        if isinstance(verse_selection, str) and verse_selection.lower() != 'all':
                            parsed_verses = parse_selection(verse_selection, max_verses, "verse")
                            if parsed_verses:
                                verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in parsed_verses]
                                logger.info(f"Processing {len(verses_to_process)} selected verses: {parsed_verses}")
                            else:
                                logger.error(f"Invalid verse selection: {verse_selection}")
                                continue
                        else:
                            verses_to_process = verses_data
                            logger.info(f"Processing all {len(verses_to_process)} verses from {book_name} {chapter}")

                    # Generate chapter context for Proverbs (wisdom literature needs full chapter context)
                    chapter_context_text = None
                    if book_name == "Proverbs":
                        # Build full chapter text from all verses
                        hebrew_chapter = "\n".join([v['hebrew'] for v in verses_data])
                        english_chapter = "\n".join([v['english'] for v in verses_data])
                        chapter_context_text = f"=== {book_name} Chapter {chapter} ===\n\nHebrew:\n{hebrew_chapter}\n\nEnglish:\n{english_chapter}"
                        logger.info(f"Generated chapter context for Proverbs {chapter} ({len(chapter_context_text)} chars)")

                    # Process verses in parallel
                    v, i, processing_time, total_attempted = process_verses_parallel(
                        verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context_text
                    )

                    total_verses += v
                    total_instances += i

                    logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s")
                    if total_attempted > 0:
                        logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                    db_manager.commit()

        total_time = time.time() - start_time
        db_manager.close()

        # Generate summary
        print(f"\n=== PARALLEL PROCESSING COMPLETE ===")
        print(f"Database: {db_name}")
        print(f"Log file: {log_file}")
        print(f"Books processed: {len(book_selections)}")
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
        print(f"\n🚀 Processed {total_verses} verses from {len(book_selections)} books")
        print(f"⚡ Total time: {total_time:.1f} seconds with {max_workers} parallel workers")

        # Save basic results summary
        summary = {
            'processing_info': {
                'books_processed': len(book_selections),
                'book_selections': {k: 'FULL_BOOK' if v == 'FULL_BOOK' else list(v.keys()) for k, v in book_selections.items()},
                'max_workers': max_workers,
                'timestamp': datetime.now().isoformat(),
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

        logger.info(f"=== PARALLEL PROCESSING COMPLETE ===")
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