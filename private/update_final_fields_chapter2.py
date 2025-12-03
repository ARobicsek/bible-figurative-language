#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Final Fields for Chapter 2 Based on Validation Results

This script updates the final_* fields (final_simile, final_metaphor, etc.)
for Chapter 2 based on the validation decisions from the enhanced validation system.

Usage:
    python update_final_fields_chapter2.py
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

def main():
    print("=== UPDATE FINAL FIELDS FOR CHAPTER 2 ===")
    print(f"Started: {datetime.now()}")
    print()

    # Database path
    project_dir = Path(__file__).parent.parent
    db_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652.db"

    # Create backup
    backup_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652_before_final_update.db"
    print(f"1. Creating backup: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    print("SUCCESS: Backup created.")
    print()

    # Connect to database
    print("2. Connecting to database...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        print("SUCCESS: Connected to database.")
        print()
    except Exception as e:
        print(f"FAIL: Could not connect to database: {e}")
        return False

    try:
        # Get all Chapter 2 instances
        print("3. Loading Chapter 2 instances...")
        cursor.execute('''
            SELECT
                fl.id,
                fl.simile, fl.metaphor, fl.personification, fl.idiom, fl.hyperbole, fl.metonymy, fl.other,
                fl.validation_decision_simile, fl.validation_decision_metaphor,
                fl.validation_decision_personification, fl.validation_decision_idiom,
                fl.validation_decision_hyperbole, fl.validation_decision_metonymy, fl.validation_decision_other,
                v.reference
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.chapter = 2
            ORDER BY v.verse, fl.id
        ''')

        instances = cursor.fetchall()
        print(f"SUCCESS: Loaded {len(instances)} Chapter 2 instances")
        print()

        # Update final_* fields based on validation decisions
        print("4. Updating final_* fields based on validation decisions...")

        updated_count = 0
        for instance in instances:
            (
                fl_id,
                simile, metaphor, personification, idiom, hyperbole, metonymy, other,
                val_dec_simile, val_dec_metaphor, val_dec_personification, val_dec_idiom,
                val_dec_hyperbole, val_dec_metonymy, val_dec_other,
                reference
            ) = instance

            # Determine final_* values based on validation decisions
            final_simile = 'yes' if val_dec_simile == 'VALID' else 'no'
            final_metaphor = 'yes' if val_dec_metaphor == 'VALID' else 'no'
            final_personification = 'yes' if val_dec_personification == 'VALID' else 'no'
            final_idiom = 'yes' if val_dec_idiom == 'VALID' else 'no'
            final_hyperbole = 'yes' if val_dec_hyperbole == 'VALID' else 'no'
            final_metonymy = 'yes' if val_dec_metonymy == 'VALID' else 'no'
            final_other = 'yes' if val_dec_other == 'VALID' else 'no'

            # Update the final_* fields
            cursor.execute('''
                UPDATE figurative_language SET
                    final_simile = ?,
                    final_metaphor = ?,
                    final_personification = ?,
                    final_idiom = ?,
                    final_hyperbole = ?,
                    final_metonymy = ?,
                    final_other = ?
                WHERE id = ?
            ''', (
                final_simile, final_metaphor, final_personification, final_idiom,
                final_hyperbole, final_metonymy, final_other, fl_id
            ))

            if cursor.rowcount > 0:
                updated_count += 1

                # Show first few updates for verification
                if updated_count <= 5:
                    print(f"  Updated {reference}: "
                          f"final_metaphor={final_metaphor}, "
                          f"final_simile={final_simile}, "
                          f"final_idiom={final_idiom}, "
                          f"final_metonymy={final_metonymy}")

        conn.commit()
        print(f"SUCCESS: Updated {updated_count} instances with final_* fields")
        print()

        # Verify the updates
        print("5. Verifying updates...")
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                COUNT(CASE WHEN final_simile = 'yes' THEN 1 END) as simile,
                COUNT(CASE WHEN final_metaphor = 'yes' THEN 1 END) as metaphor,
                COUNT(CASE WHEN final_personification = 'yes' THEN 1 END) as personification,
                COUNT(CASE WHEN final_idiom = 'yes' THEN 1 END) as idiom,
                COUNT(CASE WHEN final_hyperbole = 'yes' THEN 1 END) as hyperbole,
                COUNT(CASE WHEN final_metonymy = 'yes' THEN 1 END) as metonymy,
                COUNT(CASE WHEN final_other = 'yes' THEN 1 END) as other
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.chapter = 2
        ''')

        stats = cursor.fetchone()
        print(f"Chapter 2 final field statistics:")
        print(f"  Total instances: {stats[0]}")
        print(f"  Final simile: {stats[1]}")
        print(f"  Final metaphor: {stats[2]}")
        print(f"  Final personification: {stats[3]}")
        print(f"  Final idiom: {stats[4]}")
        print(f"  Final hyperbole: {stats[5]}")
        print(f"  Final metonymy: {stats[6]}")
        print(f"  Final other: {stats[7]}")
        print()

        conn.close()
        print("=== FINAL FIELDS UPDATE COMPLETED SUCCESSFULLY ===")
        print(f"Database: {db_path}")
        print(f"Backup saved at: {backup_path}")

        return True

    except Exception as e:
        print(f"FAIL: Update failed with error: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: Final fields update completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: Final fields update failed!")
        sys.exit(1)