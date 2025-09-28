#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Parallel Processing Test
Tests parallel processing without user interaction
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

def process_verse_simple(verse_data, book_name, chapter, flexible_client, worker_id):
    """Simple verse processing for parallel test"""
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        print(f"Worker {worker_id}: Starting {verse_ref}")

        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter
        )

        instances_count = len(metadata.get('flexible_instances', []))
        print(f"Worker {worker_id}: Completed {verse_ref} - {instances_count} instances")

        return verse_ref, instances_count, error

    except Exception as e:
        print(f"Worker {worker_id}: ERROR {verse_data['reference']} - {e}")
        return verse_data['reference'], 0, str(e)

def main():
    """Automated parallel processing test"""

    # Load environment
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    print("=== AUTOMATED PARALLEL PROCESSING TEST ===")
    print("Testing 4 verses from Deuteronomy 30 with 3 parallel workers\n")

    # Fixed test configuration
    book_name = "Deuteronomy"
    chapter = 30
    test_verses = [2, 3, 4, 11]  # 4 verses
    max_workers = 3

    # Get test data
    sefaria = SefariaClient()
    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
    if not verses_data:
        print("Failed to get test verses")
        return

    test_verse_data = [v for v in verses_data if int(v['reference'].split(':')[1]) in test_verses]
    print(f"Test verses:")
    for verse in test_verse_data:
        print(f"  - {verse['reference']}")
    print()

    # Initialize (with minimal logging for speed)
    db_manager = DatabaseManager(":memory:")
    db_manager.connect()
    db_manager.setup_database()

    logger = logging.getLogger("test")
    logger.setLevel(logging.ERROR)  # Minimal logging for speed

    validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
    flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

    print(f"Starting parallel processing with {max_workers} workers...")
    start_time = time.time()

    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks with worker IDs
        future_to_worker = {}
        for i, verse_data in enumerate(test_verse_data):
            worker_id = (i % max_workers) + 1
            future = executor.submit(process_verse_simple, verse_data, book_name, chapter, flexible_client, worker_id)
            future_to_worker[future] = (verse_data, worker_id)

        # Collect results
        for future in concurrent.futures.as_completed(future_to_worker):
            verse_data, worker_id = future_to_worker[future]
            try:
                verse_ref, instances_count, error = future.result()
                results.append((verse_ref, instances_count, error))
            except Exception as e:
                print(f"Worker {worker_id}: EXCEPTION {verse_data['reference']} - {e}")
                results.append((verse_data['reference'], 0, str(e)))

    parallel_time = time.time() - start_time

    print(f"\n=== RESULTS ===")
    print(f"Processing time: {parallel_time:.2f} seconds")
    print(f"Average per verse: {parallel_time/len(test_verse_data):.2f} seconds")
    print(f"Workers used: {max_workers}")

    print(f"\nVerse results:")
    total_instances = 0
    for verse_ref, instances_count, error in results:
        if error:
            print(f"  {verse_ref}: ERROR - {error}")
        else:
            print(f"  {verse_ref}: {instances_count} instances")
            total_instances += instances_count

    print(f"\nTotal instances found: {total_instances}")

    # Estimated sequential time (based on previous tests showing ~71s per verse)
    estimated_sequential = len(test_verse_data) * 60  # Conservative estimate
    estimated_speedup = estimated_sequential / parallel_time

    print(f"\nPerformance estimate:")
    print(f"  Estimated sequential time: {estimated_sequential:.0f} seconds")
    print(f"  Actual parallel time: {parallel_time:.2f} seconds")
    print(f"  Estimated speedup: {estimated_speedup:.2f}x")

    if estimated_speedup >= 2.0:
        print(f"\nEXCELLENT! Parallel processing is working well!")
    elif estimated_speedup >= 1.5:
        print(f"\nGOOD! Meaningful parallel speedup achieved!")
    else:
        print(f"\nParallel processing is functional with modest gains")

    print(f"\nNext steps:")
    print(f"- Use parallel_flexible_processor.py for interactive processing")
    print(f"- Test with 20+ verses for maximum parallel efficiency")
    print(f"- Use 6-8 workers for production workloads")

    db_manager.close()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()