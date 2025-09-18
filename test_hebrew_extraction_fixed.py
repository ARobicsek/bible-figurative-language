#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract Hebrew words from Genesis 1:1-5 via Sefaria (Fixed API calls)
Success criteria: Extract Hebrew words with basic word-level analysis
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import re
import json

def extract_hebrew_words_fixed():
    print("Extracting Hebrew words from Genesis 1:1-5 (Fixed)...")

    base_url = "https://www.sefaria.org/api"
    extracted_data = []

    try:
        # Try different API endpoint that gets multiple verses at once
        multi_verse_url = f"{base_url}/texts/Genesis.1.1-5"
        response = requests.get(multi_verse_url)

        if response.status_code == 200:
            data = response.json()
            hebrew_verses = data.get('he', [])
            english_verses = data.get('text', [])

            print(f"Retrieved {len(hebrew_verses)} Hebrew verses")
            print(f"Retrieved {len(english_verses)} English verses")

            for i, (hebrew, english) in enumerate(zip(hebrew_verses, english_verses), 1):
                print(f"\n--- Genesis 1:{i} ---")

                # Clean HTML tags
                clean_hebrew = re.sub(r'<[^>]+>', '', hebrew)
                clean_hebrew = clean_hebrew.replace('׃', '')  # Remove sof pasuq
                clean_english = re.sub(r'<[^>]+>', '', english)

                # Split into words
                hebrew_words = clean_hebrew.split()

                verse_data = {
                    'reference': f'Genesis 1:{i}',
                    'hebrew_text': clean_hebrew,
                    'english_text': clean_english,
                    'hebrew_words': hebrew_words,
                    'word_count': len(hebrew_words)
                }

                extracted_data.append(verse_data)

                print(f"Hebrew: {clean_hebrew}")
                print(f"English: {clean_english}")
                print(f"Words ({len(hebrew_words)}): {' | '.join(hebrew_words[:6])}...")

        else:
            # Fallback: individual verse requests with proper formatting
            print("Multi-verse API failed, trying individual requests...")

            for verse_num in range(1, 6):
                verse_url = f"{base_url}/texts/Genesis%201:{verse_num}"
                response = requests.get(verse_url)

                if response.status_code == 200:
                    data = response.json()
                    hebrew = data.get('he', [''])[0] if data.get('he') else ''
                    english = data.get('text', [''])[0] if data.get('text') else ''

                    # Process as above
                    clean_hebrew = re.sub(r'<[^>]+>', '', hebrew).replace('׃', '')
                    hebrew_words = clean_hebrew.split()

                    verse_data = {
                        'reference': f'Genesis 1:{verse_num}',
                        'hebrew_text': clean_hebrew,
                        'english_text': re.sub(r'<[^>]+>', '', english),
                        'hebrew_words': hebrew_words,
                        'word_count': len(hebrew_words)
                    }

                    extracted_data.append(verse_data)
                    print(f"\nGenesis 1:{verse_num}: {clean_hebrew}")

        if not extracted_data:
            print("[FAILURE] No verses extracted")
            return False

        # Analysis
        total_words = sum(v['word_count'] for v in extracted_data)
        print(f"\n=== Extraction Summary ===")
        print(f"Verses processed: {len(extracted_data)}")
        print(f"Total Hebrew words: {total_words}")

        # Save to file
        with open('genesis_1_1_5_extracted.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=2)

        print(f"[SUCCESS] Data saved to genesis_1_1_5_extracted.json")
        print(f"[SUCCESS] Hebrew word extraction completed")
        return True

    except Exception as e:
        print(f"[FAILURE] Error during Hebrew extraction: {e}")
        return False

if __name__ == "__main__":
    success = extract_hebrew_words_fixed()
    if success:
        print("\n[PHASE 0 CHECKPOINT] Hebrew word extraction PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Hebrew word extraction FAILED")