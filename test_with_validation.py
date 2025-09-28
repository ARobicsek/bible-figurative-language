#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test with validation for Genesis 14:20 metaphor
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

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    print("TEST WITH VALIDATION: Genesis 14:20")

    # Initialize clients
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    db_name = "test_with_validation.db"

    with DatabaseManager(db_name) as db:
        db.setup_database(drop_existing=True)

        # Initialize validator
        validator = MetaphorValidator(gemini_api_key, db_manager=db, logger=logger)
        client = FlexibleTaggingGeminiClient(gemini_api_key, validator=validator, logger=logger, db_manager=db)

        # Test Genesis 14:20
        hebrew_text = "וּבָרוּךְ֙ אֵ֣ל עֶלְי֔וֹן אֲשֶׁר־מִגֵּ֥ן צָרֶ֖יךָ בְּיָדֶ֑ךָ וַיִּתֶּן־ל֥וֹ מַעֲשֵׂ֖ר מִכֹּֽל"
        english_text = "And blessed be God Most High,Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."

        try:
            print("Step 1: Claude analysis...")
            result_text, error, metadata = client.analyze_with_claude_fallback(
                hebrew_text, english_text, "Genesis", 14
            )

            if error:
                print(f"ERROR: {error}")
                return

            instances = metadata.get('flexible_instances', [])
            print(f"Step 2: Found {len(instances)} instances")

            if instances:
                # Debug: Print the raw instance data
                print(f"DEBUG: Raw instance data:")
                for i, instance in enumerate(instances):
                    print(f"  Instance {i+1}: {instance}")

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
                print(f"Step 3: Verse inserted with ID: {verse_id}")

                # Insert instances and prepare for validation
                instances_with_db_ids = []
                for i, instance in enumerate(instances):
                    figurative_data = {
                        'figurative_language': instance.get('figurative_language', 'no'),
                        'simile': instance.get('simile', 'no'),
                        'metaphor': instance.get('metaphor', 'no'),
                        'personification': instance.get('personification', 'no'),
                        'idiom': instance.get('idiom', 'no'),
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
                    print(f"Step 4: Instance {i+1} inserted with ID: {fig_id}")

                    # Prepare for validation
                    instance_with_db_id = instance.copy()
                    instance_with_db_id['db_id'] = fig_id
                    instances_with_db_ids.append(instance_with_db_id)

                db.commit()

                # VALIDATION STEP
                print(f"Step 5: Running validation on {len(instances_with_db_ids)} instances...")
                if validator and instances_with_db_ids:
                    try:
                        # Run bulk validation
                        bulk_validation_results = validator.validate_verse_instances(
                            instances_with_db_ids, hebrew_text, english_text
                        )

                        print(f"Step 6: Validation complete, processing {len(bulk_validation_results)} results...")

                        # Create mapping for easy lookup
                        instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                        # Process validation results
                        for validation_result in bulk_validation_results:
                            instance_id = validation_result.get('instance_id')
                            results = validation_result.get('validation_results', {})

                            db_id = instance_id_to_db_id.get(instance_id)
                            if not db_id:
                                print(f"ERROR: Could not find DB ID for instance {instance_id}")
                                continue

                            print(f"Step 7: Updating validation for instance {instance_id} (DB ID: {db_id})")

                            # Update validation fields
                            validation_updates = {}
                            for fig_type, result in results.items():
                                decision_field = f'validation_decision_{fig_type}'
                                reason_field = f'validation_reason_{fig_type}'

                                validation_updates[decision_field] = result.get('decision')
                                validation_updates[reason_field] = result.get('reason')

                            validation_updates['validation_response'] = validation_result.get('full_response', '')
                            validation_updates['validation_error'] = validation_result.get('error')

                            # Update the database
                            db.update_validation_data(db_id, validation_updates)

                            print(f"  Validation decision for metaphor: {results.get('metaphor', {}).get('decision')}")
                            print(f"  Validation reason for metaphor: {results.get('metaphor', {}).get('reason', 'N/A')[:100]}...")

                        db.commit()
                        print("Step 8: Validation updates committed to database")

                    except Exception as e:
                        print(f"ERROR during validation: {e}")
                        import traceback
                        traceback.print_exc()

        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()

    # Verify results including validation
    print("\\n=== FINAL VERIFICATION ===")
    import sqlite3
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT figurative_text, metaphor,
               validation_decision_metaphor, validation_reason_metaphor
        FROM figurative_language
    ''')

    result = cursor.fetchone()
    if result:
        print(f"Instance: {result[0]}")
        print(f"Metaphor detected: {result[1]}")
        print(f"Validation decision: {result[2]}")
        print(f"Validation reason: {result[3][:100] if result[3] else 'None'}...")

        if result[2]:
            print("SUCCESS: Validation completed!")
        else:
            print("ISSUE: No validation decision recorded")
    else:
        print("ERROR: No instances found")

    conn.close()

if __name__ == "__main__":
    main()