#!/usr/bin/env python3
"""
Quick test script to check Claude Sonnet model names
"""
import os
from dotenv import load_dotenv
from claude_sonnet_client import ClaudeSonnetClient
import logging

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_name(model_name):
    """Test a specific model name"""
    print(f"\n=== Testing model: {model_name} ===")

    client = ClaudeSonnetClient(logger=logger)
    client.model_name = model_name

    # Test with a simple verse
    hebrew_text = "וברוך אל עליון אשר־מגן צריך בידך"
    english_text = "And blessed be God Most High, Who has delivered your foes into your hand."

    try:
        result, error, metadata = client.analyze_figurative_language_flexible(
            hebrew_text, english_text, "Genesis", 14
        )

        if error:
            print(f"X Error: {error}")
            return False
        else:
            print(f"SUCCESS! Found {len(metadata['flexible_instances'])} instances")
            return True

    except Exception as e:
        print(f"X Exception: {e}")
        return False

if __name__ == "__main__":
    # Test model names in order of preference
    model_names = [
        "claude-sonnet-4",
        "claude-4-sonnet",
        "claude-3-5-sonnet-20241022"
    ]

    for model_name in model_names:
        success = test_model_name(model_name)
        if success:
            print(f"\nFOUND WORKING MODEL: {model_name}")
            break
    else:
        print("\nNo working model found")