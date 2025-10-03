"""
Regenerate Hebrew non-sacred text fields using the FIXED divine names modifier.

This script updates:
1. verses.hebrew_text_non_sacred
2. figurative_language.figurative_text_in_hebrew_non_sacred
3. verses.figurative_detection_deliberation_non_sacred

The original data was generated with a buggy modifier that incorrectly changed
non-divine words like "the serpent" and "the woman". This also adds support for
the divine name Eloah (אֱלוֹהַּ) found in Psalms 114:7.
"""

import sys
sys.path.insert(0, 'private/src')

import sqlite3
import time
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

def regenerate_verse_hebrew_non_sacred():
    """Regenerate hebrew_text_non_sacred for all verses."""
    db_path = 'database/Pentateuch_Psalms_fig_language.db'

    # Try to connect with timeout
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            break
        except sqlite3.OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            print(f'Database locked, retrying in 2 seconds... (attempt {retry_count}/{max_retries})')
            time.sleep(2)

    cursor = conn.cursor()

    # Get all verses
    cursor.execute('SELECT id, hebrew_text FROM verses')
    verses = cursor.fetchall()

    print(f'Regenerating hebrew_text_non_sacred for {len(verses)} verses...')

    modifier = HebrewDivineNamesModifier()
    updated_count = 0

    for verse_id, hebrew_text in verses:
        if hebrew_text:
            # Use the FIXED modifier
            hebrew_non_sacred = modifier.modify_divine_names(hebrew_text)
            cursor.execute('UPDATE verses SET hebrew_text_non_sacred = ? WHERE id = ?',
                          (hebrew_non_sacred, verse_id))
            updated_count += 1

            # Commit every 500 updates to avoid long locks
            if updated_count % 500 == 0:
                conn.commit()
                print(f'  Updated {updated_count}/{len(verses)} verses... (committed)')

    # Final commit for any remaining updates
    conn.commit()
    print(f'[SUCCESS] Successfully updated {updated_count} verses')
    conn.close()

def regenerate_figurative_hebrew_non_sacred():
    """Regenerate figurative_text_in_hebrew_non_sacred for all annotations."""
    db_path = 'database/Pentateuch_Psalms_fig_language.db'

    # Try to connect with timeout
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            break
        except sqlite3.OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            print(f'Database locked, retrying in 2 seconds... (attempt {retry_count}/{max_retries})')
            time.sleep(2)

    cursor = conn.cursor()

    # Get all annotations with Hebrew text
    cursor.execute('SELECT id, figurative_text_in_hebrew FROM figurative_language WHERE figurative_text_in_hebrew IS NOT NULL')
    annotations = cursor.fetchall()

    print(f'\nRegenerating figurative_text_in_hebrew_non_sacred for {len(annotations)} annotations...')

    modifier = HebrewDivineNamesModifier()
    updated_count = 0

    for ann_id, hebrew_text in annotations:
        if hebrew_text:
            # Use the FIXED modifier
            hebrew_non_sacred = modifier.modify_divine_names(hebrew_text)
            cursor.execute('UPDATE figurative_language SET figurative_text_in_hebrew_non_sacred = ? WHERE id = ?',
                          (hebrew_non_sacred, ann_id))
            updated_count += 1

            # Commit every 500 updates to avoid long locks
            if updated_count % 500 == 0:
                conn.commit()
                print(f'  Updated {updated_count}/{len(annotations)} annotations... (committed)')

    # Final commit for any remaining updates
    conn.commit()
    print(f'[SUCCESS] Successfully updated {updated_count} annotations')
    conn.close()

def regenerate_figurative_deliberation_non_sacred():
    """Regenerate figurative_detection_deliberation_non_sacred for all verses."""
    db_path = 'database/Pentateuch_Psalms_fig_language.db'

    # Try to connect with timeout
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            break
        except sqlite3.OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            print(f'Database locked, retrying in 2 seconds... (attempt {retry_count}/{max_retries})')
            time.sleep(2)

    cursor = conn.cursor()

    # Get all verses with figurative_detection_deliberation
    cursor.execute('SELECT id, figurative_detection_deliberation FROM verses WHERE figurative_detection_deliberation IS NOT NULL')
    verses = cursor.fetchall()

    print(f'\nRegenerating figurative_detection_deliberation_non_sacred for {len(verses)} verses...')

    modifier = HebrewDivineNamesModifier()
    updated_count = 0

    for verse_id, deliberation_text in verses:
        if deliberation_text:
            # Use the FIXED modifier for English text with Hebrew terms
            deliberation_non_sacred = modifier.modify_english_with_hebrew_terms(deliberation_text)
            cursor.execute('UPDATE verses SET figurative_detection_deliberation_non_sacred = ? WHERE id = ?',
                          (deliberation_non_sacred, verse_id))
            updated_count += 1

            # Commit every 500 updates to avoid long locks
            if updated_count % 500 == 0:
                conn.commit()
                print(f'  Updated {updated_count}/{len(verses)} deliberations... (committed)')

    # Final commit for any remaining updates
    conn.commit()
    print(f'[SUCCESS] Successfully updated {updated_count} deliberations')
    conn.close()

def verify_fix():
    """Verify the fix by checking specific test cases."""
    db_path = 'database/Pentateuch_Psalms_fig_language.db'

    # Try to connect with timeout
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            conn = sqlite3.connect(db_path, timeout=30.0)
            break
        except sqlite3.OperationalError as e:
            retry_count += 1
            if retry_count >= max_retries:
                raise
            print(f'Database locked, retrying in 2 seconds... (attempt {retry_count}/{max_retries})')
            time.sleep(2)

    cursor = conn.cursor()

    print('\n' + '='*60)
    print('VERIFICATION TESTS')
    print('='*60)

    # Test 1: Genesis 3:14 - "the serpent" should NOT be modified
    cursor.execute('SELECT hebrew_text, hebrew_text_non_sacred FROM verses WHERE reference = "Genesis 3:14"')
    result = cursor.fetchone()
    if result:
        sacred, non_sacred = result
        has_bug = 'קַנָּחָשׁ' in non_sacred if non_sacred else False
        has_original = 'הַנָּחָשׁ' in non_sacred if non_sacred else False
        print(f'\nTest 1: Genesis 3:14 (the serpent)')
        print(f'  Sacred:     {sacred}')
        print(f'  Non-sacred: {non_sacred}')
        print(f'  Status: {"[FAIL] STILL BUGGY" if has_bug else ("[PASS] FIXED" if has_original else "[WARN] CHECK MANUALLY")}')

    # Test 2: Genesis 3:1 - "the woman" should NOT be modified
    cursor.execute('SELECT hebrew_text, hebrew_text_non_sacred FROM verses WHERE reference = "Genesis 3:1"')
    result = cursor.fetchone()
    if result:
        sacred, non_sacred = result
        has_bug = 'קָאִשָּׁק' in non_sacred if non_sacred else False
        has_original = 'הָאִשָּׁה' in non_sacred if non_sacred else False
        print(f'\nTest 2: Genesis 3:1 (the woman)')
        print(f'  Sacred:     {sacred}')
        print(f'  Non-sacred: {non_sacred}')
        print(f'  Status: {"[FAIL] STILL BUGGY" if has_bug else ("[PASS] FIXED" if has_original else "[WARN] CHECK MANUALLY")}')

    # Test 3: Genesis 1:1 - "Elohim" SHOULD be modified
    cursor.execute('SELECT hebrew_text, hebrew_text_non_sacred FROM verses WHERE reference = "Genesis 1:1"')
    result = cursor.fetchone()
    if result:
        sacred, non_sacred = result
        has_original = 'אֱלֹהִים' in non_sacred if non_sacred else False
        has_modified = 'אֱלֹקִים' in non_sacred if non_sacred else False
        print(f'\nTest 3: Genesis 1:1 (Elohim)')
        print(f'  Sacred:     {sacred}')
        print(f'  Non-sacred: {non_sacred}')
        print(f'  Status: {"[PASS] CORRECTLY MODIFIED" if has_modified else ("[FAIL] NOT MODIFIED" if has_original else "[WARN] CHECK MANUALLY")}')

    # Test 4: Psalms 114:7 - "Eloah" SHOULD be modified
    cursor.execute('SELECT hebrew_text, hebrew_text_non_sacred FROM verses WHERE reference = "Psalms 114:7"')
    result = cursor.fetchone()
    if result:
        sacred, non_sacred = result
        has_original = 'אֱל֣וֹהַּ' in non_sacred if non_sacred else False
        has_modified = 'אֱל֣וֹקַּ' in non_sacred if non_sacred else False
        print(f'\nTest 4: Psalms 114:7 (Eloah)')
        print(f'  Sacred:     {sacred[:50]}...' if len(sacred) > 50 else f'  Sacred:     {sacred}')
        print(f'  Non-sacred: {non_sacred[:50]}...' if len(non_sacred) > 50 else f'  Non-sacred: {non_sacred}')
        print(f'  Status: {"[PASS] CORRECTLY MODIFIED" if has_modified else ("[FAIL] NOT MODIFIED" if has_original else "[WARN] CHECK MANUALLY")}')

    conn.close()

if __name__ == '__main__':
    print('='*60)
    print('REGENERATING HEBREW NON-SACRED TEXT FIELDS')
    print('='*60)

    try:
        # Step 1: Regenerate verse-level Hebrew text
        regenerate_verse_hebrew_non_sacred()

        # Step 2: Regenerate annotation-level Hebrew text
        regenerate_figurative_hebrew_non_sacred()

        # Step 3: Regenerate deliberation-level English with Hebrew terms
        regenerate_figurative_deliberation_non_sacred()

        # Step 4: Verify the fix
        verify_fix()

        print('\n' + '='*60)
        print('[SUCCESS] REGENERATION COMPLETE')
        print('='*60)
        print('\nNext steps:')
        print('1. Test web interface: cd web && python api_server.py')
        print('2. Open biblical_figurative_interface.html')
        print('3. Search for Genesis 3:14 and toggle text versions')
        print('4. Verify serpent/woman are NOT modified')
        print('5. Verify Elohim/YHWH ARE modified')

    except Exception as e:
        print(f'\n[ERROR] {e}')
        import traceback
        traceback.print_exc()
