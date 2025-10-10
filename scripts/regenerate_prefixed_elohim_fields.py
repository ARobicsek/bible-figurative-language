#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate Hebrew Non-Sacred Fields - Prefixed Elohim Fix

This script regenerates Hebrew non-sacred fields with the updated modifier
that handles prefixed Elohim forms (ו, כ, ל, ב, מ + Elohim).

Fields regenerated:
1. verses.hebrew_text_non_sacred
2. verses.figurative_detection_deliberation_non_sacred
3. figurative_language.figurative_text_in_hebrew_non_sacred
4. figurative_language.figurative_text_non_sacred (English with Hebrew terms)

Fixes: וֵאלֹהִים, כֵּאלֹהִים, לֵאלֹהִים, בֵּאלֹהִים, מֵאלֹהִים patterns
Total affected: ~102 verses (21 vav + 81 other prefixes)
"""

import sys
import os
import sqlite3
import io

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the private module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'private', 'src'))

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Pentateuch_Psalms_fig_language.db')

def regenerate_verse_hebrew_non_sacred():
    """Regenerate verses.hebrew_text_non_sacred field"""
    print("\n" + "=" * 80)
    print("FIELD 1/4: Regenerating verses.hebrew_text_non_sacred")
    print("=" * 80)

    modifier = HebrewDivineNamesModifier()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all verses
    cursor.execute("SELECT id, hebrew_text FROM verses ORDER BY id")
    verses = cursor.fetchall()

    print(f"Total verses to process: {len(verses)}")

    modified_count = 0
    batch_count = 0

    for verse_id, hebrew_text in verses:
        if not hebrew_text:
            continue

        non_sacred = modifier.modify_divine_names(hebrew_text)

        if non_sacred != hebrew_text:
            modified_count += 1

        cursor.execute("""
            UPDATE verses
            SET hebrew_text_non_sacred = ?
            WHERE id = ?
        """, (non_sacred, verse_id))

        batch_count += 1
        if batch_count % 500 == 0:
            conn.commit()
            print(f"  Processed {batch_count}/{len(verses)} verses... ({modified_count} modified)")

    conn.commit()
    conn.close()

    print(f"✓ Completed: {modified_count} verses modified out of {len(verses)}")
    return modified_count

def regenerate_deliberation_non_sacred():
    """Regenerate verses.figurative_detection_deliberation_non_sacred field"""
    print("\n" + "=" * 80)
    print("FIELD 2/4: Regenerating verses.figurative_detection_deliberation_non_sacred")
    print("=" * 80)

    modifier = HebrewDivineNamesModifier()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all verses with deliberation
    cursor.execute("""
        SELECT id, figurative_detection_deliberation
        FROM verses
        WHERE figurative_detection_deliberation IS NOT NULL
        ORDER BY id
    """)
    verses = cursor.fetchall()

    print(f"Total verses to process: {len(verses)}")

    modified_count = 0
    batch_count = 0

    for verse_id, deliberation in verses:
        if not deliberation:
            continue

        non_sacred = modifier.modify_english_with_hebrew_terms(deliberation)

        if non_sacred != deliberation:
            modified_count += 1

        cursor.execute("""
            UPDATE verses
            SET figurative_detection_deliberation_non_sacred = ?
            WHERE id = ?
        """, (non_sacred, verse_id))

        batch_count += 1
        if batch_count % 500 == 0:
            conn.commit()
            print(f"  Processed {batch_count}/{len(verses)} verses... ({modified_count} modified)")

    conn.commit()
    conn.close()

    print(f"✓ Completed: {modified_count} verses modified out of {len(verses)}")
    return modified_count

def regenerate_figurative_hebrew_non_sacred():
    """Regenerate figurative_language.figurative_text_in_hebrew_non_sacred field"""
    print("\n" + "=" * 80)
    print("FIELD 3/4: Regenerating figurative_language.figurative_text_in_hebrew_non_sacred")
    print("=" * 80)

    modifier = HebrewDivineNamesModifier()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all figurative instances
    cursor.execute("""
        SELECT id, figurative_text_in_hebrew
        FROM figurative_language
        WHERE figurative_text_in_hebrew IS NOT NULL
        ORDER BY id
    """)
    instances = cursor.fetchall()

    print(f"Total instances to process: {len(instances)}")

    modified_count = 0
    batch_count = 0

    for instance_id, hebrew_text in instances:
        if not hebrew_text:
            continue

        non_sacred = modifier.modify_divine_names(hebrew_text)

        if non_sacred != hebrew_text:
            modified_count += 1

        cursor.execute("""
            UPDATE figurative_language
            SET figurative_text_in_hebrew_non_sacred = ?
            WHERE id = ?
        """, (non_sacred, instance_id))

        batch_count += 1
        if batch_count % 500 == 0:
            conn.commit()
            print(f"  Processed {batch_count}/{len(instances)} instances... ({modified_count} modified)")

    conn.commit()
    conn.close()

    print(f"✓ Completed: {modified_count} instances modified out of {len(instances)}")
    return modified_count

def regenerate_figurative_english_non_sacred():
    """Regenerate figurative_language.figurative_text_non_sacred field (English with Hebrew terms)"""
    print("\n" + "=" * 80)
    print("FIELD 4/4: Regenerating figurative_language.figurative_text_non_sacred")
    print("=" * 80)

    modifier = HebrewDivineNamesModifier()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get all figurative instances
    cursor.execute("""
        SELECT id, figurative_text
        FROM figurative_language
        WHERE figurative_text IS NOT NULL
        ORDER BY id
    """)
    instances = cursor.fetchall()

    print(f"Total instances to process: {len(instances)}")

    modified_count = 0
    batch_count = 0

    for instance_id, english_text in instances:
        if not english_text:
            continue

        non_sacred = modifier.modify_english_with_hebrew_terms(english_text)

        if non_sacred != english_text:
            modified_count += 1

        cursor.execute("""
            UPDATE figurative_language
            SET figurative_text_non_sacred = ?
            WHERE id = ?
        """, (non_sacred, instance_id))

        batch_count += 1
        if batch_count % 500 == 0:
            conn.commit()
            print(f"  Processed {batch_count}/{len(instances)} instances... ({modified_count} modified)")

    conn.commit()
    conn.close()

    print(f"✓ Completed: {modified_count} instances modified out of {len(instances)}")
    return modified_count

def main():
    """Main execution"""
    print("=" * 80)
    print("REGENERATE HEBREW NON-SACRED FIELDS - PREFIXED ELOHIM FIX")
    print("=" * 80)
    print("\nThis script fixes missed prefixed Elohim forms:")
    print("  - וֵאלֹהִים (ve-Elohim) - 'and God'")
    print("  - כֵּאלֹהִים (ke-Elohim) - 'like God'")
    print("  - לֵאלֹהִים (le-Elohim) - 'to God'")
    print("  - בֵּאלֹהִים (be-Elohim) - 'in God'")
    print("  - מֵאלֹהֵי (me-Elohei) - 'from God of'")
    print("\nEstimated affected verses: ~102 (21 vav + 81 other prefixes)")
    print("\nStarting regeneration...\n")

    # Regenerate all 4 fields
    count1 = regenerate_verse_hebrew_non_sacred()
    count2 = regenerate_deliberation_non_sacred()
    count3 = regenerate_figurative_hebrew_non_sacred()
    count4 = regenerate_figurative_english_non_sacred()

    print("\n" + "=" * 80)
    print("REGENERATION COMPLETE")
    print("=" * 80)
    print(f"verses.hebrew_text_non_sacred: {count1} modified")
    print(f"verses.figurative_detection_deliberation_non_sacred: {count2} modified")
    print(f"figurative_language.figurative_text_in_hebrew_non_sacred: {count3} modified")
    print(f"figurative_language.figurative_text_non_sacred: {count4} modified")
    print("\nDatabase successfully updated!")

if __name__ == '__main__':
    main()
