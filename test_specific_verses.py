#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Script for Specific Verses - Genesis 14:20 and Genesis 35:13
Tests the Claude JSON parsing and database insertion fix
"""
import sys
import os
import logging
import json
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def main():
    """Test specific verses: Genesis 14:20 and Genesis 35:13"""
    load_dotenv()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Test data
    test_verses = [
        {
            "reference": "Genesis 14:20",
            "book": "Genesis",
            "chapter": 14,
            "verse": 20,
            "hebrew": "וּבָרוּךְ֙ אֵ֣ל עֶלְי֔וֹן אֲשֶׁר־מִגֵּ֥ן צָרֶ֖יךָ בְּיָדֶ֑ךָ וַיִּתֶּן־ל֥וֹ מַעֲשֵׂ֖ר מִכֹּֽל",
            "english": "And blessed be God Most High,Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."
        },
        {
            "reference": "Genesis 35:13",
            "book": "Genesis",
            "chapter": 35,
            "verse": 13,
            "hebrew": "וַיַּ֥עַל מֵעָלָ֖יו אֱלֹהִ֑ים בַּמָּק֖וֹם אֲשֶׁר־דִּבֶּ֥ר אִתּֽוֹ",
            "english": "God went up from him, at the spot where He had spoken with him."
        }
    ]

    # Create database
    now = datetime.now()
    db_name = f"test_specific_verses_{now.strftime('%Y%m%d_%H%M')}.db"

    print(f"\n=== TESTING SPECIFIC VERSES ===")
    print(f"Testing Genesis 14:20 and Genesis 35:13")
    print(f"Database: {db_name}")

    # Initialize clients
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    client = FlexibleTaggingGeminiClient(gemini_api_key, logger=logger)

    with DatabaseManager(db_name) as db:
        db.setup_database(drop_existing=True)

        for verse_data in test_verses:
            print(f"\n--- Processing {verse_data['reference']} ---")

            try:
                # Try Claude fallback directly (since these verses had truncation issues)
                result_text, error, metadata = client.analyze_with_claude_fallback(
                    verse_data['hebrew'],
                    verse_data['english'],
                    verse_data['book'],
                    verse_data['chapter']
                )

                if error:
                    print(f"❌ Error: {error}")
                    continue

                instances = metadata.get('flexible_instances', [])
                print(f"✅ Claude analysis complete: {len(instances)} instances detected")

                # Insert verse
                verse_db_data = {
                    'reference': verse_data['reference'],
                    'book': verse_data['book'],
                    'chapter': verse_data['chapter'],
                    'verse': verse_data['verse'],
                    'hebrew_text': verse_data['hebrew'],
                    'english_text': verse_data['english'],
                    'instances_detected': len(instances),
                    'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
                    'model_used': metadata.get('model_used', 'claude-3-5-sonnet-20241022'),
                    'truncation_occurred': 'yes',
                    'both_models_truncated': 'yes'
                }
                verse_id = db.insert_verse(verse_db_data)
                print(f"📝 Verse inserted with ID: {verse_id}")

                # Insert instances
                instances_stored = 0
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
                    instances_stored += 1
                    print(f"  💾 Instance {i+1}: '{instance.get('english_text', 'N/A')}' -> ID {fig_id}")
                    print(f"     Types: idiom={instance.get('idiom')}, metaphor={instance.get('metaphor')}, metonymy={instance.get('metonymy')}")

                print(f"✅ {verse_data['reference']}: {instances_stored} instances stored in database")

            except Exception as e:
                print(f"❌ Error processing {verse_data['reference']}: {e}")

        db.commit()

    # Verify results
    print(f"\n=== DATABASE VERIFICATION ===")
    import sqlite3
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM verses')
    verse_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM figurative_language')
    instance_count = cursor.fetchone()[0]

    print(f"📊 Database contains:")
    print(f"   Verses: {verse_count}")
    print(f"   Instances: {instance_count}")

    if instance_count > 0:
        cursor.execute('''
            SELECT v.reference, fl.figurative_text, fl.idiom, fl.metaphor, fl.metonymy, fl.confidence
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
        ''')
        instances = cursor.fetchall()
        print(f"\n📋 Detailed instances:")
        for inst in instances:
            print(f"   {inst[0]}: '{inst[1]}' (confidence: {inst[5]})")
            print(f"     idiom={inst[2]}, metaphor={inst[3]}, metonymy={inst[4]}")

    conn.close()
    print(f"\n🎉 Test complete! Database saved as: {db_name}")

if __name__ == "__main__":
    main()