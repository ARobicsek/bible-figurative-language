#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Merge Chapter 3 Data into Chapter 2 Database

This script copies Chapter 3 verses and figurative language instances (with validation)
from private/Proverbs.db into the main proverbs_c2_multi_v_parallel_20251202_1652.db
to create a complete Chapters 1-3 database with full validation coverage.

Usage:
    python merge_chapter3_to_chapter2_db.py
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

def main():
    print("=== MERGE CHAPTER 3 INTO CHAPTER 2 DATABASE ===")
    print(f"Started: {datetime.now()}")
    print()

    # Define paths
    project_dir = Path(__file__).parent.parent
    chapter2_db_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652.db"
    chapter3_db_path = project_dir / "private" / "Proverbs.db"

    # Create backup of Chapter 2 database
    backup_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652_before_ch3_merge.db"
    print(f"1. Creating backup: {backup_path}")
    if backup_path.exists():
        print("WARNING: Backup already exists, overwriting...")
    shutil.copy2(chapter2_db_path, backup_path)
    print("SUCCESS: Backup created.")
    print()

    # Connect to both databases
    print("2. Connecting to databases...")
    try:
        conn2 = sqlite3.connect(str(chapter2_db_path))
        conn3 = sqlite3.connect(str(chapter3_db_path))
        cursor2 = conn2.cursor()
        cursor3 = conn3.cursor()
        print("SUCCESS: Connected to both databases.")
        print()
    except Exception as e:
        print(f"FAIL: Could not connect to databases: {e}")
        return False

    try:
        # Check current state
        print("3. Analyzing current database state...")

        cursor2.execute("SELECT COUNT(*) FROM verses WHERE chapter = 3")
        existing_ch3_verses = cursor2.fetchone()[0]

        cursor2.execute("SELECT COUNT(*) FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 3)")
        existing_ch3_fl = cursor2.fetchone()[0]

        print(f"Chapter 2 database currently has:")
        print(f"  - Chapter 3 verses: {existing_ch3_verses}")
        print(f"  - Chapter 3 figurative instances: {existing_ch3_fl}")

        if existing_ch3_verses > 0:
            print("WARNING: Chapter 3 data already exists. Removing existing Chapter 3 data first...")

            # Delete existing Chapter 3 figurative language
            cursor2.execute("DELETE FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 3)")
            deleted_fl = cursor2.rowcount

            # Delete existing Chapter 3 verses
            cursor2.execute("DELETE FROM verses WHERE chapter = 3")
            deleted_verses = cursor2.rowcount

            print(f"  Deleted {deleted_fl} figurative instances and {deleted_verses} verses from Chapter 3")
            conn2.commit()
        print()

        # Copy Chapter 3 verses
        print("4. Copying Chapter 3 verses...")
        cursor3.execute("""
            SELECT id, reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                   hebrew_text_non_sacred, english_text, english_text_non_sacred, word_count,
                   llm_restriction_error, figurative_detection_deliberation,
                   figurative_detection_deliberation_non_sacred, instances_detected,
                   instances_recovered, instances_lost_to_truncation, truncation_occurred,
                   both_models_truncated, model_used, processed_at
            FROM verses
            WHERE chapter = 3
            ORDER BY verse
        """)

        verses_data = cursor3.fetchall()
        print(f"Found {len(verses_data)} verses to copy")

        # Get column names for verses table
        cursor2.execute("PRAGMA table_info(verses)")
        verses_columns = [col[1] for col in cursor2.fetchall()]

        verses_inserted = 0
        verse_id_mapping = {}  # Map old IDs to new IDs

        for verse_data in verses_data:
            old_id = verse_data[0]
            # Remove the old ID and let SQLite generate new one
            verse_data_without_id = verse_data[1:]

            # Build INSERT query dynamically
            placeholders = ", ".join(["?"] * len(verse_data_without_id))
            columns = ", ".join(verses_columns[1:])  # Skip 'id' column
            query = f"INSERT INTO verses ({columns}) VALUES ({placeholders})"

            cursor2.execute(query, verse_data_without_id)
            new_id = cursor2.lastrowid
            verse_id_mapping[old_id] = new_id
            verses_inserted += 1

        print(f"SUCCESS: Inserted {verses_inserted} Chapter 3 verses")
        print()

        # Copy Chapter 3 figurative language instances
        print("5. Copying Chapter 3 figurative language instances...")
        cursor3.execute("""
            SELECT verse_id, figurative_language, simile, metaphor, personification, idiom,
                   hyperbole, metonymy, other, final_figurative_language, final_simile,
                   final_metaphor, final_personification, final_idiom, final_hyperbole,
                   final_metonymy, final_other, target, vehicle, ground, posture,
                   confidence, figurative_text, figurative_text_in_hebrew,
                   figurative_text_in_hebrew_stripped, figurative_text_in_hebrew_non_sacred,
                   explanation, speaker, purpose, tagging_analysis_deliberation,
                   validation_decision_simile, validation_decision_metaphor,
                   validation_decision_personification, validation_decision_idiom,
                   validation_decision_hyperbole, validation_decision_metonymy,
                   validation_decision_other, validation_reason_simile, validation_reason_metaphor,
                   validation_reason_personification, validation_reason_idiom,
                   validation_reason_hyperbole, validation_reason_metonymy,
                   validation_reason_other, validation_response, validation_error, model_used, processed_at
            FROM figurative_language
            WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 3)
            ORDER BY verse_id, id
        """)

        fl_data = cursor3.fetchall()
        print(f"Found {len(fl_data)} figurative instances to copy")

        fl_inserted = 0
        for instance_data in fl_data:
            old_verse_id = instance_data[0]
            new_verse_id = verse_id_mapping[old_verse_id]

            # Use explicit INSERT with all columns
            cursor2.execute("""
                INSERT INTO figurative_language (
                    verse_id, figurative_language, simile, metaphor, personification, idiom,
                    hyperbole, metonymy, other, final_figurative_language, final_simile,
                    final_metaphor, final_personification, final_idiom, final_hyperbole,
                    final_metonymy, final_other, target, vehicle, ground, posture,
                    confidence, figurative_text, figurative_text_in_hebrew,
                    figurative_text_in_hebrew_stripped, figurative_text_in_hebrew_non_sacred,
                    explanation, speaker, purpose, tagging_analysis_deliberation,
                    validation_decision_simile, validation_decision_metaphor,
                    validation_decision_personification, validation_decision_idiom,
                    validation_decision_hyperbole, validation_decision_metonymy,
                    validation_decision_other, validation_reason_simile, validation_reason_metaphor,
                    validation_reason_personification, validation_reason_idiom,
                    validation_reason_hyperbole, validation_reason_metonymy,
                    validation_reason_other, validation_response, validation_error, model_used, processed_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_verse_id,) + instance_data[1:])

            fl_inserted += 1

        print(f"SUCCESS: Inserted {fl_inserted} Chapter 3 figurative instances")
        print()

        # Commit changes
        conn2.commit()

        # Verify the merge
        print("6. Verifying merged database...")
        cursor2.execute("SELECT COUNT(*) FROM verses")
        total_verses = cursor2.fetchone()[0]

        cursor2.execute("SELECT COUNT(*) FROM figurative_language")
        total_fl = cursor2.fetchone()[0]

        cursor2.execute("SELECT COUNT(*) FROM figurative_language WHERE validation_response IS NOT NULL AND validation_response != ''")
        total_validated = cursor2.fetchone()[0]

        cursor2.execute("SELECT DISTINCT chapter FROM verses ORDER BY chapter")
        chapters = [row[0] for row in cursor2.fetchall()]

        cursor2.execute("""
            SELECT COUNT(*) FROM figurative_language
            WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 3)
            AND validation_response IS NOT NULL AND validation_response != ''
        """)
        ch3_validated = cursor2.fetchone()[0]

        print(f"Merged database summary:")
        print(f"  Total verses: {total_verses}")
        print(f"  Total figurative instances: {total_fl}")
        print(f"  Total validated instances: {total_validated}")
        print(f"  Chapters: {chapters}")
        print(f"  Chapter 3 validated instances: {ch3_validated}")

        if ch3_validated == 37:
            print("SUCCESS: All Chapter 3 instances properly validated!")
        else:
            print(f"WARNING: Expected 37 validated Chapter 3 instances, found {ch3_validated}")

        print()
        print("=== MERGE COMPLETED SUCCESSFULLY ===")
        print(f"Final database: {chapter2_db_path}")
        print(f"Backup saved at: {backup_path}")

        # Close connections
        conn2.close()
        conn3.close()

        return True

    except Exception as e:
        print(f"FAIL: Merge failed with error: {e}")
        import traceback
        traceback.print_exc()

        # Close connections
        conn2.close()
        conn3.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: Chapter 3 merge completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: Chapter 3 merge failed!")
        sys.exit(1)