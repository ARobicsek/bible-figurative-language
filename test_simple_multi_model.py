#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test of multi-model API with Genesis 49:9 (Judah lion metaphor)
"""
import sys
import os
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from src.hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient


def test_simple():
    """Simple test with one clear figurative language example"""

    print("SIMPLE MULTI-MODEL TEST")
    print("=" * 50)

    # Initialize APIs
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    multi_model_client = MultiModelGeminiClient(api_key)
    conservative_client = GeminiAPIClient(api_key)

    # Test Genesis 49:9 - Judah lion metaphor (should be detected)
    hebrew = "גּוּר אַרְיֵה יְהוּדָה מִטֶּרֶף בְּנִי עָלִיתָ כָּרַע רָבַץ כְּאַרְיֵה וּכְלָבִיא מִי יְקִימֶנּוּ"
    english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness—who dare rouse him?"

    print("Testing Genesis 49:9 - Judah lion metaphor")
    print(f"English: {english}")
    print()

    # Test multi-model API
    print("Multi-Model API Result:")
    try:
        multi_result, multi_error, multi_metadata = multi_model_client.analyze_figurative_language(
            hebrew, english, "Genesis", 49
        )

        multi_detections = json.loads(multi_result)
        print(f"  Detections: {len(multi_detections)}")
        for detection in multi_detections:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
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
            hebrew, english
        )

        conservative_detections = json.loads(conservative_result)
        print(f"  Detections: {len(conservative_detections)}")
        for detection in conservative_detections:
            print(f"  - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")

        if conservative_error:
            print(f"  Error: {conservative_error}")

    except Exception as e:
        print(f"  Exception: {e}")

    print()
    print("Test completed!")


if __name__ == "__main__":
    test_simple()