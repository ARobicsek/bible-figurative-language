#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Create and test minimal SQLite database schema
Goal: Test database operations and queries for figurative language analysis
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import json
from datetime import datetime

def create_database_schema():
    """Create minimal SQLite schema for figurative language database"""
    print("Creating minimal SQLite database schema...")

    # Create database connection
    conn = sqlite3.connect('figurative_language.db')
    cursor = conn.cursor()

    # Drop existing tables for clean test
    cursor.execute('DROP TABLE IF EXISTS figurative_language')
    cursor.execute('DROP TABLE IF EXISTS verses')

    # Create verses table
    cursor.execute('''
        CREATE TABLE verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            hebrew_text TEXT NOT NULL,
            english_text TEXT NOT NULL,
            word_count INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create figurative language table
    cursor.execute('''
        CREATE TABLE figurative_language (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            text_snippet TEXT NOT NULL,
            hebrew_snippet TEXT,
            type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'other')),
            confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            domain TEXT,
            pattern_matched TEXT,
            ai_analysis TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (verse_id) REFERENCES verses (id)
        )
    ''')

    # Create indexes for common queries
    cursor.execute('CREATE INDEX idx_verses_reference ON verses (reference)')
    cursor.execute('CREATE INDEX idx_verses_book_chapter ON verses (book, chapter)')
    cursor.execute('CREATE INDEX idx_figurative_type ON figurative_language (type)')
    cursor.execute('CREATE INDEX idx_figurative_confidence ON figurative_language (confidence)')

    conn.commit()
    print("[SUCCESS] Database schema created successfully")

    return conn, cursor

def insert_test_records(conn, cursor):
    """Insert 10 test records from Genesis examples"""
    print("\nInserting test records...")

    # Test verse data (from our previous extractions)
    test_verses = [
        {
            'reference': 'Genesis 1:1',
            'book': 'Genesis',
            'chapter': 1,
            'verse': 1,
            'hebrew': 'בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ',
            'english': 'When God began to create heaven and earth',
            'word_count': 7
        },
        {
            'reference': 'Genesis 1:26',
            'book': 'Genesis',
            'chapter': 1,
            'verse': 26,
            'hebrew': 'וַיֹּאמֶר אֱלֹהִים נַעֲשֶׂה אָדָם בְּצַלְמֵנוּ כִּדְמוּתֵנוּ',
            'english': 'And God said, "Let us make humankind in our image, after our likeness"',
            'word_count': 8
        },
        {
            'reference': 'Psalm 23:1',
            'book': 'Psalms',
            'chapter': 23,
            'verse': 1,
            'hebrew': 'יְהוָה רֹעִי לֹא אֶחְסָר',
            'english': 'The Lord is my shepherd; I shall not want',
            'word_count': 5
        }
    ]

    # Insert verses
    verse_ids = []
    for verse in test_verses:
        cursor.execute('''
            INSERT INTO verses (reference, book, chapter, verse, hebrew_text, english_text, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (verse['reference'], verse['book'], verse['chapter'], verse['verse'],
              verse['hebrew'], verse['english'], verse['word_count']))

        verse_ids.append(cursor.lastrowid)

    # Test figurative language records
    test_figurative = [
        {
            'verse_id': verse_ids[0],  # Genesis 1:1
            'text_snippet': 'When God began to create',
            'hebrew_snippet': 'בְּרֵאשִׁית בָּרָא אֱלֹהִים',
            'type': 'personification',
            'confidence': 0.8,
            'domain': 'divine_action',
            'pattern_matched': 'god_human_action',
            'ai_analysis': 'God performing human-like action of creation'
        },
        {
            'verse_id': verse_ids[1],  # Genesis 1:26
            'text_snippet': 'in our image, after our likeness',
            'hebrew_snippet': 'בְּצַלְמֵנוּ כִּדְמוּתֵנוּ',
            'type': 'metaphor',
            'confidence': 0.9,
            'domain': 'divine_similarity',
            'pattern_matched': 'image_likeness',
            'ai_analysis': 'Metaphorical comparison between divine and human nature'
        },
        {
            'verse_id': verse_ids[2],  # Psalm 23:1
            'text_snippet': 'The Lord is my shepherd',
            'hebrew_snippet': 'יְהוָה רֹעִי',
            'type': 'metaphor',
            'confidence': 0.95,
            'domain': 'divine_care',
            'pattern_matched': 'is_metaphor',
            'ai_analysis': 'God metaphorically compared to a shepherd providing care and guidance'
        }
    ]

    # Insert figurative language records
    for fig in test_figurative:
        cursor.execute('''
            INSERT INTO figurative_language
            (verse_id, text_snippet, hebrew_snippet, type, confidence, domain, pattern_matched, ai_analysis)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (fig['verse_id'], fig['text_snippet'], fig['hebrew_snippet'], fig['type'],
              fig['confidence'], fig['domain'], fig['pattern_matched'], fig['ai_analysis']))

    conn.commit()
    print(f"[SUCCESS] Inserted {len(test_verses)} verses and {len(test_figurative)} figurative language records")

    return len(test_verses), len(test_figurative)

def test_database_queries(conn, cursor):
    """Test basic queries for character metaphors, proximity analysis"""
    print("\nTesting database queries...")

    # Query 1: All figurative language by type
    cursor.execute('SELECT type, COUNT(*) FROM figurative_language GROUP BY type')
    type_counts = cursor.fetchall()
    print(f"Figurative language by type: {type_counts}")

    # Query 2: High confidence examples
    cursor.execute('''
        SELECT v.reference, fl.text_snippet, fl.type, fl.confidence
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.confidence > 0.8
        ORDER BY fl.confidence DESC
    ''')
    high_confidence = cursor.fetchall()
    print(f"High confidence examples ({len(high_confidence)}):")
    for row in high_confidence:
        print(f"  {row[0]}: '{row[1]}' ({row[2]}, {row[3]:.2f})")

    # Query 3: Metaphors by domain
    cursor.execute('''
        SELECT domain, COUNT(*) as count, AVG(confidence) as avg_confidence
        FROM figurative_language
        WHERE type = 'metaphor'
        GROUP BY domain
    ''')
    metaphor_domains = cursor.fetchall()
    print(f"Metaphor domains: {metaphor_domains}")

    # Query 4: Proximity analysis (verses in same chapter)
    cursor.execute('''
        SELECT v1.reference as verse1, v2.reference as verse2,
               fl1.type as type1, fl2.type as type2
        FROM figurative_language fl1
        JOIN verses v1 ON fl1.verse_id = v1.id
        JOIN figurative_language fl2 ON fl2.verse_id != fl1.verse_id
        JOIN verses v2 ON fl2.verse_id = v2.id
        WHERE v1.book = v2.book AND v1.chapter = v2.chapter
    ''')
    proximity = cursor.fetchall()
    print(f"Figurative language proximity in same chapter: {len(proximity)} pairs")

    # Performance test
    import time
    start_time = time.time()
    cursor.execute('SELECT COUNT(*) FROM figurative_language fl JOIN verses v ON fl.verse_id = v.id')
    count = cursor.fetchone()[0]
    query_time = time.time() - start_time

    print(f"Query performance: {count} records retrieved in {query_time:.4f} seconds")

    success = query_time < 1.0  # Success if under 1 second
    if success:
        print("[SUCCESS] Database queries execute quickly")
    else:
        print("[WARNING] Database queries are slow")

    return success

def main():
    """Main database testing function"""
    print("=== Database Schema Testing ===")

    try:
        # Create schema
        conn, cursor = create_database_schema()

        # Insert test data
        verses_count, figurative_count = insert_test_records(conn, cursor)

        # Test queries
        query_success = test_database_queries(conn, cursor)

        conn.close()

        print(f"\n=== Database Test Results ===")
        print(f"✓ Schema created successfully")
        print(f"✓ {verses_count} verses inserted")
        print(f"✓ {figurative_count} figurative language records inserted")
        print(f"✓ Queries {'passed' if query_success else 'need optimization'}")

        return True

    except Exception as e:
        print(f"[FAILURE] Database test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n[PHASE 0 CHECKPOINT] Database schema testing PASSED")
    else:
        print("\n[PHASE 0 CHECKPOINT] Database schema testing FAILED")