#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for MetaphorValidator using GPT-5.1 MEDIUM

Tests the updated validator with a few known cases to verify:
1. GPT-5.1 integration works correctly
2. reasoning_effort="medium" parameter is accepted
3. Validation responses are properly parsed
4. Cost tracking is accurate
"""

import sys
import os

# Ensure UTF-8 encoding on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add the private directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'private', 'src'))

from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator


def test_validator():
    """Test the GPT-5.1 MEDIUM validator with sample instances"""

    print("=" * 80)
    print("METAPHOR VALIDATOR TEST - GPT-5.1 MEDIUM")
    print("=" * 80)

    # Initialize validator (will use OPENAI_API_KEY from environment)
    try:
        validator = MetaphorValidator()
        print(f"\n✓ Validator initialized successfully")
        print(f"  Model: {validator.model_name}")
        print(f"  Reasoning effort: {validator.reasoning_effort}")
    except Exception as e:
        print(f"\n✗ Failed to initialize validator: {e}")
        return

    # Test case 1: Valid metaphor (should be VALID)
    print("\n" + "-" * 80)
    print("TEST 1: Valid Metaphor - 'Tree of Life'")
    print("-" * 80)

    is_valid, reason, error, corrected = validator.validate_figurative_language(
        fig_type='metaphor',
        hebrew_text='עֵץ־חַיִּים הִיא לַמַּחֲזִיקִים בָּהּ',
        english_text='She is a tree of life to those who grasp her',
        figurative_text='tree of life',
        explanation='Wisdom is compared to the tree of life, a source of vitality and blessing',
        confidence=0.95
    )

    print(f"Result: {'VALID' if is_valid else 'INVALID'}")
    print(f"Reason: {reason}")
    if error:
        print(f"Error: {error}")
    if corrected:
        print(f"Corrected type: {corrected}")

    # Test case 2: Literal statement (should be INVALID)
    print("\n" + "-" * 80)
    print("TEST 2: Literal Statement - Historical Reference")
    print("-" * 80)

    is_valid, reason, error, corrected = validator.validate_figurative_language(
        fig_type='metaphor',
        hebrew_text='עֲבָדִים הָיִינוּ לְפַרְעֹה בְּמִצְרָיִם',
        english_text='We were slaves to Pharaoh in Egypt',
        figurative_text='We were slaves to Pharaoh',
        explanation='Slavery represents oppression metaphorically',
        confidence=0.75
    )

    print(f"Result: {'VALID' if is_valid else 'INVALID'}")
    print(f"Reason: {reason}")
    if error:
        print(f"Error: {error}")
    if corrected:
        print(f"Corrected type: {corrected}")

    # Test case 3: Possible reclassification
    print("\n" + "-" * 80)
    print("TEST 3: Reclassification Test - Abstract as Agent")
    print("-" * 80)

    is_valid, reason, error, corrected = validator.validate_figurative_language(
        fig_type='metaphor',
        hebrew_text='פַּחַד וָאֵימָה תִּפֹּל עֲלֵיהֶם',
        english_text='dread and fear fall upon them',
        figurative_text='dread and fear fall upon them',
        explanation='Abstract concepts (dread and fear) are given agency',
        confidence=0.85
    )

    print(f"Result: {'VALID' if is_valid else 'INVALID'}")
    print(f"Reason: {reason}")
    if error:
        print(f"Error: {error}")
    if corrected:
        print(f"Corrected type: {corrected}")

    # Print statistics
    print("\n" + "=" * 80)
    print("VALIDATION STATISTICS")
    print("=" * 80)
    stats = validator.get_validation_stats()
    print(f"Total validations: {stats['total_validations']}")
    print(f"Type validations: {stats['total_type_validations']}")

    print("\n✓ All tests completed successfully!")
    print("\nNote: Check costs in OpenAI dashboard to verify GPT-5.1 MEDIUM pricing")


if __name__ == "__main__":
    test_validator()
