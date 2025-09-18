#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 5 verses to check latency and speaker detection with Gemini 1.5 Flash
"""
import time
from process_individual_verses import process_individual_validation_verses

def test_5_verses_latency():
    """Test exactly 5 verses for latency testing"""

    print("=== 5-VERSE LATENCY TEST WITH SPEAKER DETECTION ===")

    # Test verses including Genesis 15:5
    test_verses = [
        "Genesis.15.5",    # Stars comparison (should have figurative language)
        "Genesis.1.1",     # In the beginning
        "Exodus.3.2",      # Burning bush
        "Deuteronomy.32.4", # The Rock
        "Genesis.2.7"      # Breath of life
    ]

    print(f"Testing {len(test_verses)} verses:")
    for i, verse_ref in enumerate(test_verses, 1):
        print(f"  {i}. {verse_ref}")

    # Create timestamped database name
    timestamp = time.strftime("%H%M%S")
    output_db = f"latency_test_{timestamp}.db"

    print(f"\nUsing database: {output_db}")
    print(f"Model: Gemini 1.5 Flash")
    print(f"Enhanced with speaker detection")

    # Process verses and measure total time
    start_time = time.time()
    results = process_individual_validation_verses(test_verses, output_db)
    end_time = time.time()

    total_time = end_time - start_time
    avg_time_per_verse = total_time / len(test_verses)

    print(f"\n{'='*50}")
    print(f"LATENCY TEST RESULTS")
    print(f"{'='*50}")
    print(f"Total verses: {len(test_verses)}")
    print(f"Processed: {results['total_processed']}")
    print(f"Figurative instances: {results['total_figurative_found']}")
    print(f"Detection rate: {results['detection_rate']:.1f}%")
    print(f"")
    print(f"LATENCY METRICS:")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average per verse: {avg_time_per_verse:.1f}s")
    print(f"API time: {results['api_time']:.1f}s")
    print(f"Processing speed: {results['verses_per_second']:.2f} verses/second")

    # Check speaker detection
    print(f"\nChecking speaker detection...")
    import sqlite3
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.reference, v.speaker as verse_speaker, fl.type, fl.confidence
        FROM verses v
        LEFT JOIN figurative_language fl ON v.id = fl.verse_id
        ORDER BY v.reference
    ''')

    results_data = cursor.fetchall()
    print(f"\nSpeaker Detection Results:")
    for ref, speaker, fig_type, confidence in results_data:
        if fig_type:
            print(f"  {ref}: {speaker} -> {fig_type} ({confidence:.2f})")
        else:
            print(f"  {ref}: {speaker} -> No figurative language")

    conn.close()

    print(f"\nDatabase saved: {output_db}")
    return results, output_db

if __name__ == "__main__":
    test_5_verses_latency()