#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 22 specific Genesis verses with 12-worker parallel processing
"""
import sys
import os
import logging
import json
import time
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

# Target verses specified by user
TARGET_VERSES = [
    {"book": "Genesis", "chapter": 1, "verse": 8, "reference": "Genesis 1:8"},
    {"book": "Genesis", "chapter": 1, "verse": 11, "reference": "Genesis 1:11"},
    {"book": "Genesis", "chapter": 2, "verse": 17, "reference": "Genesis 2:17"},
    {"book": "Genesis", "chapter": 2, "verse": 21, "reference": "Genesis 2:21"},
    {"book": "Genesis", "chapter": 8, "verse": 7, "reference": "Genesis 8:7"},
    {"book": "Genesis", "chapter": 14, "verse": 20, "reference": "Genesis 14:20"},
    {"book": "Genesis", "chapter": 17, "verse": 8, "reference": "Genesis 17:8"},
    {"book": "Genesis", "chapter": 18, "verse": 29, "reference": "Genesis 18:29"},
    {"book": "Genesis", "chapter": 18, "verse": 31, "reference": "Genesis 18:31"},
    {"book": "Genesis", "chapter": 19, "verse": 4, "reference": "Genesis 19:4"},
    {"book": "Genesis", "chapter": 19, "verse": 36, "reference": "Genesis 19:36"},
    {"book": "Genesis", "chapter": 22, "verse": 8, "reference": "Genesis 22:8"},
    {"book": "Genesis", "chapter": 24, "verse": 4, "reference": "Genesis 24:4"},
    {"book": "Genesis", "chapter": 24, "verse": 65, "reference": "Genesis 24:65"},
    {"book": "Genesis", "chapter": 29, "verse": 16, "reference": "Genesis 29:16"},
    {"book": "Genesis", "chapter": 30, "verse": 6, "reference": "Genesis 30:6"},
    {"book": "Genesis", "chapter": 35, "verse": 13, "reference": "Genesis 35:13"},
    {"book": "Genesis", "chapter": 40, "verse": 5, "reference": "Genesis 40:5"},
    {"book": "Genesis", "chapter": 43, "verse": 23, "reference": "Genesis 43:23"},
    {"book": "Genesis", "chapter": 44, "verse": 6, "reference": "Genesis 44:6"},
    {"book": "Genesis", "chapter": 44, "verse": 19, "reference": "Genesis 44:19"},
    {"book": "Genesis", "chapter": 48, "verse": 10, "reference": "Genesis 48:10"}
]

def process_single_verse(verse_info, verse_data, flexible_client, validator, logger, worker_id):
    """Process a single verse for parallel execution"""
    try:
        verse_ref = verse_info['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']
        chapter = verse_info['chapter']

        logger.info(f"Worker {worker_id}: Processing {verse_ref}")

        # Use flexible tagging analysis with three-tier fallback
        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book="Genesis", chapter=chapter
        )

        # Handle truncation fallback
        truncation_occurred = metadata.get('truncation_detected', False)
        both_models_truncated = False
        tertiary_decomposed = False

        if truncation_occurred:
            logger.warning(f"Worker {worker_id}: Truncation detected in {verse_ref}, trying Pro model")
            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book="Genesis", chapter=chapter, model_override="gemini-2.5-pro"
            )

            pro_truncation_occurred = metadata.get('truncation_detected', False)
            both_models_truncated = pro_truncation_occurred

            if pro_truncation_occurred:
                logger.warning(f"Worker {worker_id}: Pro model also truncated for {verse_ref} - trying Claude Sonnet 4")
                result_text, error, metadata = flexible_client.analyze_with_claude_fallback(
                    heb_verse, eng_verse, book="Genesis", chapter=chapter
                )
                tertiary_decomposed = True

        instances = metadata.get('flexible_instances', [])
        final_model = metadata.get('model_used', 'gemini-2.5-flash')

        logger.info(f"Worker {worker_id}: {verse_ref} completed - {len(instances)} instances, model: {final_model}")

        # Prepare verse data
        verse_result = {
            'reference': verse_ref,
            'book': 'Genesis',
            'chapter': chapter,
            'verse': verse_info['verse'],
            'hebrew': heb_verse,
            'hebrew_stripped': HebrewTextProcessor.strip_diacritics(heb_verse),
            'english': eng_verse,
            'word_count': len(heb_verse.split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
            'instances_detected': len(instances),
            'instances_recovered': len(instances),
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'yes' if truncation_occurred else 'no',
            'both_models_truncated': 'yes' if both_models_truncated else 'no',
            'model_used': final_model,
            'worker_id': worker_id,
            'instances': instances,
            'tagging_analysis': metadata.get('tagging_analysis_deliberation', ''),
            'tertiary_decomposed': tertiary_decomposed
        }

        return verse_result, None

    except Exception as e:
        error_msg = f"Worker {worker_id}: Error processing {verse_info['reference']}: {str(e)}"
        logger.error(error_msg)
        return None, error_msg

def main():
    load_dotenv()

    now = datetime.now()
    db_name = f"test_22_genesis_verses_parallel_{now.strftime('%Y%m%d_%H%M')}.db"
    log_file = f"test_22_genesis_verses_parallel_{now.strftime('%Y%m%d_%H%M')}.log"

    print(f"TESTING 22 GENESIS VERSES WITH 12-WORKER PARALLEL PROCESSING")
    print(f"Using Claude Sonnet 4 three-tier fallback system")
    print(f"Database: {db_name}")
    print(f"Workers: 12")

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        print("1. Initializing clients...")
        sefaria = SefariaClient()

        with DatabaseManager(db_name) as db_manager:
            db_manager.setup_database()

            validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
            flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

            print("2. Fetching verse data...")
            # Group verses by chapter to minimize API calls
            chapters_needed = {}
            for verse_info in TARGET_VERSES:
                chapter = verse_info['chapter']
                if chapter not in chapters_needed:
                    chapters_needed[chapter] = []
                chapters_needed[chapter].append(verse_info)

            # Fetch all needed verse data
            verses_to_process = []
            for chapter, verse_list in chapters_needed.items():
                print(f"   Fetching Genesis {chapter}...")
                verses_data, _ = sefaria.extract_hebrew_text(f"Genesis.{chapter}")
                if not verses_data:
                    print(f"ERROR: Could not get text for Genesis {chapter}")
                    continue

                # Find target verses in this chapter
                for verse_info in verse_list:
                    verse_num = verse_info['verse']
                    verse_data = None
                    for v in verses_data:
                        if int(v['reference'].split(':')[1]) == verse_num:
                            verse_data = v
                            break

                    if verse_data:
                        verses_to_process.append((verse_info, verse_data))
                    else:
                        print(f"ERROR: Could not find verse {verse_num} in chapter {chapter}")

            print(f"3. Processing {len(verses_to_process)} verses with 12 workers...")

            # Process verses in parallel
            all_verse_results = []
            max_workers = 12

            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all verse processing tasks
                future_to_verse = {}
                for i, (verse_info, verse_data) in enumerate(verses_to_process):
                    worker_id = (i % max_workers) + 1
                    future = executor.submit(
                        process_single_verse, verse_info, verse_data,
                        flexible_client, validator, logger, worker_id
                    )
                    future_to_verse[future] = (verse_info, verse_data)

                # Collect results as they complete
                completed_count = 0
                for future in concurrent.futures.as_completed(future_to_verse):
                    verse_info, verse_data = future_to_verse[future]
                    try:
                        verse_result, error = future.result()
                        completed_count += 1

                        if verse_result:
                            all_verse_results.append(verse_result)

                        # Progress update
                        if completed_count % 5 == 0 or completed_count == len(verses_to_process):
                            print(f"   Progress: {completed_count}/{len(verses_to_process)} verses completed")

                    except Exception as e:
                        logger.error(f"Failed to process verse {verse_info['reference']}: {e}")

            print("4. Storing results and running validation...")

            total_verses = 0
            total_instances = 0

            for verse_result in all_verse_results:
                try:
                    # Store verse
                    verse_data = {k: v for k, v in verse_result.items()
                                 if k not in ['instances', 'tagging_analysis', 'worker_id', 'tertiary_decomposed']}
                    verse_id = db_manager.insert_verse(verse_data)
                    total_verses += 1

                    # Store instances and validate
                    instances = verse_result.get('instances', [])
                    instances_with_db_ids = []

                    for j, instance in enumerate(instances):
                        figurative_data = {
                            'figurative_language': instance.get('figurative_language', 'no'),
                            'simile': instance.get('simile', 'no'),
                            'metaphor': instance.get('metaphor', 'no'),
                            'personification': instance.get('personification', 'no'),
                            'idiom': instance.get('idiom', 'no'),
                            'hyperbole': instance.get('hyperbole', 'no'),
                            'metonymy': instance.get('metonymy', 'no'),
                            'other': instance.get('other', 'no'),
                            'confidence': instance.get('confidence', 0.5),
                            'figurative_text': instance.get('english_text', ''),
                            'figurative_text_in_hebrew': instance.get('hebrew_text', ''),
                            'figurative_text_in_hebrew_stripped': HebrewTextProcessor.strip_diacritics(instance.get('hebrew_text', '')),
                            'explanation': instance.get('explanation', ''),
                            'speaker': instance.get('speaker', ''),
                            'purpose': instance.get('purpose', ''),
                            'target': json.dumps(instance.get('target', [])),
                            'vehicle': json.dumps(instance.get('vehicle', [])),
                            'ground': json.dumps(instance.get('ground', [])),
                            'posture': json.dumps(instance.get('posture', [])),
                            'tagging_analysis_deliberation': verse_result.get('tagging_analysis', ''),
                            'model_used': verse_result.get('model_used', 'gemini-2.5-flash')
                        }

                        fig_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                        total_instances += 1

                        # Prepare for validation
                        instance_with_db_id = instance.copy()
                        instance_with_db_id['db_id'] = fig_id
                        instances_with_db_ids.append(instance_with_db_id)

                    # VALIDATION STEP
                    if validator and instances_with_db_ids:
                        logger.info(f"Validating {len(instances_with_db_ids)} instances in {verse_result['reference']}")

                        bulk_validation_results = validator.validate_verse_instances(
                            instances_with_db_ids, verse_result['hebrew'], verse_result['english']
                        )

                        instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                        for validation_result in bulk_validation_results:
                            instance_id = validation_result.get('instance_id')
                            results = validation_result.get('validation_results', {})
                            db_id = instance_id_to_db_id.get(instance_id)

                            if db_id:
                                validation_data = {}
                                any_valid = False

                                for fig_type, result in results.items():
                                    decision = result.get('decision')
                                    reason = result.get('reason', '')

                                    validation_data[f'validation_decision_{fig_type}'] = decision
                                    validation_data[f'validation_reason_{fig_type}'] = reason

                                    if decision == 'VALID':
                                        validation_data[f'final_{fig_type}'] = 'yes'
                                        any_valid = True
                                    else:
                                        validation_data[f'final_{fig_type}'] = 'no'

                                validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'
                                validation_data['validation_response'] = validation_result.get('full_response', '')
                                validation_data['validation_error'] = validation_result.get('error')

                                db_manager.update_validation_data(db_id, validation_data)

                except Exception as e:
                    logger.error(f"Error storing {verse_result['reference']}: {e}")

            db_manager.commit()

        total_time = time.time() - start_time

        print(f"\n=== RESULTS ===")
        print(f"Total verses processed: {total_verses}")
        print(f"Total instances found: {total_instances}")
        print(f"Processing time: {total_time:.1f} seconds")
        print(f"Average time per verse: {total_time/total_verses:.2f} seconds" if total_verses > 0 else "N/A")
        print(f"Workers used: {max_workers}")
        print(f"Database: {db_name}")
        print(f"Log file: {log_file}")

        # Show model usage summary
        print(f"\n=== MODEL USAGE SUMMARY ===")
        usage_stats = flexible_client.get_usage_info()
        for model, count in usage_stats.items():
            if count > 0:
                print(f"{model}: {count} verses")

        # Show validation summary
        if validator:
            val_stats = validator.get_validation_stats()
            print(f"\n=== VALIDATION SUMMARY ===")
            for stat, count in val_stats.items():
                print(f"{stat}: {count}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()