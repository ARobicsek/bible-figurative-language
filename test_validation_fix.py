#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the validation fixes for Proverbs chapter 3 processing
"""
import sys
import os
import logging
from datetime import datetime

# Add the private directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'private', 'src'))

from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from hebrew_figurative_db.database.db_manager import DatabaseManager

def test_validation_fixes():
    """Test the enhanced validation system"""

    print("=" * 80)
    print("TESTING VALIDATION FIXES FOR PROVERBS PROCESSING")
    print("=" * 80)

    # Initialize validator
    try:
        validator = MetaphorValidator(logger=logging.getLogger())
        print("SUCCESS: MetaphorValidator initialized successfully")
    except Exception as e:
        print(f"ERROR: Failed to initialize MetaphorValidator: {e}")
        return False

    # Print initial stats
    stats = validator.get_validation_stats()
    print(f"Initial stats: {stats}")

    # Create test instances that mimic what would come from Proverbs chapter 3
    test_instances = [
        {
            'instance_id': 1,
            'verse_reference': 'Proverbs 3:1',
            'hebrew_text': 'beni torati al-tishkach umitzvotai yitzer libecha',
            'english_text': 'My son, do not forget my teaching, but let your heart keep my commandments',
            'figurative_text': 'let your heart keep my commandments',
            'metaphor': 'yes',
            'simile': 'no',
            'personification': 'yes',
            'idiom': 'no',
            'hyperbole': 'no',
            'metonymy': 'no',
            'other': 'no',
            'explanation': 'Heart is metaphorically described as keeping commandments (heart as container/mind)',
            'confidence': 0.85
        },
        {
            'instance_id': 2,
            'verse_reference': 'Proverbs 3:2',
            'hebrew_text': 'ki orekh yamim ushnei chayim veshalom yosif lakh',
            'english_text': 'For length of days and years of life and peace they will add to you',
            'figurative_text': 'length of days',
            'metaphor': 'no',
            'simile': 'no',
            'personification': 'no',
            'idiom': 'yes',
            'hyperbole': 'no',
            'metonymy': 'no',
            'other': 'no',
            'explanation': 'Length of days as idiom for long life',
            'confidence': 0.75
        }
    ]

    print(f"\nTesting chapter validation with {len(test_instances)} test instances...")

    # Test the chapter validation method
    try:
        results = validator.validate_chapter_instances(test_instances)
        print(f"SUCCESS: Chapter validation completed")
        print(f"INFO: Received {len(results)} validation results")

        # Check if we got structured error results (indicating API failure) or actual validation results
        if len(results) == 1 and 'error' in results[0]:
            print("WARNING: Validation failed with structured error:")
            error = results[0]['error']
            print(f"   Error Type: {error['error_type']}")
            print(f"   Error Message: {error['error_message']}")
            print(f"   Context: {error['chapter_context']}")
            print("   This is expected if there's no API key or API issues")
        elif len(results) >= len(test_instances):
            print("SUCCESS: Successfully validated test instances")
            for i, result in enumerate(results[:3]):  # Show first 3 results
                instance_id = result.get('instance_id', i+1)
                validation_results = result.get('validation_results', {})
                print(f"   Instance {instance_id}: {len(validation_results)} type validations")
                for fig_type, validation in validation_results.items():
                    decision = validation.get('decision', 'UNKNOWN')
                    reason = validation.get('reason', '')[:50]
                    print(f"     {fig_type}: {decision} - {reason}...")
        else:
            print(f"WARNING: Unexpected result format: {len(results)} results for {len(test_instances)} instances")

    except Exception as e:
        print(f"ERROR: Chapter validation failed: {e}")
        import traceback
        traceback.print_exc()

    # Print updated stats
    updated_stats = validator.get_validation_stats()
    print(f"\nUpdated stats: {updated_stats}")

    # Print health report
    health_report = validator.get_detailed_health_report()
    print(f"\nHealth Report:")
    print(health_report)

    print("\n" + "=" * 80)
    print("TEST COMPLETED")
    print("=" * 80)

    # Check if validation is working properly
    success_rate = validator.get_success_rate()
    if success_rate > 0:
        print("SUCCESS: Validation system is working!")
        return True
    else:
        print("WARNING: Validation system may have issues (0% success rate)")
        print("   This could be due to missing API key or network issues")
        return False

if __name__ == "__main__":
    test_validation_fixes()