#!/usr/bin/env python3
"""
Run complete Deuteronomy analysis with vehicle/tenor classification system
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def run_all_deuteronomy():
    """Run the complete Deuteronomy analysis"""
    print("=== Running Complete Deuteronomy Analysis ===")
    print("FEATURES: Vehicle/Tenor classification system")
    print("FEATURES: Enhanced personification guidelines")
    print("FEATURES: Two-stage metaphor validation")
    print("DATABASE: deuteronomy_complete_final.db")
    print()

    # Initialize pipeline
    pipeline = FigurativeLanguagePipeline(
        'deuteronomy_complete_final.db',
        use_llm_detection=True,
        use_actual_llm=True
    )

    # Process all 34 chapters of Deuteronomy
    total_instances = 0
    successful_chapters = 0

    for chapter_num in range(1, 35):  # Deuteronomy has 34 chapters
        chapter = f'Deuteronomy.{chapter_num}'
        print(f"Processing {chapter}...")

        try:
            results = pipeline.process_verses(chapter)
            instances = results.get('figurative_found', 0)
            total_instances += instances
            successful_chapters += 1
            print(f"SUCCESS {chapter}: {instances} instances found")
        except Exception as e:
            print(f"ERROR {chapter}: {e}")

    print(f"\n=== DEUTERONOMY COMPLETE ANALYSIS SUMMARY ===")
    print(f"Chapters processed: {successful_chapters}/34")
    print(f"Total figurative instances: {total_instances}")

    # Check database for vehicle/tenor population
    import sqlite3
    conn = sqlite3.connect('deuteronomy_complete_final.db')
    cursor = conn.cursor()

    # Count total records
    cursor.execute('SELECT COUNT(*) FROM figurative_language')
    total = cursor.fetchone()[0]

    # Count populated vehicle/tenor records
    cursor.execute('SELECT COUNT(*) FROM figurative_language WHERE vehicle_level_1 IS NOT NULL AND vehicle_level_1 != "" AND tenor_level_1 IS NOT NULL AND tenor_level_1 != ""')
    populated = cursor.fetchone()[0]

    print(f"Records with vehicle/tenor classification: {populated}/{total}")

    if populated > 0:
        classification_rate = (populated / total) * 100
        print(f"Classification success rate: {classification_rate:.1f}%")

    # Show type breakdown
    cursor.execute('SELECT type, COUNT(*) FROM figurative_language GROUP BY type ORDER BY COUNT(*) DESC')
    type_breakdown = cursor.fetchall()
    print(f"\nType breakdown:")
    for fig_type, count in type_breakdown:
        print(f"  {fig_type}: {count}")

    # Show sample vehicle/tenor classifications
    cursor.execute('''
        SELECT figurative_text, vehicle_level_1, vehicle_level_2, tenor_level_1, tenor_level_2, type
        FROM figurative_language
        WHERE vehicle_level_1 IS NOT NULL AND tenor_level_1 IS NOT NULL
        LIMIT 10
    ''')

    samples = cursor.fetchall()
    print(f"\nSample vehicle/tenor classifications:")
    for i, (text, v1, v2, t1, t2, ftype) in enumerate(samples, 1):
        safe_text = text.encode('ascii', 'ignore').decode('ascii') if text else "N/A"
        print(f"{i}. {ftype.upper()}: {safe_text[:50]}...")
        print(f"   Vehicle: {v1} | {v2}")
        print(f"   Tenor: {t1} | {t2}")
        print()

    conn.close()

    print(f"COMPLETE: Deuteronomy analysis finished!")
    print(f"Database: deuteronomy_complete_final.db")

if __name__ == "__main__":
    run_all_deuteronomy()