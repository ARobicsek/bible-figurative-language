#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Parallel Processing Demo
Demonstrates parallel processing gains on a small set of verses
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

def process_verse_simple(verse_data, book_name, chapter, flexible_client, logger):
    """Simple verse processing for demo"""
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        if logger:
            logger.info(f"Processing {verse_ref}")

        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter
        )

        instances_count = len(metadata.get('flexible_instances', []))
        return verse_ref, instances_count, error

    except Exception as e:
        return verse_data['reference'], 0, str(e)

def test_parallel_demo():
    """Quick demo of sequential vs parallel processing"""

    # Load environment
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not found")
        return

    print("=== PARALLEL PROCESSING DEMO ===")
    print("Comparing sequential vs parallel on 6 verses\n")

    # Test data: 6 verses from Deuteronomy 30 (good mix of figurative content)
    book_name = "Deuteronomy"
    chapter = 30
    test_verses = [2, 3, 4, 11, 12, 13]  # 6 verses

    # Get test data
    sefaria = SefariaClient()
    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
    if not verses_data:
        print("Failed to get test verses")
        return

    test_verse_data = [v for v in verses_data if int(v['reference'].split(':')[1]) in test_verses]
    print(f"Testing with {len(test_verse_data)} verses:")
    for verse in test_verse_data:
        print(f"  - {verse['reference']}")

    # Setup logger
    logger = logging.getLogger("demo")
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
    logger.addHandler(handler)

    # Initialize clients
    db_manager = DatabaseManager(":memory:")  # In-memory for demo
    db_manager.connect()
    db_manager.setup_database()

    validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
    flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

    # Test 1: Sequential Processing
    print(f"\n1. SEQUENTIAL PROCESSING:")
    print("Processing verses one by one...")

    start_time = time.time()
    sequential_results = []

    for verse_data in test_verse_data:
        verse_ref, instances_count, error = process_verse_simple(
            verse_data, book_name, chapter, flexible_client, None  # No logging for speed
        )
        sequential_results.append((verse_ref, instances_count, error))
        if error:
            print(f"  ERROR: {verse_ref} - {error}")
        else:
            print(f"  DONE: {verse_ref} - {instances_count} instances")

    sequential_time = time.time() - start_time
    print(f"Sequential time: {sequential_time:.2f} seconds")

    # Test 2: Parallel Processing
    print(f"\n2. PARALLEL PROCESSING (4 workers):")
    print("Processing verses in parallel...")

    start_time = time.time()
    parallel_results = []
    max_workers = 4

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_verse = {
            executor.submit(process_verse_simple, verse_data, book_name, chapter, flexible_client, None): verse_data
            for verse_data in test_verse_data
        }

        # Collect results
        for future in concurrent.futures.as_completed(future_to_verse):
            verse_data = future_to_verse[future]
            try:
                verse_ref, instances_count, error = future.result()
                parallel_results.append((verse_ref, instances_count, error))
                if error:
                    print(f"  ERROR: {verse_ref} - {error}")
                else:
                    print(f"  DONE: {verse_ref} - {instances_count} instances")
            except Exception as e:
                print(f"  EXCEPTION: {verse_data['reference']} - {e}")

    parallel_time = time.time() - start_time
    print(f"Parallel time: {parallel_time:.2f} seconds")

    # Results
    speedup = sequential_time / parallel_time
    improvement = ((sequential_time - parallel_time) / sequential_time) * 100

    print(f"\n=== RESULTS ===")
    print(f"Sequential:  {sequential_time:.2f} seconds ({sequential_time/len(test_verse_data):.2f}s per verse)")
    print(f"Parallel:    {parallel_time:.2f} seconds ({parallel_time/len(test_verse_data):.2f}s per verse)")
    print(f"Speedup:     {speedup:.2f}x ({improvement:.1f}% improvement)")

    if speedup >= 2.0:
        print(f"\nEXCELLENT! {speedup:.1f}x speedup achieved!")
        print("This demonstrates significant parallel processing gains.")
    elif speedup >= 1.5:
        print(f"\nGOOD! {speedup:.1f}x speedup achieved!")
        print("Parallel processing is providing meaningful benefits.")
    elif speedup >= 1.2:
        print(f"\nMODERATE: {speedup:.1f}x speedup achieved.")
        print("Some parallel benefits, though limited by API latency.")
    else:
        print(f"\nLIMITED: {speedup:.1f}x speedup.")
        print("Parallel gains limited - may need more verses or workers.")

    print(f"\nFor production processing:")
    print(f"- Use 6-8 workers for best balance")
    print(f"- Process 20+ verses for maximum parallel efficiency")
    print(f"- Expected speedup on large datasets: 3-6x")

    db_manager.close()

if __name__ == "__main__":
    try:
        test_parallel_demo()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()