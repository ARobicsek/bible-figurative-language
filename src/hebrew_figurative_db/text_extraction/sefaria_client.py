#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sefaria API client for Hebrew text extraction
"""
import requests
import re
import time
from typing import List, Dict, Tuple


class SefariaClient:
    """Client for extracting Hebrew text from Sefaria API"""

    def __init__(self, base_url: str = "https://www.sefaria.org/api"):
        self.base_url = base_url

    def extract_hebrew_text(self, verses_range: str) -> Tuple[List[Dict], float]:
        """
        Extract Hebrew text from Sefaria API

        Args:
            verses_range: Range like "Genesis.1.1-10" or "Genesis.1" for whole chapter

        Returns:
            Tuple of (verses_list, api_response_time)
        """
        print(f"Extracting Hebrew text for {verses_range}...")

        url = f"{self.base_url}/texts/{verses_range}"

        start_time = time.time()
        response = requests.get(url)
        api_time = time.time() - start_time

        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.status_code}")

        data = response.json()
        hebrew_verses = data.get('he', [])
        english_verses = data.get('text', [])

        print(f"API response time: {api_time:.2f}s")
        print(f"Retrieved {len(hebrew_verses)} Hebrew verses, {len(english_verses)} English verses")

        # Parse chapter/verse info from range
        book, chapter_info = verses_range.split('.', 1)
        chapter = int(chapter_info.split('.')[0])

        verses = []
        for i, (hebrew, english) in enumerate(zip(hebrew_verses, english_verses), 1):
            clean_hebrew = self._clean_text(hebrew)
            clean_english = self._clean_text(english)

            verses.append({
                'reference': f'{book} {chapter}:{i}',
                'book': book,
                'chapter': chapter,
                'verse': i,
                'hebrew': clean_hebrew,
                'english': clean_english,
                'word_count': len(clean_hebrew.split())
            })

        return verses, api_time

    def _clean_text(self, text: str) -> str:
        """Clean HTML tags and special characters from text"""
        if not text:
            return ""

        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', '', text)
        # Remove special Hebrew punctuation
        clean_text = clean_text.replace('׃', '').strip()

        return clean_text