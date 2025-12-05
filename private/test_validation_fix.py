#!/usr/bin/env python3
"""
Test script to validate the validation system fixes.
Tests with Isaiah 50 (a small chapter) to verify:
1. No more "validation_coverage_rate" errors
2. Validation data is properly stored
3. Missing validations are recovered inline
"""
import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

def test_validation_fixes():
    """Test the validation fixes on an existing database"""

    # Database to test
    db_path = "isaiah_c10_multi_v_parallel_20251204_1859.db"

    if not os.path.exists(db_path):
        print(f"Error: Database {db_path} not found")
        print("Please run the processor first to create a test database")
        return

    print(f"Testing validation fixes on: {db_path}")
    print("="*60)

    # Initialize database and validator
    db_manager = DatabaseManager(db_path)
    db_manager.connect()

    # Check a specific chapter that had issues
    test_chapters = [50, 51, 52, 53]

    for chapter in test_chapters:
        print(f"\n--- Checking Isaiah {chapter} ---")

        try:
            # Run verification
            verification = db_manager.verify_validation_data_for_chapter("Isaiah", chapter)

            print(f"Total instances: {verification.get('total_instances', 0)}")
            print(f"Instances with validation_response: {verification.get('instances_with_validation', 0)}")
            print(f"Instances with validation decisions: {verification.get('instances_with_decisions', 0)}")
            print(f"Validation coverage rate: {verification.get('validation_coverage_rate', 0):.1f}%")
            print(f"Decision coverage rate: {verification.get('decision_coverage_rate', 0):.1f}%")
            print(f"Needs recovery: {verification.get('needs_recovery', False)}")

            # Check specific verse 53:8 that had missing validation
            if chapter == 53:
                print("\nChecking Isaiah 53:8 specifically...")
                db_manager.cursor.execute("""
                    SELECT fl.id, fl.figurative_language,
                           fl.validation_response, fl.validation_decision_metaphor,
                           fl.final_metaphor, fl.final_figurative_language
                    FROM figurative_language fl
                    JOIN verses v ON fl.verse_id = v.id
                    WHERE v.book = 'Isaiah' AND v.chapter = 53 AND v.verse = 8
                """)
                result = db_manager.cursor.fetchone()

                if result:
                    print(f"  Instance ID: {result[0]}")
                    print(f"  Has figurative_language: {result[1]}")
                    print(f"  Has validation_response: {'Yes' if result[2] else 'No'}")
                    print(f"  Has validation_decision_metaphor: {'Yes' if result[3] else 'No'}")
                    print(f"  Final metaphor: {result[4]}")
                    print(f"  Final figurative_language: {result[5]}")

                    if not result[2] and not result[3]:
                        print("  ⚠️  This instance is missing validation data!")
                        print("  Recommendation: Run recovery script or re-process chapter")
                else:
                    print("  No figurative language found for Isaiah 53:8")

        except Exception as e:
            print(f"Error verifying chapter {chapter}: {e}")

    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY:")
    print("1. If verification passes without errors, the 'validation_coverage_rate' issue is fixed")
    print("2. If decision coverage > 0 but validation coverage = 0, the fallback logic is working")
    print("3. If instances show validation_decision_* fields, validation is being stored")
    print("4. Run the recovery script for any chapters still showing issues:")
    print(f"   python scripts/recover_missing_validation.py --database {db_path}")

    db_manager.close()

if __name__ == "__main__":
    test_validation_fixes()