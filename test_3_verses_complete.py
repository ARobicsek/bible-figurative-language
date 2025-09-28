#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test 3 verses with complete pipeline to verify everything works
"""
import sys
import os
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def main():
    load_dotenv()

    # Test with just 3 verses first
    target_verses = [
        {"book": "Genesis", "chapter": 14, "verse": 20, "reference": "Genesis 14:20"},
        {"book": "Genesis", "chapter": 35, "verse": 13, "reference": "Genesis 35:13"},
        {"book": "Genesis", "chapter": 48, "verse": 10, "reference": "Genesis 48:10"}
    ]

    now = datetime.now()
    db_name = f"test_3_verses_complete_{now.strftime('%Y%m%d_%H%M')}.db"

    print(f"TESTING 3 VERSES WITH COMPLETE PIPELINE")
    print(f"Using Claude Sonnet 4 fallback system")
    print(f"Database: {db_name}")

    # Minimal logging to avoid Unicode issues
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    start_time = time.time()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        print("1. Initializing clients...")
        sefaria = SefariaClient()

        with DatabaseManager(db_name) as db_manager:
            db_manager.setup_database()

            validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
            flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

            total_verses = 0
            total_instances = 0

            for i, verse_info in enumerate(target_verses):
                print(f"\\n2.{i+1} Processing {verse_info['reference']}...")

                # Get the verse data
                chapter = verse_info['chapter']
                verse_num = verse_info['verse']

                verses_data, _ = sefaria.extract_hebrew_text(f"Genesis.{chapter}")
                if not verses_data:
                    print(f"ERROR: Could not get text for Genesis {chapter}")
                    continue

                # Find the target verse
                verse_data = None
                for v in verses_data:
                    if int(v['reference'].split(':')[1]) == verse_num:
                        verse_data = v
                        break

                if not verse_data:
                    print(f"ERROR: Could not find verse {verse_num} in chapter {chapter}")
                    continue

                # Process the verse with full pipeline logic
                try:
                    heb_verse = verse_data['hebrew']
                    eng_verse = verse_data['english']
                    verse_ref = verse_data['reference']

                    print(f"   Analyzing with Gemini Flash...")
                    result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                        heb_verse, eng_verse, book="Genesis", chapter=chapter
                    )

                    # Check for truncation and handle fallbacks
                    truncation_occurred = metadata.get('truncation_detected', False)
                    both_models_truncated = False
                    tertiary_decomposed = False

                    if truncation_occurred:
                        print(f"   Truncation detected, trying Pro model...")
                        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                            heb_verse, eng_verse, book="Genesis", chapter=chapter, model_override="gemini-2.5-pro"
                        )

                        pro_truncation_occurred = metadata.get('truncation_detected', False)
                        both_models_truncated = pro_truncation_occurred

                        if pro_truncation_occurred:
                            print(f"   Pro model also truncated, trying Claude Sonnet 4...")
                            result_text, error, metadata = flexible_client.analyze_with_claude_fallback(
                                heb_verse, eng_verse, book="Genesis", chapter=chapter
                            )
                            tertiary_decomposed = True

                    instances = metadata.get('flexible_instances', [])
                    final_model = metadata.get('model_used', 'gemini-2.5-flash')

                    print(f"   Model used: {final_model}")
                    print(f"   Instances found: {len(instances)}")

                    # Store verse in database
                    verse_db_data = {
                        'reference': verse_ref,
                        'book': 'Genesis',
                        'chapter': chapter,
                        'verse': verse_num,
                        'hebrew': heb_verse,
                        'hebrew_stripped': HebrewTextProcessor.strip_diacritics(heb_verse),
                        'english': eng_verse,
                        'word_count': len(heb_verse.split()),
                        'llm_restriction_error': error,
                        'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
                        'instances_detected': len(instances),
                        'instances_recovered': len(instances),
                        'instances_lost_to_truncation': 0,
                        'truncation_occurred': 'yes' if truncation_occurred else 'no',
                        'both_models_truncated': 'yes' if both_models_truncated else 'no',
                        'model_used': final_model
                    }

                    verse_id = db_manager.insert_verse(verse_db_data)
                    total_verses += 1

                    # Store instances and validate
                    instances_with_db_ids = []
                    for j, instance in enumerate(instances):
                        figurative_data = {
                            'figurative_language': instance.get('figurative_language', 'no'),
                            'simile': instance.get('simile', 'no'),
                            'metaphor': instance.get('metaphor', 'no'),
                            'personification': instance.get('personification', 'no'),
                            'idiom': instance.get('idiom', 'no'),
                            'hyperbole': instance.get('hyperbole', 'no'),
                            'metonymy': instance.get('metonymy', 'no'),
                            'other': instance.get('other', 'no'),
                            'confidence': instance.get('confidence', 0.5),
                            'figurative_text': instance.get('english_text', ''),
                            'figurative_text_in_hebrew': instance.get('hebrew_text', ''),
                            'figurative_text_in_hebrew_stripped': HebrewTextProcessor.strip_diacritics(instance.get('hebrew_text', '')),
                            'explanation': instance.get('explanation', ''),
                            'speaker': instance.get('speaker', ''),
                            'purpose': instance.get('purpose', ''),
                            'target': json.dumps(instance.get('target', [])),
                            'vehicle': json.dumps(instance.get('vehicle', [])),
                            'ground': json.dumps(instance.get('ground', [])),
                            'posture': json.dumps(instance.get('posture', [])),
                            'tagging_analysis_deliberation': metadata.get('tagging_analysis_deliberation', ''),
                            'model_used': final_model
                        }

                        fig_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                        total_instances += 1

                        # Prepare for validation
                        instance_with_db_id = instance.copy()
                        instance_with_db_id['db_id'] = fig_id
                        instances_with_db_ids.append(instance_with_db_id)

                        print(f"   Instance {j+1}: '{instance.get('english_text', 'N/A')}' -> {instance.get('idiom')} idiom, {instance.get('metaphor')} metaphor")

                    # VALIDATION STEP
                    if validator and instances_with_db_ids:
                        print(f"   Running validation on {len(instances_with_db_ids)} instances...")

                        bulk_validation_results = validator.validate_verse_instances(
                            instances_with_db_ids, heb_verse, eng_verse
                        )

                        instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                        for validation_result in bulk_validation_results:
                            instance_id = validation_result.get('instance_id')
                            results = validation_result.get('validation_results', {})
                            db_id = instance_id_to_db_id.get(instance_id)

                            if db_id:
                                validation_data = {}
                                any_valid = False

                                for fig_type, result in results.items():
                                    decision = result.get('decision')
                                    reason = result.get('reason', '')

                                    validation_data[f'validation_decision_{fig_type}'] = decision
                                    validation_data[f'validation_reason_{fig_type}'] = reason

                                    if decision == 'VALID':
                                        validation_data[f'final_{fig_type}'] = 'yes'
                                        any_valid = True
                                    else:
                                        validation_data[f'final_{fig_type}'] = 'no'

                                    print(f"     {fig_type}: {decision}")

                                validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'
                                validation_data['validation_response'] = validation_result.get('full_response', '')
                                validation_data['validation_error'] = validation_result.get('error')

                                db_manager.update_validation_data(db_id, validation_data)

                    db_manager.commit()
                    print(f"   Completed: {len(instances)} instances stored and validated")

                except Exception as e:
                    print(f"   ERROR processing {verse_ref}: {e}")

        total_time = time.time() - start_time

        print(f"\\n=== RESULTS ===")
        print(f"Total verses processed: {total_verses}")
        print(f"Total instances found: {total_instances}")
        print(f"Processing time: {total_time:.1f} seconds")
        print(f"Database: {db_name}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()