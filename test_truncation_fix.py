#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify the truncation detection fix
Tests a few Genesis verses that should NOT trigger false positive truncation
"""
import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def test_truncation_fix():
    """Test the truncation detection fix with simple verses"""

    # Load environment
    dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
    load_dotenv(dotenv_path=dotenv_path)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    print("=== TESTING TRUNCATION DETECTION FIX ===")
    print("Testing verses that should NOT trigger false positive truncation...")

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        # Initialize clients
        sefaria = SefariaClient()
        flexible_client = FlexibleTaggingGeminiClient(api_key, logger=logger)

        # Test verses from Genesis 1 that are unlikely to have figurative language
        test_verses = [
            ("Genesis", 1, 1),  # "In the beginning God created..."
            ("Genesis", 1, 2),  # "The earth was without form..."
            ("Genesis", 1, 3),  # "And God said, Let there be light..."
        ]

        for book, chapter, verse in test_verses:
            print(f"\n--- Testing {book} {chapter}:{verse} ---")

            # Get verse text
            verses_data, _ = sefaria.extract_hebrew_text(f"{book}.{chapter}")
            verse_data = next((v for v in verses_data if int(v['reference'].split(':')[1]) == verse), None)

            if not verse_data:
                print(f"❌ Could not find verse {book} {chapter}:{verse}")
                continue

            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']

            print(f"Hebrew: {heb_verse}")
            print(f"English: {eng_verse}")

            # Analyze with flexible client
            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book=book, chapter=chapter
            )

            # Check results
            truncation_detected = metadata.get('truncation_detected', False)
            instances_count = metadata.get('instances_count', 0)
            model_used = metadata.get('model_used', 'unknown')

            if truncation_detected:
                print(f"❌ FALSE POSITIVE: Truncation incorrectly detected!")
                print(f"   Model used: {model_used}")
                print(f"   Instances count: {instances_count}")
            else:
                print(f"✅ CORRECT: No truncation detected (as expected)")
                print(f"   Model used: {model_used}")
                print(f"   Instances count: {instances_count}")

            if error:
                print(f"⚠️  Error: {error}")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

    print("\n=== TEST COMPLETE ===")
    return True

if __name__ == "__main__":
    try:
        test_truncation_fix()
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
    except Exception as e:
        print(f"Test error: {e}")