#!/usr/bin/env python3
"""
Debug validator's handling of subcategory fields
"""
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.hybrid_detector import HybridFigurativeDetector

def test_validator_subcategory_handling():
    """Test if validator preserves subcategory fields"""
    print("=== Testing Validator Subcategory Handling ===")

    # Initialize detector with validation enabled
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    detector = HybridFigurativeDetector(
        prefer_llm=True,
        use_actual_llm=True,
        allow_rule_fallback=False,
        enable_metaphor_validation=True,
        gemini_api_key=api_key
    )

    # Test with simple shepherd metaphor
    hebrew_text = "יְהוָה רֹעִי לֹא אֶחְסָר"
    english_text = "The LORD is my shepherd; I shall not want"

    print("Testing with shepherd metaphor...")
    print("Hebrew: [Hebrew text]")
    print(f"English: {english_text}")

    # This will go through the full pipeline including validation
    results, error = detector.detect_figurative_language(english_text, hebrew_text)

    if error:
        print(f"Error: {error}")
        return

    print(f"\nFound {len(results)} results after validation")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  Type: {result.get('type')}")
        print(f"  Confidence: {result.get('confidence')}")
        print(f"  Text: {result.get('figurative_text', '')[:50]}...")
        print(f"  Has subcategory: {'subcategory' in result}")
        print(f"  Has subcategory_level_1: {'subcategory_level_1' in result}")
        print(f"  Has subcategory_level_2: {'subcategory_level_2' in result}")
        print(f"  subcategory_level_1: '{result.get('subcategory_level_1', 'MISSING')}'")
        print(f"  subcategory_level_2: '{result.get('subcategory_level_2', 'MISSING')}'")
        print(f"  All keys: {list(result.keys())}")

if __name__ == "__main__":
    test_validator_subcategory_handling()