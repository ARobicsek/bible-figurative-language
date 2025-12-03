# Future Book Additions: Practical Guide

## Overview

This guide provides step-by-step instructions for adding new biblical books to the Hebrew Figurative Language Analysis project. It incorporates all lessons learned from the Proverbs addition process to ensure smooth, efficient processing.

## Prerequisites

### System Requirements
- Python 3.8+ with required dependencies installed
- Access to AI model APIs (GPT-5.1, Gemini, Claude)
- Sufficient storage for database backups and processing artifacts
- Git for version control

### Required Files (Must Exist)
- `private/interactive_parallel_processor.py` - Main processing pipeline
- `private/flexible_tagging_gemini_client.py` - Enhanced AI client
- `private/universal_validation_recovery.py` - Recovery system
- `consolidate_proverbs_to_pentateuch.py` - Consolidation template
- `database/Pentateuch_Psalms_fig_language.db` - Main database

---

## Quick Start: Add Your First Book

### Step 1: Backup Current Database
```bash
# Create timestamped backup
cp database/Pentateuch_Psalms_fig_language.db database/Pentateuch_Psalms_fig_language.db_backup_$(date +%Y%m%d_%H%M%S)
```

### Step 2: Process the New Book
```bash
cd private
# Single chapter
python interactive_parallel_processor.py Ecclesiastes 1

# Multiple chapters
python interactive_parallel_processor.py Ecclesiastes 1-12

# Interactive mode (select chapters)
python interactive_parallel_processor.py
```

### Step 3: Verify Results
```bash
# Check database integrity
python universal_validation_recovery.py --database ../database/Pentateuch_Psalms_fig_language.db --health-check
```

### Step 4: Consolidate (If Separate Database Created)
```bash
# Adapt the consolidation script for your new book
python consolidate_new_book_to_main.py
```

---

## Detailed Workflow

## Phase 1: Pre-Processing Preparation

### 1.1 Analyze Target Database
```python
# Connect to main database and analyze ID ranges
import sqlite3

conn = sqlite3.connect('database/Pentateuch_Psalms_fig_language.db')
cursor = conn.cursor()

# Get current ID ranges
cursor.execute("SELECT MAX(id) FROM verses")
max_verse_id = cursor.fetchone()[0]  # e.g., 9217

cursor.execute("SELECT MAX(id) FROM figurative_language")
max_instance_id = cursor.fetchone()[0]  # e.g., 5982

print(f"Next available verse_id: {max_verse_id + 1}")
print(f"Next available instance_id: {max_instance_id + 1}")

conn.close()
```

### 1.2 Verify Schema Compatibility
```python
# Ensure your processing database schema matches target
# Use PRAGMA table_info to compare schemas
cursor.execute("PRAGMA table_info(verses)")
verses_columns = cursor.fetchall()

cursor.execute("PRAGMA table_info(figurative_language)")
instances_columns = cursor.fetchall()
```

### 1.3 Create Backup Strategy
```python
# Automated backup before any processing
import shutil
from datetime import datetime

def create_backup(database_path):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{database_path}_backup_{timestamp}"
    shutil.copy2(database_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path
```

## Phase 2: Book Processing

### 2.1 Single Chapter Processing
```bash
# Process individual chapter with full pipeline
cd private
python interactive_parallel_processor.py <BookName> <ChapterNumber>

# Examples:
python interactive_parallel_processor.py Ecclesiastes 1
python interactive_parallel_processor.py Song_of_Songs 1
python interactive_parallel_processor.py Job 1
```

### 2.2 Batch Chapter Processing
```bash
# Process multiple chapters efficiently
python interactive_parallel_processor.py <BookName> <StartChapter>-<EndChapter>

# Examples:
python interactive_parallel_processor.py Ecclesiastes 1-12
python interactive_parallel_processor.py Job 1-42
python interactive_parallel_processor.py Isaiah 1-10
```

### 2.3 Interactive Processing
```bash
# Launch interactive mode for flexible selection
python interactive_parallel_processor.py
# Follow prompts to select book(s) and chapter(s)
```

### 2.4 Monitoring During Processing
Watch for these key indicators:
- **JSON Extraction Strategy**: Should show high success rate for Strategy 1
- **Validation Coverage**: Should maintain >=95% coverage
- **Cost Tracking**: Monitor API costs per chapter
- **Error Logs**: Watch for constraint violations or parsing issues

## Phase 3: Quality Assurance

### 3.1 Automated Health Check
```bash
cd private
python universal_validation_recovery.py --database ../database/Pentateuch_Psalms_fig_language.db --health-check
```

### 3.2 Validation Coverage Verification
```python
# Manually check validation coverage
def verify_book_coverage(book_name):
    cursor.execute("""
        SELECT chapter,
               COUNT(*) as total_instances,
               SUM(CASE WHEN validation_response IS NOT NULL THEN 1 ELSE 0 END) as validated_instances
        FROM verses v
        LEFT JOIN figurative_language fl ON v.id = fl.verse_id
        WHERE v.book = ?
        GROUP BY chapter
        ORDER BY chapter
    """, (book_name,))

    results = cursor.fetchall()
    for chapter, total, validated in results:
        if total > 0:
            coverage = (validated / total) * 100
            print(f"Chapter {chapter}: {coverage:.1f}% coverage ({validated}/{total})")
```

### 3.3 Database Integrity Checks
```python
# Check for orphaned records
cursor.execute("""
    SELECT COUNT(*) FROM figurative_language fl
    LEFT JOIN verses v ON fl.verse_id = v.id
    WHERE v.id IS NULL
""")
orphaned_count = cursor.fetchone()[0]
assert orphaned_count == 0, f"Found {orphaned_count} orphaned instances"

# Check for duplicate IDs
cursor.execute("SELECT COUNT(*) - COUNT(DISTINCT id) FROM verses")
duplicate_verses = cursor.fetchone()[0]
assert duplicate_verses == 0, f"Found {duplicate_verses} duplicate verse IDs"
```

## Phase 4: Database Consolidation

### 4.1 Adapt Consolidation Template
Copy and modify `consolidate_proverbs_to_pentateuch.py`:

```python
# Key modifications needed:
SOURCE_DATABASE = "path/to/your/book_database.db"
TARGET_DATABASE = "database/Pentateuch_Psalms_fig_language.db"
BOOK_NAME = "YourBookName"

# The rest of the script handles ID mapping automatically
```

### 4.2 Execute Consolidation
```bash
python consolidate_your_book.py
```

### 4.3 Verify Consolidation Results
```python
# Verify book was added correctly
cursor.execute("""
    SELECT
        book,
        COUNT(DISTINCT chapter) as chapters,
        COUNT(*) as verses,
        COUNT(DISTINCT fl.id) as instances
    FROM verses v
    LEFT JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE book = ?
    GROUP BY book
""", (BOOK_NAME,))

results = cursor.fetchone()
print(f"Book {BOOK_NAME}: {results[1]} chapters, {results[2]} verses, {results[3]} instances")
```

## Phase 5: Recovery and Troubleshooting

### 5.1 Validation Recovery
```bash
# Auto-detect and fix validation issues
python universal_validation_recovery.py --database path/to/database.db --auto-detect

# Target specific chapters
python universal_validation_recovery.py --database path/to/database.db --chapters 1,2,3

# Update final fields only
python universal_validation_recovery.py --database path/to/database.db --final-fields-only
```

### 5.2 Common Issues and Solutions

**Issue**: Constraint violations during processing
```bash
# Solution: Database constraint handling is automatic
# Monitor logs for constraint violation messages
# The system will sanitize data and continue processing
```

**Issue**: JSON extraction failures
```bash
# Solution: 10-strategy extraction handles this automatically
# Monitor strategy success rates in logs
# If issues persist, the system has multiple fallback mechanisms
```

**Issue**: Low validation coverage
```bash
# Solution: Run recovery system
python universal_validation_recovery.py --database path/to/database.db --auto-detect
```

## Cost Optimization Guidelines

### Per-Chapter Cost Estimates
Based on Proverbs processing experience:
- **Average cost**: ~$0.13 per chapter (including validation)
- **Cost per verse**: ~$0.0076 (less than 1 cent)
- **Full book estimate**: ~$0.13 × chapter_count

### Cost Control Measures
1. **Batched Validation**: Always batch validation (built into pipeline)
2. **Model Selection**: Use cost-effective models for detection
3. **Processing Strategy**: Process in logical chapter groups
4. **Monitoring**: Track costs during processing

## Sample Processing Scripts

### Batch Processing Multiple Books
```python
# process_multiple_books.py
import subprocess
import sys

books_chapters = {
    "Ecclesiastes": list(range(1, 13)),
    "Song_of_Songs": list(range(1, 9)),
    "Job": list(range(1, 43))
}

for book, chapters in books_chapters.items():
    print(f"Processing {book}...")
    for chapter in chapters:
        cmd = ["python", "interactive_parallel_processor.py", book, str(chapter)]
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"  Chapter {chapter}: SUCCESS")
        else:
            print(f"  Chapter {chapter}: FAILED")
            print(f"    Error: {result.stderr}")
```

### Automated Quality Checks
```python
# quality_check.py
def run_quality_checks(database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Check 1: Validation coverage
    cursor.execute("""
        SELECT book, chapter,
               COUNT(*) as total,
               SUM(CASE WHEN validation_response IS NOT NULL THEN 1 ELSE 0 END) as validated
        FROM verses v
        LEFT JOIN figurative_language fl ON v.id = fl.verse_id
        GROUP BY book, chapter
        HAVING total > 0
    """)

    print("Validation Coverage:")
    for book, chapter, total, validated in cursor.fetchall():
        coverage = (validated / total) * 100 if total > 0 else 100
        status = "✅" if coverage >= 95 else "❌"
        print(f"  {status} {book} {chapter}: {coverage:.1f}% ({validated}/{total})")

    # Check 2: Database integrity
    cursor.execute("SELECT COUNT(*) - COUNT(DISTINCT id) FROM verses")
    dup_verses = cursor.fetchone()[0]
    print(f"Duplicate verse IDs: {dup_verses} (should be 0)")

    cursor.execute("""
        SELECT COUNT(*) FROM figurative_language fl
        LEFT JOIN verses v ON fl.verse_id = v.id
        WHERE v.id IS NULL
    """)
    orphaned = cursor.fetchone()[0]
    print(f"Orphaned instances: {orphaned} (should be 0)")

    conn.close()

if __name__ == "__main__":
    run_quality_checks("database/Pentateuch_Psalms_fig_language.db")
```

## Success Criteria

A book addition is considered successful when:

- [ ] All chapters processed without errors
- [ ] Validation coverage >= 95% for all chapters
- [ ] Zero orphaned figurative language instances
- [ ] No duplicate IDs in database
- [ ] Foreign key relationships maintained
- [ ] Database consolidates successfully with main database
- [ ] All backups created and verified

## Support and Troubleshooting

### Getting Help
1. Check `PROVERBS_LESSONS_LEARNED.md` for detailed technical guidance
2. Run health checks: `python universal_validation_recovery.py --health-check`
3. Monitor logs during processing for error patterns
4. Use recovery tools for validation issues

### Emergency Recovery
If processing fails completely:
1. Restore from backup: `cp database.db_backup_TIMESTAMP database.db`
2. Run validation recovery: `python universal_validation_recovery.py --auto-detect`
3. Restart processing with smaller chapter batches

---

**This guide incorporates all lessons learned from processing Proverbs and provides a reliable path for adding additional biblical books to the project.**