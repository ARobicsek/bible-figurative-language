#!/usr/bin/env python3
"""
Simple test of JSON extraction from markdown
"""
import json

def test_json_extraction():
    """Test the exact JSON extraction logic"""

    # Sample response that should include subcategory levels
    sample_response = '''```json
[
  {
    "type": "metaphor",
    "hebrew_text": "test",
    "english_text": "The LORD is my shepherd",
    "explanation": "Test explanation",
    "subcategory_level_1": "Human Institutions and Relationships",
    "subcategory_level_2": "agricultural",
    "confidence": 0.95,
    "speaker": "David",
    "purpose": "Test purpose"
  }
]
```'''

    print("=== Testing JSON Extraction ===")
    print("Original response includes subcategory levels")

    # Extract JSON from markdown code block (same logic as hybrid_detector.py)
    json_content = sample_response
    if sample_response.startswith("```json"):
        lines = sample_response.split('\n')
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

    print("Extracted JSON content:")
    print(json_content)

    try:
        data = json.loads(json_content)
        print("\nParsing successful!")

        for item in data:
            print(f"\nItem found:")
            print(f"  Type: {item.get('type')}")
            print(f"  Has subcategory_level_1: {'subcategory_level_1' in item}")
            print(f"  Has subcategory_level_2: {'subcategory_level_2' in item}")
            print(f"  subcategory_level_1: '{item.get('subcategory_level_1', 'MISSING')}'")
            print(f"  subcategory_level_2: '{item.get('subcategory_level_2', 'MISSING')}'")

            # Simulate hybrid_detector logic
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

            print(f"\nResult object subcategory_level_1: '{result['subcategory_level_1']}'")
            print(f"Result object subcategory_level_2: '{result['subcategory_level_2']}'")
            print(f"Result object is empty level_1: {result['subcategory_level_1'] == ''}")
            print(f"Result object is empty level_2: {result['subcategory_level_2'] == ''}")

    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")

if __name__ == "__main__":
    test_json_extraction()