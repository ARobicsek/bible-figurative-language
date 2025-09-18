#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Genesis 2:1-15 with updated API quota
"""
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def test_genesis_2_verses():
    """Test processing Genesis 2:1-15 with LLM"""

    print("=== TESTING GENESIS 2:1-15 WITH UPDATED API QUOTA ===")

    # Initialize pipeline with LLM detection and new database
    pipeline = FigurativeLanguagePipeline(
        db_path="genesis_2_test.db",
        use_llm_detection=True,
        use_actual_llm=True
    )

    try:
        # Process Genesis 2:1-15
        verse_range = "Genesis.2.1-15"
        print(f"\nProcessing: {verse_range}")

        results = pipeline.process_verses(verse_range, drop_existing=True)

        print(f"\n{'='*50}")
        print(f"RESULTS SUMMARY")
        print(f"{'='*50}")
        print(f"Verses processed: {results.get('processed_verses', 0)}")
        print(f"Figurative instances found: {results.get('figurative_found', 0)}")
        print(f"Processing errors: {results.get('processing_errors', 0)}")
        print(f"Processing time: {results.get('processing_time', 0):.2f}s")
        print(f"Detection rate: {results['statistics']['detection_rate']:.1f}%")

        if results.get('figurative_found', 0) > 0:
            print(f"\nTop findings:")
            for ref, fig_type, confidence, snippet in results.get('top_findings', []):
                print(f"  {ref}: {fig_type} ({confidence:.2f})")

        print(f"\n📁 Results saved to: genesis_2_test.db")
        return results

    except Exception as e:
        print(f"❌ Error processing verses: {e}")
        return None

if __name__ == "__main__":
    test_genesis_2_verses()