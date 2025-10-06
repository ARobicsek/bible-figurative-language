#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refresh English Text from Sefaria API (Auto-run version)

This script:
1. Fetches fresh English text from Sefaria API for all verses in the database
2. Applies footnote removal using the updated _clean_text() method (with <br> → space fix)
3. Updates existing columns:
   - english_text_clean: Clean text with footnotes removed and proper spacing
   - english_text_clean_non_sacred: Clean text with Hebrew divine names modified
"""
import sys
import os
import sqlite3
import time
from typing import Dict, List, Tuple

# Add the private module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'private'))

from src.hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from src.hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'Pentateuch_Psalms_fig_language.db')

class EnglishTextRefresher:
    """Refreshes English text from Sefaria API with footnote removal and divine names modification"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.sefaria_client = SefariaClient()
        self.divine_modifier = HebrewDivineNamesModifier()
        self.api_call_count = 0
        self.total_api_time = 0.0

    def get_all_verses_to_refresh(self) -> List[Tuple[int, str, str, int, int]]:
        """Get all verses that need English text refreshed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, reference, book, chapter, verse
            FROM verses
            ORDER BY book, chapter, verse
        """)
        verses = cursor.fetchall()
        conn.close()

        return verses

    def fetch_english_for_book_chapter(self, book: str, chapter: int) -> Dict[int, str]:
        """Fetch all English verses for a specific book and chapter"""
        print(f"  Fetching {book} {chapter}...", end=" ", flush=True)

        # Sefaria API call
        verses_range = f"{book}.{chapter}"

        try:
            verses, api_time = self.sefaria_client.extract_hebrew_text(verses_range)
            self.api_call_count += 1
            self.total_api_time += api_time

            # Create mapping of verse number to clean English text
            english_map = {}
            for verse in verses:
                verse_num = verse['verse']
                english_map[verse_num] = verse['english']

            print(f"OK ({len(english_map)} verses, {api_time:.2f}s)")
            return english_map

        except Exception as e:
            print(f"ERROR: {e}")
            return {}

    def refresh_all_verses(self):
        """Refresh English text for all verses in the database"""
        print("=" * 80)
        print("Fetching fresh English text from Sefaria API")
        print("=" * 80)

        verses_to_refresh = self.get_all_verses_to_refresh()
        print(f"\nTotal verses to refresh: {len(verses_to_refresh)}\n")

        # Group verses by book and chapter for efficient API calls
        chapters_by_book = {}
        for verse_id, reference, book, chapter, verse in verses_to_refresh:
            if book not in chapters_by_book:
                chapters_by_book[book] = {}
            if chapter not in chapters_by_book[book]:
                chapters_by_book[book][chapter] = []
            chapters_by_book[book][chapter].append((verse_id, verse))

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        updated_count = 0
        error_count = 0

        # Process each book and chapter
        for book in sorted(chapters_by_book.keys()):
            print(f"\n{book}:")

            for chapter in sorted(chapters_by_book[book].keys()):
                # Fetch all English verses for this chapter
                english_map = self.fetch_english_for_book_chapter(book, chapter)

                if not english_map:
                    error_count += len(chapters_by_book[book][chapter])
                    continue

                # Update each verse
                for verse_id, verse_num in chapters_by_book[book][chapter]:
                    if verse_num in english_map:
                        clean_english = english_map[verse_num]

                        # Apply divine names transformation for non-sacred version
                        clean_non_sacred = self.divine_modifier.modify_english_with_hebrew_terms(clean_english)

                        # Update database
                        cursor.execute("""
                            UPDATE verses
                            SET english_text_clean = ?,
                                english_text_clean_non_sacred = ?
                            WHERE id = ?
                        """, (clean_english, clean_non_sacred, verse_id))

                        updated_count += 1
                    else:
                        print(f"  WARNING: Verse {verse_num} not found in API response")
                        error_count += 1

                # Rate limiting - be nice to Sefaria API
                time.sleep(0.5)

        conn.commit()
        conn.close()

        print(f"\n{'=' * 80}")
        print(f"Summary:")
        print(f"  Updated: {updated_count} verses")
        print(f"  Errors: {error_count} verses")
        print(f"  API calls: {self.api_call_count}")
        print(f"  Total API time: {self.total_api_time:.2f}s")
        print(f"{'=' * 80}\n")

    def verify_results(self):
        """Verify the refresh worked correctly - check spacing fix"""
        print("=" * 80)
        print("Verifying results")
        print("=" * 80)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check specific verses with spacing issues
        test_verses = ["Deuteronomy 33:8", "Deuteronomy 33:4", "Deuteronomy 33:10"]

        print(f"\nTesting verses with spacing issues:")
        for ref in test_verses:
            cursor.execute("""
                SELECT english_text_clean
                FROM verses
                WHERE reference = ?
            """, (ref,))
            result = cursor.fetchone()

            if result:
                new_text = result[0]
                print(f"\n  {ref}:")
                print(f"    {new_text[:120]}...")

        conn.close()
        print()

    def run(self):
        """Run the full refresh process"""
        print("\n" + "=" * 80)
        print("ENGLISH TEXT REFRESH - FIX MISSING SPACES")
        print("=" * 80)
        print("\nThis script will fix missing spaces after line breaks in English text")
        print("by re-fetching from Sefaria API with improved <br> tag handling.\n")

        self.refresh_all_verses()
        self.verify_results()

        print("=" * 80)
        print("REFRESH COMPLETE!")
        print("=" * 80)

if __name__ == "__main__":
    refresher = EnglishTextRefresher(DB_PATH)
    refresher.run()
