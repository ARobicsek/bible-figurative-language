# 🚨 CRITICAL BUG - Action Required

## Quick Summary
The Hebrew divine names modifier has been **fixed in code** but **not yet applied to the database**. This means the web interface still shows incorrect Hebrew text when "Traditional Jewish" is selected.

---

## The Bug

### What's Wrong?
Non-divine Hebrew words are being incorrectly modified in "Traditional Jewish" mode:
- ❌ `הַנָּחָשׁ` (the serpent) → `קַנָּחָשׁ`
- ❌ `הָאִשָּׁה` (the woman) → `קָאִשָּׁק`

### Where to See It
1. Open the web interface
2. Search for "Genesis 3:14"
3. Select "Traditional Jewish" text version
4. The Hebrew text shows `קַנָּחָשׁ` instead of `הַנָּחָשׁ`

---

## What Was Fixed (Already Done ✅)

### The Code
- **File**: `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py`
- **Lines**: 113, 124
- **Fix**: Made Elohim vowels required (not optional) to prevent false matches
- **Test**: Run `python test_divine_modifier.py` - all tests pass ✅

### The Deliberation Field
- **Column**: `figurative_detection_deliberation_non_sacred`
- **Status**: ✅ Already regenerated with fixed modifier (8,368 verses)
- **Works**: Deliberation text displays correctly in web interface

---

## What Still Needs to Be Fixed (TODO ⚠️)

### 1. Hebrew Text in Verses Table
- **Column**: `hebrew_text_non_sacred` in `verses` table
- **Rows**: All 5,846+ verses
- **Status**: ❌ Still contains OLD buggy data
- **Impact**: Web interface shows incorrect Hebrew when "Traditional Jewish" selected

### 2. Figurative Text in Annotations Table
- **Column**: `figurative_text_in_hebrew_non_sacred` in `figurative_language` table
- **Rows**: All 3,000+ annotations
- **Status**: ❌ Still contains OLD buggy data
- **Impact**: Highlighted figurative text may be incorrect in "Traditional Jewish" mode

---

## How to Fix (Copy & Paste)

### Step 1: Regenerate Hebrew Verse Text
```bash
python -c "
import sys
sys.path.insert(0, 'private/src')
import sqlite3
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

db_path = 'database/Pentateuch_Psalms_fig_language.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id, hebrew_text FROM verses')
verses = cursor.fetchall()
print(f'Regenerating hebrew_text_non_sacred for {len(verses)} verses...')

modifier = HebrewDivineNamesModifier()
count = 0
for verse_id, hebrew_text in verses:
    if hebrew_text:
        hebrew_non_sacred = modifier.modify_divine_names(hebrew_text)
        cursor.execute('UPDATE verses SET hebrew_text_non_sacred = ? WHERE id = ?',
                      (hebrew_non_sacred, verse_id))
        count += 1
        if count % 1000 == 0:
            print(f'  Progress: {count}/{len(verses)}')

conn.commit()
print(f'✅ Done! Updated {count} verses')
conn.close()
"
```

### Step 2: Regenerate Figurative Text in Annotations
```bash
python -c "
import sys
sys.path.insert(0, 'private/src')
import sqlite3
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

db_path = 'database/Pentateuch_Psalms_fig_language.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute('SELECT id, figurative_text_in_hebrew FROM figurative_language WHERE figurative_text_in_hebrew IS NOT NULL')
annotations = cursor.fetchall()
print(f'Regenerating figurative_text_in_hebrew_non_sacred for {len(annotations)} annotations...')

modifier = HebrewDivineNamesModifier()
count = 0
for ann_id, hebrew_text in annotations:
    if hebrew_text:
        hebrew_non_sacred = modifier.modify_divine_names(hebrew_text)
        cursor.execute('UPDATE figurative_language SET figurative_text_in_hebrew_non_sacred = ? WHERE id = ?',
                      (hebrew_non_sacred, ann_id))
        count += 1
        if count % 500 == 0:
            print(f'  Progress: {count}/{len(annotations)}')

conn.commit()
print(f'✅ Done! Updated {count} annotations')
conn.close()
"
```

### Step 3: Verify the Fix
```bash
python -c "
import sqlite3
db = sqlite3.connect('database/Pentateuch_Psalms_fig_language.db')
c = db.cursor()

print('Testing Genesis 3:14...')
c.execute('SELECT hebrew_text, hebrew_text_non_sacred FROM verses WHERE reference = \"Genesis 3:14\"')
r = c.fetchone()

if r:
    print('Sacred:', r[0][:50])
    print('Non-sacred:', r[1][:50])

    # Check for the bug
    if 'קַנָּחָשׁ' in r[1]:
        print('❌ BUG STILL PRESENT: Serpent incorrectly modified')
    elif 'הַנָּחָשׁ' in r[1] or 'הַנָּחָשׁ' in r[0]:
        print('✅ FIXED: Serpent correctly preserved')
    else:
        print('⚠️  Cannot verify - serpent text not found')
else:
    print('❌ Genesis 3:14 not found in database')

db.close()
"
```

---

## Expected Output

After running the fix, you should see:
```
✅ FIXED: Serpent correctly preserved
```

And in the web interface:
- Genesis 3:14 in "Traditional Jewish" mode should show `הַנָּחָשׁ` (correct)
- Divine names should still be modified: `אֱלֹהִים` → `אֱלֹקִים` (correct)

---

## Time Estimate
- Step 1: ~30 seconds (5,846 verses)
- Step 2: ~15 seconds (3,000 annotations)
- Step 3: Instant verification

---

## More Details
See `NEXT_SESSION_PROMPT.md` for comprehensive context and explanation.
