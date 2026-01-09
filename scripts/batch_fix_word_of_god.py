#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch fix for "word of God" divine action false positives.

This script does a targeted SQL update to:
- KEEP metonymy tags (valid for "word of God" patterns)  
- REMOVE personification and metaphor tags (invalid for divine speech)

This is a much simpler fix than full LLM re-validation since the rule is clear:
"The word of God came to..." is metonymy (word stands for message), 
but NOT personification or metaphor in ANE context.
"""

import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = r"C:\Users\ariro\OneDrive\Documents\Bible\database\Biblical_fig_language.db"
BACKUP_DIR = r"C:\Users\ariro\OneDrive\Documents\Bible\database\backups"

def create_backup(db_path: str, backup_dir: str) -> str:
    """Create a timestamped backup of the database."""
    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"Biblical_fig_language_backup_{timestamp}.db"
    backup_path = os.path.join(backup_dir, backup_filename)
    shutil.copy2(db_path, backup_path)
    print(f"✓ Created backup: {backup_path}")
    return backup_path


def preview_changes(conn: sqlite3.Connection):
    """Preview what will be changed."""
    cursor = conn.cursor()
    
    # Find all "word of God/Lord" patterns with personification or metaphor
    query = '''
    SELECT fl.id, v.reference, fl.figurative_text, 
           fl.metaphor, fl.personification, fl.metonymy,
           fl.final_metaphor, fl.final_personification, fl.final_metonymy
    FROM figurative_language fl
    JOIN verses v ON fl.verse_id = v.id
    WHERE (fl.personification = 'yes' OR fl.metaphor = 'yes')
    AND (
        LOWER(fl.figurative_text) LIKE '%word of%god%' OR
        LOWER(fl.figurative_text) LIKE '%word of%lord%' OR
        LOWER(fl.figurative_text) LIKE '%word of%yhwh%'
    )
    ORDER BY v.book, v.chapter, v.verse
    '''
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    print(f"\n=== PREVIEW: {len(rows)} instances will be updated ===\n")
    
    for row in rows[:10]:  # Show first 10
        fl_id, ref, fig_text, met, pers, meto, f_met, f_pers, f_meto = row
        print(f"ID {fl_id}: {ref}")
        print(f"  Text: {fig_text[:60]}..." if len(fig_text) > 60 else f"  Text: {fig_text}")
        print(f"  BEFORE: metaphor={met}, personification={pers}, metonymy={meto}")
        print(f"  AFTER:  metaphor=no, personification=no, metonymy={meto} (unchanged)")
        print()
    
    if len(rows) > 10:
        print(f"  ... and {len(rows) - 10} more instances\n")
    
    return len(rows)


def apply_batch_fix(conn: sqlite3.Connection, dry_run: bool = False):
    """Apply the batch fix to remove personification/metaphor from word of God patterns."""
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d")
    remediation_note = f"[BATCH FIX {timestamp}] Removed due to divine speech being literal in ANE context; metonymy retained."
    
    # Update query - removes personification and metaphor, keeps metonymy
    update_query = f'''
    UPDATE figurative_language
    SET 
        personification = 'no',
        final_personification = 'no',
        validation_decision_personification = 'INVALID_DIVINE_ACTION_BATCH_FIX',
        validation_reason_personification = '{remediation_note}',
        metaphor = 'no',
        final_metaphor = 'no', 
        validation_decision_metaphor = 'INVALID_DIVINE_ACTION_BATCH_FIX',
        validation_reason_metaphor = '{remediation_note}'
    WHERE id IN (
        SELECT fl.id
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE (fl.personification = 'yes' OR fl.metaphor = 'yes')
        AND (
            LOWER(fl.figurative_text) LIKE '%word of%god%' OR
            LOWER(fl.figurative_text) LIKE '%word of%lord%' OR
            LOWER(fl.figurative_text) LIKE '%word of%yhwh%'
        )
    )
    '''
    
    if dry_run:
        print("[DRY RUN] Would execute update query...")
        print("No changes made.")
        return 0
    
    cursor.execute(update_query)
    affected = cursor.rowcount
    conn.commit()
    
    print(f"✓ Updated {affected} instances")
    return affected


def verify_fix(conn: sqlite3.Connection):
    """Verify the fix was applied correctly."""
    cursor = conn.cursor()
    
    # Check: Any "word of" patterns still have pers/met?
    cursor.execute('''
        SELECT COUNT(*) FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id  
        WHERE (fl.personification = 'yes' OR fl.metaphor = 'yes')
        AND (
            LOWER(fl.figurative_text) LIKE '%word of%god%' OR
            LOWER(fl.figurative_text) LIKE '%word of%lord%' OR
            LOWER(fl.figurative_text) LIKE '%word of%yhwh%'
        )
    ''')
    remaining = cursor.fetchone()[0]
    
    # Check: Metonymy preserved?
    cursor.execute('''
        SELECT COUNT(*) FROM figurative_language fl
        WHERE fl.metonymy = 'yes'
        AND fl.validation_reason_personification LIKE '%BATCH FIX%'
    ''')
    metonymy_preserved = cursor.fetchone()[0]
    
    print("\n=== VERIFICATION ===")
    print(f"Remaining 'word of' patterns with pers/met: {remaining} (expected: 0)")
    print(f"Fixed instances that still have metonymy: {metonymy_preserved}")
    
    # Sample of fixed instances
    cursor.execute('''
        SELECT v.reference, fl.figurative_text, fl.metonymy, fl.personification, fl.metaphor
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.validation_reason_personification LIKE '%BATCH FIX%'
        LIMIT 5
    ''')
    print("\nSample of fixed instances:")
    for row in cursor.fetchall():
        print(f"  {row[0]}: metonymy={row[2]}, pers={row[3]}, met={row[4]}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Batch fix word of God false positives")
    parser.add_argument("--dry-run", action="store_true", help="Preview without making changes")
    parser.add_argument("--verify", action="store_true", help="Run verification only")
    args = parser.parse_args()
    
    conn = sqlite3.connect(DB_PATH)
    print(f"Connected to: {DB_PATH}")
    
    if args.verify:
        verify_fix(conn)
        conn.close()
        return
    
    # Preview what will change
    count = preview_changes(conn)
    
    if count == 0:
        print("Nothing to fix!")
        conn.close()
        return
    
    if args.dry_run:
        print("\n[DRY RUN MODE] No changes will be made.\n")
        apply_batch_fix(conn, dry_run=True)
    else:
        # Confirm before proceeding
        print(f"\nThis will update {count} instances.")
        response = input("Proceed? (y/n): ")
        if response.lower() != 'y':
            print("Aborted.")
            conn.close()
            return
        
        # Create backup first
        create_backup(DB_PATH, BACKUP_DIR)
        
        # Apply fix
        apply_batch_fix(conn, dry_run=False)
        
        # Verify
        verify_fix(conn)
    
    conn.close()
    print("\nDone!")


if __name__ == "__main__":
    main()
