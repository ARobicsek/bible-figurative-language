#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Flexible Tagging Processor with Full Validation Pipeline
Combines flexible tagging with comprehensive MetaphorValidator validation
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

    print("\n=== HEBREW FIGURATIVE LANGUAGE FLEXIBLE TAGGING + VALIDATION PIPELINE ===")
    print("🚀 Revolutionary hierarchical tagging with comprehensive validation")
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

def process_chapter_with_validation(book_name, chapter, verse_selection, sefaria, flexible_client, validator, db_manager, logger):
    """Process a single chapter using flexible tagging with full validation"""
    logger.info(f"--- FLEXIBLE TAGGING + VALIDATION: {book_name} {chapter} ---")

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
    chapter_validated = 0
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

            logger.info(f"    📊 Flexible Tagging: {metadata.get('model_used', 'unknown')} | "
                       f"Detected: {metadata.get('instances_count', 0)} | "
                       f"Fallback: {metadata.get('fallback_used', False)}")

            # Strip diacritics from Hebrew text
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)

            # Store basic verse data in database
            verse_data_dict = {
                'reference': verse_ref, 'book': book_name, 'chapter': chapter,
                'verse': int(verse_ref.split(':')[1]), 'hebrew': heb_verse,
                'hebrew_stripped': hebrew_stripped,
                'english': eng_verse, 'word_count': len(heb_verse.split()),
                'llm_restriction_error': error,
                'llm_deliberation': metadata.get('llm_deliberation')
            }
            verse_id = db_manager.insert_verse(verse_data_dict)
            logger.debug(f"    💾 Verse stored with ID: {verse_id}")

            if error:
                logger.error(f"❌ Flexible tagging error for {verse_ref}: {error}")
                chapter_errors += 1
                continue

            # Process flexible tagging results with validation
            flexible_instances = metadata.get('flexible_instances', [])
            llm_deliberation = metadata.get('llm_deliberation', '')

            if llm_deliberation:
                logger.debug(f"    💭 DELIBERATION: {llm_deliberation[:100]}...")

            if flexible_instances:
                logger.info(f"    ✅ DETECTED: {len(flexible_instances)} flexible instances")

                for j, instance in enumerate(flexible_instances):
                    instance_type = instance.get('type', 'unknown')
                    english_text = instance.get('english_text', '')
                    confidence = instance.get('confidence', 'medium')
                    explanation = instance.get('explanation', '')

                    logger.info(f"      🏷️  Instance {j+1}: {instance_type} - '{english_text}'")

                    # VALIDATION STEP - Use MetaphorValidator
                    if validator:
                        logger.info(f"        🔍 Validating {instance_type}...")
                        is_valid, reason, val_error, reclassified_type = validator.validate_figurative_type(
                            instance_type,
                            heb_verse,
                            eng_verse,
                            english_text,
                            explanation,
                            0.8 if confidence == 'high' else 0.6 if confidence == 'medium' else 0.4
                        )

                        validation_info = {
                            'is_valid': is_valid,
                            'validation_reason': reason,
                            'validation_error': val_error,
                            'reclassified_type': reclassified_type,
                            'original_type': instance_type
                        }

                        if is_valid:
                            final_type = reclassified_type if reclassified_type else instance_type
                            logger.info(f"        ✅ VALID: {final_type} - {reason}")
                            chapter_validated += 1
                        else:
                            final_type = instance_type
                            logger.info(f"        ❌ INVALID: {reason}")

                    else:
                        validation_info = {'is_valid': True, 'validation_reason': 'No validation', 'final_type': instance_type}
                        final_type = instance_type

                    # Store comprehensive flexible instance data with validation
                    flexible_data = {
                        'verse': verse_ref,
                        'instance_number': j + 1,
                        'figurative_text': instance.get('figurative_text', ''),
                        'english_text': english_text,
                        'original_type': instance_type,
                        'final_type': final_type,
                        'explanation': explanation,
                        'confidence': confidence,
                        'tags': instance.get('tags', {}),
                        'speaker_posture': instance.get('speaker_posture', []),
                        'speaker_attitude_specific': instance.get('speaker_attitude_specific', ''),
                        'scholarly_research_notes': instance.get('scholarly_research_notes', ''),
                        'llm_deliberation': llm_deliberation,
                        'validation': validation_info,
                        'metadata': metadata
                    }

                    # Add to results for JSON output
                    all_flexible_results.append(flexible_data)

                    # Log hierarchical tags
                    tags = instance.get('tags', {})
                    for dimension, tag_list in tags.items():
                        logger.info(f"        {dimension.upper()}: {tag_list}")

                    # Log speaker posture
                    speaker_posture = instance.get('speaker_posture', [])
                    speaker_attitude = instance.get('speaker_attitude_specific', '')
                    if speaker_posture:
                        logger.info(f"        SPEAKER_POSTURE: {speaker_posture}")
                    if speaker_attitude:
                        logger.info(f"        SPEAKER_ATTITUDE: {speaker_attitude}")

                chapter_instances += len(flexible_instances)
            else:
                logger.debug(f"    ⚪ No figurative language detected")

        except Exception as e:
            logger.error(f"❌ Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            chapter_errors += 1

    logger.info(f"✅ {book_name} {chapter} COMPLETED: {chapter_instances} detected, {chapter_validated} validated from {chapter_verses} verses")
    return chapter_verses, chapter_instances, chapter_validated, chapter_errors, all_flexible_results

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

    base_filename = f"{book_part}_{chapter_part}_{verse_part}_validated_{date_part}_{time_part}"
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"
    json_file = f"{base_filename}_results.json"

    print(f"\n🚀 Processing {book_name}, chapter(s): {chapter_part}, verse(s): {verse_part}")
    print(f"📁 Output files will be based on: {base_filename}")

    logger = setup_logging(log_file)
    if was_loaded:
        logger.info(f"✅ Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"⚠️  Warning: .env file not found at {dotenv_path}")

    logger.info(f"=== 🏷️  FLEXIBLE TAGGING + VALIDATION: {book_name.upper()} CHAPTER(S) {chapters} ===")
    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found.")

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

        total_verses, total_instances, total_validated, total_errors = 0, 0, 0, 0
        all_results = []

        for chapter in chapters:
            v, i, val, e, chapter_results = process_chapter_with_validation(
                book_name, chapter, verse_selection, sefaria, flexible_client, validator, db_manager, logger
            )
            total_verses += v
            total_instances += i
            total_validated += val
            total_errors += e
            all_results.extend(chapter_results)
            db_manager.conn.commit()

        total_time = time.time() - start_time
        db_manager.close()

        # Save comprehensive results to JSON
        output_data = {
            'processing_info': {
                'book': book_name,
                'chapters': chapters,
                'verse_selection': verse_selection,
                'timestamp': now.isoformat(),
                'total_verses': total_verses,
                'total_instances_detected': total_instances,
                'total_instances_validated': total_validated,
                'validation_rate': (total_validated / max(1, total_instances)) * 100,
                'total_errors': total_errors,
                'processing_time_seconds': total_time
            },
            'flexible_tagging_results': all_results,
            'usage_statistics': flexible_client.get_usage_info(),
            'validation_statistics': validator.get_validation_stats() if validator else {}
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        logger.info(f"\n=== ✅ {book_name.upper()} FLEXIBLE TAGGING + VALIDATION COMPLETE ===")
        logger.info(f"📊 Database: {db_name}")
        logger.info(f"📄 JSON Results: {json_file}")
        logger.info(f"📋 Log file: {log_file}")
        logger.info(f"📝 Total verses processed: {total_verses}")
        logger.info(f"🏷️  Total instances detected: {total_instances}")
        logger.info(f"✅ Total instances validated: {total_validated}")
        logger.info(f"📊 Validation rate: {(total_validated / max(1, total_instances)) * 100:.1f}%")
        logger.info(f"❌ Errors: {total_errors}")
        logger.info(f"⏱️  Processing time: {total_time:.1f} seconds")

        print(f"\n✅ Flexible tagging + validation complete!")
        print(f"📁 Database: {db_name}")
        print(f"📄 JSON Results: {json_file}")
        print(f"📊 Validation Rate: {(total_validated / max(1, total_instances)) * 100:.1f}%")

        # Show sample results
        if total_instances > 0:
            print(f"\n🎯 Sample Validated Flexible Tagging Results (first 3):")
            for i, result in enumerate(all_results[:3]):
                validation = result.get('validation', {})
                tags = result.get('tags', {})
                print(f"  {i+1}. {result.get('verse', 'Unknown')} - {result.get('original_type', 'Unknown')} → {result.get('final_type', 'Unknown')}")
                print(f"     Text: {result.get('english_text', 'N/A')}")
                print(f"     Validation: {'VALID' if validation.get('is_valid') else 'INVALID'} - {validation.get('validation_reason', 'N/A')}")

                for dimension, tag_list in tags.items():
                    print(f"     {dimension.upper()}: {tag_list}")

                speaker_posture = result.get('speaker_posture', [])
                if speaker_posture:
                    print(f"     SPEAKER_POSTURE: {speaker_posture}")

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
        print(f"\n❌ An error occurred: {e}")
        print("Check the log file for detailed error information.")