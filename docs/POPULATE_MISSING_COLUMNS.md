# Populating Missing Columns for New Books

## Overview

When new books are processed through the pipeline and merged into `Biblical_fig_language.db`, some columns may be NULL if they weren't part of the original processing. This document explains how to populate those missing columns.

## Affected Columns

### verses table
- `english_text_clean` - English text with footnotes removed (same as Sefaria's cleaned output)
- `english_text_clean_non_sacred` - Clean English text with Hebrew divine names modified for traditional Jews

### figurative_language table
- `figurative_text_non_sacred` - English figurative text with divine names modified for traditional Jews

## Why These Columns Exist

These columns were added after the initial schema was created:
- `english_text_clean` fields enable clean text search without footnote artifacts
- `*_non_sacred` fields replace divine names (LORD, God, etc.) with Hebrew terms (HaShem, Elokim) for users who prefer not to display sacred names

## How to Populate Missing Columns

### Option 1: Run the existing refresh scripts

The project includes scripts that can populate these fields:

```bash
# For english_text_clean and english_text_clean_non_sacred
cd scripts
python refresh_english_text_auto.py
```

This script:
1. Fetches fresh English text from Sefaria API
2. Applies footnote removal via `_clean_text()` method
3. Applies divine names transformation using `HebrewDivineNamesModifier`
4. Updates the database

### Option 2: Direct SQL update using Python

For a targeted fix (e.g., just Jeremiah), use this approach:

```python
import sqlite3
import sys
sys.path.insert(0, 'private/src')

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

db_path = "database/Biblical_fig_language.db"
modifier = HebrewDivineNamesModifier()

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Update verses table
cursor.execute("""
    SELECT id, english_text
    FROM verses
    WHERE book = 'Jeremiah'
    AND (english_text_clean IS NULL OR english_text_clean_non_sacred IS NULL)
""")

for row in cursor.fetchall():
    english_clean = row['english_text']  # Sefaria already provides clean text
    english_clean_non_sacred = modifier.modify_english_with_hebrew_terms(english_clean)

    cursor.execute("""
        UPDATE verses
        SET english_text_clean = ?, english_text_clean_non_sacred = ?
        WHERE id = ?
    """, (english_clean, english_clean_non_sacred, row['id']))

# Update figurative_language table
cursor.execute("""
    SELECT fl.id, fl.figurative_text
    FROM figurative_language fl
    JOIN verses v ON fl.verse_id = v.id
    WHERE v.book = 'Jeremiah'
    AND fl.figurative_text_non_sacred IS NULL
    AND fl.figurative_text IS NOT NULL
""")

for row in cursor.fetchall():
    fig_text_non_sacred = modifier.modify_english_with_hebrew_terms(row['figurative_text'])

    cursor.execute("""
        UPDATE figurative_language
        SET figurative_text_non_sacred = ?
        WHERE id = ?
    """, (fig_text_non_sacred, row['id']))

conn.commit()
conn.close()
print("Done!")
```

### Option 3: Re-run regeneration script

For the `figurative_text_non_sacred` field specifically:

```bash
cd scripts
python regenerate_prefixed_elohim_fields.py
```

This regenerates all non-sacred fields across the entire database.

## Verification

After populating, verify the columns are filled:

```sql
-- Check verses table
SELECT book,
       COUNT(*) as total,
       SUM(CASE WHEN english_text_clean IS NULL THEN 1 ELSE 0 END) as missing_clean,
       SUM(CASE WHEN english_text_clean_non_sacred IS NULL THEN 1 ELSE 0 END) as missing_clean_ns
FROM verses
GROUP BY book;

-- Check figurative_language table
SELECT v.book,
       COUNT(*) as total,
       SUM(CASE WHEN fl.figurative_text_non_sacred IS NULL THEN 1 ELSE 0 END) as missing_ns
FROM figurative_language fl
JOIN verses v ON fl.verse_id = v.id
GROUP BY v.book;
```

## Pipeline Fix (December 2024)

As of December 2024, the pipeline has been updated to populate these fields during initial processing:

**Files modified:**
- `private/src/hebrew_figurative_db/database/db_manager.py` - Schema and insert methods updated
- `private/interactive_parallel_processor.py` - Now computes and passes these fields

Future books processed through the pipeline will have all columns populated automatically.

## Related Files

- `scripts/refresh_english_text.py` - Interactive version of the refresh script
- `scripts/refresh_english_text_auto.py` - Automatic version (no prompts)
- `scripts/regenerate_prefixed_elohim_fields.py` - Regenerates all non-sacred fields
- `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py` - The modifier class
