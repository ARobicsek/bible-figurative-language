#!/usr/bin/env python3
"""
Add processed chapters to the consolidated Proverbs database
"""
import sqlite3
import os
from datetime import datetime

def add_chapters_to_consolidated(target_db, source_chapters):
    """Add chapters from source databases to the consolidated Proverbs database"""

    print(f"=== ADDING CHAPTERS TO CONSOLIDATED PROVERBS DATABASE ===")
    print(f"Target database: {target_db}")
    print(f"Chapters to add: {source_chapters}")

    if not os.path.exists(target_db):
        print(f"ERROR: Target database {target_db} not found!")
        return False

    target_conn = sqlite3.connect(target_db)
    target_cursor = target_conn.cursor()

    total_verses_added = 0
    total_instances_added = 0

    for chapter_info in source_chapters:
        source_db = chapter_info['database']
        chapter = chapter_info['chapter']

        print(f"\\nAdding Chapter {chapter} from {source_db}...")

        if not os.path.exists(source_db):
            print(f"  ERROR: Source database {source_db} not found, skipping")
            continue

        try:
            source_conn = sqlite3.connect(source_db)
            source_cursor = source_conn.cursor()

            # Check if chapter already exists in target database
            target_cursor.execute('SELECT COUNT(*) FROM verses WHERE book = "Proverbs" AND chapter = ?', (chapter,))
            existing_count = target_cursor.fetchone()[0]

            if existing_count > 0:
                print(f"  WARNING: Chapter {chapter} already has {existing_count} verses, skipping...")
                source_conn.close()
                continue

            # Get verse data from source
            source_cursor.execute('''
                SELECT id, reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                       hebrew_text_non_sacred, english_text, english_text_non_sacred, word_count,
                       llm_restriction_error, figurative_detection_deliberation,
                       figurative_detection_deliberation_non_sacred, instances_detected,
                       instances_recovered, instances_lost_to_truncation, truncation_occurred,
                       both_models_truncated, model_used, processed_at
                FROM verses WHERE book = "Proverbs" AND chapter = ?
                ORDER BY verse
            ''', (chapter,))

            verses = source_cursor.fetchall()
            print(f"  Found {len(verses)} verses to copy")

            for verse_data in verses:
                # Insert verse into target database
                target_cursor.execute('''
                    INSERT INTO verses (
                        reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                        hebrew_text_non_sacred, english_text, english_text_non_sacred, word_count,
                        llm_restriction_error, figurative_detection_deliberation,
                        figurative_detection_deliberation_non_sacred, instances_detected,
                        instances_recovered, instances_lost_to_truncation, truncation_occurred,
                        both_models_truncated, model_used, processed_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', verse_data[1:])

                verse_id = target_cursor.lastrowid
                source_verse_id = verse_data[0]
                total_verses_added += 1

                # Copy figurative language data
                source_cursor.execute('SELECT * FROM figurative_language WHERE verse_id = ?', (source_verse_id,))
                figurative_data = source_cursor.fetchall()

                for fig_data in figurative_data:
                    # Get column names and build dynamic INSERT
                    source_cursor.execute('PRAGMA table_info(figurative_language)')
                    columns_info = source_cursor.fetchall()
                    column_names = [col[1] for col in columns_info]

                    data_dict = {}
                    for i, col_name in enumerate(column_names[1:], start=1):
                        if col_name == 'verse_id':
                            data_dict[col_name] = verse_id
                        else:
                            data_dict[col_name] = fig_data[i]

                    cols = list(data_dict.keys())
                    placeholders = ','.join(['?'] * len(cols))
                    values = list(data_dict.values())

                    target_cursor.execute(f'INSERT INTO figurative_language ({cols[0]}' +
                                       ''.join(f', {col}' for col in cols[1:]) +
                                       f') VALUES ({placeholders})', values)
                    total_instances_added += 1

            source_conn.close()
            print(f"  SUCCESS: Added Chapter {chapter} ({len(verses)} verses)")

        except Exception as e:
            print(f"  ERROR: Failed to add Chapter {chapter}: {e}")
            continue

    target_conn.commit()
    target_conn.close()

    print(f"\\n=== ADDITION COMPLETE ===")
    print(f"Total verses added: {total_verses_added}")
    print(f"Total figurative instances added: {total_instances_added}")

    return True

def verify_final_database(target_db):
    """Verify the final consolidated database has all chapters 1-18"""

    print(f"\\n=== FINAL DATABASE VERIFICATION ===")

    expected_chapters = {
        1: 33, 2: 22, 3: 35, 4: 27, 5: 23, 6: 35, 7: 27, 8: 36,
        9: 18, 10: 32, 11: 31, 12: 28, 13: 25, 14: 35, 15: 33,
        16: 33, 17: 28, 18: 24
    }

    conn = sqlite3.connect(target_db)
    cursor = conn.cursor()

    cursor.execute('SELECT chapter, COUNT(*) FROM verses WHERE book = "Proverbs" GROUP BY chapter ORDER BY chapter')
    actual_chapters = dict(cursor.fetchall())

    print("Chapter coverage:")
    all_complete = True
    for chapter, expected_verses in expected_chapters.items():
        actual_verses = actual_chapters.get(chapter, 0)
        if actual_verses == expected_verses:
            print(f"  COMPLETE: Chapter {chapter}: {actual_verses} verses")
        else:
            print(f"  MISSING: Chapter {chapter}: {actual_verses}/{expected_verses} verses")
            all_complete = False

    # Count total figurative instances
    cursor.execute('SELECT COUNT(*) FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE book = "Proverbs")')
    total_instances = cursor.fetchone()[0]
    print(f"\\nTotal figurative language instances: {total_instances}")

    conn.close()

    if all_complete:
        print("\\n🎉 SUCCESS: All chapters 1-18 complete!")
        return True
    else:
        print("\\n❌ INCOMPLETE: Some chapters are missing")
        return False

def main():
    print("Starting at:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    # Define source databases and chapters
    source_chapters = [
        # Newly processed chapters
        {'database': 'private/proverbs_c7_all_v_batched_20251202_2150.db', 'chapter': 7},
        {'database': 'private/proverbs_c9_all_v_batched_20251202_2141.db', 'chapter': 9},
        {'database': 'private/proverbs_c10_all_v_batched_20251202_2058.db', 'chapter': 10},
    ]

    # Check which source databases actually exist
    existing_chapters = []
    for chapter_info in source_chapters:
        if os.path.exists(chapter_info['database']):
            existing_chapters.append(chapter_info)
        else:
            print(f"Warning: {chapter_info['database']} not found, skipping Chapter {chapter_info['chapter']}")

    if not existing_chapters:
        print("ERROR: No source databases found!")
        return

    # Add chapters to consolidated database
    target_db = 'Proverbs.db'

    if add_chapters_to_consolidated(target_db, existing_chapters):
        # Verify final database
        verify_final_database(target_db)

if __name__ == "__main__":
    main()