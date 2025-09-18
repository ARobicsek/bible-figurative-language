#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test exactly 3 specific verses with Gemini 2.5 Pro
"""
from process_individual_verses import extract_single_verse, process_single_verse_direct
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def test_three_verses():
    """Test exactly 3 specific verses from different chapters"""

    print("=== TESTING 3 SPECIFIC VERSES WITH GEMINI 2.5 PRO ===")

    # Test verses from different chapters
    test_verses = [
        "Genesis.1.27",    # Genesis 1:27 - "in the image of God"
        "Exodus.3.2",      # Exodus 3:2 - burning bush
        "Deuteronomy.32.4" # Deuteronomy 32:4 - "The Rock, his work is perfect"
    ]

    # Initialize pipeline
    pipeline = FigurativeLanguagePipeline(
        db_path="test_3_verses.db",
        use_llm_detection=True,
        use_actual_llm=True
    )

    print(f"\nProcessing exactly {len(test_verses)} verses:")
    for i, verse_ref in enumerate(test_verses, 1):
        print(f"  {i}. {verse_ref}")

    total_figurative = 0

    for i, verse_ref in enumerate(test_verses, 1):
        try:
            print(f"\n[{i}/{len(test_verses)}] Processing: {verse_ref}")

            # Extract single verse
            verse_data, api_time = extract_single_verse(verse_ref)
            print(f"  API time: {api_time:.2f}s")
            print(f"  Hebrew: [Hebrew text - {len(verse_data['hebrew'])} chars]")
            print(f"  English: {verse_data['english']}")

            # Process through pipeline
            result = process_single_verse_direct(pipeline, verse_data, drop_existing=(i == 1))
            figurative_count = result.get('figurative_found', 0)
            total_figurative += figurative_count

            print(f"  Result: {figurative_count} figurative language instances found")

        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\n{'='*50}")
    print(f"TEST COMPLETE")
    print(f"{'='*50}")
    print(f"Verses processed: {len(test_verses)}")
    print(f"Total figurative instances: {total_figurative}")
    print(f"Average per verse: {total_figurative / len(test_verses):.1f}")
    print(f"Database saved: test_3_verses.db")

if __name__ == "__main__":
    test_three_verses()