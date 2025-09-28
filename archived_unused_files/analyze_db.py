#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analyze the Deuteronomy database for Sankey visualization planning
"""
import sqlite3
import pandas as pd
from collections import Counter

def analyze_database():
    """Analyze the database structure and content"""
    db_path = "deuteronomy_all_c_all_v_20250922_0959.db"

    try:
        conn = sqlite3.connect(db_path)

        # Get schema information
        print("=== DATABASE SCHEMA ===")
        cursor = conn.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='figurative_language'")
        schema = cursor.fetchone()
        if schema:
            print(schema[0])

        # Get sample data
        print("\n=== SAMPLE DATA ===")
        query = """
        SELECT
            fl.target_level_1, fl.target_specific,
            fl.vehicle_level_1, fl.vehicle_specific,
            fl.figurative_text, fl.figurative_text_in_hebrew,
            fl.final_figurative_language, fl.final_simile, fl.final_metaphor, fl.final_personification,
            fl.final_idiom, fl.final_hyperbole, fl.final_metonymy, fl.final_other,
            v.llm_deliberation, v.hebrew_text, v.english_text, v.reference
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE fl.final_figurative_language = 'yes'
        LIMIT 10
        """

        df = pd.read_sql_query(query, conn)
        print(f"Sample of {len(df)} records:")
        for idx, row in df.iterrows():
            print(f"\nRecord {idx + 1}:")
            print(f"  Reference: {row['reference']}")
            print(f"  Target: {row['target_specific']} ({row['target_level_1']})")
            print(f"  Vehicle: {row['vehicle_specific']} ({row['vehicle_level_1']})")
            print(f"  Figurative Text: {row['figurative_text']}")
            # Handle Hebrew text safely
            try:
                hebrew_fig = row['figurative_text_in_hebrew'] or 'N/A'
                print(f"  Hebrew Text: {hebrew_fig}")
            except UnicodeEncodeError:
                print(f"  Hebrew Text: [Hebrew text present but cannot display]")
            print(f"  Types: ", end="")
            types = []
            for col in ['final_simile', 'final_metaphor', 'final_personification', 'final_idiom', 'final_hyperbole', 'final_metonymy', 'final_other']:
                if row[col] == 'yes':
                    types.append(col.replace('final_', ''))
            print(", ".join(types) if types else "none")
            if row['llm_deliberation']:
                try:
                    delib = row['llm_deliberation'][:200] + "..." if len(row['llm_deliberation']) > 200 else row['llm_deliberation']
                    print(f"  Deliberation: {delib}")
                except UnicodeEncodeError:
                    print(f"  Deliberation: [Contains Hebrew text that cannot display]")

        # Get statistics
        print("\n=== DATA STATISTICS ===")

        # Total figurative language instances
        total_query = "SELECT COUNT(*) FROM figurative_language WHERE final_figurative_language = 'yes'"
        total_count = conn.execute(total_query).fetchone()[0]
        print(f"Total validated figurative language instances: {total_count}")

        # Target level 1 distribution
        target_query = """
        SELECT target_level_1, COUNT(*) as count
        FROM figurative_language
        WHERE final_figurative_language = 'yes' AND target_level_1 IS NOT NULL
        GROUP BY target_level_1
        ORDER BY count DESC
        """
        target_df = pd.read_sql_query(target_query, conn)
        print(f"\nTarget Level 1 Distribution:")
        for _, row in target_df.iterrows():
            print(f"  {row['target_level_1']}: {row['count']}")

        # Vehicle level 1 distribution
        vehicle_query = """
        SELECT vehicle_level_1, COUNT(*) as count
        FROM figurative_language
        WHERE final_figurative_language = 'yes' AND vehicle_level_1 IS NOT NULL
        GROUP BY vehicle_level_1
        ORDER BY count DESC
        """
        vehicle_df = pd.read_sql_query(vehicle_query, conn)
        print(f"\nVehicle Level 1 Distribution:")
        for _, row in vehicle_df.iterrows():
            print(f"  {row['vehicle_level_1']}: {row['count']}")

        # Target specific examples
        target_specific_query = """
        SELECT target_specific, COUNT(*) as count
        FROM figurative_language
        WHERE final_figurative_language = 'yes' AND target_specific IS NOT NULL
        GROUP BY target_specific
        ORDER BY count DESC
        LIMIT 20
        """
        target_specific_df = pd.read_sql_query(target_specific_query, conn)
        print(f"\nTop 20 Target Specific:")
        for _, row in target_specific_df.iterrows():
            print(f"  {row['target_specific']}: {row['count']}")

        # Vehicle specific examples
        vehicle_specific_query = """
        SELECT vehicle_specific, COUNT(*) as count
        FROM figurative_language
        WHERE final_figurative_language = 'yes' AND vehicle_specific IS NOT NULL
        GROUP BY vehicle_specific
        ORDER BY count DESC
        LIMIT 20
        """
        vehicle_specific_df = pd.read_sql_query(vehicle_specific_query, conn)
        print(f"\nTop 20 Vehicle Specific:")
        for _, row in vehicle_specific_df.iterrows():
            print(f"  {row['vehicle_specific']}: {row['count']}")

        # Type distribution
        type_query = """
        SELECT
            SUM(CASE WHEN final_simile = 'yes' THEN 1 ELSE 0 END) as simile,
            SUM(CASE WHEN final_metaphor = 'yes' THEN 1 ELSE 0 END) as metaphor,
            SUM(CASE WHEN final_personification = 'yes' THEN 1 ELSE 0 END) as personification,
            SUM(CASE WHEN final_idiom = 'yes' THEN 1 ELSE 0 END) as idiom,
            SUM(CASE WHEN final_hyperbole = 'yes' THEN 1 ELSE 0 END) as hyperbole,
            SUM(CASE WHEN final_metonymy = 'yes' THEN 1 ELSE 0 END) as metonymy,
            SUM(CASE WHEN final_other = 'yes' THEN 1 ELSE 0 END) as other
        FROM figurative_language
        WHERE final_figurative_language = 'yes'
        """
        type_df = pd.read_sql_query(type_query, conn)
        print(f"\nFigurative Language Type Distribution:")
        for col in type_df.columns:
            print(f"  {col}: {type_df[col].iloc[0]}")

        conn.close()
        return True

    except Exception as e:
        print(f"Error analyzing database: {e}")
        return False

if __name__ == "__main__":
    analyze_database()