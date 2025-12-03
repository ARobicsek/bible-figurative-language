#!/usr/bin/env python3
"""
Database Consolidation Script for Proverbs
Merges complete chapters from multiple source databases into a single consolidated database
"""
import sqlite3
import os
import sys
from datetime import datetime

def create_database_schema(conn):
    """Create the database schema for the consolidated database"""

    # Create verses table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT,
            book TEXT,
            chapter INTEGER,
            verse INTEGER,
            hebrew_text TEXT,
            hebrew_text_stripped TEXT,
            hebrew_text_non_sacred TEXT,
            english_text TEXT,
            english_text_non_sacred TEXT,
            word_count INTEGER,
            llm_restriction_error TEXT,
            figurative_detection_deliberation TEXT,
            figurative_detection_deliberation_non_sacred TEXT,
            instances_detected INTEGER,
            instances_recovered INTEGER,
            instances_lost_to_truncation INTEGER,
            truncation_occurred TEXT,
            both_models_truncated TEXT,
            model_used TEXT,
            processed_at TIMESTAMP
        )
    ''')

    # Create figurative_language table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS figurative_language (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER,
            figurative_language TEXT CHECK(figurative_language IN ('yes', 'no')) DEFAULT 'no',
            simile TEXT CHECK(simile IN ('yes', 'no')) DEFAULT 'no',
            metaphor TEXT CHECK(metaphor IN ('yes', 'no')) DEFAULT 'no',
            personification TEXT CHECK(personification IN ('yes', 'no')) DEFAULT 'no',
            idiom TEXT CHECK(idiom IN ('yes', 'no')) DEFAULT 'no',
            hyperbole TEXT CHECK(hyperbole IN ('yes', 'no')) DEFAULT 'no',
            metonymy TEXT CHECK(metonymy IN ('yes', 'no')) DEFAULT 'no',
            other TEXT CHECK(other IN ('yes', 'no')) DEFAULT 'no',
            final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')) DEFAULT 'no',
            final_simile TEXT CHECK(final_simile IN ('yes', 'no')) DEFAULT 'no',
            final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')) DEFAULT 'no',
            final_personification TEXT CHECK(final_personification IN ('yes', 'no')) DEFAULT 'no',
            final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')) DEFAULT 'no',
            final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')) DEFAULT 'no',
            final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')) DEFAULT 'no',
            final_other TEXT CHECK(final_other IN ('yes', 'no')) DEFAULT 'no',
            target TEXT,
            vehicle TEXT,
            ground TEXT,
            posture TEXT,
            confidence REAL,
            figurative_text TEXT,
            figurative_text_in_hebrew TEXT,
            figurative_text_in_hebrew_stripped TEXT,
            figurative_text_in_hebrew_non_sacred TEXT,
            explanation TEXT,
            speaker TEXT,
            purpose TEXT,
            tagging_analysis_deliberation TEXT,
            validation_decision_simile TEXT CHECK(validation_decision_simile IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_metaphor TEXT CHECK(validation_decision_metaphor IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_personification TEXT CHECK(validation_decision_personification IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_idiom TEXT CHECK(validation_decision_idiom IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_hyperbole TEXT CHECK(validation_decision_hyperbole IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_metonymy TEXT CHECK(validation_decision_metonymy IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_decision_other TEXT CHECK(validation_decision_other IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
            validation_reason_simile TEXT,
            validation_reason_metaphor TEXT,
            validation_reason_personification TEXT,
            validation_reason_idiom TEXT,
            validation_reason_hyperbole TEXT,
            validation_reason_metonymy TEXT,
            validation_reason_other TEXT,
            validation_response TEXT,
            validation_error TEXT,
            model_used TEXT,
            processed_at TIMESTAMP,
            FOREIGN KEY (verse_id) REFERENCES verses (id)
        )
    ''')

    # Create indexes
    conn.execute('CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses (book, chapter)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_figurative_verse_id ON figurative_language (verse_id)')

def copy_chapters_from_database(source_conn, target_conn, chapters_to_copy):
    """Copy specified chapters from source database to target database"""
    cursor_source = source_conn.cursor()
    cursor_target = target_conn.cursor()

    for chapter in chapters_to_copy:
        print(f"  Copying Chapter {chapter}...")

        # Get verse mapping for this chapter
        cursor_source.execute('''
            SELECT id, reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                   hebrew_text_non_sacred, english_text, english_text_non_sacred, word_count,
                   llm_restriction_error, figurative_detection_deliberation,
                   figurative_detection_deliberation_non_sacred, instances_detected,
                   instances_recovered, instances_lost_to_truncation, truncation_occurred,
                   both_models_truncated, model_used, processed_at
            FROM verses WHERE book = "Proverbs" AND chapter = ?
            ORDER BY verse
        ''', (chapter,))

        verses = cursor_source.fetchall()

        for verse_data in verses:
            # Insert verse into target database
            cursor_target.execute('''
                INSERT INTO verses (
                    reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                    hebrew_text_non_sacred, english_text, english_text_non_sacred, word_count,
                    llm_restriction_error, figurative_detection_deliberation,
                    figurative_detection_deliberation_non_sacred, instances_detected,
                    instances_recovered, instances_lost_to_truncation, truncation_occurred,
                    both_models_truncated, model_used, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', verse_data[1:])

            verse_id = cursor_target.lastrowid
            source_verse_id = verse_data[0]

            # Copy figurative language data for this verse
            cursor_source.execute('SELECT * FROM figurative_language WHERE verse_id = ?', (source_verse_id,))

            figurative_data = cursor_source.fetchall()

            for fig_data in figurative_data:
                # Get the column names for this database
                cursor_source.execute('PRAGMA table_info(figurative_language)')
                columns_info = cursor_source.fetchall()
                column_names = [col[1] for col in columns_info]

                # Build data dict excluding the id column (index 0)
                data_dict = {}
                for i, col_name in enumerate(column_names[1:], start=1):  # Skip id column
                    if col_name == 'verse_id':
                        data_dict[col_name] = verse_id  # Use new verse_id
                    else:
                        data_dict[col_name] = fig_data[i]

                # Build dynamic INSERT statement
                cols = list(data_dict.keys())
                placeholders = ','.join(['?'] * len(cols))
                values = list(data_dict.values())

                cursor_target.execute(f'INSERT INTO figurative_language ({cols[0]}' +
                                   ''.join(f', {col}' for col in cols[1:]) +
                                   f') VALUES ({placeholders})', values)

def verify_database_integrity(conn):
    """Verify the consolidated database has all expected chapters"""
    cursor = conn.cursor()

    expected_chapters = {
        1: 33, 2: 22, 3: 35, 4: 27, 5: 23, 6: 35, 7: 27, 8: 36,
        11: 31, 12: 28, 13: 25, 14: 35, 16: 33, 17: 28, 18: 24
    }

    print("\\n=== DATABASE INTEGRITY VERIFICATION ===")

    cursor.execute('SELECT chapter, COUNT(*) FROM verses WHERE book = "Proverbs" GROUP BY chapter ORDER BY chapter')
    actual_chapters = dict(cursor.fetchall())

    all_good = True
    for chapter, expected_verses in expected_chapters.items():
        actual_verses = actual_chapters.get(chapter, 0)
        if actual_verses == expected_verses:
            print(f"COMPLETE: Chapter {chapter}: {actual_verses} verses")
        else:
            print(f"MISSING: Chapter {chapter}: {actual_verses}/{expected_verses} verses")
            all_good = False

    # Count total figurative instances
    cursor.execute('SELECT COUNT(*) FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE book = "Proverbs")')
    total_instances = cursor.fetchone()[0]
    print(f"\\nTotal figurative language instances: {total_instances}")

    return all_good

def main():
    print("=== PROVERBS DATABASE CONSOLIDATION ===")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Source databases and chapters to copy
    source_databases = {
        'proverbs_c2_multi_v_parallel_20251202_1652.db': [1, 2, 3],
        'proverbs_c3_multi_v_parallel_20251202_1815.db': [4, 5, 6],
        'proverbs_c6_multi_v_parallel_20251202_1834.db': [8, 11, 12],
        'proverbs_c6_multi_v_parallel_20251202_2038.db': [13, 14, 16, 17, 18]
    }

    target_database = 'Proverbs.db'

    # Remove existing target database if it exists
    if os.path.exists(target_database):
        os.remove(target_database)
        print(f"Removed existing {target_database}")

    # Create target database
    target_conn = sqlite3.connect(target_database)
    create_database_schema(target_conn)
    target_conn.commit()

    print(f"Created {target_database}")

    # Copy chapters from each source database
    total_chapters = sum(len(chapters) for chapters in source_databases.values())
    copied_chapters = 0

    for source_db, chapters in source_databases.items():
        print(f"\\nProcessing {source_db}...")

        if not os.path.exists(source_db):
            print(f"  Warning: {source_db} not found, skipping")
            continue

        try:
            source_conn = sqlite3.connect(source_db)
            copy_chapters_from_database(source_conn, target_conn, chapters)
            source_conn.close()
            copied_chapters += len(chapters)
            print(f"  SUCCESS: Copied chapters: {chapters}")
        except Exception as e:
            print(f"  ERROR: Failed copying from {source_db}: {e}")

    target_conn.commit()

    # Verify database integrity
    if verify_database_integrity(target_conn):
        print("\\nSUCCESS: DATABASE CONSOLIDATION COMPLETED!")
        print(f"Total chapters copied: {copied_chapters}/{total_chapters}")
    else:
        print("\\nWARNING: DATABASE CONSOLIDATION COMPLETED WITH ISSUES!")

    target_conn.close()
    print(f"\\nConsolidated database saved as: {target_database}")

if __name__ == "__main__":
    main()