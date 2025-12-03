#!/usr/bin/env python3
"""
Add Chapter 15 to the consolidated Proverbs database.
Based on the consolidation system from Session 27.
"""

import sqlite3
import shutil
from datetime import datetime
import os

def backup_database(db_path):
    """Create a backup of the database before modification"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{db_path}_backup_{timestamp}"
    shutil.copy2(db_path, backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def get_table_schema(conn, table_name):
    """Get column information for a table"""
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    return [col[1] for col in columns]  # Return column names

def add_chapter15_to_proverbs():
    """Add Chapter 15 data to the consolidated Proverbs database"""

    # Paths
    chapter15_db = "private/proverbs_c15_all_v_batched_20251202_2228.db"
    consolidated_db = "Proverbs.db"

    if not os.path.exists(chapter15_db):
        print(f"ERROR: Chapter 15 database not found: {chapter15_db}")
        return False

    if not os.path.exists(consolidated_db):
        print(f"ERROR: Consolidated Proverbs database not found: {consolidated_db}")
        return False

    print(f"Adding Chapter 15 from {chapter15_db} to {consolidated_db}")

    # Create backup
    backup_path = backup_database(consolidated_db)

    try:
        # Connect to both databases
        conn_main = sqlite3.connect(consolidated_db)
        conn_ch15 = sqlite3.connect(chapter15_db)

        # Get current stats
        main_verses = conn_main.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        main_instances = conn_main.execute("SELECT COUNT(*) FROM figurative_language").fetchone()[0]

        ch15_verses = conn_ch15.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        ch15_instances = conn_ch15.execute("SELECT COUNT(*) FROM figurative_language").fetchone()[0]

        print(f"Current consolidated database: {main_verses} verses, {main_instances} instances")
        print(f"Chapter 15 data to add: {ch15_verses} verses, {ch15_instances} instances")

        # Check if Chapter 15 already exists
        existing_ch15 = conn_main.execute("SELECT COUNT(*) FROM verses WHERE chapter = 15").fetchone()[0]
        if existing_ch15 > 0:
            print(f"WARNING: Chapter 15 already exists with {existing_ch15} verses")
            response = input("Remove existing Chapter 15 data? (y/n): ")
            if response.lower() == 'y':
                # Delete existing Chapter 15 data
                conn_main.execute("DELETE FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE chapter = 15)")
                conn_main.execute("DELETE FROM verses WHERE chapter = 15")
                conn_main.commit()
                print("Removed existing Chapter 15 data")
            else:
                print("Aborted - Chapter 15 data already exists")
                conn_main.close()
                conn_ch15.close()
                return False

        # Get schemas
        main_verse_cols = get_table_schema(conn_main, "verses")
        ch15_verse_cols = get_table_schema(conn_ch15, "verses")

        main_instance_cols = get_table_schema(conn_main, "figurative_language")
        ch15_instance_cols = get_table_schema(conn_ch15, "figurative_language")

        print(f"Main verse columns: {len(main_verse_cols)}")
        print(f"Chapter 15 verse columns: {len(ch15_verse_cols)}")
        print(f"Main instance columns: {len(main_instance_cols)}")
        print(f"Chapter 15 instance columns: {len(ch15_instance_cols)}")

        # Transfer verses data
        print("Transferring verses...")
        ch15_verses_data = conn_ch15.execute("""
            SELECT * FROM verses ORDER BY verse
        """).fetchall()

        verses_added = 0
        verse_id_mapping = {}  # Map old verse_id to new verse_id

        for verse_data in ch15_verses_data:
            # Convert to dictionary and create new record
            verse_dict = dict(zip(ch15_verse_cols, verse_data))

            # Remove old ID and let SQLite generate new one
            if 'id' in verse_dict:
                del verse_dict['id']

            # Insert into main database
            columns = list(verse_dict.keys())
            values = list(verse_dict.values())
            placeholders = ', '.join(['?' for _ in values])

            cursor = conn_main.cursor()
            cursor.execute(f"""
                INSERT INTO verses ({', '.join(columns)})
                VALUES ({placeholders})
            """, values)

            new_verse_id = cursor.lastrowid
            old_verse_id = verse_data[0]  # Assuming first column is id
            verse_id_mapping[old_verse_id] = new_verse_id
            verses_added += 1

        # Transfer figurative language instances
        print("Transferring figurative language instances...")
        ch15_instances_data = conn_ch15.execute("""
            SELECT * FROM figurative_language
        """).fetchall()

        instances_added = 0
        for instance_data in ch15_instances_data:
            # Convert to dictionary
            instance_dict = dict(zip(ch15_instance_cols, instance_data))

            # Update verse_id to new mapped value
            old_verse_id = instance_dict.get('verse_id')
            if old_verse_id in verse_id_mapping:
                instance_dict['verse_id'] = verse_id_mapping[old_verse_id]
            else:
                print(f"WARNING: Could not map verse_id {old_verse_id}")
                continue

            # Remove old ID if present
            if 'id' in instance_dict:
                del instance_dict['id']

            # Insert into main database
            columns = list(instance_dict.keys())
            values = list(instance_dict.values())
            placeholders = ', '.join(['?' for _ in values])

            conn_main.execute(f"""
                INSERT INTO figurative_language ({', '.join(columns)})
                VALUES ({placeholders})
            """, values)

            instances_added += 1

        # Commit all changes
        conn_main.commit()

        # Verify final counts
        final_verses = conn_main.execute("SELECT COUNT(*) FROM verses").fetchone()[0]
        final_instances = conn_main.execute("SELECT COUNT(*) FROM figurative_language").fetchone()[0]

        # Check chapter distribution
        chapter_stats = conn_main.execute("""
            SELECT chapter, COUNT(*) as verse_count
            FROM verses
            GROUP BY chapter
            ORDER BY chapter
        """).fetchall()

        print(f"\n=== CONSOLIDATION SUCCESSFUL ===")
        print(f"Backup created: {backup_path}")
        print(f"Verses added: {verses_added}")
        print(f"Instances added: {instances_added}")
        print(f"Total verses: {main_verses} to {final_verses}")
        print(f"Total instances: {main_instances} to {final_instances}")
        print(f"\nChapter distribution:")
        for chapter, count in chapter_stats:
            status = "OK" if chapter <= 18 else "  "
            print(f"  [{status}] Chapter {chapter:2d}: {count:2d} verses")

        # Check for completion
        chapters_with_data = len([c for c, _ in chapter_stats if c <= 18])
        print(f"\nProverbs completion: {chapters_with_data}/18 chapters ({chapters_with_data/18*100:.1f}%)")

        if chapters_with_data == 18:
            print("*** PROVERBS DATABASE IS NOW 100% COMPLETE! ***")

        conn_main.close()
        conn_ch15.close()

        return True

    except Exception as e:
        print(f"ERROR during consolidation: {e}")
        import traceback
        traceback.print_exc()

        # Restore from backup if available
        if os.path.exists(backup_path):
            print(f"Restoring backup from {backup_path}")
            shutil.copy2(backup_path, consolidated_db)
            print("Backup restored")

        return False

if __name__ == "__main__":
    print("=== ADDING CHAPTER 15 TO CONSOLIDATED PROVERBS DATABASE ===")
    success = add_chapter15_to_proverbs()

    if success:
        print("\n*** SUCCESS: Chapter 15 has been added to the consolidated Proverbs database! ***")
    else:
        print("\n*** FAILED: Could not add Chapter 15 to the consolidated database ***")