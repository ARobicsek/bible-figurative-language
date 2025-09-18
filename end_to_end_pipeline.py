#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
End-to-End Pipeline: Hebrew extraction → AI analysis → database storage
Process Genesis 1:1-10 completely without manual intervention
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
import re
import sqlite3
import json
from datetime import datetime
import time

def confidence_scoring(text, detected_type, pattern_matched=None):
    """
    Develop confidence scoring approach for figurative language detection
    """
    confidence = 0.5  # Base confidence

    # Increase confidence for clear markers
    if detected_type == 'simile':
        if re.search(r'\b(like|as)\s+\w+', text.lower()):
            confidence = 0.9  # Very high for clear simile markers
        elif 'כְּ' in text:  # Hebrew simile marker
            confidence = 0.95

    elif detected_type == 'metaphor':
        # "X is Y" patterns
        if re.search(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text.lower()):
            confidence = 0.85
        elif 'image' in text.lower() or 'likeness' in text.lower():
            confidence = 0.8
        else:
            confidence = 0.7

    elif detected_type == 'personification':
        # God performing human actions
        human_actions = ['said', 'saw', 'called', 'made', 'separated', 'blessed']
        if any(action in text.lower() for action in human_actions) and 'god' in text.lower():
            confidence = 0.8
        else:
            confidence = 0.6

    # Adjust based on pattern matching
    if pattern_matched:
        confidence += 0.1  # Boost for rule-based pattern match

    # Ensure confidence stays in valid range
    return min(max(confidence, 0.0), 1.0)

def detect_figurative_language_enhanced(text, hebrew_text=""):
    """Enhanced figurative language detection with confidence scoring"""
    text_lower = text.lower()

    # Simile detection
    if re.search(r'\b(like|as)\s+\w+', text_lower) or 'כְּ' in hebrew_text:
        pattern = 'like_as_marker' if 'like' in text_lower or 'as' in text_lower else 'hebrew_simile_marker'
        confidence = confidence_scoring(text, 'simile', pattern)
        return 'simile', confidence, pattern

    # Metaphor detection
    if re.search(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text_lower):
        confidence = confidence_scoring(text, 'metaphor', 'is_metaphor')
        return 'metaphor', confidence, 'is_metaphor'

    if 'image' in text_lower or 'likeness' in text_lower:
        confidence = confidence_scoring(text, 'metaphor', 'image_likeness')
        return 'metaphor', confidence, 'image_likeness'

    # Personification detection
    human_actions = ['said', 'saw', 'called', 'made', 'separated', 'blessed']
    if any(action in text_lower for action in human_actions) and 'god' in text_lower:
        confidence = confidence_scoring(text, 'personification', 'god_human_action')
        return 'personification', confidence, 'god_human_action'

    return None, 0.0, None

def setup_database():
    """Set up database connection and schema"""
    conn = sqlite3.connect('figurative_language_pipeline.db')
    cursor = conn.cursor()

    # Create tables (drop existing for clean test)
    cursor.execute('DROP TABLE IF EXISTS figurative_language')
    cursor.execute('DROP TABLE IF EXISTS verses')

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
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute('''
        CREATE TABLE figurative_language (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            text_snippet TEXT NOT NULL,
            hebrew_snippet TEXT,
            type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'other')),
            confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            pattern_matched TEXT,
            ai_analysis TEXT,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (verse_id) REFERENCES verses (id)
        )
    ''')

    conn.commit()
    return conn, cursor

def extract_hebrew_text(verses_range="Genesis.1.1-10"):
    """Extract Hebrew text from Sefaria API"""
    print(f"Extracting Hebrew text for {verses_range}...")

    base_url = "https://www.sefaria.org/api"
    url = f"{base_url}/texts/{verses_range}"

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

    # Process verses
    verses = []
    for i, (hebrew, english) in enumerate(zip(hebrew_verses[:10], english_verses[:10]), 1):  # First 10 verses
        clean_hebrew = re.sub(r'<[^>]+>', '', hebrew).replace('׃', '').strip()
        clean_english = re.sub(r'<[^>]+>', '', english).strip()

        verses.append({
            'reference': f'Genesis 1:{i}',
            'book': 'Genesis',
            'chapter': 1,
            'verse': i,
            'hebrew': clean_hebrew,
            'english': clean_english,
            'word_count': len(clean_hebrew.split())
        })

    return verses

def process_complete_pipeline():
    """Process Genesis 1:1-10 through complete pipeline"""
    print("=== End-to-End Pipeline Processing ===")

    # Step 1: Setup database
    print("\n[STEP 1] Setting up database...")
    conn, cursor = setup_database()

    # Step 2: Extract Hebrew text
    print("\n[STEP 2] Extracting Hebrew text...")
    verses = extract_hebrew_text()

    # Step 3: Process each verse
    print(f"\n[STEP 3] Processing {len(verses)} verses...")

    processed_verses = 0
    figurative_found = 0

    for verse in verses:
        # Insert verse into database
        cursor.execute('''
            INSERT INTO verses (reference, book, chapter, verse, hebrew_text, english_text, word_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (verse['reference'], verse['book'], verse['chapter'], verse['verse'],
              verse['hebrew'], verse['english'], verse['word_count']))

        verse_id = cursor.lastrowid
        processed_verses += 1

        # AI analysis for figurative language
        detected_type, confidence, pattern = detect_figurative_language_enhanced(
            verse['english'], verse['hebrew']
        )

        if detected_type:
            # Determine text snippet and domain
            text_snippet = verse['english']
            if detected_type == 'personification' and 'god' in verse['english'].lower():
                # Extract the action phrase
                words = verse['english'].split()
                god_index = next((i for i, word in enumerate(words) if 'god' in word.lower()), 0)
                text_snippet = ' '.join(words[god_index:god_index+4])  # God + action + object

            domain = 'divine_action' if 'god' in verse['english'].lower() else 'general'

            # Insert figurative language record
            cursor.execute('''
                INSERT INTO figurative_language
                (verse_id, text_snippet, hebrew_snippet, type, confidence, pattern_matched, ai_analysis)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (verse_id, text_snippet, verse['hebrew'][:50], detected_type, confidence, pattern,
                  f"Detected {detected_type} with {confidence:.2f} confidence using pattern: {pattern}"))

            figurative_found += 1

            print(f"  {verse['reference']}: {detected_type} ({confidence:.2f}) - '{text_snippet[:50]}...'")
        else:
            print(f"  {verse['reference']}: No figurative language detected")

    # Step 4: Commit and validate
    conn.commit()

    # Step 5: Validation queries
    print(f"\n[STEP 4] Validation...")

    # Count records
    cursor.execute('SELECT COUNT(*) FROM verses')
    verse_count = cursor.fetchone()[0]

    cursor.execute('SELECT COUNT(*) FROM figurative_language')
    figurative_count = cursor.fetchone()[0]

    # Test queries
    cursor.execute('''
        SELECT v.reference, fl.type, fl.confidence
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        ORDER BY fl.confidence DESC
    ''')
    results = cursor.fetchall()

    conn.close()

    # Results
    print(f"\n=== Pipeline Results ===")
    print(f"✓ Processed {processed_verses} verses")
    print(f"✓ Found {figurative_found} instances of figurative language")
    print(f"✓ Database contains {verse_count} verses, {figurative_count} figurative language records")

    print(f"\nTop figurative language findings:")
    for ref, fig_type, conf in results[:5]:
        print(f"  {ref}: {fig_type} (confidence: {conf:.2f})")

    # Success criteria
    success = (
        processed_verses == 10 and  # All 10 verses processed
        verse_count == 10 and      # All verses in database
        figurative_found > 0       # At least some figurative language found
    )

    return success, processed_verses, figurative_found

if __name__ == "__main__":
    try:
        success, verses_processed, figurative_found = process_complete_pipeline()

        if success:
            print(f"\n🎉 [PHASE 0 FINAL] End-to-End Pipeline PASSED")
            print("✓ Complete pipeline works without manual intervention")
            print("✓ Hebrew extraction → AI analysis → database storage successful")
            print("✓ Ready to proceed to Phase 1")
        else:
            print(f"\n⚠️ [PHASE 0 FINAL] End-to-End Pipeline FAILED")
            print("Pipeline has issues that need resolution")

    except Exception as e:
        print(f"\n❌ [PHASE 0 FINAL] Pipeline ERROR: {e}")
        print("Critical failure - cannot proceed to Phase 1")