#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test LLM-based pipeline vs rule-based pipeline
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline


def compare_detection_methods():
    """Compare LLM-based vs rule-based detection"""
    print("=== COMPARING DETECTION METHODS ===\n")

    # Test on a small sample first
    test_verse = "Genesis.1.26"

    print("1. Testing LLM-BASED Detection (Hebrew + English):")
    print("-" * 50)
    llm_pipeline = FigurativeLanguagePipeline(
        'test_llm_detection.db',
        use_llm_detection=True,
        use_actual_llm=False  # Use simulation for now
    )

    try:
        llm_results = llm_pipeline.process_verses(test_verse, drop_existing=True)
        print(f"LLM Results: {llm_results['figurative_found']} instances found")
        print(f"LLM Detection rate: {llm_results['statistics']['detection_rate']:.1f}%")
        print(f"LLM Type breakdown: {llm_results['statistics']['type_breakdown']}")
    except Exception as e:
        print(f"LLM Pipeline error: {e}")

    print("\n" + "="*60 + "\n")

    print("2. Testing RULE-BASED Detection (English only):")
    print("-" * 50)
    rule_pipeline = FigurativeLanguagePipeline(
        'test_rule_detection.db',
        use_llm_detection=False
    )

    try:
        rule_results = rule_pipeline.process_verses(test_verse, drop_existing=True)
        print(f"Rule Results: {rule_results['figurative_found']} instances found")
        print(f"Rule Detection rate: {rule_results['statistics']['detection_rate']:.1f}%")
        print(f"Rule Type breakdown: {rule_results['statistics']['type_breakdown']}")
    except Exception as e:
        print(f"Rule Pipeline error: {e}")

    print("\n" + "="*60 + "\n")

    # Compare results
    if 'llm_results' in locals() and 'rule_results' in locals():
        print("3. COMPARISON SUMMARY:")
        print("-" * 50)
        print(f"LLM Detection:  {llm_results['figurative_found']} instances")
        print(f"Rule Detection: {rule_results['figurative_found']} instances")
        print()

        print("Advantages of LLM Detection:")
        print("+ Works with original Hebrew text")
        print("+ Can find patterns not pre-coded")
        print("+ Provides detailed explanations")
        print("+ Adapts to varied expressions")
        print()

        print("Advantages of Rule Detection:")
        print("+ Fast and deterministic")
        print("+ No API costs")
        print("+ Consistent results")


def test_hebrew_specific_detection():
    """Test detection of Hebrew-specific figurative language"""
    print("\n=== TESTING HEBREW-SPECIFIC DETECTION ===\n")

    from src.hebrew_figurative_db.ai_analysis.hybrid_detector import HybridFigurativeDetector

    detector = HybridFigurativeDetector(prefer_llm=True)

    # Test cases that should show Hebrew advantages
    test_cases = [
        {
            "name": "Hebrew simile marker כְּ",
            "hebrew": "כַּאֲשֶׁר שָׂשׂ עַל־אֲבֹתֶיךָ",
            "english": "as he delighted in your ancestors"
        },
        {
            "name": "Divine name יהוה",
            "hebrew": "יְהוָה יָשִׂישׂ עָלַיִךְ",
            "english": "the LORD will delight in you"
        },
        {
            "name": "Image/likeness metaphor",
            "hebrew": "בְּצַלְמֵנוּ כִּדְמוּתֵנוּ",
            "english": "in our image, after our likeness"
        }
    ]

    for case in test_cases:
        print(f"Testing: {case['name']}")
        print(f"Hebrew: {case['hebrew']}")
        print(f"English: {case['english']}")

        results = detector.detect_figurative_language(case['english'], case['hebrew'])

        if results:
            print(f"Found {len(results)} instances:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['type']} - {result['figurative_text']}")
                print(f"     {result['explanation']}")
        else:
            print("No figurative language detected")

        print()


if __name__ == "__main__":
    compare_detection_methods()
    test_hebrew_specific_detection()