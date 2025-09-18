#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Sefaria API integration and rate limits
Goal: Retrieve Genesis 1:1-5 in Hebrew + English with <2 second response times
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import time
import json

def test_sefaria_api():
    print("Testing Sefaria API integration...")

    base_url = "https://www.sefaria.org/api"

    try:
        # Test 1: Basic API connectivity
        print("\n--- Test 1: API Connectivity ---")
        start_time = time.time()

        test_url = f"{base_url}/texts/Genesis.1.1"
        response = requests.get(test_url)

        response_time = time.time() - start_time
        print(f"Response time: {response_time:.2f} seconds")

        if response.status_code != 200:
            print(f"[FAILURE] API returned status {response.status_code}")
            return False

        if response_time > 2.0:
            print(f"[WARNING] Response time {response_time:.2f}s exceeds 2s target")
        else:
            print("[SUCCESS] Response time within target")

        # Test 2: Hebrew text retrieval
        print("\n--- Test 2: Hebrew Text Retrieval ---")
        data = response.json()

        if 'he' not in data:
            print("[FAILURE] No Hebrew text found in response")
            return False

        hebrew_text = data['he'][0] if isinstance(data['he'], list) else data['he']
        english_text = data['text'][0] if isinstance(data['text'], list) else data['text']

        print(f"Hebrew: {hebrew_text}")
        print(f"English: {english_text}")
        print("[SUCCESS] Hebrew and English text retrieved")

        # Test 3: Multiple verses (Genesis 1:1-5)
        print("\n--- Test 3: Multiple Verses (Genesis 1:1-5) ---")
        verses_data = []

        for verse in range(1, 6):
            verse_url = f"{base_url}/texts/Genesis.1.{verse}"
            start_time = time.time()

            verse_response = requests.get(verse_url)
            response_time = time.time() - start_time

            if verse_response.status_code != 200:
                print(f"[FAILURE] Failed to get Genesis 1:{verse}")
                return False

            verse_data = verse_response.json()
            hebrew = verse_data['he'][0] if isinstance(verse_data['he'], list) else verse_data['he']
            english = verse_data['text'][0] if isinstance(verse_data['text'], list) else verse_data['text']

            verses_data.append({
                'verse': verse,
                'hebrew': hebrew,
                'english': english,
                'response_time': response_time
            })

            print(f"Genesis 1:{verse} - {response_time:.2f}s")

        avg_response_time = sum(v['response_time'] for v in verses_data) / len(verses_data)
        print(f"\nAverage response time: {avg_response_time:.2f} seconds")

        if avg_response_time > 2.0:
            print("[WARNING] Average response time exceeds 2s target")
        else:
            print("[SUCCESS] Average response time within target")

        # Test 4: Rate limiting check
        print("\n--- Test 4: Rate Limiting ---")
        rapid_requests = []

        for i in range(5):
            start_time = time.time()
            test_response = requests.get(f"{base_url}/texts/Genesis.1.1")
            end_time = time.time()

            rapid_requests.append({
                'request': i+1,
                'status': test_response.status_code,
                'time': end_time - start_time
            })

        rate_limit_issues = [r for r in rapid_requests if r['status'] != 200]

        if rate_limit_issues:
            print(f"[WARNING] {len(rate_limit_issues)} requests failed - possible rate limiting")
        else:
            print("[SUCCESS] No rate limiting detected in rapid requests")

        print(f"\n[SUCCESS] Sefaria API integration working correctly")
        print(f"Retrieved {len(verses_data)} verses successfully")

        return True

    except Exception as e:
        print(f"[FAILURE] Error during Sefaria API test: {e}")
        return False

if __name__ == "__main__":
    success = test_sefaria_api()
    if success:
        print("\n[PHASE 0 CHECKPOINT] Sefaria API validation PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Sefaria API validation FAILED")
        print("Consider local text files as alternative")