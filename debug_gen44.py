#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to investigate Genesis 44:29 search issue"""

import sqlite3
import json

# Connect to database
conn = sqlite3.connect('database/Biblical_fig_language.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 80)
print("Investigating Genesis 44:29 search for vehicle 'air'")
print("=" * 80)

# First, get all figurative entries in Genesis 44
print("\n1. All figurative entries in Genesis 44:")
cursor.execute("""
    SELECT v.book, v.chapter, v.verse, v.reference, fl.figurative_text, fl.vehicle
    FROM verses v
    JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.book = 'Genesis' AND v.chapter = 44
""")
gen44_entries = cursor.fetchall()
print(f"Found {len(gen44_entries)} figurative entries in Genesis 44")

# Check if any have 'air' in the vehicle field
print("\n2. Checking for 'air' in vehicle field:")
for row in gen44_entries:
    vehicle = row['vehicle']
    if vehicle and 'air' in vehicle.lower():
        print(f"\n✓ FOUND 'air' in Genesis {row['chapter']}:{row['verse']}")
        print(f"  Reference: {row['reference']}")
        print(f"  Figurative text: {row['figurative_text'][:100]}...")
        print(f"  Vehicle: {vehicle}")

# Specifically check Genesis 44:29
print("\n3. Specifically checking Genesis 44:29:")
cursor.execute("""
    SELECT v.*, fl.*
    FROM verses v
    LEFT JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.book = 'Genesis' AND v.chapter = 44 AND v.verse = 29
""")
verse_29 = cursor.fetchall()
print(f"Found {len(verse_29)} entries for Genesis 44:29")

for row in verse_29:
    print(f"\nVerse ID: {row['id']}")
    print(f"English: {row['english_text_clean'][:150]}")
    if row['figurative_text']:
        print(f"Figurative text: {row['figurative_text']}")
        print(f"Vehicle: {row['vehicle']}")
    else:
        print("No figurative language entry for this verse")

# Check Genesis 42:38 as well (shown in the screenshot)
print("\n4. Checking Genesis 42:38:")
cursor.execute("""
    SELECT v.*, fl.*
    FROM verses v
    LEFT JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.book = 'Genesis' AND v.chapter = 42 AND v.verse = 38
""")
verse_42_38 = cursor.fetchall()
print(f"Found {len(verse_42_38)} entries for Genesis 42:38")

for row in verse_42_38:
    print(f"\nVerse ID: {row['id']}")
    print(f"English: {row['english_text_clean'][:150]}")
    if row['figurative_text']:
        print(f"Figurative text: {row['figurative_text']}")
        print(f"Vehicle: {row['vehicle']}")

# Search for 'air' in vehicle field across all Genesis
print("\n5. ALL Genesis verses with 'air' in vehicle field:")
cursor.execute("""
    SELECT v.book, v.chapter, v.verse, v.reference, fl.figurative_text, fl.vehicle
    FROM verses v
    JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.book = 'Genesis' AND fl.vehicle LIKE '%air%'
""")
all_air_entries = cursor.fetchall()
print(f"Found {len(all_air_entries)} entries with 'air' in vehicle field in Genesis")

for row in all_air_entries:
    print(f"\n  {row['reference']}")
    print(f"  Figurative: {row['figurative_text'][:80]}...")
    print(f"  Vehicle: {row['vehicle']}")

conn.close()
print("\n" + "=" * 80)
