#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Migration script to add two-level subcategories to existing database
"""
import sqlite3
import sys
from subcategory_mapping import get_two_level_subcategory

def migrate_database(db_path: str):
    """
    Migrate existing database to include two-level subcategories

    Args:
        db_path: Path to the database file
    """
    print(f"Migrating database: {db_path}")

    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(figurative_language)")
        columns = [row[1] for row in cursor.fetchall()]

        if 'subcategory_level_1' not in columns:
            print("Adding subcategory_level_1 column...")
            cursor.execute("ALTER TABLE figurative_language ADD COLUMN subcategory_level_1 TEXT")

        if 'subcategory_level_2' not in columns:
            print("Adding subcategory_level_2 column...")
            cursor.execute("ALTER TABLE figurative_language ADD COLUMN subcategory_level_2 TEXT")

        # Create indexes for new columns
        print("Creating indexes for new columns...")
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_figurative_subcategory_level_1
            ON figurative_language (subcategory_level_1)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_figurative_subcategory_level_2
            ON figurative_language (subcategory_level_2)
        ''')

        # Get all records with subcategory data
        print("Fetching existing subcategory data...")
        cursor.execute('''
            SELECT id, subcategory
            FROM figurative_language
            WHERE subcategory IS NOT NULL AND subcategory != ''
        ''')
        records = cursor.fetchall()

        print(f"Found {len(records)} records to migrate")

        # Migrate each record
        migrated_count = 0
        unmapped_subcategories = set()

        for record_id, old_subcategory in records:
            level_1, level_2 = get_two_level_subcategory(old_subcategory)

            if level_1 and level_2:
                cursor.execute('''
                    UPDATE figurative_language
                    SET subcategory_level_1 = ?, subcategory_level_2 = ?
                    WHERE id = ?
                ''', (level_1, level_2, record_id))
                migrated_count += 1
            else:
                unmapped_subcategories.add(old_subcategory)

        # Show migration results
        print(f"Successfully migrated {migrated_count} records")

        if unmapped_subcategories:
            print(f"Unmapped subcategories found: {sorted(unmapped_subcategories)}")

        # Show distribution of new subcategories
        print("\nSubcategory Level 1 distribution:")
        cursor.execute('''
            SELECT subcategory_level_1, COUNT(*)
            FROM figurative_language
            WHERE subcategory_level_1 IS NOT NULL
            GROUP BY subcategory_level_1
            ORDER BY COUNT(*) DESC
        ''')
        for level_1, count in cursor.fetchall():
            print(f"  {level_1}: {count}")

        print("\nSubcategory Level 2 distribution:")
        cursor.execute('''
            SELECT subcategory_level_2, COUNT(*)
            FROM figurative_language
            WHERE subcategory_level_2 IS NOT NULL
            GROUP BY subcategory_level_2
            ORDER BY COUNT(*) DESC
        ''')
        for level_2, count in cursor.fetchall():
            print(f"  {level_2}: {count}")

        # Commit changes
        conn.commit()
        print("\nMigration completed successfully!")

    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def validate_migration(db_path: str):
    """
    Validate that migration was successful

    Args:
        db_path: Path to the database file
    """
    print(f"\nValidating migration for: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Check total records
        cursor.execute("SELECT COUNT(*) FROM figurative_language")
        total_records = cursor.fetchone()[0]

        # Check records with original subcategory
        cursor.execute('''
            SELECT COUNT(*) FROM figurative_language
            WHERE subcategory IS NOT NULL AND subcategory != ''
        ''')
        original_subcategory_count = cursor.fetchone()[0]

        # Check records with new subcategories
        cursor.execute('''
            SELECT COUNT(*) FROM figurative_language
            WHERE subcategory_level_1 IS NOT NULL AND subcategory_level_2 IS NOT NULL
        ''')
        new_subcategory_count = cursor.fetchone()[0]

        print(f"Total records: {total_records}")
        print(f"Records with original subcategory: {original_subcategory_count}")
        print(f"Records with new two-level subcategories: {new_subcategory_count}")

        if new_subcategory_count >= original_subcategory_count:
            print("✅ Migration validation passed!")
        else:
            print("❌ Migration validation failed - some records may not have been migrated")

        # Show sample of migrated data
        print("\nSample migrated records:")
        cursor.execute('''
            SELECT subcategory, subcategory_level_1, subcategory_level_2, type, figurative_text
            FROM figurative_language
            WHERE subcategory_level_1 IS NOT NULL
            LIMIT 5
        ''')

        for row in cursor.fetchall():
            old_sub, level_1, level_2, fig_type, text = row
            print(f"  {old_sub} -> {level_1} | {level_2} ({fig_type}: {text[:50]}...)")

    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python migrate_subcategories.py <database_path>")
        print("Example: python migrate_subcategories.py deuteronomy_improved_20250918_171933.db")
        sys.exit(1)

    db_path = sys.argv[1]

    try:
        migrate_database(db_path)
        validate_migration(db_path)
    except Exception as e:
        print(f"Migration failed: {e}")
        sys.exit(1)