#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for the updated multi-type figurative language classification system
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Load environment variables
load_dotenv()

def test_multi_type_detection():
    """Test the multi-type detection and validation system"""

    # Get API key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        return False

    print("=== TESTING MULTI-TYPE FIGURATIVE LANGUAGE SYSTEM ===\n")

    # Initialize components
    db_path = "test_multi_type.db"

    # Clean up any existing test database
    if os.path.exists(db_path):
        os.remove(db_path)

    try:
        with DatabaseManager(db_path) as db_manager:
            # Set up database
            db_manager.setup_database(drop_existing=True)

            # Initialize validator and API client
            validator = MetaphorValidator(api_key, db_manager)
            api_client = MultiModelGeminiClient(api_key, validator, db_manager=db_manager)

            # Test case: Genesis 49:9 (should detect multiple types)
            print("--- Testing Genesis 49:9 (Lion metaphor) ---")
            hebrew = "גּוּר אַרְיֵה יְהוּדָה מִטֶּרֶף בְּנִי עָלִיתָ כָּרַע רָבַץ כְּאַרְיֵה וּכְלָבִיא מִי יְקִימֶנּוּ"
            english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness—who dare rouse him?"

            # Analyze with new multi-type system
            result, error, metadata = api_client.analyze_figurative_language(
                hebrew, english, "Genesis", 49
            )

            if error:
                print(f"ERROR: {error}")
                return False

            print(f"Raw Result: {result}")
            print(f"Metadata keys: {list(metadata.keys())}")

            # Parse the result
            try:
                instances = json.loads(result)
                print(f"Detected {len(instances)} instance(s)")

                for i, instance in enumerate(instances):
                    print(f"\nInstance {i+1}:")
                    print(f"  Text: {instance.get('english_text')}")
                    print(f"  Figurative Language: {instance.get('figurative_language')}")
                    print(f"  Types detected:")
                    for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                        if instance.get(fig_type) == 'yes':
                            print(f"    - {fig_type}: yes")
                    print(f"  Confidence: {instance.get('confidence')}")
                    explanation = instance.get('explanation', '').replace('\u05db\u05b0\u05bc', 'like').replace('\u05d1\u05b0\u05bc', 'b').replace('\u05d5\u05bc', 'v')
                    print(f"  Explanation: {explanation}")

                # Test database insertion
                if instances:
                    print("\n--- Testing Database Insertion ---")

                    # Insert verse
                    verse_data = {
                        'reference': 'Genesis 49:9',
                        'book': 'Genesis',
                        'chapter': 49,
                        'verse': 9,
                        'hebrew': hebrew,
                        'english': english,
                        'word_count': len(english.split()),
                        'llm_deliberation': metadata.get('llm_deliberation', '')
                    }

                    verse_id = db_manager.insert_verse(verse_data)
                    print(f"Inserted verse with ID: {verse_id}")

                    # Insert and validate instances
                    all_instances = metadata.get('all_detected_instances', instances)
                    valid_count = api_client.insert_and_validate_instances(
                        verse_id, all_instances, hebrew, english
                    )

                    print(f"Validated {valid_count} instances")

                    # Check database contents - both initial detection and final validation
                    db_manager.cursor.execute("""
                        SELECT figurative_language, simile, metaphor, personification, idiom,
                               hyperbole, metonymy, other,
                               final_figurative_language, final_simile, final_metaphor, final_personification,
                               final_idiom, final_hyperbole, final_metonymy, final_other,
                               validation_decision_simile, validation_decision_metaphor, validation_decision_personification,
                               validation_decision_idiom, validation_decision_hyperbole, validation_decision_metonymy, validation_decision_other,
                               figurative_text, confidence
                        FROM figurative_language WHERE verse_id = ?
                    """, (verse_id,))

                    db_results = db_manager.cursor.fetchall()
                    print(f"\nDatabase contains {len(db_results)} record(s):")

                    for i, row in enumerate(db_results):
                        print(f"\n  Record {i+1}:")
                        print(f"    Text: {row[23]}")  # Updated index for figurative_text
                        print(f"    Confidence: {row[24]}")  # Updated index for confidence

                        # Initial detection
                        initial_types = []
                        type_names = ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']
                        for j, type_name in enumerate(type_names):
                            if row[j+1] == 'yes':
                                initial_types.append(type_name)
                        print(f"    Initial Detection: {row[0]} - Types: {', '.join(initial_types) if initial_types else 'none'}")

                        # Final validation
                        final_types = []
                        reclassified_info = []
                        for j, type_name in enumerate(type_names):
                            if row[j+9] == 'yes':  # final fields start at index 9
                                final_types.append(type_name)

                            # Check validation decisions for reclassification
                            validation_decision = row[j+16]  # validation decisions start at index 16
                            if validation_decision == 'RECLASSIFIED':
                                reclassified_info.append(f"{type_name} -> reclassified")

                        print(f"    Final Validation: {row[8]} - Types: {', '.join(final_types) if final_types else 'none'}")

                        # Show validation details
                        if reclassified_info:
                            print(f"    [RECLASSIFIED] {', '.join(reclassified_info)}")
                        elif initial_types != final_types:
                            print(f"    [CHANGED] VALIDATION CHANGED RESULTS!")
                        else:
                            print(f"    [CONFIRMED] Validation confirmed initial detection")

            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                return False

            # Test statistics
            print("\n--- Database Statistics ---")
            stats = db_manager.get_statistics()
            print(f"Total verses: {stats['total_verses']}")
            print(f"Total figurative instances: {stats['total_figurative']}")
            print(f"Type breakdown: {stats['type_breakdown']}")

            # Test usage info
            print("\n--- API Usage ---")
            usage = api_client.get_usage_info()
            print(f"Total requests: {usage['total_requests']}")
            print(f"Primary model success rate: {usage['primary_success_rate']:.2%}")

            # Test validator stats
            print("\n--- Validator Statistics ---")
            validator_stats = validator.get_validation_stats()
            print(f"Total validations: {validator_stats['total_validations']}")
            print(f"Total type validations: {validator_stats['total_type_validations']}")

            print("\n=== TEST COMPLETED SUCCESSFULLY ===")
            return True

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        # Clean up test database
        if os.path.exists(db_path):
            os.remove(db_path)

if __name__ == "__main__":
    success = test_multi_type_detection()
    if not success:
        sys.exit(1)