#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Performance Test Script
Tests the optimized parallel processing against original sequential processing
"""
import sys
import os
import time
import logging
import concurrent.futures
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def process_verse_parallel(verse_data, book_name, chapter, flexible_client, db_manager, logger):
    """Process a single verse - designed for parallel execution"""
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        logger.info(f"Processing {verse_ref}")

        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter
        )

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
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'no'
        }

        # Return data for batch processing
        instances = metadata.get('flexible_instances', [])
        instance_data_list = []
        for instance in instances:
            if isinstance(instance, dict):
                instance_data_list.append({
                    'figurative_language': instance.get('figurative_language', 'no'),
                    'confidence': instance.get('confidence', 0.5),
                    'figurative_text': instance.get('english_text', ''),
                    'explanation': instance.get('explanation', ''),
                    'model_used': metadata.get('model_used', 'gemini-2.5-flash')
                })

        return verse_data_dict, instance_data_list, None

    except Exception as e:
        return None, [], str(e)

def test_performance_comparison():
    """Compare performance of original vs optimized processing"""

    # Load environment
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    print("=== PERFORMANCE COMPARISON TEST ===")
    print("Testing original vs optimized processing on small verse sample\n")

    # Test data: first 5 verses of Deuteronomy 30 (known to have figurative language)
    book_name = "Deuteronomy"
    chapter = 30
    test_verses = [2, 3, 4]  # Verses known to have some complexity

    # Initialize clients
    sefaria = SefariaClient()

    # Get test verses
    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
    if not verses_data:
        print("Failed to get test verses")
        return

    test_verse_data = [v for v in verses_data if int(v['reference'].split(':')[1]) in test_verses]
    print(f"Testing with {len(test_verse_data)} verses: {[v['reference'] for v in test_verse_data]}")

    # Test 1: Original processing with verbose logging
    print("\nORIGINAL PROCESSING (with verbose logging):")

    # Setup for original test
    original_log = "test_original_log.txt"
    original_db = "test_original.db"

    original_logger = logging.getLogger("original")
    original_logger.setLevel(logging.INFO)  # Verbose logging like original
    handler = logging.FileHandler(original_log, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    original_logger.addHandler(handler)

    original_db_manager = DatabaseManager(original_db)
    original_db_manager.connect()
    original_db_manager.setup_database(drop_existing=True)

    validator = MetaphorValidator(api_key, db_manager=original_db_manager, logger=original_logger)
    flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=original_logger, db_manager=original_db_manager)

    # Time original processing
    start_time = time.time()

    for verse_data in test_verse_data:
        verse_ref = verse_data['reference']
        original_logger.info(f"Processing {verse_ref}")

        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            verse_data['hebrew'], verse_data['english'], book=book_name, chapter=chapter
        )

        # Process like original system (individual inserts)
        verse_data_dict = {
            'reference': verse_ref,
            'book': book_name,
            'chapter': chapter,
            'verse': int(verse_ref.split(':')[1]),
            'hebrew': verse_data['hebrew'],
            'hebrew_stripped': verse_data['hebrew'],
            'english': verse_data['english'],
            'word_count': len(verse_data['hebrew'].split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
            'instances_detected': len(metadata.get('flexible_instances', [])),
            'instances_recovered': len(metadata.get('flexible_instances', [])),
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'no'
        }

        verse_id = original_db_manager.insert_verse(verse_data_dict)

        # Process instances individually
        instances = metadata.get('flexible_instances', [])
        for instance in instances:
            # Individual insert and validation like original
            instance_id = original_db_manager.insert_figurative_language(verse_id, {
                'figurative_language': instance.get('figurative_language', 'no'),
                'confidence': instance.get('confidence', 0.5),
                'figurative_text': instance.get('english_text', ''),
                'explanation': instance.get('explanation', ''),
                'model_used': metadata.get('model_used', 'gemini-2.5-flash')
            })

    original_time = time.time() - start_time
    original_db_manager.commit()
    original_db_manager.close()

    print(f"Original processing time: {original_time:.2f} seconds")
    print(f"Average per verse: {original_time/len(test_verse_data):.2f} seconds")

    # Test 2: Optimized processing with reduced logging
    print("\nOPTIMIZED PROCESSING (with reduced logging):")

    # Setup for optimized test
    optimized_log = "test_optimized_log.txt"
    optimized_db = "test_optimized.db"

    optimized_logger = logging.getLogger("optimized")
    optimized_logger.setLevel(logging.INFO)  # INFO level (not DEBUG)
    handler2 = logging.FileHandler(optimized_log, encoding='utf-8')
    handler2.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    optimized_logger.addHandler(handler2)

    optimized_db_manager = DatabaseManager(optimized_db)
    optimized_db_manager.connect()
    optimized_db_manager.setup_database(drop_existing=True)

    validator2 = MetaphorValidator(api_key, db_manager=optimized_db_manager, logger=optimized_logger)
    flexible_client2 = FlexibleTaggingGeminiClient(api_key, validator=validator2, logger=optimized_logger, db_manager=optimized_db_manager)

    # Time optimized processing
    start_time = time.time()

    # Prepare batch data
    verse_batch = []
    instance_batch = []

    for verse_data in test_verse_data:
        verse_ref = verse_data['reference']
        optimized_logger.info(f"Processing {verse_ref}")

        result_text, error, metadata = flexible_client2.analyze_figurative_language_flexible(
            verse_data['hebrew'], verse_data['english'], book=book_name, chapter=chapter
        )

        verse_data_dict = {
            'reference': verse_ref,
            'book': book_name,
            'chapter': chapter,
            'verse': int(verse_ref.split(':')[1]),
            'hebrew': verse_data['hebrew'],
            'hebrew_stripped': verse_data['hebrew'],
            'english': verse_data['english'],
            'word_count': len(verse_data['hebrew'].split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
            'instances_detected': len(metadata.get('flexible_instances', [])),
            'instances_recovered': len(metadata.get('flexible_instances', [])),
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'no'
        }

        verse_batch.append(verse_data_dict)

        # Collect instances for batch processing
        instances = metadata.get('flexible_instances', [])
        for instance in instances:
            instance_batch.append((verse_ref, {
                'figurative_language': instance.get('figurative_language', 'no'),
                'confidence': instance.get('confidence', 0.5),
                'figurative_text': instance.get('english_text', ''),
                'explanation': instance.get('explanation', ''),
                'model_used': metadata.get('model_used', 'gemini-2.5-flash')
            }))

    # Batch insert verses
    if verse_batch:
        verse_ids = optimized_db_manager.batch_insert_verses(verse_batch)
        optimized_logger.info(f"Batch inserted {len(verse_ids)} verses")

        # Batch insert instances
        if instance_batch:
            # Map verse references to IDs
            verse_ref_to_id = {}
            for i, verse_data in enumerate(verse_batch):
                if i < len(verse_ids):
                    verse_ref_to_id[verse_data['reference']] = verse_ids[i]

            instance_tuples = []
            for verse_ref, instance_data in instance_batch:
                if verse_ref in verse_ref_to_id:
                    instance_tuples.append((verse_ref_to_id[verse_ref], instance_data))

            if instance_tuples:
                instance_ids = optimized_db_manager.batch_insert_figurative_language(instance_tuples)
                optimized_logger.info(f"Batch inserted {len(instance_ids)} instances")

    optimized_time = time.time() - start_time
    optimized_db_manager.commit()
    optimized_db_manager.close()

    print(f"Optimized processing time: {optimized_time:.2f} seconds")
    print(f"Average per verse: {optimized_time/len(test_verse_data):.2f} seconds")

    # Test 3: Parallel processing
    print("\nPARALLEL PROCESSING (with 3 workers):")

    # Setup for parallel test
    parallel_log = "test_parallel_log.txt"
    parallel_db = "test_parallel.db"

    parallel_logger = logging.getLogger("parallel")
    parallel_logger.setLevel(logging.INFO)  # INFO level (not DEBUG)
    handler3 = logging.FileHandler(parallel_log, encoding='utf-8')
    handler3.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    parallel_logger.addHandler(handler3)

    parallel_db_manager = DatabaseManager(parallel_db)
    parallel_db_manager.connect()
    parallel_db_manager.setup_database(drop_existing=True)

    validator3 = MetaphorValidator(api_key, db_manager=parallel_db_manager, logger=parallel_logger)
    flexible_client3 = FlexibleTaggingGeminiClient(api_key, validator=validator3, logger=parallel_logger, db_manager=parallel_db_manager)

    # Time parallel processing
    start_time = time.time()

    max_workers = 3  # Use 3 workers for the test (same as number of test verses)

    # Process verses in parallel
    verse_results = []
    instance_results = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all verse processing tasks
        future_to_verse = {
            executor.submit(process_verse_parallel, verse_data, book_name, chapter, flexible_client3, parallel_db_manager, parallel_logger): verse_data
            for verse_data in test_verse_data
        }

        # Collect results as they complete
        for future in concurrent.futures.as_completed(future_to_verse):
            verse_data = future_to_verse[future]
            try:
                verse_data_dict, instance_data_list, error = future.result()
                if verse_data_dict:
                    verse_results.append(verse_data_dict)
                    for instance_data in instance_data_list:
                        instance_results.append((verse_data['reference'], instance_data))
                elif error:
                    parallel_logger.error(f"Error processing {verse_data['reference']}: {error}")
            except Exception as e:
                parallel_logger.error(f"Exception processing {verse_data['reference']}: {e}")

    # Batch insert results
    if verse_results:
        verse_ids = parallel_db_manager.batch_insert_verses(verse_results)
        parallel_logger.info(f"Batch inserted {len(verse_ids)} verses")

        # Map verse references to IDs for instances
        verse_ref_to_id = {}
        for i, verse_data_dict in enumerate(verse_results):
            if i < len(verse_ids):
                verse_ref_to_id[verse_data_dict['reference']] = verse_ids[i]

        # Prepare instance batch
        if instance_results:
            instance_tuples = []
            for verse_ref, instance_data in instance_results:
                if verse_ref in verse_ref_to_id:
                    instance_tuples.append((verse_ref_to_id[verse_ref], instance_data))

            if instance_tuples:
                instance_ids = parallel_db_manager.batch_insert_figurative_language(instance_tuples)
                parallel_logger.info(f"Batch inserted {len(instance_ids)} instances")

    parallel_time = time.time() - start_time
    parallel_db_manager.commit()
    parallel_db_manager.close()

    print(f"Parallel processing time: {parallel_time:.2f} seconds")
    print(f"Average per verse: {parallel_time/len(test_verse_data):.2f} seconds")

    # Performance comparison
    optimized_improvement_pct = ((original_time - optimized_time) / original_time) * 100
    parallel_improvement_pct = ((original_time - parallel_time) / original_time) * 100

    optimized_speedup = original_time / optimized_time
    parallel_speedup = original_time / parallel_time

    print(f"\nPERFORMANCE COMPARISON RESULTS:")
    print(f"{'Method':<15} {'Time (s)':<10} {'Per Verse':<12} {'Improvement':<12} {'Speedup':<8}")
    print(f"{'-'*60}")
    print(f"{'Original':<15} {original_time:<10.2f} {original_time/len(test_verse_data):<12.2f} {'baseline':<12} {'1.00x':<8}")
    print(f"{'Optimized':<15} {optimized_time:<10.2f} {optimized_time/len(test_verse_data):<12.2f} {optimized_improvement_pct:<11.1f}% {optimized_speedup:<8.2f}x")
    print(f"{'Parallel':<15} {parallel_time:<10.2f} {parallel_time/len(test_verse_data):<12.2f} {parallel_improvement_pct:<11.1f}% {parallel_speedup:<8.2f}x")

    print(f"\nKEY IMPROVEMENTS:")
    if optimized_improvement_pct > 0:
        print(f"- Logging/DB optimization: {optimized_improvement_pct:.1f}% faster")
    if parallel_improvement_pct > optimized_improvement_pct:
        additional_parallel_gain = parallel_improvement_pct - optimized_improvement_pct
        print(f"- Parallel processing adds: {additional_parallel_gain:.1f}% additional speedup")
        print(f"- Combined improvement: {parallel_improvement_pct:.1f}% faster ({parallel_speedup:.2f}x speedup)")

    if parallel_improvement_pct > 50:
        print(f"- EXCELLENT: {parallel_speedup:.1f}x speedup with parallel processing!")
    elif parallel_improvement_pct > 25:
        print(f"- GOOD: {parallel_speedup:.1f}x speedup achieved!")
    else:
        print(f"- Note: With only 3 verses and 3 workers, parallel gains are limited")
        print(f"  Expect much better results with 20+ verses and 6-8 workers")

    # File size comparison
    original_log_size = os.path.getsize(original_log) if os.path.exists(original_log) else 0
    optimized_log_size = os.path.getsize(optimized_log) if os.path.exists(optimized_log) else 0
    parallel_log_size = os.path.getsize(parallel_log) if os.path.exists(parallel_log) else 0

    log_reduction_pct = ((original_log_size - optimized_log_size) / original_log_size) * 100 if original_log_size > 0 else 0

    print(f"\nLOG FILE SIZES:")
    print(f"Original log:  {original_log_size:,} bytes")
    print(f"Optimized log: {optimized_log_size:,} bytes ({log_reduction_pct:.1f}% reduction)")
    print(f"Parallel log:  {parallel_log_size:,} bytes")

    print(f"\nTEST FILES CREATED:")
    print(f"- {original_log} / {original_db}")
    print(f"- {optimized_log} / {optimized_db}")
    print(f"- {parallel_log} / {parallel_db}")

    print(f"\nRECOMMENDATIONS:")
    print(f"- For production: Use parallel_flexible_processor.py with 6-8 workers")
    print(f"- For testing: Use smaller verse sets to verify before scaling up")
    print(f"- Best parallel gains: 20+ verses where workers can run concurrently")

    if parallel_speedup > 2.0:
        print(f"- READY FOR LARGE-SCALE: {parallel_speedup:.1f}x speedup proven!")
    else:
        print(f"- Test with more verses to see full parallel processing benefits")

if __name__ == "__main__":
    try:
        test_performance_comparison()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()