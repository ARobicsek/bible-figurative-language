#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final validation test for Genesis 14:20 metaphor - no Unicode output
"""
import sys
import os
import json
import logging
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def main():
    load_dotenv()

    print("FINAL VALIDATION TEST: Genesis 14:20")

    # Initialize clients
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    db_name = "final_validation_test.db"

    # Setup minimal logging to avoid Unicode issues
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    with DatabaseManager(db_name) as db:
        db.setup_database(drop_existing=True)

        # Initialize validator
        validator = MetaphorValidator(gemini_api_key, db_manager=db, logger=logger)
        client = FlexibleTaggingGeminiClient(gemini_api_key, validator=validator, logger=logger, db_manager=db)

        # Test Genesis 14:20
        hebrew_text = "וּבָרוּךְ֙ אֵ֣ל עֶלְי֔וֹן אֲשֶׁר־מִגֵּ֥ן צָרֶ֖יךָ בְּיָדֶ֑ךָ וַיִּתֶּן־ל֥וֹ מַעֲשֵׂ֖ר מִכֹּֽל"
        english_text = "And blessed be God Most High,Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."

        try:
            print("1. Running Claude analysis...")
            result_text, error, metadata = client.analyze_with_claude_fallback(
                hebrew_text, english_text, "Genesis", 14
            )

            if error:
                print(f"ERROR: {error}")
                return

            instances = metadata.get('flexible_instances', [])
            print(f"2. Claude found {len(instances)} instances")

            if instances:
                instance = instances[0]
                print(f"3. Instance details:")
                print(f"   English: {instance.get('english_text', 'N/A')}")
                print(f"   Metaphor: {instance.get('metaphor', 'N/A')}")
                print(f"   Idiom: {instance.get('idiom', 'N/A')}")

                # Insert verse
                verse_data = {
                    'reference': 'Genesis 14:20',
                    'book': 'Genesis',
                    'chapter': 14,
                    'verse': 20,
                    'hebrew': hebrew_text,
                    'english': english_text,
                    'word_count': len(hebrew_text.split()),
                    'instances_detected': len(instances),
                    'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
                    'model_used': metadata.get('model_used', 'claude-3-5-sonnet-20241022'),
                    'truncation_occurred': 'yes',
                    'both_models_truncated': 'yes'
                }
                verse_id = db.insert_verse(verse_data)
                print(f"4. Verse inserted with ID: {verse_id}")

                # Insert instance with correct mapping
                figurative_data = {
                    'figurative_language': instance.get('figurative_language', 'no'),
                    'simile': instance.get('simile', 'no'),
                    'metaphor': instance.get('metaphor', 'no'),  # This should be 'yes'
                    'personification': instance.get('personification', 'no'),
                    'idiom': instance.get('idiom', 'no'),  # This should be 'yes'
                    'hyperbole': instance.get('hyperbole', 'no'),
                    'metonymy': instance.get('metonymy', 'no'),
                    'other': instance.get('other', 'no'),
                    'confidence': instance.get('confidence', 0.0),
                    'figurative_text': instance.get('english_text', ''),
                    'figurative_text_in_hebrew': instance.get('hebrew_text', ''),
                    'explanation': instance.get('explanation', ''),
                    'speaker': instance.get('speaker', ''),
                    'purpose': instance.get('purpose', ''),
                    'target': json.dumps(instance.get('target', [])),
                    'vehicle': json.dumps(instance.get('vehicle', [])),
                    'ground': json.dumps(instance.get('ground', [])),
                    'posture': json.dumps(instance.get('posture', [])),
                    'model_used': metadata.get('model_used', 'claude-3-5-sonnet-20241022')
                }

                fig_id = db.insert_figurative_language(verse_id, figurative_data)
                print(f"5. Instance inserted with ID: {fig_id}")
                print(f"   Database metaphor value: {figurative_data['metaphor']}")
                print(f"   Database idiom value: {figurative_data['idiom']}")

                # Prepare for validation
                instance_with_db_id = instance.copy()
                instance_with_db_id['db_id'] = fig_id
                instances_with_db_ids = [instance_with_db_id]

                db.commit()

                # VALIDATION STEP
                print(f"6. Running validation...")
                if validator and instances_with_db_ids:
                    try:
                        # Run bulk validation
                        bulk_validation_results = validator.validate_verse_instances(
                            instances_with_db_ids, hebrew_text, english_text
                        )

                        print(f"7. Validation returned {len(bulk_validation_results)} results")

                        # Process validation results
                        for validation_result in bulk_validation_results:
                            instance_id = validation_result.get('instance_id')
                            results = validation_result.get('validation_results', {})

                            print(f"8. Processing validation for instance {instance_id}...")

                            # Check if we have metaphor validation
                            metaphor_result = results.get('metaphor', {})
                            print(f"   Metaphor validation decision: {metaphor_result.get('decision', 'N/A')}")

                            # Prepare validation updates for the database
                            # Use the method signature from db_manager.py
                            validation_data = {
                                'validation_decision_simile': results.get('simile', {}).get('decision'),
                                'validation_decision_metaphor': results.get('metaphor', {}).get('decision'),
                                'validation_decision_personification': results.get('personification', {}).get('decision'),
                                'validation_decision_idiom': results.get('idiom', {}).get('decision'),
                                'validation_decision_hyperbole': results.get('hyperbole', {}).get('decision'),
                                'validation_decision_metonymy': results.get('metonymy', {}).get('decision'),
                                'validation_decision_other': results.get('other', {}).get('decision'),
                                'validation_reason_simile': results.get('simile', {}).get('reason'),
                                'validation_reason_metaphor': results.get('metaphor', {}).get('reason'),
                                'validation_reason_personification': results.get('personification', {}).get('reason'),
                                'validation_reason_idiom': results.get('idiom', {}).get('reason'),
                                'validation_reason_hyperbole': results.get('hyperbole', {}).get('reason'),
                                'validation_reason_metonymy': results.get('metonymy', {}).get('reason'),
                                'validation_reason_other': results.get('other', {}).get('reason'),
                                'final_figurative_language': 'yes',  # Assume valid unless all types are invalid
                                'final_simile': results.get('simile', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_metaphor': results.get('metaphor', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_personification': results.get('personification', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_idiom': results.get('idiom', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_hyperbole': results.get('hyperbole', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_metonymy': results.get('metonymy', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'final_other': results.get('other', {}).get('decision') == 'VALID' and 'yes' or 'no',
                                'validation_response': validation_result.get('full_response', ''),
                                'validation_error': validation_result.get('error')
                            }

                            # Update the database
                            db.update_validation_data(fig_id, validation_data)
                            print(f"9. Validation data updated in database")

                        db.commit()
                        print("10. Validation updates committed")

                    except Exception as e:
                        print(f"ERROR during validation: {e}")

        except Exception as e:
            print(f"ERROR: {e}")

    # Final verification
    print("\\n=== FINAL VERIFICATION ===")
    import sqlite3
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT figurative_text, metaphor, idiom,
               validation_decision_metaphor, validation_decision_idiom,
               validation_reason_metaphor
        FROM figurative_language
    ''')

    result = cursor.fetchone()
    if result:
        print(f"Instance: {result[0]}")
        print(f"Original detection - Metaphor: {result[1]}, Idiom: {result[2]}")
        print(f"Validation decision - Metaphor: {result[3]}, Idiom: {result[4]}")
        validation_reason = result[5][:100] if result[5] else "None"
        print(f"Validation reason (metaphor): {validation_reason}...")

        if result[3] or result[4]:
            print("SUCCESS: Validation completed and recorded!")
        else:
            print("ISSUE: No validation decisions recorded")
    else:
        print("ERROR: No instances found")

    conn.close()

if __name__ == "__main__":
    main()