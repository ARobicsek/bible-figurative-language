#!/usr/bin/env python3
"""
Test the subcategory fix
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def test_subcategory_fix():
    """Test that subcategories are now populated"""
    print("=== Testing Subcategory Fix ===")

    # Initialize pipeline
    pipeline = FigurativeLanguagePipeline(
        'test_subcategory_fix.db',
        use_llm_detection=True,
        use_actual_llm=True
    )

    # Test with a single verse
    print("Testing Deuteronomy 30:20 (contains 'he is your life' metaphor)...")

    results = pipeline.process_verses('Deuteronomy.30.20')

    print(f"Results: {results}")

    # Check database
    import sqlite3
    conn = sqlite3.connect('test_subcategory_fix.db')
    cursor = conn.cursor()

    cursor.execute('''
        SELECT figurative_text, subcategory_level_1, subcategory_level_2, speaker, purpose
        FROM figurative_language
        WHERE subcategory_level_1 IS NOT NULL AND subcategory_level_1 != ""
    ''')

    populated_records = cursor.fetchall()
    print(f"\nRecords with populated subcategories: {len(populated_records)}")

    for record in populated_records:
        text, level1, level2, speaker, purpose = record
        safe_text = text.encode('ascii', 'ignore').decode('ascii') if text else "N/A"
        print(f"  Text: {safe_text[:40]}...")
        print(f"  Level 1: {level1}")
        print(f"  Level 2: {level2}")
        print(f"  Speaker: {speaker}")
        print(f"  Purpose: {purpose}")
        print()

    conn.close()

    if populated_records:
        print("✅ SUCCESS: Subcategory levels are being populated!")
    else:
        print("❌ FAILED: Subcategory levels still not populated")

if __name__ == "__main__":
    test_subcategory_fix()