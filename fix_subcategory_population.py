#!/usr/bin/env python3
"""
Script to test and fix subcategory population in the database
"""
import sys
import os
import sqlite3
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api import GeminiAPIClient

def test_markdown_parsing():
    """Test the markdown parsing logic"""
    # Sample response from LLM with markdown
    sample_response = '''```json
[
  {
    "type": "metaphor",
    "hebrew_text": "test",
    "english_text": "The LORD is my shepherd",
    "explanation": "Test explanation",
    "subcategory_level_1": "Human Institutions and Relationships",
    "subcategory_level_2": "agricultural",
    "confidence": 0.95,
    "speaker": "David",
    "purpose": "Test purpose"
  }
]
```'''

    print("=== Testing Markdown Parsing ===")

    # Extract JSON from markdown code block (same logic as hybrid_detector.py)
    json_content = sample_response
    if sample_response.startswith("```json"):
        lines = sample_response.split('\n')
        json_lines = []
        in_json = False
        for line in lines:
            if line.strip() == "```json":
                in_json = True
                continue
            elif line.strip() == "```":
                break
            elif in_json:
                json_lines.append(line)
        json_content = '\n'.join(json_lines)

    print("Extracted JSON:", json_content)

    try:
        data = json.loads(json_content)
        print("Parsing successful!")
        for item in data:
            print(f"Type: {item.get('type')}")
            print(f"Subcategory Level 1: {item.get('subcategory_level_1', 'NOT_FOUND')}")
            print(f"Subcategory Level 2: {item.get('subcategory_level_2', 'NOT_FOUND')}")
        return True
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}")
        return False

def check_database_state():
    """Check current database state"""
    print("\n=== Database State Check ===")
    conn = sqlite3.connect('deuteronomy_enhanced_validation_20250918_232507.db')
    cursor = conn.cursor()

    # Check total records
    cursor.execute('SELECT COUNT(*) FROM figurative_language')
    total = cursor.fetchone()[0]
    print(f"Total records: {total}")

    # Check missing subcategory levels
    cursor.execute('SELECT COUNT(*) FROM figurative_language WHERE subcategory_level_1 IS NULL OR subcategory_level_2 IS NULL')
    missing = cursor.fetchone()[0]
    print(f"Records missing subcategory levels: {missing}")

    # Sample of missing records
    cursor.execute('SELECT id, type, figurative_text FROM figurative_language WHERE subcategory_level_1 IS NULL LIMIT 5')
    missing_samples = cursor.fetchall()
    print("Sample missing records:")
    for record in missing_samples:
        print(f"  ID {record[0]}: {record[1]} - {record[2][:50]}...")

    conn.close()

def populate_missing_subcategories():
    """Populate missing subcategory levels using LLM"""
    print("\n=== Populating Missing Subcategories ===")

    conn = sqlite3.connect('deuteronomy_enhanced_validation_20250918_232507.db')
    cursor = conn.cursor()

    # Initialize Gemini client
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    # Get records missing subcategory levels
    cursor.execute('''
        SELECT fl.id, fl.type, fl.figurative_text, fl.explanation, v.hebrew_text, v.english_text
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.subcategory_level_1 IS NULL OR fl.subcategory_level_2 IS NULL
        LIMIT 10
    ''')

    records = cursor.fetchall()
    print(f"Processing {len(records)} records...")

    for record in records:
        record_id, fig_type, fig_text, explanation, hebrew_text, english_text = record
        print(f"\nProcessing ID {record_id}: {fig_type} - {fig_text[:30]}...")

        try:
            # Get LLM analysis
            response, error = client.analyze_figurative_language(hebrew_text, english_text)

            if error:
                print(f"  Error: {error}")
                continue

            # Parse response
            json_content = response
            if response.startswith("```json"):
                lines = response.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip() == "```json":
                        in_json = True
                        continue
                    elif line.strip() == "```":
                        break
                    elif in_json:
                        json_lines.append(line)
                json_content = '\n'.join(json_lines)

            data = json.loads(json_content)

            # Find matching figurative language instance
            for item in data:
                if item.get('type', '').lower() == fig_type.lower():
                    level1 = item.get('subcategory_level_1', '')
                    level2 = item.get('subcategory_level_2', '')

                    if level1 and level2:
                        # Update database
                        cursor.execute('''
                            UPDATE figurative_language
                            SET subcategory_level_1 = ?, subcategory_level_2 = ?
                            WHERE id = ?
                        ''', (level1, level2, record_id))

                        print(f"  Updated: {level1} | {level2}")
                        break
            else:
                print(f"  No matching type found in LLM response")

        except Exception as e:
            print(f"  Error processing record: {e}")

    conn.commit()
    conn.close()
    print("Database updated!")

if __name__ == "__main__":
    # Test parsing logic first
    if test_markdown_parsing():
        print("Parsing logic works correctly!")

        # Check database state
        check_database_state()

        # Automatically populate missing subcategories
        print("\nAutomatically populating missing subcategories...")
        populate_missing_subcategories()

        # Check final state
        print("\n=== Final Check ===")
        check_database_state()
    else:
        print("Parsing logic failed - check implementation")