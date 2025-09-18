#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze database schema and performance for optimization opportunities
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hebrew_figurative_db.database import DatabaseManager
import sqlite3
import time


def analyze_database():
    """Analyze current database for optimization opportunities"""
    print("=== Database Analysis & Optimization ===")

    with DatabaseManager('performance_test.db') as db:
        # 1. Data distribution analysis
        print(f"\n📊 Data Distribution Analysis:")

        stats = db.get_statistics()
        print(f"  Total verses: {stats['total_verses']}")
        print(f"  Total figurative instances: {stats['total_figurative']}")
        print(f"  Detection rate: {stats['detection_rate']:.1f}%")

        print(f"\n  Type distribution:")
        for fig_type, count in stats['type_breakdown'].items():
            percentage = (count / stats['total_figurative'] * 100)
            print(f"    {fig_type}: {count} ({percentage:.1f}%)")

        # 2. Query performance testing
        print(f"\n⚡ Query Performance Testing:")

        # Test common query patterns
        queries = [
            ("Simple verse lookup", "SELECT * FROM verses WHERE reference = 'Genesis 1:1'"),
            ("Figurative by type", "SELECT COUNT(*) FROM figurative_language WHERE type = 'personification'"),
            ("Join query", """
                SELECT v.reference, fl.type, fl.confidence
                FROM verses v
                JOIN figurative_language fl ON v.id = fl.verse_id
                WHERE fl.confidence > 0.8
            """),
            ("Complex aggregation", """
                SELECT v.book, v.chapter, COUNT(fl.id) as fig_count
                FROM verses v
                LEFT JOIN figurative_language fl ON v.id = fl.verse_id
                GROUP BY v.book, v.chapter
                ORDER BY fig_count DESC
            """),
            ("Pattern search", """
                SELECT v.reference, fl.text_snippet
                FROM verses v
                JOIN figurative_language fl ON v.id = fl.verse_id
                WHERE fl.pattern_matched LIKE '%god%'
            """)
        ]

        for query_name, query in queries:
            times = []
            for _ in range(10):  # Run each query 10 times
                start = time.time()
                db.cursor.execute(query)
                results = db.cursor.fetchall()
                end = time.time()
                times.append(end - start)

            avg_time = sum(times) / len(times)
            print(f"  {query_name}: {avg_time*1000:.2f}ms avg (n={len(results)})")

        # 3. Index analysis
        print(f"\n🔍 Index Analysis:")

        # Check existing indexes
        db.cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        existing_indexes = [row[0] for row in db.cursor.fetchall()]
        print(f"  Existing indexes: {len(existing_indexes)}")
        for idx in existing_indexes:
            if not idx.startswith('sqlite_'):  # Skip auto-generated indexes
                print(f"    - {idx}")

        # Suggest optimizations
        print(f"\n💡 Optimization Recommendations:")

        # 4. Storage analysis
        db.cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = db.cursor.fetchone()[0]

        db.cursor.execute("SELECT COUNT(*) FROM figurative_language")
        fig_count = db.cursor.fetchone()[0]

        # Calculate average text lengths
        db.cursor.execute("SELECT AVG(LENGTH(hebrew_text)), AVG(LENGTH(english_text)) FROM verses")
        avg_hebrew_len, avg_english_len = db.cursor.fetchone()

        db.cursor.execute("SELECT AVG(LENGTH(text_snippet)), AVG(LENGTH(ai_analysis)) FROM figurative_language")
        avg_snippet_len, avg_analysis_len = db.cursor.fetchone()

        print(f"\n📏 Storage Analysis:")
        print(f"  Average Hebrew text length: {avg_hebrew_len:.1f} chars")
        print(f"  Average English text length: {avg_english_len:.1f} chars")
        print(f"  Average snippet length: {avg_snippet_len:.1f} chars")
        print(f"  Average analysis length: {avg_analysis_len:.1f} chars")

        # 5. Schema optimization suggestions
        print(f"\n🔧 Schema Optimization Suggestions:")

        suggestions = []

        # Check for potential improvements
        if verse_count > 100:  # For larger datasets
            suggestions.append("Add index on (book, chapter, verse) for faster verse lookups")

        if fig_count > 50:
            suggestions.append("Add index on (type, confidence) for figurative language queries")

        if avg_analysis_len > 100:
            suggestions.append("Consider shortening ai_analysis field or moving to separate table")

        # Check confidence distribution
        db.cursor.execute("SELECT MIN(confidence), MAX(confidence), COUNT(DISTINCT confidence) FROM figurative_language")
        min_conf, max_conf, unique_conf = db.cursor.fetchone()

        if unique_conf < 10:
            suggestions.append(f"Confidence values have low diversity ({unique_conf} unique values)")

        if not suggestions:
            suggestions.append("✅ Current schema is well-optimized for current dataset size")

        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion}")

        return {
            'verse_count': verse_count,
            'figurative_count': fig_count,
            'avg_query_time': sum(times) / len(times),
            'suggestions': suggestions
        }


def implement_optimizations():
    """Implement recommended database optimizations"""
    print(f"\n🛠️ Implementing Database Optimizations:")

    with DatabaseManager('performance_test.db') as db:
        # Add recommended indexes
        optimizations = [
            ("Verse lookup index", "CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses(book, chapter, verse)"),
            ("Figurative type index", "CREATE INDEX IF NOT EXISTS idx_figurative_type_conf ON figurative_language(type, confidence)"),
            ("Pattern search index", "CREATE INDEX IF NOT EXISTS idx_figurative_pattern ON figurative_language(pattern_matched)"),
        ]

        for opt_name, query in optimizations:
            try:
                start = time.time()
                db.cursor.execute(query)
                end = time.time()
                print(f"  ✅ {opt_name}: {(end-start)*1000:.2f}ms")
            except Exception as e:
                print(f"  ❌ {opt_name}: {e}")

        db.commit()

        # Test performance improvement
        print(f"\n📈 Performance Test After Optimization:")
        test_query = """
            SELECT v.reference, fl.type, fl.confidence
            FROM verses v
            JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE fl.type = 'personification' AND fl.confidence > 0.8
        """

        times = []
        for _ in range(10):
            start = time.time()
            db.cursor.execute(test_query)
            results = db.cursor.fetchall()
            end = time.time()
            times.append(end - start)

        avg_time = sum(times) / len(times)
        print(f"  Optimized query time: {avg_time*1000:.2f}ms avg (n={len(results)})")


if __name__ == "__main__":
    analysis_results = analyze_database()
    implement_optimizations()