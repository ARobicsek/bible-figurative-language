#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script specifically for reclassification functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Load environment variables
load_dotenv()

def test_reclassification():
    """Test the reclassification functionality directly"""

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return False

    print("=== TESTING RECLASSIFICATION FUNCTIONALITY ===\n")

    validator = MetaphorValidator(api_key)

    # Test case: Something that might be misclassified as metaphor but should be simile
    # "like a lion" - this is clearly a simile, not a metaphor
    test_cases = [
        {
            "name": "Clear Simile (should VALID)",
            "detected_type": "simile",
            "hebrew": "כְּאַרְיֵה",
            "english": "like a lion",
            "figurative_text": "like a lion",
            "explanation": "Direct comparison using 'like'",
            "confidence": 1.0
        },
        {
            "name": "Simile Misclassified as Metaphor (should RECLASSIFY)",
            "detected_type": "metaphor",
            "hebrew": "כְּאַרְיֵה",
            "english": "like a lion",
            "figurative_text": "like a lion",
            "explanation": "This is supposedly a metaphor", # Wrong explanation
            "confidence": 0.8
        },
        {
            "name": "Clear Metaphor (should VALID)",
            "detected_type": "metaphor",
            "hebrew": "גּוּר אַרְיֵה יְהוּדָה",
            "english": "Judah is a lion's whelp",
            "figurative_text": "Judah is a lion's whelp",
            "explanation": "Direct identification without comparison words",
            "confidence": 1.0
        }
    ]

    for test_case in test_cases:
        print(f"--- {test_case['name']} ---")
        print(f"Detected as: {test_case['detected_type']}")
        print(f"Text: {test_case['figurative_text']}")

        is_valid, reason, error, reclassified_type = validator.validate_figurative_type(
            test_case['detected_type'],
            test_case['hebrew'],
            test_case['english'],
            test_case['figurative_text'],
            test_case['explanation'],
            test_case['confidence']
        )

        if error:
            print(f"ERROR: {error}")
        elif reclassified_type:
            print(f"RESULT: RECLASSIFIED from {test_case['detected_type']} to {reclassified_type}")
            print(f"Reason: {reason}")
        elif is_valid:
            print(f"RESULT: VALID as {test_case['detected_type']}")
            print(f"Reason: {reason}")
        else:
            print(f"RESULT: INVALID")
            print(f"Reason: {reason}")

        print()

    # Test validator stats
    stats = validator.get_validation_stats()
    print(f"Validation Stats: {stats}")

    return True

if __name__ == "__main__":
    success = test_reclassification()
    if not success:
        sys.exit(1)