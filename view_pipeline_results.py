#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
View Pipeline Results - Show what was detected in Genesis 1:1-10
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import json

def view_pipeline_results():
    """Display the complete results from our pipeline test"""
    print("=== Pipeline Results for Genesis 1:1-10 ===")

    try:
        conn = sqlite3.connect('figurative_language_pipeline.db')
        cursor = conn.cursor()

        # Get all verses with their figurative language findings
        cursor.execute('''
            SELECT
                v.reference,
                v.hebrew_text,
                v.english_text,
                v.word_count,
                fl.type,
                fl.confidence,
                fl.text_snippet,
                fl.pattern_matched,
                fl.ai_analysis
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            ORDER BY v.chapter, v.verse
        ''')

        results = cursor.fetchall()

        if not results:
            print("No results found. Make sure the pipeline has been run.")
            return

        current_verse = None

        for row in results:
            reference, hebrew, english, word_count, fig_type, confidence, snippet, pattern, analysis = row

            if reference != current_verse:
                current_verse = reference
                print(f"\n{'='*60}")
                print(f"📖 {reference}")
                print(f"{'='*60}")
                print(f"Hebrew: {hebrew}")
                print(f"English: {english}")
                print(f"Word count: {word_count}")

            if fig_type:
                print(f"\n🎭 FIGURATIVE LANGUAGE DETECTED:")
                print(f"   Type: {fig_type.upper()}")
                print(f"   Confidence: {confidence:.2f}")
                print(f"   Text: \"{snippet}\"")
                print(f"   Pattern: {pattern}")
                print(f"   Analysis: {analysis}")
            else:
                print(f"\n📝 No figurative language detected")

        # Summary statistics
        cursor.execute('SELECT COUNT(*) FROM verses')
        total_verses = cursor.fetchone()[0]

        cursor.execute('SELECT COUNT(*) FROM figurative_language')
        total_figurative = cursor.fetchone()[0]

        cursor.execute('SELECT type, COUNT(*) FROM figurative_language GROUP BY type')
        type_counts = cursor.fetchall()

        cursor.execute('SELECT AVG(confidence) FROM figurative_language')
        avg_confidence = cursor.fetchone()[0]

        print(f"\n{'='*60}")
        print(f"📊 SUMMARY STATISTICS")
        print(f"{'='*60}")
        print(f"Total verses processed: {total_verses}")
        print(f"Figurative language instances: {total_figurative}")
        print(f"Detection rate: {(total_figurative/total_verses)*100:.1f}%")
        print(f"Average confidence: {avg_confidence:.2f}")

        print(f"\nBreakdown by type:")
        for fig_type, count in type_counts:
            print(f"  {fig_type}: {count}")

        conn.close()

    except Exception as e:
        print(f"Error reading results: {e}")

if __name__ == "__main__":
    view_pipeline_results()