#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Genesis 15:5 specifically to check figurative language detection
"""
from process_individual_verses import extract_single_verse, process_single_verse_direct
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def test_genesis_15_5():
    """Test Genesis 15:5 specifically"""

    print("=== TESTING GENESIS 15:5 FOR FIGURATIVE LANGUAGE ===")

    verse_ref = "Genesis.15.5"

    # Initialize pipeline
    pipeline = FigurativeLanguagePipeline(
        db_path="test_genesis_15_5.db",
        use_llm_detection=True,
        use_actual_llm=True
    )

    try:
        print(f"Processing: {verse_ref}")

        # Extract single verse
        verse_data, api_time = extract_single_verse(verse_ref)
        print(f"API time: {api_time:.2f}s")
        print(f"Hebrew: [Hebrew text - {len(verse_data['hebrew'])} chars]")
        print(f"English: {verse_data['english']}")

        # Process through pipeline
        result = process_single_verse_direct(pipeline, verse_data, drop_existing=True)
        figurative_count = result.get('figurative_found', 0)

        print(f"\nResult: {figurative_count} figurative language instances found")

        # Check database for details
        if figurative_count > 0:
            import sqlite3
            conn = sqlite3.connect('test_genesis_15_5.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT fl.type, fl.confidence, fl.figurative_text, fl.explanation
                FROM figurative_language fl JOIN verses v ON fl.verse_id = v.id
                WHERE v.reference = ?
            ''', (verse_data['reference'],))

            results = cursor.fetchall()
            print(f"\nDetected figurative language:")
            for fig_type, conf, text, explanation in results:
                print(f"  {fig_type} ({conf:.2f}): '{text}'")
                print(f"    Why: {explanation}")
            conn.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_genesis_15_5()