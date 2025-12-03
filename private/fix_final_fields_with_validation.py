#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix All Final Fields Based on Validation Results

This script updates ALL final_* fields (final_simile, final_metaphor, etc.)
based on the validation decisions from the enhanced validation system,
including handling RECLASSIFIED instances.

Usage:
    python fix_final_fields_with_validation.py
"""

import sqlite3
import sys
import json
from datetime import datetime
from pathlib import Path

def main():
    print("=== FIX ALL FINAL FIELDS BASED ON VALIDATION ===")
    print(f"Started: {datetime.now()}")
    print()

    # Database path
    project_dir = Path(__file__).parent.parent
    db_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652.db"

    # Create backup
    backup_path = project_dir / "proverbs_c2_multi_v_parallel_20251202_1652_before_validation_fix.db"
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
        # Get all instances with validation data
        print("3. Loading instances with validation data...")
        cursor.execute('''
            SELECT
                fl.id, verse_id,
                fl.final_figurative_language,
                fl.simile, fl.metaphor, fl.personification, fl.idiom, fl.hyperbole, fl.metonymy, fl.other,
                fl.final_simile, fl.final_metaphor, fl.final_personification, fl.final_idiom, fl.final_hyperbole, fl.metonymy, fl.final_other,
                fl.validation_decision_simile, fl.validation_decision_metaphor, fl.validation_decision_personification,
                fl.validation_decision_idiom, fl.validation_decision_hyperbole, fl.validation_decision_metonymy, fl.validation_decision_other,
                fl.validation_response,
                v.reference
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE fl.validation_response IS NOT NULL AND fl.validation_response != ''
            ORDER BY v.chapter, v.verse, fl.id
        ''')

        instances = cursor.fetchall()
        print(f"SUCCESS: Loaded {len(instances)} instances with validation data")
        print()

        # Update final_* fields based on validation decisions
        print("4. Updating final_* fields based on validation decisions...")
        updated_count = 0

        for instance in instances:
            (
                fl_id, verse_id,
                final_fig_lang,
                simile, metaphor, personification, idiom, hyperbole, metonymy, other,
                final_simile, final_metaphor, final_personification, final_idiom, final_hyperbole, final_metonymy, final_other,
                val_dec_simile, val_dec_metaphor, val_dec_personification,
                val_dec_idiom, val_dec_hyperbole, val_dec_metonymy, val_dec_other,
                validation_response,
                reference
            ) = instance

            # Parse validation response to get reclassification info
            validation_data = {}
            try:
                if validation_response:
                    validation_data = json.loads(validation_response)
            except:
                validation_data = {}

            # Determine final_* values based on validation decisions
            # Use validation decisions if available, otherwise fall back to original detection
            final_simile = val_dec_simile if val_dec_simile in ['VALID'] else 'no'
            final_metaphor = val_dec_metaphor if val_dec_metaphor in ['VALID'] else 'no'
            final_personification = val_dec_personification if val_dec_personification in ['VALID'] else 'no'
            final_idiom = val_dec_idiom if val_dec_idiom in ['VALID'] else 'no'
            final_hyperbole = val_dec_hyperbole if val_dec_hyperbole in ['VALID'] else 'no'
            final_metonymy = val_dec_metonymy if val_dec_metonymy in ['VALID'] else 'no'
            final_other = val_dec_other if val_dec_other in ['VALID'] else 'no'

            # Check for reclassification in validation results
            if 'validation_results' in validation_data:
                validation_results = validation_data.get('validation_results', {})

                # Use reclassified type if available
                for fig_type, result in validation_results.items():
                    if isinstance(result, dict):
                        decision = result.get('decision', '')
                        if decision == 'VALID':
                            # Update the corresponding final field
                            if fig_type.lower() == 'simile':
                                final_simile = 'yes'
                            elif fig_type.lower() == 'metaphor':
                                final_metaphor = 'yes'
                            elif fig_type.lower() == 'personification':
                                final_personification = 'yes'
                            elif fig_type.lower() == 'idiom':
                                final_idiom = 'yes'
                            elif fig_type.lower() == 'hyperbole':
                                final_hyperbole = 'yes'
                            elif fig_type.lower() == 'metonymy':
                                final_metonymy = 'yes'
                            elif fig_type.lower() == 'other':
                                final_other = 'yes'
                        elif decision == 'RECLASSIFIED':
                            # This was reclassified, so update the NEW type
                            new_type = result.get('reclassified_type', '').lower()
                            if new_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                                if new_type == 'simile':
                                    final_simile = 'yes'
                                    final_metaphor = 'no'
                                elif new_type == 'metaphor':
                                    final_simile = 'no'
                                    final_metaphor = 'yes'
                                elif new_type == 'personification':
                                    final_simile = 'no'
                                    final_metaphor = 'no'
                                    final_personification = 'yes'
                                elif new_type == 'idiom':
                                    final_simile = 'no'
                                    final_metaphor = 'no'
                                    final_idiom = 'yes'
                                elif new_type == 'hyperbole':
                                    final_simile = 'no'
                                    final_metaphor = 'no'
                                    final_hyperbole = 'yes'
                                elif new_type == 'metonymy':
                                    final_simile = 'no'
                                    final_metaphor = 'no'
                                    final_metonymy = 'yes'
                                elif new_type == 'other':
                                    final_simile = 'no'
                                    final_metaphor = 'no'
                                    final_other = 'yes'

            # Set final_figurative_language based on any final_* fields being 'yes'
            has_any_final_yes = any([
                final_simile == 'yes', final_metaphor == 'yes', final_personification == 'yes',
                final_idiom == 'yes', final_hyperbole == 'yes', final_metonymy == 'yes', final_other == 'yes'
            ])
            final_figurative_language = 'yes' if has_any_final_yes else 'no'

            # Update the instance
            cursor.execute('''
                UPDATE figurative_language SET
                    final_simile = ?,
                    final_metaphor = ?,
                    final_personification = ?,
                    final_idiom = ?,
                    final_hyperbole = ?,
                    final_metonymy = ?,
                    final_other = ?,
                    final_figurative_language = ?
                WHERE id = ?
            ''', (
                final_simile, final_metaphor, final_personification, final_idiom,
                final_hyperbole, final_metonymy, final_other, final_figurative_language, fl_id
            ))

            if cursor.rowcount > 0:
                updated_count += 1

                # Show first few updates for verification
                if updated_count <= 5:
                    types_with_yes = []
                    if final_simile == 'yes': types_with_yes.append('simile')
                    if final_metaphor == 'yes': types_with_yes.append('metaphor')
                    if final_personification == 'yes': types_with_yes.append('personification')
                    if final_idiom == 'yes': types_with_yes.append('idiom')
                    if final_hyperbole == 'yes': types_with_yes.append('hyperbole')
                    if final_metonymy == 'yes': types_with_yes.append('metonymy')
                    if final_other == 'yes': types_with_yes.append('other')

                    old_types = []
                    if simile == 'yes': old_types.append('simile')
                    if metaphor == 'yes': old_types.append('metaphor')
                    if personification == 'yes': old_types.append('personification')
                    if idiom == 'yes': old_types.append('idiom')
                    if hyperbole == 'yes': old_types.append('hyperbole')
                    if metonymy == 'yes': old_types.append('metonymy')
                    if other == 'yes': old_types.append('other')

                    print(f"  Updated {reference}:")
                    print(f"    Original: simile={simile}, metaphor={metaphor}")
                    print(f"    Final: final_simile={final_simile}, final_metaphor={final_metaphor}")
                    print(f"    Additional final types: {types_with_yes}")
                    print()

        conn.commit()
        print(f"SUCCESS: Updated {updated_count} instances based on validation decisions")
        print()

        # Verify the fixes
        print("5. Verifying fixes...")

        # Check the specific instance you mentioned
        cursor.execute('''
            SELECT
                v.reference,
                fl.final_figurative_language,
                fl.final_simile, fl.final_metaphor, final_personification,
                fl.final_idiom, fl.final_hyperbole, fl.final_metonymy, fl.final_other,
                fl.validation_decision_hyperbole, fl.validation_decision_metaphor
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.reference = 'Proverbs 2:19'
        ''')

        print("Proverbs 2:19 verification:")
        for row in cursor.fetchall():
            ref, final_fig, final_simile, final_metaphor, final_person, final_idiom, final_hyper, final_metonymy, final_other, val_dec_hyper, val_dec_metaphor = row

            print(f"  Reference: {ref}")
            print(f"  final_figurative_language: {final_fig}")
            print(f"  Final hyperbole: {final_hyper} (was reclassified)")
            print(f"  Final metaphor: {final_metaphor}")
            print(f"  Validation decisions: hyperbole={val_dec_hyper}, metaphor={val_dec_metaphor}")

            # Check consistency
            if val_dec_hyper == 'RECLASSIFIED':
                expected_hyperbole = 'yes'
                expected_metaphor = 'no'
            elif val_dec_metaphor == 'RECLASSIFIED':
                expected_hyperbole = 'no'
                expected_metaphor = 'yes'
            else:
                expected_hyperbole = val_dec_hyper in ['VALID']  # 'VALID' or None
                expected_metaphor = val_dec_metaphor in ['VALID']  # 'VALID' or None

            is_hyper_correct = final_hyper == expected_hyperbole
            is_metaphor_correct = final_metaphor == expected_metaphor

            if is_hyper_correct and is_metaphor_correct:
                print(f"  SUCCESS: Both hyperbole and metaphor fields match validation decisions")
            else:
                print(f"  ERROR: Fields don't match validation decisions")

        print()

        # Overall statistics
        cursor.execute('''
            SELECT
                COUNT(*) as total_instances,
                COUNT(CASE WHEN final_figurative_language = 'yes' THEN 1 END) as final_yes
            FROM figurative_language
        ''')

        final_stats = cursor.fetchone()
        total_final, final_yes = final_stats
        print(f"Overall verification:")
        print(f"  Total instances: {total_final}")
        print(f"  final_figurative_language='yes': {final_yes}")

        conn.close()
        print("=== ALL FINAL FIELDS FIX COMPLETED ===")
        print(f"Database: {db_path}")
        print(f"Backup saved at: {backup_path}")
        print(f"Updated {updated_count} instances")

        return True

    except Exception as e:
        print(f"FAIL: Fix failed with error: {e}")
        import traceback
        traceback.print_exc()
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\nSUCCESS: All final fields fix completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: All final fields fix failed!")
        sys.exit(1)