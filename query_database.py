#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive SQLite query interface for the figurative language database
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import sqlite3
import pandas as pd

def query_database(query, db_path='performance_test.db'):
    """Execute a SQL query and display results nicely"""
    try:
        conn = sqlite3.connect(db_path)

        # Use pandas for nice formatting
        df = pd.read_sql_query(query, conn)

        print(f"Query: {query}")
        print(f"Results: {len(df)} rows")
        print("=" * 80)

        if len(df) > 0:
            # Display with better formatting
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            pd.set_option('display.max_colwidth', 100)
            print(df.to_string(index=False))
        else:
            print("No results found.")

        conn.close()
        return df

    except Exception as e:
        print(f"Error executing query: {e}")
        return None

def interactive_mode():
    """Interactive SQL query mode"""
    print("=== Interactive SQLite Query Interface ===")
    print("Database: performance_test.db")
    print("Type 'exit' to quit, 'tables' to see all tables")
    print("Example queries:")
    print("  SELECT * FROM verses LIMIT 5")
    print("  SELECT * FROM figurative_language WHERE type = 'metaphor'")
    print()

    while True:
        try:
            query = input("SQL> ").strip()

            if query.lower() in ['exit', 'quit']:
                break

            if query.lower() == 'tables':
                query = "SELECT name FROM sqlite_master WHERE type='table'"

            if query.lower() == 'schema':
                print("\nTable schemas:")
                query_database("SELECT sql FROM sqlite_master WHERE type='table'")
                continue

            if query:
                query_database(query)
                print()

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except EOFError:
            break

# Pre-defined useful queries
def common_queries():
    """Run some common useful queries"""
    print("=== Common Queries ===\n")

    queries = [
        ("All verses with figurative language", """
            SELECT v.reference, v.english_text, fl.type, fl.confidence
            FROM verses v
            JOIN figurative_language fl ON v.id = fl.verse_id
            ORDER BY v.chapter, v.verse
        """),

        ("Count by figurative type", """
            SELECT type, COUNT(*) as count
            FROM figurative_language
            GROUP BY type
            ORDER BY count DESC
        """),

        ("High confidence metaphors and similes", """
            SELECT v.reference, fl.type, fl.confidence, fl.text_snippet
            FROM verses v
            JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE fl.type IN ('metaphor', 'simile') AND fl.confidence > 0.85
        """),

        ("Verses by chapter with figurative count", """
            SELECT v.chapter, COUNT(v.id) as total_verses, COUNT(fl.id) as figurative_verses
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            GROUP BY v.chapter
        """)
    ]

    for name, query in queries:
        print(f"\n--- {name} ---")
        query_database(query)
        print()

if __name__ == "__main__":
    # Check if pandas is available
    try:
        import pandas as pd
    except ImportError:
        print("Installing pandas for better formatting...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pandas"])
        import pandas as pd

    if len(sys.argv) > 1:
        # Run specific query from command line
        query = " ".join(sys.argv[1:])
        query_database(query)
    else:
        # Show some common queries first
        common_queries()

        # Then enter interactive mode
        print("\n" + "="*60)
        interactive_mode()