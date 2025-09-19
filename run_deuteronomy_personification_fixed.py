#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Reprocess complete Deuteronomy with improved personification classification
"""
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def main():
    """Process complete Deuteronomy with enhanced personification classification"""

    # Create timestamped database name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f"deuteronomy_personification_fixed_{timestamp}.db"

    print(f"=== DEUTERONOMY REPROCESSING WITH PERSONIFICATION FIXES ===")
    print(f"Database: {db_name}")
    print(f"Started: {datetime.now()}")
    print()

    # Initialize pipeline with enhanced validation
    pipeline = FigurativeLanguagePipeline(
        db_name,
        use_llm_detection=True,
        use_actual_llm=True
    )

    print("Processing all Deuteronomy chapters (1-34)...")

    # Process all Deuteronomy chapters
    total_results = {
        'total_verses': 0,
        'figurative_found': 0,
        'processing_errors': 0
    }

    for chapter in range(1, 35):  # Deuteronomy has 34 chapters
        chapter_ref = f"Deuteronomy.{chapter}"
        print(f"\nProcessing {chapter_ref}...")

        try:
            results = pipeline.process_verses(chapter_ref)

            print(f"  Verses processed: {results.get('verses_processed', 0)}")
            print(f"  Figurative instances: {results.get('figurative_found', 0)}")

            # Accumulate totals
            total_results['total_verses'] += results.get('verses_processed', 0)
            total_results['figurative_found'] += results.get('figurative_found', 0)
            total_results['processing_errors'] += results.get('processing_errors', 0)

        except Exception as e:
            print(f"  ERROR processing {chapter_ref}: {e}")
            total_results['processing_errors'] += 1

    print(f"\n=== DEUTERONOMY PROCESSING COMPLETE ===")
    print(f"Database: {db_name}")
    print(f"Total verses processed: {total_results['total_verses']}")
    print(f"Total figurative instances: {total_results['figurative_found']}")
    print(f"Processing errors: {total_results['processing_errors']}")
    print(f"Completed: {datetime.now()}")

    # Quick validation query
    print(f"\n=== PERSONIFICATION VALIDATION ===")
    try:
        from hebrew_figurative_db.database.db_manager import DatabaseManager
        db_manager = DatabaseManager(db_name)

        # Count personifications vs metaphors
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT type, COUNT(*) FROM figurative_language GROUP BY type ORDER BY COUNT(*) DESC")
        type_counts = cursor.fetchall()

        print("Figurative language type distribution:")
        for fig_type, count in type_counts:
            print(f"  {fig_type}: {count}")

        # Check specific verses mentioned by user
        test_verses = ['Deuteronomy 5:9', 'Deuteronomy 31:3', 'Deuteronomy 34:9', 'Deuteronomy 32:24']
        print(f"\nSpecific verse classifications:")
        for verse in test_verses:
            cursor.execute('''
                SELECT fl.type, COUNT(*)
                FROM verses v
                JOIN figurative_language fl ON v.id = fl.verse_id
                WHERE v.reference = ?
                GROUP BY fl.type
            ''', (verse,))
            verse_types = cursor.fetchall()
            types_str = ', '.join([f'{t[0]} ({t[1]})' for t in verse_types])
            print(f"  {verse}: {types_str if types_str else 'No figurative language'}")

        db_manager.close()

    except Exception as e:
        print(f"Validation query error: {e}")

if __name__ == "__main__":
    main()