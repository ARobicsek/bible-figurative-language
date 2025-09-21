#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test multi-model API with English-only text to avoid encoding issues
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from src.hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient


def test_english_only():
    """Test with English-only text to avoid encoding issues"""

    print("ENGLISH-ONLY MULTI-MODEL TEST")
    print("=" * 50)

    # Initialize APIs
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    multi_model_client = MultiModelGeminiClient(api_key)
    conservative_client = GeminiAPIClient(api_key)

    # Test with simple Hebrew transliteration and English
    hebrew_transliteration = "Gur aryeh Yehudah mi-teref beni alita"
    english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness who dare rouse him?"

    print("Testing Genesis 49:9 - Judah lion metaphor (English only)")
    print(f"English: {english}")
    print()

    # Test multi-model API
    print("Multi-Model API Result:")
    try:
        multi_result, multi_error, multi_metadata = multi_model_client.analyze_figurative_language(
            hebrew_transliteration, english, "Genesis", 49
        )

        multi_detections = json.loads(multi_result)
        print(f"  Detections: {len(multi_detections)}")
        for detection in multi_detections:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
            print(f"    Explanation: {detection.get('explanation', 'N/A')}")
        print(f"  Model: {multi_metadata.get('model_used', 'unknown')}")
        print(f"  Fallback: {multi_metadata.get('fallback_used', False)}")

        if multi_error:
            print(f"  Error: {multi_error}")

    except Exception as e:
        print(f"  Exception: {e}")

    print()

    # Test conservative API
    print("Conservative API Result:")
    try:
        conservative_result, conservative_error = conservative_client.analyze_figurative_language(
            hebrew_transliteration, english
        )

        conservative_detections = json.loads(conservative_result)
        print(f"  Detections: {len(conservative_detections)}")
        for detection in conservative_detections:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
            print(f"    Explanation: {detection.get('explanation', 'N/A')}")

        if conservative_error:
            print(f"  Error: {conservative_error}")

    except Exception as e:
        print(f"  Exception: {e}")

    print()

    # Test another verse - Benjamin wolf metaphor
    print("Testing Genesis 49:27 - Benjamin wolf metaphor")
    english2 = "Benjamin is a ravenous wolf; In the morning he consumes the foe, And in the evening he divides the spoil."
    hebrew2 = "Binyamin zeev yitraf ba-boker yokhal ad ve-la-erev yechallek shalal"

    print(f"English: {english2}")
    print()

    # Multi-model test
    print("Multi-Model API Result:")
    try:
        multi_result2, multi_error2, multi_metadata2 = multi_model_client.analyze_figurative_language(
            hebrew2, english2, "Genesis", 49
        )

        multi_detections2 = json.loads(multi_result2)
        print(f"  Detections: {len(multi_detections2)}")
        for detection in multi_detections2:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
            print(f"    Explanation: {detection.get('explanation', 'N/A')}")

    except Exception as e:
        print(f"  Exception: {e}")

    print()

    # Conservative test
    print("Conservative API Result:")
    try:
        conservative_result2, conservative_error2 = conservative_client.analyze_figurative_language(
            hebrew2, english2
        )

        conservative_detections2 = json.loads(conservative_result2)
        print(f"  Detections: {len(conservative_detections2)}")
        for detection in conservative_detections2:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")

    except Exception as e:
        print(f"  Exception: {e}")

    print()
    print("Tests completed!")


if __name__ == "__main__":
    test_english_only()