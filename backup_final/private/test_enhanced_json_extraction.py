#!/usr/bin/env python3
"""
Test script for enhanced JSON extraction system

This script tests the new 10-strategy JSON extraction system with various
corruption patterns to ensure it can handle Chapter 15-style failures.
"""

import sys
import os
import json
import logging

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_enhanced_json_extraction():
    """Test the enhanced JSON extraction system with various corruption patterns"""

    print("TESTING Enhanced JSON Extraction System")
    print("=" * 50)

    # Initialize client with enhanced extraction enabled
    client = FlexibleTaggingGeminiClient(api_key="test", logger=logging.getLogger())

    # Test cases representing various corruption patterns
    test_cases = [
        {
            "name": "Normal JSON (should work with strategy 1)",
            "response": '''```json
[
    {
        "figurative_language": "yes",
        "metaphor": "yes",
        "simile": "no",
        "confidence": 0.9,
        "figurative_text": "test",
        "explanation": "test explanation",
        "target": ["domain1"],
        "vehicle": ["domain2"],
        "ground": ["domain3"],
        "posture": ["posture1"]
    }
]
```'''
        },
        {
            "name": "Corrupted JSON with missing comma (Chapter 15-style)",
            "response": '''Here's the detection:

[
    {
        "figurative_language": "yes"
        "metaphor": "yes",
        "simile": "no",
        "confidence": 0.8
    }
]'''
        },
        {
            "name": "Truncated JSON (strategy 5)",
            "response": '''Results:
[
    {
        "figurative_language": "yes",
        "metaphor": "yes",
        "simile": "no",
        "confidence": 0.85
    '''
        },
        {
            "name": "Unescaped quotes in text (strategy 7)",
            "response": '''[
    {
        "figurative_language": "yes",
        "metaphor": "yes",
        "figurative_text": "He said "I am the way"",
        "explanation": "Quote with unescaped quotes",
        "confidence": 0.7
    }
]'''
        },
        {
            "name": "No JSON found (should return None)",
            "response": '''No figurative language detected in this text. The language appears to be literal and straightforward.'''
        }
    ]

    # Run test cases
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTEST {i}: {test_case['name']}")
        print("-" * 40)

        # Test enhanced extraction
        result = client._extract_json_with_fallbacks(
            test_case['response'],
            context=f"test_case_{i}"
        )

        if result:
            try:
                parsed = json.loads(result)
                print(f"SUCCESS: Extracted valid JSON with {len(parsed)} objects")
                if parsed:
                    print(f"   First object keys: {list(parsed[0].keys())}")
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON returned: {e}")
                print(f"   Result: {result[:100]}...")
        else:
            print("FAILED: No JSON extracted")

        # Show strategy usage
        stats = client.get_json_extraction_stats()
        if stats['total_extractions'] > 0:
            print(f"Strategy usage: {stats['most_successful_strategy']}")

    # Final statistics
    print("\n" + "=" * 50)
    print("Final JSON Extraction Statistics:")
    final_stats = client.get_json_extraction_stats()
    print(f"Total extractions: {final_stats['total_extractions']}")
    print(f"Enhanced extraction enabled: {final_stats['enhanced_extraction_enabled']}")

    if final_stats['total_extractions'] > 0:
        print("Strategy usage:")
        for strategy, count in final_stats['strategy_usage'].items():
            if count > 0:
                rate = final_stats['strategy_success_rates'].get(strategy, 0)
                print(f"  {strategy}: {count} uses ({rate:.1f}%)")

    print("\nEnhanced JSON Extraction Test Complete!")

    # Test detection validation
    print("\nTesting detection JSON validation:")
    test_json = '''[
        {"figurative_language": "yes", "metaphor": "yes", "confidence": 0.8},
        {"figurative_language": "no", "metaphor": "no", "confidence": 0.9}
    ]'''

    is_valid = client._validate_detection_json(test_json)
    print(f"Detection JSON validation: {'PASS' if is_valid else 'FAIL'}")

if __name__ == "__main__":
    test_enhanced_json_extraction()