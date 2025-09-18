#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View results from Genesis 1-3 processing (80 verses)
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3

def view_genesis_1_3_results():
    """Display results from Genesis 1-3 processing"""
    print("=== Genesis 1-3 Processing Results (80 Verses) ===\n")

    try:
        conn = sqlite3.connect('performance_test.db')
        cursor = conn.cursor()

        # Get all verses with their figurative language findings
        cursor.execute('''
            SELECT
                v.reference,
                v.english_text,
                fl.type,
                fl.confidence,
                fl.text_snippet,
                fl.pattern_matched
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            ORDER BY v.book, v.chapter, v.verse
        ''')

        results = cursor.fetchall()

        if not results:
            print("No results found. Make sure the performance test has been run.")
            return

        current_chapter = None
        chapter_figurative_count = 0
        total_figurative = 0

        for row in results:
            reference, english, fig_type, confidence, snippet, pattern = row

            # Extract chapter info
            chapter = reference.split(':')[0]

            # Chapter header
            if chapter != current_chapter:
                if current_chapter:
                    print(f"\n📊 {current_chapter} Summary: {chapter_figurative_count} figurative instances\n")

                current_chapter = chapter
                chapter_figurative_count = 0
                print(f"{'='*60}")
                print(f"📖 {chapter}")
                print(f"{'='*60}")

            # Display verse
            print(f"\n{reference}")
            print(f"Text: {english}")

            if fig_type:
                print(f"🎭 FIGURATIVE: {fig_type.upper()} (confidence: {confidence:.2f})")
                print(f"   Snippet: \"{snippet}\"")
                print(f"   Pattern: {pattern}")
                chapter_figurative_count += 1
                total_figurative += 1
            else:
                print("📝 No figurative language detected")

        # Final chapter summary
        if current_chapter:
            print(f"\n📊 {current_chapter} Summary: {chapter_figurative_count} figurative instances\n")

        # Overall statistics
        cursor.execute('SELECT COUNT(*) FROM verses')
        total_verses = cursor.fetchone()[0]

        cursor.execute('SELECT type, COUNT(*) FROM figurative_language GROUP BY type')
        type_counts = cursor.fetchall()

        print(f"{'='*60}")
        print(f"📊 OVERALL STATISTICS")
        print(f"{'='*60}")
        print(f"Total verses processed: {total_verses}")
        print(f"Total figurative instances: {total_figurative}")
        print(f"Detection rate: {(total_figurative/total_verses)*100:.1f}%")

        print(f"\nBreakdown by type:")
        for fig_type, count in type_counts:
            percentage = (count / total_figurative * 100) if total_figurative > 0 else 0
            print(f"  {fig_type}: {count} ({percentage:.1f}%)")

        conn.close()

    except Exception as e:
        print(f"Error reading results: {e}")

if __name__ == "__main__":
    view_genesis_1_3_results()