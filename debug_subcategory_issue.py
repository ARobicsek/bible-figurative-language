#!/usr/bin/env python3
"""
Debug why subcategory levels aren't being populated
"""
import sys
import os
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api import GeminiAPIClient

def debug_subcategory_issue():
    """Debug the subcategory level population issue"""
    print("=== Debug Subcategory Issue ===")

    # Initialize client
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    # Test with a simple example
    hebrew_text = "יְהוָה רֹעִי לֹא אֶחְסָר"
    english_text = "The LORD is my shepherd; I shall not want"

    print("Testing with shepherd metaphor...")

    response, error = client.analyze_figurative_language(hebrew_text, english_text)

    if error:
        print(f"Error: {error}")
        return

    print("Raw LLM Response:")
    print("=" * 50)
    # Only show ASCII characters to avoid encoding issues
    safe_response = response.encode('ascii', 'ignore').decode('ascii')
    print(safe_response)

    # Now parse exactly like hybrid_detector does
    print("\n" + "=" * 50)
    print("Parsing like hybrid_detector...")

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

    print("Extracted JSON:")
    print(json_content)

    try:
        data = json.loads(json_content)
        print("\nParsed successfully!")

        for item in data:
            print(f"\nItem keys: {list(item.keys())}")
            print(f"Type: {item.get('type')}")
            print(f"English text: {item.get('english_text', '')[:50]}...")
            print(f"Has subcategory_level_1: {'subcategory_level_1' in item}")
            print(f"Has subcategory_level_2: {'subcategory_level_2' in item}")
            print(f"subcategory_level_1 value: {item.get('subcategory_level_1', 'NOT_FOUND')}")
            print(f"subcategory_level_2 value: {item.get('subcategory_level_2', 'NOT_FOUND')}")

            # Show what would be stored in DB
            result = {
                'type': item.get('type', '').lower(),
                'confidence': float(item.get('confidence', 0.0)),
                'pattern': 'llm_detected',
                'figurative_text': item.get('english_text', ''),
                'explanation': item.get('explanation', ''),
                'subcategory': item.get('subcategory', ''),  # Keep for backward compatibility
                'subcategory_level_1': item.get('subcategory_level_1', ''),
                'subcategory_level_2': item.get('subcategory_level_2', ''),
                'hebrew_source': item.get('hebrew_text', ''),
                'speaker': item.get('speaker', ''),
                'purpose': item.get('purpose', '')
            }

            print(f"Would store subcategory_level_1: '{result['subcategory_level_1']}'")
            print(f"Would store subcategory_level_2: '{result['subcategory_level_2']}'")

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")

if __name__ == "__main__":
    debug_subcategory_issue()