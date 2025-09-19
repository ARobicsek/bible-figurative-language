#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test conservative API on Genesis 1-3 to verify false positive reduction
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
import json

def test_conservative_genesis():
    """Test conservative approach on Genesis 1-3"""

    print("=== TESTING CONSERVATIVE APPROACH ON GENESIS 1-3 ===")

    # Initialize clients
    sefaria = SefariaClient()
    conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

    total_instances = 0
    total_verses = 0

    for chapter in range(1, 4):  # Genesis 1, 2, 3
        print(f"\n--- Processing Genesis {chapter} ---")

        # Get text (extract_hebrew_text returns (verses_list, api_time))
        verses_data, api_time = sefaria.extract_hebrew_text(f"Genesis.{chapter}")

        if not verses_data:
            print(f"Failed to get text for Genesis {chapter}")
            continue

        chapter_instances = 0

        # Process each verse
        for verse_data in verses_data:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            total_verses += 1

            # Analyze with conservative API
            result_json, error = conservative_api.analyze_figurative_language(heb_verse, eng_verse)

            if error:
                print(f"  {verse_ref}: ERROR - {error}")
                continue

            try:
                results = json.loads(result_json)
                if results:  # Found figurative language
                    chapter_instances += len(results)
                    total_instances += len(results)
                    print(f"  {verse_ref}: {len(results)} instances")
                    for result in results:
                        print(f"    {result['type']}: '{result['english_text']}' - {result['explanation']}")

            except json.JSONDecodeError:
                print(f"  {verse_ref}: JSON decode error - {result_json}")

        print(f"Genesis {chapter}: {chapter_instances} figurative instances")

    print(f"\n=== SUMMARY ===")
    print(f"Total verses processed: {total_verses}")
    print(f"Total figurative instances: {total_instances}")
    print(f"Instances per verse: {total_instances/total_verses:.2f}")

    usage = conservative_api.get_usage_info()
    print(f"API usage: {usage}")

if __name__ == "__main__":
    test_conservative_genesis()