#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix final_figurative_language Field

This script updates the final_figurative_language field to 'yes'
whenever any of the final_* fields (final_simile, final_metaphor, etc.) are 'yes'.

Usage:
    python fix_final_figurative_language.py
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

def main():
    print("=== FIX FINAL_FIGURATIVE_LANGUAGE FIELD ===")
    print(f"Started: {datetime.now()}")
    print()

    # Database path
    project_dir = Path(__file__).parent.parent
    db_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652.db"

    # Create backup
    backup_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652_before_final_fig_fix.db"
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
        # Check current state
        print("3. Analyzing current final_figurative_language field...")
        cursor.execute('''
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN final_figurative_language = 'yes' THEN 1 END) as current_yes,
                COUNT(CASE WHEN
                    final_simile = 'yes' OR final_metaphor = 'yes' OR
                    final_personification = 'yes' OR final_idiom = 'yes' OR
                    final_hyperbole = 'yes' OR final_metonymy = 'yes' OR final_other = 'yes'
                THEN 1 END) as should_be_yes
            FROM figurative_language
        ''')

        stats = cursor.fetchone()
        total, current_yes, should_be_yes = stats
        print(f"Current status:")
        print(f"  Total instances: {total}")
        print(f"  Current final_figurative_language='yes': {current_yes}")
        print(f"  Should be final_figurative_language='yes': {should_be_yes}")

        if current_yes == should_be_yes:
            print("  No fixes needed!")
            conn.close()
            return True
        else:
            print(f"  Need to fix {should_be_yes - current_yes} instances")
        print()

        # Find instances that need fixing
        print("4. Identifying instances that need fixing...")
        cursor.execute('''
            SELECT id, verse_id,
                   final_figurative_language,
                   final_simile, final_metaphor, final_personification,
                   final_idiom, final_hyperbole, final_metonymy, final_other
            FROM figurative_language
            WHERE final_figurative_language != 'yes' AND (
                final_simile = 'yes' OR final_metaphor = 'yes' OR
                final_personification = 'yes' OR final_idiom = 'yes' OR
                final_hyperbole = 'yes' OR final_metonymy = 'yes' OR final_other = 'yes'
            )
        ''')

        instances_to_fix = cursor.fetchall()
        print(f"SUCCESS: Found {len(instances_to_fix)} instances that need fixing")
        print()

        # Get verse references for display
        if len(instances_to_fix) > 0:
            verse_ids = [str(row[1]) for row in instances_to_fix]
            cursor.execute(f'''
                SELECT reference FROM verses WHERE id IN ({','.join(verse_ids)})
            ''')
            verses = cursor.fetchall()
            verse_map = {f'{i+1}': verses[i][0] for i in range(len(verses))}

        # Fix the instances
        print("5. Fixing final_figurative_language field...")
        fixed_count = 0
        for i, instance in enumerate(instances_to_fix):
            (
                fl_id, verse_id,
                final_fig_lang,
                final_simile, final_metaphor, final_personification,
                final_idiom, final_hyperbole, final_metonymy, final_other
            ) = instance

            # Update the field
            cursor.execute('''
                UPDATE figurative_language
                SET final_figurative_language = 'yes'
                WHERE id = ?
            ''', (fl_id,))

            if cursor.rowcount > 0:
                fixed_count += 1

                # Show first few fixes
                if i < 5:
                    verse_ref = verse_map.get(str(i+1), f"Verse {verse_id}")
                    types_with_yes = []
                    if final_simile == 'yes': types_with_yes.append('simile')
                    if final_metaphor == 'yes': types_with_yes.append('metaphor')
                    if final_personification == 'yes': types_with_yes.append('personification')
                    if final_idiom == 'yes': types_with_yes.append('idiom')
                    if final_hyperbole == 'yes': types_with_yes.append('hyperbole')
                    if final_metonymy == 'yes': types_with_yes.append('metonymy')
                    if final_other == 'yes': types_with_yes.append('other')

                    print(f"  Fixed {verse_ref}: final_figurative_language='yes' (has {', '.join(types_with_yes)})")

        conn.commit()
        print(f"SUCCESS: Fixed {fixed_count} instances")
        print()

        # Verify the fixes
        print("6. Verifying fixes...")
        cursor.execute('''
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN final_figurative_language = 'yes' THEN 1 END) as final_yes
            FROM figurative_language
        ''')

        final_stats = cursor.fetchone()
        total_final, final_yes = final_stats

        print(f"Final verification:")
        print(f"  Total instances: {total_final}")
        print(f"  final_figurative_language='yes': {final_yes}")

        # Chapter-by-chapter breakdown
        cursor.execute('''
            SELECT
                v.chapter,
                COUNT(*) as total,
                COUNT(CASE WHEN fl.final_figurative_language = 'yes' THEN 1 END) as final_yes
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            GROUP BY v.chapter
            ORDER BY v.chapter
        ''')

        print("  Chapter-by-chapter breakdown:")
        for row in cursor.fetchall():
            chapter, total, final_count = row
            coverage = (final_count / total * 100) if total > 0 else 0
            print(f"    Chapter {chapter}: {final_count}/{total} ({coverage:.1f}%) have final_figurative_language=yes")

        print()
        conn.close()
        print("=== FINAL_FIGURATIVE_LANGUAGE FIELD FIX COMPLETED ===")
        print(f"Database: {db_path}")
        print(f"Backup saved at: {backup_path}")
        print(f"Fixed {fixed_count} instances")

        return True

    except Exception as e:
        print(f"FAIL: Fix failed with error: {e}")
        import traceback
        traceback.print_exc()
        conn.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: final_figurative_language field fix completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: final_figurative_language field fix failed!")
        sys.exit(1)