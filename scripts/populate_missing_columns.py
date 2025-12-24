#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Populate Missing Columns Script

Populates NULL values for columns that may be missing after merging new books
into Biblical_fig_language.db:

Verses table:
- english_text_clean: copied from english_text
- english_text_clean_non_sacred: divine names modifier applied to english_text

Figurative_language table:
- figurative_text_non_sacred: divine names modifier applied to figurative_text

Usage:
    python populate_missing_columns.py --book Jeremiah
    python populate_missing_columns.py --all
"""

import sys
import os
import sqlite3
import io
import argparse

# Force UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add the private module to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'private', 'src'))

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database', 'Biblical_fig_language.db')


def get_books_with_missing_columns(cursor):
    """Get list of books that have NULL values in the target columns"""
    cursor.execute("""
        SELECT DISTINCT book FROM verses
        WHERE english_text_clean IS NULL
           OR english_text_clean_non_sacred IS NULL
        ORDER BY book
    """)
    verse_books = [row[0] for row in cursor.fetchall()]

    cursor.execute("""
        SELECT DISTINCT v.book
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.figurative_text_non_sacred IS NULL
          AND fl.figurative_text IS NOT NULL
        ORDER BY v.book
    """)
    fig_books = [row[0] for row in cursor.fetchall()]

    return list(set(verse_books + fig_books))


def populate_verses_columns(cursor, book_filter=None):
    """Populate english_text_clean and english_text_clean_non_sacred for verses"""
    modifier = HebrewDivineNamesModifier()

    if book_filter:
        query = """
            SELECT id, english_text, book
            FROM verses
            WHERE book = ?
            AND (english_text_clean IS NULL OR english_text_clean_non_sacred IS NULL)
            AND english_text IS NOT NULL
            ORDER BY id
        """
        cursor.execute(query, (book_filter,))
    else:
        query = """
            SELECT id, english_text, book
            FROM verses
            WHERE (english_text_clean IS NULL OR english_text_clean_non_sacred IS NULL)
            AND english_text IS NOT NULL
            ORDER BY id
        """
        cursor.execute(query)

    rows = cursor.fetchall()

    if not rows:
        return 0, {}

    updated_count = 0
    book_counts = {}

    for verse_id, english_text, book in rows:
        english_clean = english_text  # Sefaria already provides clean text
        english_clean_non_sacred = modifier.modify_english_with_hebrew_terms(english_clean)

        cursor.execute("""
            UPDATE verses
            SET english_text_clean = ?, english_text_clean_non_sacred = ?
            WHERE id = ?
        """, (english_clean, english_clean_non_sacred, verse_id))

        updated_count += 1
        book_counts[book] = book_counts.get(book, 0) + 1

    return updated_count, book_counts


def populate_figurative_columns(cursor, book_filter=None):
    """Populate figurative_text_non_sacred for figurative_language"""
    modifier = HebrewDivineNamesModifier()

    if book_filter:
        query = """
            SELECT fl.id, fl.figurative_text, v.book
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE v.book = ?
            AND fl.figurative_text_non_sacred IS NULL
            AND fl.figurative_text IS NOT NULL
            ORDER BY fl.id
        """
        cursor.execute(query, (book_filter,))
    else:
        query = """
            SELECT fl.id, fl.figurative_text, v.book
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE fl.figurative_text_non_sacred IS NULL
            AND fl.figurative_text IS NOT NULL
            ORDER BY fl.id
        """
        cursor.execute(query)

    rows = cursor.fetchall()

    if not rows:
        return 0, {}

    updated_count = 0
    book_counts = {}

    for fig_id, figurative_text, book in rows:
        fig_text_non_sacred = modifier.modify_english_with_hebrew_terms(figurative_text)

        cursor.execute("""
            UPDATE figurative_language
            SET figurative_text_non_sacred = ?
            WHERE id = ?
        """, (fig_text_non_sacred, fig_id))

        updated_count += 1
        book_counts[book] = book_counts.get(book, 0) + 1

    return updated_count, book_counts


def main():
    parser = argparse.ArgumentParser(
        description='Populate missing columns (english_text_clean, english_text_clean_non_sacred, figurative_text_non_sacred)'
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--book', type=str, help='Specific book to process (e.g., Jeremiah)')
    group.add_argument('--all', action='store_true', help='Process all books with NULL values')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be updated without making changes')

    args = parser.parse_args()

    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        sys.exit(1)

    print("=" * 70)
    print("POPULATE MISSING COLUMNS")
    print("=" * 70)
    print(f"Database: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Show which books have missing data
    books_with_missing = get_books_with_missing_columns(cursor)
    if books_with_missing:
        print(f"Books with missing column data: {', '.join(books_with_missing)}")
    else:
        print("No books have missing column data.")
        conn.close()
        return

    book_filter = args.book if args.book else None

    if book_filter:
        print(f"Target: {book_filter}")
        if book_filter not in books_with_missing:
            print(f"Note: {book_filter} has no missing column data.")
            conn.close()
            return
    else:
        print("Target: All books with NULL values")

    if args.dry_run:
        print("\n[DRY RUN - No changes will be made]")

    # Process verses table
    print("\n" + "-" * 70)
    print("VERSES TABLE: english_text_clean, english_text_clean_non_sacred")
    print("-" * 70)

    verse_count, verse_books = populate_verses_columns(cursor, book_filter)

    if verse_count > 0:
        print(f"Updated {verse_count} verses:")
        for book, count in sorted(verse_books.items()):
            print(f"  - {book}: {count} verses")
    else:
        print("No verses needed updating.")

    # Process figurative_language table
    print("\n" + "-" * 70)
    print("FIGURATIVE_LANGUAGE TABLE: figurative_text_non_sacred")
    print("-" * 70)

    fig_count, fig_books = populate_figurative_columns(cursor, book_filter)

    if fig_count > 0:
        print(f"Updated {fig_count} figurative instances:")
        for book, count in sorted(fig_books.items()):
            print(f"  - {book}: {count} instances")
    else:
        print("No figurative instances needed updating.")

    # Commit or rollback based on dry-run
    if args.dry_run:
        conn.rollback()
        print("\n[DRY RUN - Changes rolled back]")
    else:
        conn.commit()
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total verses updated: {verse_count}")
        print(f"Total figurative instances updated: {fig_count}")
        print("Database updated successfully!")

    conn.close()


if __name__ == '__main__':
    main()
