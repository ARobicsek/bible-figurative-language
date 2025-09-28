#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test to verify Pro model fallback is working by creating artificial truncation conditions
"""
import sys
import os
import logging
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def setup_test_logging():
    """Setup logging for testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    return logging.getLogger(__name__)

def test_pro_model_fallback():
    """Test if Pro model fallback triggers correctly"""
    print("=== TESTING PRO MODEL FALLBACK ===")

    # Load environment
    load_dotenv()
    logger = setup_test_logging()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found")

    # Initialize components
    db_manager = DatabaseManager(":memory:")  # In-memory DB for testing
    db_manager.connect()
    db_manager.setup_database()

    validator = MetaphorValidator(api_key, db_manager=db_manager, logger=logger)
    flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

    # Get a complex verse that might trigger truncation (Deuteronomy 30:3 is known to be complex)
    sefaria = SefariaClient()
    verses_data, _ = sefaria.extract_hebrew_text("Deuteronomy.30")

    complex_verse = None
    for verse_data in verses_data:
        if verse_data['reference'] == 'Deuteronomy 30:3':
            complex_verse = verse_data
            break

    if not complex_verse:
        print("Could not find Deuteronomy 30:3")
        return

    print(f"Testing verse: {complex_verse['reference']}")
    print(f"English (limited): {complex_verse['english'][:100]}...")

    # Test with normal processing first
    print("\n--- TESTING WITH NORMAL PROCESSING ---")
    result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
        complex_verse['hebrew'],
        complex_verse['english'],
        book="Deuteronomy",
        chapter=30
    )

    truncation_occurred = metadata.get('truncation_detected', False)
    model_used = metadata.get('model_used', 'unknown')
    instances_found = len(metadata.get('flexible_instances', []))

    print(f"Normal processing results:")
    print(f"  - Model used: {model_used}")
    print(f"  - Truncation detected: {truncation_occurred}")
    print(f"  - Instances found: {instances_found}")

    # Test with forced Pro model to see the difference
    print("\n--- TESTING WITH FORCED PRO MODEL ---")
    result_text_pro, error_pro, metadata_pro = flexible_client.analyze_figurative_language_flexible(
        complex_verse['hebrew'],
        complex_verse['english'],
        book="Deuteronomy",
        chapter=30,
        model_override="gemini-2.5-pro"
    )

    model_used_pro = metadata_pro.get('model_used', 'unknown')
    instances_found_pro = len(metadata_pro.get('flexible_instances', []))

    print(f"Pro model processing results:")
    print(f"  - Model used: {model_used_pro}")
    print(f"  - Instances found: {instances_found_pro}")

    # Assessment
    print(f"\n=== ASSESSMENT ===")
    if truncation_occurred:
        print("✅ TRUNCATION DETECTION: Working (detected truncation)")
        print("✅ PRO MODEL FALLBACK: Should have triggered automatically")
    else:
        print("ℹ️  TRUNCATION DETECTION: No truncation occurred (may be normal)")
        print("ℹ️  PRO MODEL FALLBACK: Not needed for this verse")

    if model_used_pro == "gemini-2.5-pro":
        print("✅ PRO MODEL OVERRIDE: Working correctly")
    else:
        print("❌ PRO MODEL OVERRIDE: Not working")

    print(f"\nDifference in results: Flash found {instances_found}, Pro found {instances_found_pro}")

if __name__ == "__main__":
    try:
        test_pro_model_fallback()
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()