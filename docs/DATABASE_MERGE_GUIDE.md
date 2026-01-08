# Database Merge Guide

This guide provides instructions for merging chapter databases into a complete book database, and then merging that book into the main `Biblical_fig_language.db`.

## Quick Reference Workflow

```
1. Process book with interactive_parallel_processor.py
2. Check for failed chapters → retry if needed
3. Verify ALL chapters present (completeness check)
4. Merge chapter DBs → Book.db in database/
5. Verify Book.db integrity
6. Merge Book.db → Biblical_fig_language.db
7. Verify main database integrity
```

## Overview

The pipeline generates separate SQLite databases for different chapter ranges. These must be merged while maintaining **foreign key integrity** between the `verses` and `figurative_language` tables.

**Key constraint:** `figurative_language.verse_id` references `verses.id`

**Output locations:**
- Individual book databases: `database/{BookName}.db` (keep for reference/backup)
- Main merged database: `database/Biblical_fig_language.db`

## Database Schema

Both tables use auto-increment `id` columns:

```
verses
├── id (INTEGER PRIMARY KEY)
├── reference, book, chapter, verse
├── hebrew_text, english_text, ...
└── (22 other columns)

figurative_language
├── id (INTEGER PRIMARY KEY)
├── verse_id (INTEGER) ──────────► verses.id
├── figurative_language, simile, metaphor, ...
└── (48 other columns)
```

---

## Pre-Merge Checklist: Verify Chapter Completeness

**CRITICAL:** Before merging, ensure ALL chapters are present. Missing chapters mean incomplete data!

### Expected Chapter Counts (Sefaria Hebrew Versification)

```python
EXPECTED_CHAPTERS = {
    # Torah
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    # Former Prophets
    "Joshua": 24, "Judges": 21, "1_Samuel": 31, "2_Samuel": 24, "1_Kings": 22, "2_Kings": 25,
    # Major Prophets
    "Isaiah": 66, "Jeremiah": 52, "Ezekiel": 48,
    # Minor Prophets (The Twelve)
    "Hosea": 14, "Joel": 4, "Amos": 9, "Obadiah": 1, "Jonah": 4, "Micah": 7,
    "Nahum": 3, "Habakkuk": 3, "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 3,
    # Ketuvim (Writings)
    "Psalms": 150, "Proverbs": 31, "Job": 42, "Song_of_Songs": 8, "Ruth": 4,
    "Lamentations": 5, "Ecclesiastes": 12, "Esther": 10, "Daniel": 12,
    "Ezra": 10, "Nehemiah": 13, "I_Chronicles": 29, "II_Chronicles": 36
}
```

### Completeness Check Script

```python
import sqlite3
import os
from collections import defaultdict

def check_completeness(db_files: list, book_name: str, expected_chapters: int, source_dir: str = 'private/'):
    """
    Check if all chapters are covered across the database files.

    Returns:
        tuple: (chapters_found, missing_chapters, coverage_map)
    """
    coverage = defaultdict(list)  # chapter -> list of db files containing it

    for db_file in db_files:
        path = os.path.join(source_dir, db_file)
        if not os.path.exists(path):
            print(f"WARNING: {db_file} not found!")
            continue

        db = sqlite3.connect(path)
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT chapter FROM verses ORDER BY chapter')
        chapters = [r[0] for r in cursor.fetchall()]
        db.close()

        for ch in chapters:
            coverage[ch].append(db_file)

        print(f'{db_file}: chapters {chapters}')

    # Check for missing chapters
    found = set(coverage.keys())
    expected = set(range(1, expected_chapters + 1))
    missing = expected - found

    print(f'\n=== COMPLETENESS CHECK: {book_name} ===')
    print(f'Expected chapters: 1-{expected_chapters}')
    print(f'Found chapters: {sorted(found)}')

    if missing:
        print(f'⚠️  MISSING CHAPTERS: {sorted(missing)}')
        print(f'\nTo process missing chapters, run:')
        for ch in sorted(missing):
            print(f'  python interactive_parallel_processor.py {book_name} {ch}')
        return False, sorted(missing), coverage
    else:
        print(f'✅ ALL {expected_chapters} CHAPTERS PRESENT')
        return True, [], coverage

# Usage example
db_files = ['ezekiel_ch1-10.db', 'ezekiel_ch11-24.db', 'ezekiel_ch25-48.db']
complete, missing, coverage = check_completeness(db_files, 'Ezekiel', 48)

if not complete:
    print(f'\n❌ Cannot proceed with merge - {len(missing)} chapters missing!')
```

### Check Failure Manifests

After processing, check the failure manifest for failed chapters:

```python
import json

def check_failures(manifest_path: str):
    """Check failure manifest for chapters that need retry."""
    with open(manifest_path) as f:
        manifest = json.load(f)

    failed = manifest.get('failed_items', [])
    if failed:
        print(f'⚠️  {len(failed)} FAILED CHAPTERS:')
        for item in failed:
            print(f"  • {item['book']} {item['chapter']}: {item['reason'][:60]}...")
            print(f"    Retry: {item['retry_command']}")
        return False
    else:
        print('✅ No failed chapters')
        return True

# Check most recent failure manifest
check_failures('output/book_ch1-48_all_v_parallel_YYYYMMDD_HHMM_failures.json')
```

---

## Part 1: Merging Chapter Databases into a Book Database

Use this when you have multiple chapter-range databases for the same book (e.g., `ezekiel_ch1-10.db`, `ezekiel_ch11-20.db`, etc.).

### Step 1: Analyze Chapter Coverage

First, identify which chapters exist in each database:

```python
import sqlite3
import os

db_files = [
    'book_ch1-10.db',
    'book_ch11-20.db',
    # ... add all your database files
]

for db_file in db_files:
    db = sqlite3.connect(db_file)
    cursor = db.cursor()
    cursor.execute('SELECT DISTINCT chapter FROM verses ORDER BY chapter')
    chapters = [r[0] for r in cursor.fetchall()]
    cursor.execute('SELECT COUNT(*) FROM verses')
    verse_count = cursor.fetchone()[0]
    print(f'{db_file}: Chapters {chapters}, {verse_count} verses')
    db.close()
```

### Step 2: Create Chapter-to-Database Mapping

Map each chapter to its source database. When chapters appear in multiple databases, prefer the most recent/complete version:

```python
# Example mapping for Ezekiel
coverage = {
    1: 'ezekiel_ch1.db',
    2: 'ezekiel_ch1-10.db',
    3: 'ezekiel_ch1-10.db',
    4: 'ezekiel_ch1-4.db',
    # ... map all chapters
}

# Verify all chapters are covered
book_chapters = 48  # Ezekiel has 48 chapters
for ch in range(1, book_chapters + 1):
    if ch not in coverage:
        print(f'WARNING: Chapter {ch} not covered!')
```

### Step 3: Merge with Foreign Key Remapping

```python
import sqlite3
import os

def merge_chapters_to_book(coverage: dict, output_path: str, source_dir: str):
    """
    Merge chapter databases into a single book database.

    Args:
        coverage: Dict mapping chapter numbers to source database filenames
        output_path: Path for the merged output database
        source_dir: Directory containing source databases
    """
    # Remove existing output
    if os.path.exists(output_path):
        os.remove(output_path)

    # Get schema from first source database
    first_db = list(coverage.values())[0]
    source = sqlite3.connect(os.path.join(source_dir, first_db))
    cursor = source.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='verses'")
    verses_schema = cursor.fetchone()[0]
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='figurative_language'")
    fl_schema = cursor.fetchone()[0]

    # Get column names (excluding 'id')
    cursor.execute('PRAGMA table_info(verses)')
    verse_cols = [c[1] for c in cursor.fetchall() if c[1] != 'id']
    cursor.execute('PRAGMA table_info(figurative_language)')
    fl_cols = [c[1] for c in cursor.fetchall() if c[1] != 'id']
    fl_cols_no_verse_id = [c for c in fl_cols if c != 'verse_id']
    source.close()

    # Create target database
    target = sqlite3.connect(output_path)
    target_cursor = target.cursor()
    target_cursor.execute(verses_schema)
    target_cursor.execute(fl_schema)
    target.commit()

    # Process chapters in order
    total_verses = 0
    total_fl = 0

    for chapter in sorted(coverage.keys()):
        db_file = coverage[chapter]
        source = sqlite3.connect(os.path.join(source_dir, db_file))
        source_cursor = source.cursor()

        # Get verses for this chapter
        source_cursor.execute(
            f'SELECT id, {", ".join(verse_cols)} FROM verses WHERE chapter = ? ORDER BY verse',
            (chapter,)
        )

        for verse_row in source_cursor.fetchall():
            old_verse_id = verse_row[0]
            verse_data = verse_row[1:]

            # Insert verse (new ID auto-generated)
            placeholders = ', '.join(['?' for _ in verse_cols])
            target_cursor.execute(
                f'INSERT INTO verses ({", ".join(verse_cols)}) VALUES ({placeholders})',
                verse_data
            )
            new_verse_id = target_cursor.lastrowid
            total_verses += 1

            # Get and insert figurative_language entries with updated verse_id
            source_cursor.execute(
                f'SELECT {", ".join(fl_cols_no_verse_id)} FROM figurative_language WHERE verse_id = ?',
                (old_verse_id,)
            )

            for fl_row in source_cursor.fetchall():
                placeholders = ', '.join(['?' for _ in range(len(fl_cols_no_verse_id) + 1)])
                target_cursor.execute(
                    f'INSERT INTO figurative_language (verse_id, {", ".join(fl_cols_no_verse_id)}) VALUES ({placeholders})',
                    (new_verse_id,) + fl_row
                )
                total_fl += 1

        source.close()
        print(f'Chapter {chapter}: processed')

    target.commit()
    target.close()

    print(f'\nMerge complete: {total_verses} verses, {total_fl} FL entries')
    return total_verses, total_fl

# Usage - IMPORTANT: Save to database/ directory for backup/reference
coverage = {1: 'ch1.db', 2: 'ch1-10.db', ...}
merge_chapters_to_book(coverage, 'database/Ezekiel.db', 'private/')  # Keep individual book DBs!
```

### Step 4: Verify the Merge

```python
def verify_book_database(db_path: str):
    """Verify foreign key integrity in merged database."""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Check counts
    cursor.execute('SELECT COUNT(*) FROM verses')
    verse_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM figurative_language')
    fl_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(DISTINCT chapter) FROM verses')
    chapter_count = cursor.fetchone()[0]

    print(f'Verses: {verse_count}')
    print(f'FL entries: {fl_count}')
    print(f'Chapters: {chapter_count}')

    # Check for orphaned FL entries
    cursor.execute('''
        SELECT COUNT(*) FROM figurative_language fl
        LEFT JOIN verses v ON fl.verse_id = v.id
        WHERE v.id IS NULL
    ''')
    orphans = cursor.fetchone()[0]
    print(f'Orphaned FL entries: {orphans}')

    # Verify JOIN works
    cursor.execute('''
        SELECT v.reference, fl.figurative_text
        FROM verses v
        JOIN figurative_language fl ON v.id = fl.verse_id
        LIMIT 3
    ''')
    print('\nSample JOINs:')
    for row in cursor.fetchall():
        print(f'  {row[0]}: {row[1][:50] if row[1] else ""}...')

    db.close()

    if orphans > 0:
        raise ValueError(f'INTEGRITY ERROR: {orphans} orphaned FL entries!')

    return True

verify_book_database('database/Ezekiel.db')  # Verify the book database in database/
```

---

## Part 2: Merging a Book into Biblical_fig_language.db

### Step 1: Check Target Database State

```python
import sqlite3

target = sqlite3.connect('database/Biblical_fig_language.db')
cursor = target.cursor()

# Check existing books
cursor.execute('SELECT DISTINCT book FROM verses ORDER BY book')
books = [r[0] for r in cursor.fetchall()]
print(f'Existing books: {books}')

# Check if book already exists
book_name = 'Ezekiel'  # The book you're adding
cursor.execute('SELECT COUNT(*) FROM verses WHERE book = ?', (book_name,))
existing = cursor.fetchone()[0]
if existing > 0:
    print(f'WARNING: {book_name} already has {existing} verses!')

# Get max IDs
cursor.execute('SELECT MAX(id) FROM verses')
max_verse_id = cursor.fetchone()[0] or 0
cursor.execute('SELECT MAX(id) FROM figurative_language')
max_fl_id = cursor.fetchone()[0] or 0

print(f'Max verse ID: {max_verse_id}')
print(f'Max FL ID: {max_fl_id}')

target.close()
```

### Step 2: Verify Schema Compatibility

```python
def verify_schema_match(target_path: str, source_path: str):
    """Ensure both databases have matching schemas."""
    target = sqlite3.connect(target_path)
    source = sqlite3.connect(source_path)

    for table in ['verses', 'figurative_language']:
        target.execute(f'PRAGMA table_info({table})')
        target_cols = set(c[1] for c in target.fetchall())

        source.execute(f'PRAGMA table_info({table})')
        source_cols = set(c[1] for c in source.fetchall())

        if target_cols != source_cols:
            missing_in_target = source_cols - target_cols
            missing_in_source = target_cols - source_cols
            print(f'{table} schema mismatch!')
            print(f'  Missing in target: {missing_in_target}')
            print(f'  Missing in source: {missing_in_source}')
            return False

    print('Schemas match!')
    target.close()
    source.close()
    return True

verify_schema_match('database/Biblical_fig_language.db', 'database/Book.db')
```

### Step 3: Merge with ID Offset

```python
import sqlite3

def merge_book_into_main(source_path: str, target_path: str):
    """
    Merge a book database into Biblical_fig_language.db.

    Args:
        source_path: Path to the book database (e.g., 'database/Ezekiel.db')
        target_path: Path to main database ('database/Biblical_fig_language.db')
    """
    target = sqlite3.connect(target_path)
    source = sqlite3.connect(source_path)
    target_cursor = target.cursor()
    source_cursor = source.cursor()

    # Get max IDs from target
    target_cursor.execute('SELECT MAX(id) FROM verses')
    max_verse_id = target_cursor.fetchone()[0] or 0
    target_cursor.execute('SELECT MAX(id) FROM figurative_language')
    max_fl_id = target_cursor.fetchone()[0] or 0

    print(f'Target max verse ID: {max_verse_id}')
    print(f'Target max FL ID: {max_fl_id}')

    # Get column names
    source_cursor.execute('PRAGMA table_info(verses)')
    verse_cols = [c[1] for c in source_cursor.fetchall() if c[1] != 'id']

    source_cursor.execute('PRAGMA table_info(figurative_language)')
    fl_cols = [c[1] for c in source_cursor.fetchall() if c[1] != 'id']
    fl_cols_no_verse_id = [c for c in fl_cols if c != 'verse_id']

    # Build old_id -> new_id mapping
    source_cursor.execute('SELECT id FROM verses ORDER BY id')
    verse_id_map = {}
    for i, (old_id,) in enumerate(source_cursor.fetchall(), start=1):
        verse_id_map[old_id] = max_verse_id + i

    print(f'Mapping {len(verse_id_map)} verses to IDs {max_verse_id + 1} - {max_verse_id + len(verse_id_map)}')

    # Insert verses with explicit new IDs
    source_cursor.execute(f'SELECT id, {", ".join(verse_cols)} FROM verses ORDER BY id')
    verses_inserted = 0

    for row in source_cursor.fetchall():
        old_id = row[0]
        new_id = verse_id_map[old_id]
        verse_data = row[1:]

        cols_with_id = ['id'] + verse_cols
        placeholders = ', '.join(['?' for _ in cols_with_id])
        target_cursor.execute(
            f'INSERT INTO verses ({", ".join(cols_with_id)}) VALUES ({placeholders})',
            (new_id,) + verse_data
        )
        verses_inserted += 1

    print(f'Inserted {verses_inserted} verses')

    # Insert FL entries with updated verse_id foreign keys
    source_cursor.execute(
        f'SELECT id, verse_id, {", ".join(fl_cols_no_verse_id)} FROM figurative_language ORDER BY id'
    )
    fl_inserted = 0

    for row in source_cursor.fetchall():
        old_fl_id = row[0]
        old_verse_id = row[1]
        fl_data = row[2:]

        new_verse_id = verse_id_map[old_verse_id]
        new_fl_id = max_fl_id + old_fl_id

        cols_with_ids = ['id', 'verse_id'] + fl_cols_no_verse_id
        placeholders = ', '.join(['?' for _ in cols_with_ids])
        target_cursor.execute(
            f'INSERT INTO figurative_language ({", ".join(cols_with_ids)}) VALUES ({placeholders})',
            (new_fl_id, new_verse_id) + fl_data
        )
        fl_inserted += 1

    print(f'Inserted {fl_inserted} FL entries')

    target.commit()
    target.close()
    source.close()

    return verses_inserted, fl_inserted

merge_book_into_main('database/Ezekiel.db', 'database/Biblical_fig_language.db')
```

### Step 4: Verify the Merge

```python
def verify_main_database(db_path: str, book_name: str):
    """Verify the book was merged correctly."""
    db = sqlite3.connect(db_path)
    cursor = db.cursor()

    # Check book exists
    cursor.execute('SELECT COUNT(*) FROM verses WHERE book = ?', (book_name,))
    verse_count = cursor.fetchone()[0]
    print(f'{book_name} verses: {verse_count}')

    # Check FL entries via JOIN
    cursor.execute('''
        SELECT COUNT(*) FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE v.book = ?
    ''', (book_name,))
    fl_count = cursor.fetchone()[0]
    print(f'{book_name} FL entries (via JOIN): {fl_count}')

    # Check for orphans (should be 0)
    cursor.execute('''
        SELECT COUNT(*) FROM figurative_language fl
        LEFT JOIN verses v ON fl.verse_id = v.id
        WHERE v.id IS NULL
    ''')
    orphans = cursor.fetchone()[0]
    print(f'Total orphaned FL entries: {orphans}')

    # Test JOIN
    cursor.execute('''
        SELECT v.reference, fl.figurative_language, fl.figurative_text
        FROM verses v
        JOIN figurative_language fl ON v.id = fl.verse_id
        WHERE v.book = ?
        LIMIT 3
    ''', (book_name,))

    print(f'\nSample JOINs for {book_name}:')
    for row in cursor.fetchall():
        text = row[2][:40] + '...' if row[2] and len(row[2]) > 40 else row[2]
        print(f'  {row[0]}: {row[1]} - "{text}"')

    db.close()

    if orphans > 0:
        raise ValueError(f'INTEGRITY ERROR: {orphans} orphaned FL entries!')

    return True

verify_main_database('database/Biblical_fig_language.db', 'Ezekiel')
```

---

## Complete Example Script

Here's a complete script combining both steps:

```python
#!/usr/bin/env python3
"""
merge_book.py - Merge chapter databases into Biblical_fig_language.db

Usage:
    python merge_book.py --book Ezekiel --chapters-dir private/ --output database/
"""

import sqlite3
import os
import argparse
from typing import Dict

def analyze_chapter_databases(directory: str, book_prefix: str) -> Dict[int, str]:
    """Analyze available chapter databases and return coverage mapping."""
    coverage = {}
    db_files = [f for f in os.listdir(directory) if f.startswith(book_prefix.lower()) and f.endswith('.db')]

    for db_file in sorted(db_files):
        db = sqlite3.connect(os.path.join(directory, db_file))
        cursor = db.cursor()
        cursor.execute('SELECT DISTINCT chapter FROM verses ORDER BY chapter')
        chapters = [r[0] for r in cursor.fetchall()]
        db.close()

        for ch in chapters:
            # Later files override earlier ones (assuming chronological naming)
            coverage[ch] = db_file

        print(f'{db_file}: chapters {chapters}')

    return coverage

def merge_chapters_to_book(coverage: Dict[int, str], output_path: str, source_dir: str):
    # ... (implementation from Part 1 Step 3)
    pass

def merge_book_into_main(source_path: str, target_path: str):
    # ... (implementation from Part 2 Step 3)
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--book', required=True, help='Book name (e.g., Ezekiel)')
    parser.add_argument('--chapters-dir', default='private/', help='Directory with chapter DBs')
    parser.add_argument('--output', default='database/', help='Output directory')
    args = parser.parse_args()

    # Step 1: Analyze and merge chapters
    print(f'=== Analyzing {args.book} chapter databases ===')
    coverage = analyze_chapter_databases(args.chapters_dir, args.book)

    # Step 2: Merge into book database
    book_db = os.path.join(args.output, f'{args.book}.db')
    print(f'\n=== Merging chapters into {book_db} ===')
    merge_chapters_to_book(coverage, book_db, args.chapters_dir)

    # Step 3: Merge into main database
    main_db = os.path.join(args.output, 'Biblical_fig_language.db')
    print(f'\n=== Merging into {main_db} ===')
    merge_book_into_main(book_db, main_db)

    print('\n=== COMPLETE ===')
```

---

## Troubleshooting

### Schema Mismatch

If schemas don't match, you may need to add missing columns to the target:

```python
# Add missing column to target
cursor.execute('ALTER TABLE verses ADD COLUMN new_column TEXT')
```

### Duplicate Book Data

If the book already exists in the target, remove it first:

```python
# Remove existing book data (careful - this deletes data!)
cursor.execute('DELETE FROM figurative_language WHERE verse_id IN (SELECT id FROM verses WHERE book = ?)', (book_name,))
cursor.execute('DELETE FROM verses WHERE book = ?', (book_name,))
db.commit()
```

### ID Gaps

The main database may have ID gaps due to deletions. The merge process handles this by using `MAX(id) + offset` rather than assuming sequential IDs.

---

## Summary

### Complete Workflow

1. **Process** book with `interactive_parallel_processor.py`
2. **Check failures** - review failure manifest, retry any failed chapters
3. **Verify completeness** - ensure ALL chapters are present (use completeness check script)
4. **Analyze** chapter databases to understand coverage/overlaps
5. **Map** each chapter to its source database (prefer latest/most complete)
6. **Merge chapters** into `database/{BookName}.db` with FK remapping
7. **Verify** book database - no orphaned FL entries, JOINs work
8. **Merge into main** `database/Biblical_fig_language.db` with ID offsets
9. **Verify** main database integrity across all books

### File Organization

```
Bible/
├── private/                          # Source chapter databases (temporary)
│   ├── ezekiel_ch1-10.db
│   ├── ezekiel_ch11-24.db
│   └── ...
├── database/                         # Final databases (permanent)
│   ├── Ezekiel.db                   # Complete book (keep for backup!)
│   ├── Isaiah.db
│   ├── ...
│   └── Biblical_fig_language.db     # Main merged database
└── output/                          # Logs and manifests
    └── *_failures.json              # Check these for failed chapters!
```

### Key Points

- **Always verify completeness** before merging - missing chapters = incomplete data
- **Keep individual book databases** in `database/` as backups
- **Check failure manifests** after processing to catch failed chapters
- **Foreign key integrity** is critical - always verify JOINs work after merging
