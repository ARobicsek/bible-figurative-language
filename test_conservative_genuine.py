#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test conservative API on verses with genuine figurative language
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
import json

def test_genuine_figurative():
    """Test conservative approach on verses with genuine figurative language"""

    print("=== TESTING CONSERVATIVE API ON GENUINE FIGURATIVE LANGUAGE ===")

    conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

    # Test cases with known genuine figurative language
    test_cases = [
        {
            "name": "Psalm 23:1 - Clear metaphor",
            "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
            "english": "The LORD is my shepherd; I shall not want",
            "expected": "metaphor"
        },
        {
            "name": "Deuteronomy 32:11 - Clear simile",
            "hebrew": "כְּנֶשֶׁר יָעִיר קִנּוֹ עַל־גּוֹזָלָיו יְרַחֵף",
            "english": "Like an eagle that stirs up its nest, hovers over its young",
            "expected": "simile"
        },
        {
            "name": "Psalm 18:8 - Clear personification",
            "hebrew": "גָּעַשׁ וַתִּרְעַשׁ הָאָרֶץ",
            "english": "The earth reeled and rocked",
            "expected": "personification"
        },
        {
            "name": "Isaiah 55:12 - Clear personification",
            "hebrew": "כִּי־בְשִׂמְחָה תֵצֵאוּ וּבְשָׁלוֹם תּוּבָלוּן הֶהָרִים וְהַגְּבָעוֹת יִפְצְחוּ לִפְנֵיכֶם רִנָּה",
            "english": "the mountains and the hills shall break forth before you into singing",
            "expected": "personification"
        },
        {
            "name": "Deuteronomy 32:22 - Divine emotion personification",
            "hebrew": "כִּי־אֵשׁ קָדְחָה בְאַפִּי",
            "english": "For a fire is kindled in My anger",
            "expected": "personification or metaphor"
        }
    ]

    genuine_found = 0
    total_tests = len(test_cases)

    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"English: {case['english']}")
        print(f"Expected: {case['expected']}")

        result_json, error = conservative_api.analyze_figurative_language(case['hebrew'], case['english'])

        if error:
            print(f"ERROR: {error}")
            continue

        try:
            results = json.loads(result_json)
            if results:
                genuine_found += 1
                print(f"FOUND: {len(results)} instances")
                for result in results:
                    print(f"  {result['type']}: '{result['english_text']}'")
            else:
                print("NOT FOUND: [] (may be too conservative)")

        except json.JSONDecodeError:
            print(f"JSON decode error. Raw response: {repr(result_json)}")

    print(f"\n=== GENUINE FIGURATIVE LANGUAGE TEST RESULTS ===")
    print(f"Total test cases: {total_tests}")
    print(f"Genuine figurative found: {genuine_found}")
    print(f"Detection rate: {genuine_found/total_tests:.1%}")

    if genuine_found == 0:
        print("WARNING: Conservative approach may be too restrictive!")
    elif genuine_found == total_tests:
        print("PERFECT: Conservative approach catches genuine figurative language!")
    else:
        print("BALANCED: Conservative approach catches some but not all genuine instances")

    usage = conservative_api.get_usage_info()
    print(f"API usage: {usage}")

if __name__ == "__main__":
    test_genuine_figurative()