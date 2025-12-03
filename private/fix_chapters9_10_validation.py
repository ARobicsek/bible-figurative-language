#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Chapters 9-10 Validation Issues

This script clears the incorrect validation data for chapters 9-10 and re-runs
the universal recovery script with the fixed logic.

Usage:
    python fix_chapters9_10_validation.py
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path
import subprocess

def main():
    print("=== FIXING CHAPTERS 9-10 VALIDATION ISSUES ===")
    print(f"Started: {datetime.now()}")
    print()

    # Database path
    db_path = Path("proverbs_c6_multi_v_parallel_20251202_1834.db")

    if not db_path.exists():
        print(f"FAIL: Database not found: {db_path}")
        return False

    # Create backup
    backup_path = db_path.parent / f"{db_path.stem}_before_ch9_10_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}{db_path.suffix}"
    print(f"1. Creating backup: {backup_path}")
    import shutil
    shutil.copy2(db_path, backup_path)
    print("SUCCESS: Backup created.")
    print()

    # Connect to database
    print("2. Clearing incorrect validation data for chapters 9-10...")
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Clear validation data for chapters 9 and 10
        cursor.execute("""
            UPDATE figurative_language SET
                validation_response = NULL,
                validation_decision_simile = NULL,
                validation_decision_metaphor = NULL,
                validation_decision_personification = NULL,
                validation_decision_idiom = NULL,
                validation_decision_hyperbole = NULL,
                validation_decision_metonymy = NULL,
                validation_decision_other = NULL,
                validation_reason_simile = NULL,
                validation_reason_metaphor = NULL,
                validation_reason_personification = NULL,
                validation_reason_idiom = NULL,
                validation_reason_hyperbole = NULL,
                validation_reason_metonymy = NULL,
                validation_reason_other = NULL,
                validation_error = NULL,
                final_figurative_language = NULL,
                final_simile = NULL,
                final_metaphor = NULL,
                final_personification = NULL,
                final_idiom = NULL,
                final_hyperbole = NULL,
                final_metonymy = NULL,
                final_other = NULL
            WHERE verse_id IN (
                SELECT id FROM verses WHERE book = 'Proverbs' AND chapter IN (9, 10)
            )
        """)

        cleared_count = cursor.rowcount
        conn.commit()
        conn.close()

        print(f"SUCCESS: Cleared validation data for {cleared_count} instances in chapters 9-10")
        print()

    except Exception as e:
        print(f"FAIL: Failed to clear validation data: {e}")
        return False

    # Run the fixed universal recovery script
    print("3. Running fixed universal recovery script...")
    try:
        result = subprocess.run([
            sys.executable,
            "private/universal_validation_recovery.py",
            "--database", str(db_path),
            "--chapters", "9,10"
        ], capture_output=True, text=True, timeout=300)

        print("Recovery script output:")
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)

        if result.returncode == 0:
            print("SUCCESS: Recovery completed successfully")
        else:
            print(f"FAIL: Recovery failed with exit code {result.returncode}")
            return False

    except subprocess.TimeoutExpired:
        print("FAIL: Recovery script timed out")
        return False
    except Exception as e:
        print(f"FAIL: Error running recovery script: {e}")
        return False

    print("=== CHAPTERS 9-10 VALIDATION FIX COMPLETED ===")
    print(f"Database: {db_path}")
    print(f"Backup: {backup_path}")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: Chapters 9-10 validation fix completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: Chapters 9-10 validation fix failed!")
        sys.exit(1)