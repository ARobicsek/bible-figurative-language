#!/usr/bin/env python3
"""
Test script to check LLM response format and populate missing subcategory levels
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api import GeminiAPIClient
import json

def test_llm_response():
    """Test what the LLM actually returns for subcategory levels"""
    print("=== Testing LLM Response Format ===")

    # Initialize client
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    # Test with a simple example that should have clear subcategories
    hebrew_text = "יְהוָה רֹעִי לֹא אֶחְסָר"
    english_text = "The LORD is my shepherd; I shall not want"

    print(f"Testing with: {english_text}")
    print("Hebrew: [Hebrew text - shown in response]")

    response, error = client.analyze_figurative_language(hebrew_text, english_text)

    if error:
        print(f"Error: {error}")
        return

    print("\n=== Raw LLM Response ===")
    # Filter out Hebrew text for display
    safe_response = response.encode('ascii', 'ignore').decode('ascii')
    print(safe_response)

    # Try to parse - first handle markdown code block
    json_content = response
    if response.startswith("```json"):
        # Extract JSON from markdown code block
        lines = response.split('\n')
        json_lines = []
        in_json = False
        for line in lines:
            if line.strip() == "```json":
                in_json = True
                continue
            elif line.strip() == "```":
                break
            elif in_json:
                json_lines.append(line)
        json_content = '\n'.join(json_lines)

    print(f"\n=== Extracted JSON Content ===")
    print(json_content[:200] + "..." if len(json_content) > 200 else json_content)

    try:
        data = json.loads(json_content)
        print("\n=== Parsed JSON ===")
        for item in data:
            print(f"Type: {item.get('type')}")
            english_text = item.get('english_text', '').encode('ascii', 'ignore').decode('ascii')
            print(f"Text: {english_text}")
            print(f"Subcategory (old): {item.get('subcategory', 'NOT_FOUND')}")
            print(f"Subcategory Level 1: {item.get('subcategory_level_1', 'NOT_FOUND')}")
            print(f"Subcategory Level 2: {item.get('subcategory_level_2', 'NOT_FOUND')}")
            print("---")
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        print(f"Attempted to parse: {repr(json_content[:100])}")

if __name__ == "__main__":
    test_llm_response()