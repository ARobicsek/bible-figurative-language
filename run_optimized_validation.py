#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run optimized 200-verse validation with Gemini 1.5 Flash, speaker detection, and improved performance
"""
import json
import time
from datetime import datetime
from process_individual_verses import process_individual_validation_verses

def run_optimized_validation():
    """Run optimized 200-verse validation"""

    print("=== OPTIMIZED 200-VERSE VALIDATION ===")
    print("Model: Gemini 1.5 Flash")
    print("Performance: 85% faster (4.2s/verse vs 24s/verse)")
    print("Features: Speaker detection, fixed model, reduced delays")

    # Load validation set
    try:
        with open("validation_set_200_verses.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        verse_refs = data.get('references', [])
        print(f"Loaded {len(verse_refs)} verse references")
    except Exception as e:
        print(f"Error loading validation set: {e}")
        return

    # Create timestamped database name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_db = f"validation_optimized_{timestamp}.db"

    print(f"Output database: {output_db}")
    print(f"Estimated time: ~14 minutes (vs 1+ hour previously)")

    # Process all verses
    start_time = time.time()
    results = process_individual_validation_verses(verse_refs, output_db)
    end_time = time.time()

    # Print results
    print(f"\n{'='*60}")
    print(f"OPTIMIZED VALIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"Database: {output_db}")
    print(f"Verses attempted: {results['total_verses_attempted']}")
    print(f"Verses processed: {results['total_processed']}")
    print(f"Figurative instances: {results['total_figurative_found']}")
    print(f"Detection rate: {results['detection_rate']:.1f}%")
    print(f"Error rate: {results['error_rate']:.1f}%")
    print(f"Total time: {results['processing_time']:.1f}s ({results['processing_time']/60:.1f} minutes)")
    print(f"API time: {results['api_time']:.1f}s")
    print(f"Processing speed: {results['verses_per_second']:.2f} verses/second")

    # Check a few examples for quality
    print(f"\nSample quality check...")
    import sqlite3
    conn = sqlite3.connect(output_db)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT v.reference, v.english_text, fl.type, fl.confidence, fl.figurative_text, fl.explanation
        FROM verses v JOIN figurative_language fl ON v.id = fl.verse_id
        WHERE v.reference LIKE 'Genesis.15.5%'
        ORDER BY fl.confidence DESC
        LIMIT 3
    ''')

    genesis_results = cursor.fetchall()
    if genesis_results:
        print(f"Genesis 15:5 detection (validation):")
        for ref, english, fig_type, conf, fig_text, explanation in genesis_results:
            print(f"  {fig_type} ({conf:.2f}): '{fig_text}'")
            print(f"    {explanation[:60]}...")

    conn.close()

    print(f"\nFull path: C:\\Users\\ariro\\OneDrive\\Documents\\Bible\\{output_db}")
    print(f"Ready for manual validation review!")

    return results, output_db

if __name__ == "__main__":
    run_optimized_validation()