#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rule-Based Detection Validation
Test queries for common figurative patterns in Hebrew text
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import re
import json

def test_figurative_patterns():
    """Test rule-based detection of figurative language patterns"""
    print("Testing rule-based figurative language patterns...")

    # Get Genesis 1-3 data from Sefaria
    base_url = "https://www.sefaria.org/api"

    # Get multiple chapters for testing
    chapters_data = []
    for chapter in range(1, 4):  # Genesis 1-3
        chapter_url = f"{base_url}/texts/Genesis.{chapter}"
        response = requests.get(chapter_url)

        if response.status_code == 200:
            data = response.json()
            hebrew_verses = data.get('he', [])
            english_verses = data.get('text', [])

            for i, (hebrew, english) in enumerate(zip(hebrew_verses, english_verses), 1):
                clean_hebrew = re.sub(r'<[^>]+>', '', hebrew).replace('׃', '')
                clean_english = re.sub(r'<[^>]+>', '', english)

                chapters_data.append({
                    'reference': f'Genesis {chapter}:{i}',
                    'hebrew': clean_hebrew,
                    'english': clean_english
                })

    print(f"Loaded {len(chapters_data)} verses from Genesis 1-3")

    # Test figurative language patterns
    patterns = {
        'similes_hebrew': {
            'description': 'Hebrew similes with כְּ (like/as)',
            'pattern': r'כְּ\w+',
            'examples': []
        },
        'similes_english': {
            'description': 'English similes with like/as',
            'pattern': r'\b(like|as)\s+\w+',
            'examples': []
        },
        'personification': {
            'description': 'Human actions with non-human subjects',
            'keywords': ['said', 'saw', 'called', 'made', 'separated'],
            'examples': []
        },
        'metaphorical_language': {
            'description': 'Potential metaphorical expressions',
            'keywords': ['image', 'likeness', 'face', 'spirit', 'breath'],
            'examples': []
        }
    }

    # Search for patterns
    for verse in chapters_data:
        hebrew = verse['hebrew']
        english = verse['english'].lower()

        # Test Hebrew simile patterns
        if re.search(patterns['similes_hebrew']['pattern'], hebrew):
            patterns['similes_hebrew']['examples'].append(verse)

        # Test English simile patterns
        if re.search(patterns['similes_english']['pattern'], english):
            patterns['similes_english']['examples'].append(verse)

        # Test personification (God performing human actions)
        for keyword in patterns['personification']['keywords']:
            if keyword in english and 'god' in english:
                patterns['personification']['examples'].append(verse)
                break

        # Test metaphorical language
        for keyword in patterns['metaphorical_language']['keywords']:
            if keyword in english:
                patterns['metaphorical_language']['examples'].append(verse)
                break

    # Report results
    print(f"\n=== Rule-Based Pattern Detection Results ===")
    total_found = 0

    for pattern_name, pattern_data in patterns.items():
        examples = pattern_data['examples']
        print(f"\n{pattern_data['description']}: {len(examples)} examples")

        for example in examples[:3]:  # Show first 3 examples
            print(f"  {example['reference']}: {example['english'][:80]}...")

        if len(examples) > 3:
            print(f"  ... and {len(examples) - 3} more")

        total_found += len(examples)

    print(f"\nTotal figurative patterns found: {total_found}")

    # Success criteria: Find 5-10 clear examples
    success = total_found >= 5

    if success:
        print("[SUCCESS] Found sufficient examples for rule-based detection")
    else:
        print("[WARNING] Limited examples found - may need to expand search")

    return success, patterns

if __name__ == "__main__":
    success, patterns = test_figurative_patterns()

    if success:
        print("\n[PHASE 0 CHECKPOINT] Rule-based pattern detection PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Rule-based pattern detection needs improvement")