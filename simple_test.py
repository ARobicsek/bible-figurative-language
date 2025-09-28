#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test without Unicode characters
"""
import sys
import os
import json
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from hebrew_figurative_db.database.db_manager import DatabaseManager
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def main():
    load_dotenv()

    print("SIMPLE TEST: Genesis 14:20 with Claude")

    # Initialize client
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    client = FlexibleTaggingGeminiClient(gemini_api_key)

    # Test Genesis 14:20
    hebrew_text = "וּבָרוּךְ֙ אֵ֣ל עֶלְי֔וֹן אֲשֶׁר־מִגֵּ֥ן צָרֶ֖יךָ בְּיָדֶ֑ךָ וַיִּתֶּן־ל֥וֹ מַעֲשֵׂ֖ר מִכֹּֽל"
    english_text = "And blessed be God Most High,Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."

    try:
        print("Testing Claude fallback...")
        result_text, error, metadata = client.analyze_with_claude_fallback(
            hebrew_text, english_text, "Genesis", 14
        )

        if error:
            print(f"ERROR: {error}")
            return

        instances = metadata.get('flexible_instances', [])
        print(f"RESULT: {len(instances)} instances found")

        if instances:
            for i, instance in enumerate(instances):
                print(f"  Instance {i+1}: {instance.get('english_text', 'N/A')}")
                print(f"    idiom={instance.get('idiom')}, metaphor={instance.get('metaphor')}")

            # Test database insertion
            db_name = "simple_test.db"
            print(f"Testing database insertion...")

            with DatabaseManager(db_name) as db:
                db.setup_database(drop_existing=True)

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
                print(f"Verse inserted with ID: {verse_id}")

                # Insert instances
                for i, instance in enumerate(instances):
                    figurative_data = {
                        'figurative_language': instance.get('figurative_language', 'no'),
                        'idiom': instance.get('idiom', 'no'),
                        'metaphor': instance.get('metaphor', 'no'),
                        'metonymy': instance.get('metonymy', 'no'),
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
                    print(f"Instance {i+1} inserted with ID: {fig_id}")

                db.commit()

            # Verify
            import sqlite3
            conn = sqlite3.connect(db_name)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM verses')
            verse_count = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM figurative_language')
            instance_count = cursor.fetchone()[0]

            print(f"VERIFICATION: {verse_count} verses, {instance_count} instances in database")

            if instance_count > 0:
                print("SUCCESS: Both detection and database insertion working!")
            else:
                print("PROBLEM: Detection worked but database insertion failed")

            conn.close()

    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()