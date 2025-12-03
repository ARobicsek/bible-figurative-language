#!/usr/bin/env python3
"""
Consolidate Proverbs database into Pentateuch_Psalms database with proper ID mapping
Handles ID conflicts by remapping all verse_ids and instance_ids to avoid duplicates
"""

import sqlite3
import shutil
from datetime import datetime
import sys

def backup_target_database():
    """Create a backup of the target database"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    source_path = "database/Pentateuch_Psalms_fig_language.db"
    backup_path = f"database/Pentateuch_Psalms_fig_language.db_backup_{timestamp}"

    try:
        shutil.copy2(source_path, backup_path)
        print(f"SUCCESS: Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"ERROR: Failed to create backup: {e}")
        return None

def get_next_available_ids(target_conn):
    """Get next available IDs for both tables"""
    target_cursor = target_conn.cursor()

    # Get next verse_id
    target_cursor.execute("SELECT MAX(id) FROM verses")
    max_verse_id = target_cursor.fetchone()[0] or 0
    next_verse_id = max_verse_id + 1

    # Get next instance_id
    target_cursor.execute("SELECT MAX(id) FROM figurative_language")
    max_instance_id = target_cursor.fetchone()[0] or 0
    next_instance_id = max_instance_id + 1

    return next_verse_id, next_instance_id

def get_schema_compatibility(source_conn, target_conn):
    """Check schema compatibility between databases"""
    source_cursor = source_conn.cursor()
    target_cursor = target_conn.cursor()

    # Check verses table
    source_cursor.execute("PRAGMA table_info(verses)")
    source_verses_cols = {row[1]: row[2] for row in source_cursor.fetchall()}

    target_cursor.execute("PRAGMA table_info(verses)")
    target_verses_cols = {row[1]: row[2] for row in target_cursor.fetchall()}

    # Check figurative language table
    source_cursor.execute("PRAGMA table_info(figurative_language)")
    source_instances_cols = {row[1]: row[2] for row in source_cursor.fetchall()}

    target_cursor.execute("PRAGMA table_info(figurative_language)")
    target_instances_cols = {row[1]: row[2] for row in target_cursor.fetchall()}

    # Find missing columns in target
    missing_verses_cols = set(source_verses_cols.keys()) - set(target_verses_cols.keys())
    missing_instances_cols = set(source_instances_cols.keys()) - set(target_instances_cols.keys())

    # Find extra columns in target
    extra_verses_cols = set(target_verses_cols.keys()) - set(source_verses_cols.keys())
    extra_instances_cols = set(target_instances_cols.keys()) - set(source_instances_cols.keys())

    return {
        'missing_verses': missing_verses_cols,
        'missing_instances': missing_instances_cols,
        'extra_verses': extra_verses_cols,
        'extra_instances': extra_instances_cols,
        'compatible': len(missing_verses_cols) == 0 and len(missing_instances_cols) == 0
    }

def consolidate_proverbs():
    """Main consolidation function"""
    source_path = "Proverbs.db"
    target_path = "database/Pentateuch_Psalms_fig_language.db"

    print("Starting Proverbs to Pentateuch_Psalms consolidation...")
    print(f"Source: {source_path}")
    print(f"Target: {target_path}")

    # Create backup
    backup_path = backup_target_database()
    if not backup_path:
        return False

    try:
        # Connect to both databases
        source_conn = sqlite3.connect(source_path)
        target_conn = sqlite3.connect(target_path)

        source_cursor = source_conn.cursor()
        target_cursor = target_conn.cursor()

        # Check schema compatibility
        compatibility = get_schema_compatibility(source_conn, target_conn)
        print(f"Schema compatibility: {compatibility}")

        if not compatibility['compatible']:
            print(f"ERROR: Schema incompatibility detected")
            print(f"Missing verses columns: {compatibility['missing_verses']}")
            print(f"Missing instances columns: {compatibility['missing_instances']}")
            return False

        print("SUCCESS: Schema compatibility verified")

        # Get next available IDs
        next_verse_id, next_instance_id = get_next_available_ids(target_conn)
        print(f"Starting verse_id from: {next_verse_id}")
        print(f"Starting instance_id from: {next_instance_id}")

        # Get all Proverbs verses from source
        source_cursor.execute("""
            SELECT * FROM verses
            WHERE book = 'Proverbs'
            ORDER BY chapter, verse
        """)
        verses = source_cursor.fetchall()

        # Get column names
        source_cursor.execute("PRAGMA table_info(verses)")
        verse_columns = [row[1] for row in source_cursor.fetchall()]

        print(f"Found {len(verses)} Proverbs verses to transfer")

        # Create verse_id mapping (old_id -> new_id)
        verse_id_map = {}
        total_verses_added = 0

        # Transfer verses with new IDs
        for verse_data in verses:
            verse_dict = dict(zip(verse_columns, verse_data))
            old_verse_id = verse_dict['id']

            # Assign new ID
            verse_dict['id'] = next_verse_id

            # Handle extra target columns by setting them to NULL
            for extra_col in compatibility['extra_verses']:
                verse_dict[extra_col] = None

            # Build INSERT query dynamically
            cols_str = ', '.join(verse_dict.keys())
            placeholders = ', '.join(['?' for _ in verse_dict])
            values = list(verse_dict.values())

            target_cursor.execute(f"""
                INSERT INTO verses ({cols_str})
                VALUES ({placeholders})
            """, values)

            # Store mapping for figurative language table
            verse_id_map[old_verse_id] = next_verse_id

            next_verse_id += 1
            total_verses_added += 1

        print(f"SUCCESS: Added {total_verses_added} verses")

        # Transfer figurative language instances
        source_cursor.execute("""
            SELECT fl.* FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.book = 'Proverbs'
        """)
        instances = source_cursor.fetchall()

        # Get column names for figurative language
        source_cursor.execute("PRAGMA table_info(figurative_language)")
        instance_columns = [row[1] for row in source_cursor.fetchall()]

        print(f"Found {len(instances)} figurative instances to transfer")

        total_instances_added = 0
        for instance_data in instances:
            instance_dict = dict(zip(instance_columns, instance_data))

            # Update IDs
            old_verse_id = instance_dict['verse_id']
            instance_dict['verse_id'] = verse_id_map[old_verse_id]
            instance_dict['id'] = next_instance_id

            # Handle extra target columns
            for extra_col in compatibility['extra_instances']:
                instance_dict[extra_col] = None

            # Build INSERT query
            cols_str = ', '.join(instance_dict.keys())
            placeholders = ', '.join(['?' for _ in instance_dict])
            values = list(instance_dict.values())

            target_cursor.execute(f"""
                INSERT INTO figurative_language ({cols_str})
                VALUES ({placeholders})
            """, values)

            next_instance_id += 1
            total_instances_added += 1

        print(f"SUCCESS: Added {total_instances_added} figurative instances")

        # Commit all changes
        target_conn.commit()

        # Verify final state
        target_cursor.execute("SELECT COUNT(*) FROM verses WHERE book = 'Proverbs'")
        final_proverbs_verses = target_cursor.fetchone()[0]

        target_cursor.execute("""
            SELECT COUNT(*) FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.book = 'Proverbs'
        """)
        final_proverbs_instances = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM verses")
        total_verses = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM figurative_language")
        total_instances = target_cursor.fetchone()[0]

        print(f"\nCONSOLIDATION COMPLETE!")
        print(f"Proverbs verses: {final_proverbs_verses}")
        print(f"Proverbs instances: {final_proverbs_instances}")
        print(f"Total database verses: {total_verses}")
        print(f"Total database instances: {total_instances}")
        print(f"Backup created: {backup_path}")

        # Verify no ID conflicts
        target_cursor.execute("SELECT COUNT(*) FROM verses WHERE id IN (SELECT id FROM verses GROUP BY id HAVING COUNT(*) > 1)")
        duplicate_verses = target_cursor.fetchone()[0]

        target_cursor.execute("SELECT COUNT(*) FROM figurative_language WHERE id IN (SELECT id FROM figurative_language GROUP BY id HAVING COUNT(*) > 1)")
        duplicate_instances = target_cursor.fetchone()[0]

        if duplicate_verses == 0 and duplicate_instances == 0:
            print("SUCCESS: No ID conflicts detected!")
        else:
            print(f"WARNING: Found {duplicate_verses} duplicate verse IDs and {duplicate_instances} duplicate instance IDs")

        # Close connections
        source_conn.close()
        target_conn.close()

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Proverbs to Pentateuch_Psalms Database Consolidation")
    print("=" * 60)

    success = consolidate_proverbs()

    if success:
        print("\nSUCCESS: Consolidation completed successfully!")
    else:
        print("\nFAILED: Consolidation failed. Check error messages above.")
        sys.exit(1)