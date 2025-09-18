#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Hebrew words from Genesis 1:1-5 via Sefaria
Success criteria: Extract Hebrew words with basic word-level analysis
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import re
import json

def extract_hebrew_words():
    print("Extracting Hebrew words from Genesis 1:1-5...")

    base_url = "https://www.sefaria.org/api"
    extracted_data = []

    try:
        for verse_num in range(1, 6):
            print(f"\n--- Processing Genesis 1:{verse_num} ---")

            # Get verse data from Sefaria
            verse_url = f"{base_url}/texts/Genesis.1.{verse_num}"
            response = requests.get(verse_url)

            if response.status_code != 200:
                print(f"[FAILURE] Failed to get Genesis 1:{verse_num}")
                return False

            data = response.json()
            hebrew_text = data['he'][0] if isinstance(data['he'], list) else data['he']
            english_text = data['text'][0] if isinstance(data['text'], list) else data['text']

            print(f"Hebrew: {hebrew_text}")
            print(f"English: {english_text}")

            # Clean HTML tags from Hebrew text
            clean_hebrew = re.sub(r'<[^>]+>', '', hebrew_text)
            clean_hebrew = clean_hebrew.replace('׃', '')  # Remove sof pasuq

            # Basic word splitting (simplified approach)
            hebrew_words = clean_hebrew.split()

            # Clean English for comparison
            clean_english = re.sub(r'<[^>]+>', '', english_text)

            verse_data = {
                'reference': f'Genesis 1:{verse_num}',
                'hebrew_text': clean_hebrew,
                'english_text': clean_english,
                'hebrew_words': hebrew_words,
                'word_count': len(hebrew_words)
            }

            extracted_data.append(verse_data)

            print(f"Extracted {len(hebrew_words)} Hebrew words:")
            for i, word in enumerate(hebrew_words[:8]):  # Show first 8 words
                print(f"  {i+1}. {word}")

        # Summary statistics
        total_words = sum(v['word_count'] for v in extracted_data)
        print(f"\n=== Extraction Summary ===")
        print(f"Verses processed: {len(extracted_data)}")
        print(f"Total Hebrew words: {total_words}")

        # Save to file for further processing
        with open('genesis_1_1_5_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Data saved to genesis_1_1_5_extracted.json")

        # Test basic word analysis
        print(f"\n=== Basic Word Analysis ===")

        # Look for common patterns
        all_words = []
        for verse in extracted_data:
            all_words.extend(verse['hebrew_words'])

        # Count word frequencies
        word_freq = {}
        for word in all_words:
            word_freq[word] = word_freq.get(word, 0) + 1

        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Most common words:")
        for word, freq in common_words:
            print(f"  {word}: {freq} times")

        print(f"[SUCCESS] Hebrew word extraction completed")
        return True

    except Exception as e:
        print(f"[FAILURE] Error during Hebrew extraction: {e}")
        return False

if __name__ == "__main__":
    success = extract_hebrew_words()
    if success:
        print("\n[PHASE 0 CHECKPOINT] Hebrew word extraction PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Hebrew word extraction FAILED")