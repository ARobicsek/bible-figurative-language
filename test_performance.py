#!/usr/bin/env python3
"""
Test script to verify database performance improvements after adding indexes
"""

import sqlite3
import time

DB_PATH = r'C:\Users\ariro\OneDrive\Documents\Bible\database\Pentateuch_Psalms_fig_language.db'

def get_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA cache_size = -8000")  # 8MB cache
    conn.execute("PRAGMA temp_store = MEMORY")
    conn.execute("PRAGMA mmap_size = 30000000")  # 30MB memory-mapped I/O
    return conn

def test_query(name, query, params=()):
    """Run a query and measure performance"""
    conn = get_connection()
    cursor = conn.cursor()

    start = time.time()
    cursor.execute(query, params)
    results = cursor.fetchall()
    elapsed = time.time() - start

    print(f"{name}: {len(results)} results in {elapsed:.3f}s")
    conn.close()
    return elapsed

print("=" * 70)
print("DATABASE PERFORMANCE TEST - After Index Optimization")
print("=" * 70)

# Test 1: Metadata search on vehicle (common use case)
print("\n1. Vehicle metadata search (LIKE query):")
test_query(
    "Search for 'lion' in vehicle",
    "SELECT * FROM figurative_language WHERE vehicle LIKE ?",
    ('%lion%',)
)

# Test 2: Target search
print("\n2. Target metadata search:")
test_query(
    "Search for 'God' in target",
    "SELECT * FROM figurative_language WHERE target LIKE ?",
    ('%God%',)
)

# Test 3: Book filter
print("\n3. Book filtering:")
test_query(
    "All verses in Genesis",
    "SELECT * FROM verses WHERE book = ?",
    ('Genesis',)
)

# Test 4: Complex JOIN query (typical frontend query)
print("\n4. Complex JOIN query (verses + figurative language):")
test_query(
    "Genesis verses with metaphors",
    """
    SELECT v.*, fl.*
    FROM verses v
    LEFT JOIN figurative_language fl ON v.id = fl.verse_id
    WHERE v.book = ? AND fl.final_metaphor = 'yes'
    """,
    ('Genesis',)
)

# Test 5: Multi-term metadata search (semicolon-separated)
print("\n5. Multi-term metadata search:")
test_query(
    "Search for 'walk' OR 'leap' in vehicle",
    """
    SELECT * FROM figurative_language
    WHERE vehicle LIKE ? OR vehicle LIKE ?
    """,
    ('%walk%', '%leap%')
)

# Test 6: Verify indexes exist
print("\n6. Verifying indexes:")
conn = get_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT name FROM sqlite_master
    WHERE type='index'
    AND (name LIKE 'idx_fl_%' OR name LIKE 'idx_verses_%')
    ORDER BY name
""")
indexes = cursor.fetchall()
print(f"Found {len(indexes)} performance indexes:")
for idx in indexes:
    print(f"  [OK] {idx[0]}")
conn.close()

print("\n" + "=" * 70)
print("Performance test complete!")
print("=" * 70)
print("\nExpected results with indexes:")
print("  - Metadata searches: < 0.1s (was 1-5s without indexes)")
print("  - Book filtering: < 0.05s")
print("  - Complex JOINs: < 0.2s (was 5-20s without indexes)")
print("\nIf queries are still slow, consider:")
print("  1. Analyzing query plans with EXPLAIN QUERY PLAN")
print("  2. Adding composite indexes for common filter combinations")
print("  3. Migrating to PostgreSQL/Supabase for better scalability")
