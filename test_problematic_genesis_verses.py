#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Problematic Genesis Verses
Re-runs specific verses that had issues in the full Genesis processing
"""
import sys
import os
import logging
import traceback
import json
import time
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

def setup_logging(log_file, enable_debug=True):
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

def process_single_verse(verse_data, book_name, chapter, flexible_client, validator, logger, worker_id):
    """Process a single verse for parallel execution - IDENTICAL to interactive_parallel_processor.py"""
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
                    logger.warning(f"Worker {worker_id}: Pro model also truncated for {verse_ref} - trying tertiary decomposition fallback")

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
            'english': eng_verse,
            'word_count': len(heb_verse.split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': figurative_detection,
            'instances_detected': instances_count,
            'instances_recovered': instances_count,
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'yes' if truncation_occurred else 'no',
            'both_models_truncated': 'yes' if both_models_truncated else 'no',
            'model_used': final_model_used,
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

def main():
    """Main execution function"""
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    # Define problematic verses from genesis_issues.md
    problematic_verses = [
        {"book": "Genesis", "chapter": 14, "verse": 20, "issue": "Tertiary fallback; LLM found fig language, was truncated in its deliberations, did NOT get recorded as fig language"},
        {"book": "Genesis", "chapter": 35, "verse": 13, "issue": "Tertiary fallback"},
        {"book": "Genesis", "chapter": 2, "verse": 17, "issue": "Tertiary fallback; LLM figurative deliberation field was empty"},
        {"book": "Genesis", "chapter": 17, "verse": 8, "issue": "Tertiary fallback; LLM figurative deliberation field was empty"},
        {"book": "Genesis", "chapter": 18, "verse": 29, "issue": "Tertiary fallback; LLM figurative deliberation field was empty"},
        {"book": "Genesis", "chapter": 24, "verse": 65, "issue": "Tertiary fallback; LLM figurative deliberation field was empty"},
        {"book": "Genesis", "chapter": 48, "verse": 10, "issue": "Tertiary fallback; LLM figurative deliberation field was truncated"},
        {"book": "Genesis", "chapter": 30, "verse": 6, "issue": "Tertiary fallback"},
        {"book": "Genesis", "chapter": 29, "verse": 16, "issue": "Tertiary fallback"},
        {"book": "Genesis", "chapter": 24, "verse": 4, "issue": "Tertiary fallback"},
        {"book": "Genesis", "chapter": 22, "verse": 8, "issue": "API issue with Gemini 1.5"}
    ]

    # Generate filenames
    now = datetime.now()
    date_part = now.strftime("%Y%m%d")
    time_part = now.strftime("%H%M")

    base_filename = f"test_problematic_genesis_verses_{date_part}_{time_part}"
    log_file = f"{base_filename}.log"
    db_name = f"{base_filename}.db"
    results_file = f"{base_filename}_results.json"

    print(f"\n=== TESTING PROBLEMATIC GENESIS VERSES ===")
    print(f"Testing {len(problematic_verses)} verses that had issues in full Genesis run")
    print(f"Output files: {base_filename}.*")

    logger = setup_logging(log_file, True)

    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}")

    logger.info(f"=== TESTING PROBLEMATIC GENESIS VERSES ===")
    logger.info(f"Verses to test: {len(problematic_verses)}")

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

        results = []
        max_workers = 12

        # Group verses by chapter for efficient processing
        chapters_to_process = {}
        for verse_info in problematic_verses:
            chapter = verse_info["chapter"]
            if chapter not in chapters_to_process:
                chapters_to_process[chapter] = []
            chapters_to_process[chapter].append(verse_info)

        for chapter, verse_infos in chapters_to_process.items():
            logger.info(f"--- PROCESSING: Genesis {chapter} ---")

            # Fetch all verses for the chapter
            verses_data, _ = sefaria.extract_hebrew_text(f"Genesis.{chapter}")
            if not verses_data:
                logger.error(f"Failed to get text for Genesis {chapter}")
                continue

            # Filter to only the problematic verses
            target_verse_numbers = [v["verse"] for v in verse_infos]
            verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in target_verse_numbers]

            logger.info(f"Processing {len(verses_to_process)} problematic verses from Genesis {chapter}")

            # Process verses using ThreadPoolExecutor (same as parallel processor)
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_verse = {}
                for i, verse_data in enumerate(verses_to_process):
                    worker_id = (i % max_workers) + 1
                    future = executor.submit(
                        process_single_verse, verse_data, "Genesis", chapter,
                        flexible_client, validator, logger, worker_id
                    )
                    future_to_verse[future] = verse_data

                # Collect results
                for future in concurrent.futures.as_completed(future_to_verse):
                    verse_data = future_to_verse[future]
                    try:
                        verse_result, error = future.result()
                        if verse_result:
                            # Find the original issue description
                            verse_num = verse_result['verse']
                            original_issue = next((v["issue"] for v in verse_infos if v["verse"] == verse_num), "Unknown issue")

                            result_summary = {
                                'reference': verse_result['reference'],
                                'original_issue': original_issue,
                                'truncation_occurred': verse_result['truncation_occurred'],
                                'both_models_truncated': verse_result['both_models_truncated'],
                                'model_used': verse_result['model_used'],
                                'tertiary_decomposed': verse_result['tertiary_decomposed'],
                                'instances_detected': verse_result['instances_detected'],
                                'figurative_detection_deliberation': verse_result['figurative_detection_deliberation'][:500] + "..." if len(verse_result['figurative_detection_deliberation']) > 500 else verse_result['figurative_detection_deliberation'],
                                'llm_restriction_error': verse_result['llm_restriction_error']
                            }
                            results.append(result_summary)

                            # Store in database (same as parallel processor)
                            verse_db_data = {k: v for k, v in verse_result.items()
                                           if k not in ['instances', 'tagging_analysis', 'worker_id', 'tertiary_decomposed']}
                            verse_id = db_manager.insert_verse(verse_db_data)

                            # INSERT MISSING FIGURATIVE LANGUAGE INSTANCES
                            instances_stored = 0
                            if 'instances' in verse_result and verse_result['instances']:
                                for instance_result in verse_result['instances']:
                                    instance_data = instance_result

                                    # Prepare data for database insertion
                                    figurative_data = {
                                        'figurative_language': instance_data.get('figurative_language', 'no'),
                                        'simile': instance_data.get('simile', 'no'),
                                        'metaphor': instance_data.get('metaphor', 'no'),
                                        'personification': instance_data.get('personification', 'no'),
                                        'idiom': instance_data.get('idiom', 'no'),
                                        'hyperbole': instance_data.get('hyperbole', 'no'),
                                        'metonymy': instance_data.get('metonymy', 'no'),
                                        'other': instance_data.get('other', 'no'),
                                        'final_figurative_language': instance_data.get('final_figurative_language', 'no'),
                                        'final_simile': instance_data.get('final_simile', 'no'),
                                        'final_metaphor': instance_data.get('final_metaphor', 'no'),
                                        'final_personification': instance_data.get('final_personification', 'no'),
                                        'final_idiom': instance_data.get('final_idiom', 'no'),
                                        'final_hyperbole': instance_data.get('final_hyperbole', 'no'),
                                        'final_metonymy': instance_data.get('final_metonymy', 'no'),
                                        'final_other': instance_data.get('final_other', 'no'),
                                        'target': json.dumps(instance_data.get('target', [])) if instance_data.get('target') else '[]',
                                        'vehicle': json.dumps(instance_data.get('vehicle', [])) if instance_data.get('vehicle') else '[]',
                                        'ground': json.dumps(instance_data.get('ground', [])) if instance_data.get('ground') else '[]',
                                        'posture': json.dumps(instance_data.get('posture', [])) if instance_data.get('posture') else '[]',
                                        'confidence': instance_data.get('confidence', 0.0),
                                        'figurative_text': instance_data.get('english_text', ''),
                                        'figurative_text_in_hebrew': instance_data.get('hebrew_text', ''),
                                        'figurative_text_in_hebrew_stripped': instance_data.get('hebrew_text_stripped', ''),
                                        'explanation': instance_data.get('explanation', ''),
                                        'speaker': instance_data.get('speaker', ''),
                                        'purpose': instance_data.get('purpose', ''),
                                        'tagging_analysis_deliberation': instance_result.get('tagging_analysis', ''),
                                        'model_used': instance_result.get('model_used', verse_result.get('model_used', 'gemini-2.5-flash'))
                                    }

                                    figurative_language_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                                    instances_stored += 1

                            logger.info(f"Completed {verse_result['reference']}: "
                                       f"Truncation={verse_result['truncation_occurred']}, "
                                       f"BothTruncated={verse_result['both_models_truncated']}, "
                                       f"Model={verse_result['model_used']}, "
                                       f"Instances={verse_result['instances_detected']}, "
                                       f"StoredInDB={instances_stored}")

                    except Exception as e:
                        logger.error(f"Failed to process verse {verse_data.get('reference', 'unknown')}: {e}")

            db_manager.commit()

        total_time = time.time() - start_time
        db_manager.close()

        # Save results
        summary = {
            'test_info': {
                'timestamp': now.isoformat(),
                'total_verses_tested': len(problematic_verses),
                'processing_time_seconds': total_time,
                'max_workers': max_workers
            },
            'results': results,
            'usage_statistics': flexible_client.get_usage_info()
        }

        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"\n=== TEST COMPLETE ===")
        print(f"Database: {db_name}")
        print(f"Log file: {log_file}")
        print(f"Results file: {results_file}")
        print(f"Total verses tested: {len(problematic_verses)}")
        print(f"Total processing time: {total_time:.1f} seconds")

        # Print summary of results
        print(f"\n=== RESULTS SUMMARY ===")
        for result in results:
            print(f"{result['reference']}: "
                  f"Truncation={result['truncation_occurred']}, "
                  f"BothTruncated={result['both_models_truncated']}, "
                  f"Model={result['model_used']}, "
                  f"Instances={result['instances_detected']}")

        logger.info(f"=== TEST COMPLETE ===")
        logger.info(f"Tested {len(problematic_verses)} problematic verses")

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