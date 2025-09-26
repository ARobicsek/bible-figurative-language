#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Flexible Tagging Processor
Adapts the interactive multi-model processor for the revolutionary flexible tagging system.
Allows testing on specific chapters/verses with hierarchical tag output.
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
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Import our flexible tagging client
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

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

    print("\n=== HEBREW FIGURATIVE LANGUAGE FLEXIBLE TAGGING PROCESSOR ===")
    print("Revolutionary hierarchical tag generation system")
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

def process_chapter_flexible(book_name, chapter, verse_selection, sefaria, flexible_client, validator, db_manager, logger):
    """Process a single chapter using flexible tagging"""
    logger.info(f"--- FLEXIBLE TAGGING: {book_name} {chapter} ---")

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
    all_flexible_results = []

    for i, verse_data in enumerate(verses_to_process):
        try:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            chapter_verses += 1

            logger.info(f"  🔍 Processing {verse_ref} ({i+1}/{len(verses_to_process)})...")

            # Use flexible tagging analysis
            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book=book_name, chapter=chapter
            )

            truncation_occurred = metadata.get('truncation_detected', False)
            pro_model_recovery_successful = False
            if truncation_occurred:
                logger.warning(f"  ⚠️ Truncation detected in initial analysis of {verse_ref}. Retrying with fallback model.")
                # Retry with fallback model
                result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                    heb_verse, eng_verse, book=book_name, chapter=chapter, model_override="gemini-2.5-pro"
                )
                # Check if Pro model successfully recovered (no truncation in second attempt)
                pro_model_recovery_successful = not metadata.get('truncation_detected', False)
                logger.info(f"    📊 Fallback Analysis Metadata: {metadata.get('model_used', 'unknown')} | "
                           f"Instances: {metadata.get('instances_count', 0)} | "
                           f"Recovery successful: {pro_model_recovery_successful}")

            logger.info(f"    📊 Flexible Tagging Metadata: {metadata.get('model_used', 'unknown')} | "
                       f"Instances: {metadata.get('instances_count', 0)} | "
                       f"Fallback: {metadata.get('fallback_used', False)}")

            # Strip diacritics from Hebrew text
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)

            # Store complete verse data in database with all required fields
            instances_count = len(metadata.get('flexible_instances', []))

            # Extract deliberation data that should be stored with verse
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
                'figurative_detection_deliberation': figurative_detection,  # Store with every verse
                'instances_detected': instances_count,
                'instances_recovered': instances_count,  # Same as detected for flexible tagging
                'instances_lost_to_truncation': 1 if truncation_occurred and not pro_model_recovery_successful else 0,
                'truncation_occurred': 'yes' if truncation_occurred else 'no'
            }
            verse_id = db_manager.insert_verse(verse_data_dict)
            logger.debug(f"    💾 Verse stored in database with ID: {verse_id}")

            if error:
                logger.error(f"❌ Flexible tagging error for {verse_ref}: {error}")
                chapter_errors += 1
                continue

            # Process flexible tagging results
            flexible_instances = metadata.get('flexible_instances', [])
            tagging_analysis = metadata.get('tagging_analysis_deliberation', '')

            # Log deliberation for debugging
            if figurative_detection:
                logger.info(f"    💭 FIGURATIVE DETECTION: {figurative_detection[:150]}...")
            if tagging_analysis:
                logger.info(f"    🏷️  TAGGING ANALYSIS: {tagging_analysis[:150]}...")
            if not figurative_detection and not tagging_analysis:
                logger.warning(f"    ⚠️ No deliberation found in metadata")

            if flexible_instances:
                logger.info(f"    ✅ DETECTED: {len(flexible_instances)} flexible instances")

                # First, insert all detected instances and get their DB IDs
                instances_with_db_ids = []
                for j, instance in enumerate(flexible_instances):
                    if not isinstance(instance, dict):
                        logger.warning(f"    ⚠️ Instance {j+1} is not a dict, skipping.")
                        continue

                    hebrew_text = instance.get('hebrew_text', '')
                    english_text = instance.get('english_text', '')
                    hebrew_stripped = HebrewTextProcessor.strip_diacritics(hebrew_text) if hebrew_text else ''

                    flexible_data = {
                        'verse': verse_ref,
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
                        'figurative_text_in_hebrew_stripped': hebrew_stripped,
                        'tagging_analysis_deliberation': tagging_analysis,
                        'model_used': metadata.get('model_used', 'gemini-2.5-flash')
                    }

                    figurative_language_id = db_manager.insert_figurative_language(verse_id, flexible_data)
                    logger.debug(f"        💾 Flexible instance stored with ID: {figurative_language_id}")
                    
                    # Keep track of instance and its new DB ID
                    instance['db_id'] = figurative_language_id
                    instances_with_db_ids.append(instance)

                # VALIDATION STEP - New bulk validation call
                if validator and instances_with_db_ids:
                    logger.info(f"    🔍 Starting bulk validation for {len(instances_with_db_ids)} instances...")
                    bulk_validation_results = validator.validate_verse_instances(instances_with_db_ids, heb_verse, eng_verse)

                    # Create a mapping from instance_id to db_id for easy lookup
                    instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                    # Process the bulk results
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
                                logger.info(f"        🔄 RECLASSIFIED: {fig_type} → {reclassified_type} - {reason}")
                            elif decision == 'VALID':
                                validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                validation_data[f'final_{fig_type}'] = 'yes'
                                any_valid = True
                                logger.info(f"        ✅ VALID: {fig_type} - {reason}")
                            else: # INVALID
                                validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                logger.info(f"        ❌ INVALID: {fig_type} - {reason}")

                        validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'
                        
                        db_manager.update_validation_data(db_id, validation_data)
                        logger.debug(f"        💾 Bulk validation data updated for ID: {db_id}")

                # Prepare data for JSON output
                for instance in instances_with_db_ids:
                    display_data = instance.copy()
                    # Clean up internal IDs before final output
                    display_data.pop('db_id', None)
                    display_data.pop('instance_id', None)
                    display_data['figurative_language_id'] = instance['db_id'] # Ensure the final JSON has the db id
                    display_data['metadata'] = metadata
                    all_flexible_results.append(display_data)

                chapter_instances += len(instances_with_db_ids)
            else:
                logger.debug(f"    ⚪ No figurative language detected")

        except Exception as e:
            logger.error(f"❌ Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            chapter_errors += 1

    logger.info(f"✅ {book_name} {chapter} COMPLETED: {chapter_instances} flexible instances from {chapter_verses} verses")
    return chapter_verses, chapter_instances, chapter_errors, all_flexible_results

def main():
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    book_name, chapters, verse_selection, verse_input_str = get_user_selection()
    if not book_name:
        return

    # Generate filenames
    book_part = book_name.lower()
    chapter_part = "all_c" if len(chapters) > 1 else str(chapters[0])
    verse_part = "all_v" if verse_input_str == 'all' else verse_input_str

    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")

    base_filename = f"{book_part}_{chapter_part}_{verse_part}_flexible_{date_part}_{time_part}"
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"
    json_file = f"{base_filename}_results.json"

    print(f"\n🚀 Processing {book_name}, chapter(s): {chapter_part}, verse(s): {verse_part}")
    print(f"📁 Output files will be based on: {base_filename}")

    logger = setup_logging(log_file)
    if was_loaded:
        logger.info(f"✅ Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"⚠️  Warning: .env file not found at {dotenv_path}. Relying on system environment variables.")

    logger.info(f"=== 🏷️  FLEXIBLE TAGGING ANALYSIS: {book_name.upper()} CHAPTER(S) {chapters} ===")
    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found. Please ensure a .env file with the key exists in the script's directory, or that the environment variable is set.")

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

        total_verses, total_instances, total_errors = 0, 0, 0
        all_results = []

        for chapter in chapters:
            v, i, e, chapter_results = process_chapter_flexible(
                book_name, chapter, verse_selection, sefaria, flexible_client, validator, db_manager, logger
            )
            total_verses += v
            total_instances += i
            total_errors += e
            all_results.extend(chapter_results)
            db_manager.conn.commit()

        total_time = time.time() - start_time
        db_manager.close()

        # Save flexible tagging results to JSON
        output_data = {
            'processing_info': {
                'book': book_name,
                'chapters': chapters,
                'verse_selection': verse_selection,
                'timestamp': now.isoformat(),
                'total_verses': total_verses,
                'total_instances': total_instances,
                'total_errors': total_errors,
                'processing_time_seconds': total_time
            },
            'flexible_tagging_results': all_results,
            'usage_statistics': flexible_client.get_usage_info(),
            'validation_statistics': validator.get_validation_stats() if validator else {}
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n=== ✅ {book_name.upper()} FLEXIBLE TAGGING COMPLETE ===")
        logger.info(f"📊 Database: {db_name}")
        logger.info(f"📄 JSON Results: {json_file}")
        logger.info(f"📋 Log file: {log_file}")
        logger.info(f"📝 Total verses processed: {total_verses}")
        logger.info(f"🏷️  Total flexible instances: {total_instances}")
        logger.info(f"❌ Errors: {total_errors}")
        logger.info(f"⏱️  Processing time: {total_time:.1f} seconds")

        logger.info("\n--- 📈 Flexible Tagging API Usage Statistics ---")
        usage_stats = flexible_client.get_usage_info()
        for key, value in usage_stats.items():
            logger.info(f"{key.replace('_', ' ').title()}: {value}")

        print(f"\n✅ Flexible tagging analysis complete!")
        print(f"📁 Database: {db_name}")
        print(f"📄 JSON Results: {json_file}")
        print(f"📋 Detailed log: {log_file}")

        # Show sample results if any instances found
        if total_instances > 0:
            print(f"\n🎯 Sample Flexible Tagging Results (first 3 instances):")
            for i, result in enumerate(all_results[:3]):
                # Determine main type
                main_types = []
                for fig_type in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    if result.get(fig_type) == 'yes':
                        main_types.append(fig_type)

                print(f"  {i+1}. {result.get('verse', 'Unknown')} - {', '.join(main_types) if main_types else 'Unknown'}")
                print(f"     Text: {result.get('english_text', 'N/A')}")
                print(f"     Confidence: {result.get('confidence', 'N/A')}")

                # Show hierarchical tags
                target = result.get('target', [])
                vehicle = result.get('vehicle', [])
                ground = result.get('ground', [])
                posture = result.get('posture', [])

                if target:
                    print(f"     TARGET: {target}")
                if vehicle:
                    print(f"     VEHICLE: {vehicle}")
                if ground:
                    print(f"     GROUND: {ground}")
                if posture:
                    print(f"     POSTURE: {posture}")

                # Show deliberation excerpts
                fig_detection = result.get('figurative_detection_deliberation', '')
                tag_analysis = result.get('tagging_analysis_deliberation', '')
                if fig_detection:
                    print(f"     FIGURATIVE_DETECTION (first 100 chars): {fig_detection[:100]}...")
                if tag_analysis:
                    print(f"     TAGGING_ANALYSIS (first 100 chars): {tag_analysis[:100]}...")

                print()

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