#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Genesis 22:8 specifically to verify the hardcoded fallback model fix
"""
import sys
import os
import logging
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

    now = datetime.now()
    db_name = f"test_genesis_22_8_fix_{now.strftime('%Y%m%d_%H%M')}.db"

    print(f"TESTING GENESIS 22:8 FIX")
    print(f"Database: {db_name}")

    # Minimal logging
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

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

            print("2. Processing Genesis 22:8...")

            # Get Genesis 22 data
            verses_data, _ = sefaria.extract_hebrew_text("Genesis.22")
            if not verses_data:
                print("ERROR: Could not get text for Genesis 22")
                return

            # Find verse 8
            verse_data = None
            for v in verses_data:
                if int(v['reference'].split(':')[1]) == 8:
                    verse_data = v
                    break

            if not verse_data:
                print("ERROR: Could not find verse 8 in chapter 22")
                return

            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            verse_ref = verse_data['reference']

            print(f"   English: {eng_verse}")
            print(f"   Hebrew length: {len(heb_verse)} characters")

            print("3. Analyzing with flexible tagging system...")
            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book="Genesis", chapter=22
            )

            instances = metadata.get('flexible_instances', [])
            final_model = metadata.get('model_used', 'unknown')

            print(f"   Model used: {final_model}")
            print(f"   Error: {error}")
            print(f"   Instances found: {len(instances)}")

            if error:
                print(f"   ERROR DETAILS: {error}")
            else:
                print("   SUCCESS: No errors occurred!")

            # Store in database
            verse_db_data = {
                'reference': verse_ref,
                'book': 'Genesis',
                'chapter': 22,
                'verse': 8,
                'hebrew': heb_verse,
                'hebrew_stripped': HebrewTextProcessor.strip_diacritics(heb_verse),
                'english': eng_verse,
                'word_count': len(heb_verse.split()),
                'llm_restriction_error': error,
                'figurative_detection_deliberation': metadata.get('figurative_detection_deliberation', ''),
                'instances_detected': len(instances),
                'instances_recovered': len(instances),
                'instances_lost_to_truncation': 0,
                'truncation_occurred': 'no',
                'both_models_truncated': 'no',
                'model_used': final_model
            }

            verse_id = db_manager.insert_verse(verse_db_data)
            db_manager.commit()

            print(f"\\n=== RESULTS ===")
            print(f"Verse processed: {verse_ref}")
            print(f"Model used: {final_model}")
            print(f"Error: {error if error else 'None'}")
            print(f"Instances found: {len(instances)}")
            print(f"Database: {db_name}")

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()