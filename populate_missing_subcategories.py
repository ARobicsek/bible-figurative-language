#!/usr/bin/env python3
"""
Populate missing subcategory levels in the database
"""
import sys
import os
import sqlite3
import json
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api import GeminiAPIClient

def populate_subcategories(database_path, limit=20):
    """Populate missing subcategory levels"""
    print(f"=== Populating Subcategories in {database_path} ===")

    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Initialize Gemini client
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    # Get records missing subcategory levels
    cursor.execute('''
        SELECT fl.id, fl.type, fl.figurative_text, v.hebrew_text, v.english_text
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.subcategory_level_1 IS NULL OR fl.subcategory_level_1 = ''
        LIMIT ?
    ''', (limit,))

    records = cursor.fetchall()
    print(f"Found {len(records)} records missing subcategory levels")

    successful_updates = 0

    for record in records:
        record_id, fig_type, fig_text, hebrew_text, english_text = record

        # Safe text display
        safe_fig_text = fig_text.encode('ascii', 'ignore').decode('ascii') if fig_text else "N/A"
        print(f"\nProcessing ID {record_id}: {fig_type} - {safe_fig_text[:30]}...")

        try:
            # Get LLM analysis
            response, error = client.analyze_figurative_language(hebrew_text, english_text)

            if error:
                print(f"  Error: {error}")
                continue

            # Parse response (handle markdown)
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

            # Find matching figurative language instance by type
            updated = False
            for item in data:
                item_type = item.get('type', '').lower()
                if item_type == fig_type.lower():
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
                        successful_updates += 1
                        updated = True
                        break

            if not updated:
                print(f"  No matching type '{fig_type}' found in LLM response")

        except Exception as e:
            print(f"  Error processing record: {e}")

    conn.commit()
    conn.close()

    print(f"\n=== Summary ===")
    print(f"Successfully updated: {successful_updates}/{len(records)} records")

if __name__ == "__main__":
    # Populate both databases
    print("Populating main database...")
    populate_subcategories('deuteronomy_enhanced_validation_20250918_232507.db', limit=10)

    print("\nPopulating test database...")
    populate_subcategories('test_deuteronomy_30_32.db', limit=10)