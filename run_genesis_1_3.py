#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Genesis chapters 1-3 with enhanced personification classification
"""
import sys
import os
from datetime import datetime

# Add the src directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def main():
    """Process Genesis 1-3 with enhanced personification classification"""

    # Create timestamped database name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f"genesis_1_3_personification_enhanced_{timestamp}.db"

    print(f"=== GENESIS 1-3 PROCESSING WITH ENHANCED CLASSIFICATION ===")
    print(f"Database: {db_name}")
    print(f"Started: {datetime.now()}")
    print()

    # Initialize pipeline with enhanced validation
    pipeline = FigurativeLanguagePipeline(
        db_name,
        use_llm_detection=True,
        use_actual_llm=True
    )

    print("Processing Genesis chapters 1-3...")

    # Process Genesis chapters 1-3
    total_results = {
        'total_verses': 0,
        'figurative_found': 0,
        'processing_errors': 0
    }

    for chapter in range(1, 4):  # Genesis 1, 2, 3
        chapter_ref = f"Genesis.{chapter}"
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

    print(f"\n=== GENESIS 1-3 PROCESSING COMPLETE ===")
    print(f"Database: {db_name}")
    print(f"Total verses processed: {total_results['total_verses']}")
    print(f"Total figurative instances: {total_results['figurative_found']}")
    print(f"Processing errors: {total_results['processing_errors']}")
    print(f"Completed: {datetime.now()}")

    # Analysis of results
    print(f"\n=== FIGURATIVE LANGUAGE ANALYSIS ===")
    try:
        from hebrew_figurative_db.database.db_manager import DatabaseManager
        db_manager = DatabaseManager(db_name)

        # Count by type
        cursor = db_manager.connection.cursor()
        cursor.execute("SELECT type, COUNT(*) FROM figurative_language GROUP BY type ORDER BY COUNT(*) DESC")
        type_counts = cursor.fetchall()

        print("Figurative language type distribution:")
        for fig_type, count in type_counts:
            print(f"  {fig_type}: {count}")

        # Show personification examples
        cursor.execute('''
            SELECT v.reference, fl.figurative_text, fl.explanation
            FROM verses v
            JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE fl.type = 'personification'
            ORDER BY v.chapter, v.verse
            LIMIT 5
        ''')
        personifications = cursor.fetchall()

        if personifications:
            print(f"\nPersonification examples found:")
            for ref, text, explanation in personifications:
                print(f"  {ref}: '{text}' - {explanation[:100]}{'...' if len(explanation) > 100 else ''}")
        else:
            print(f"\nNo personifications found in Genesis 1-3")

        # Show metaphor examples
        cursor.execute('''
            SELECT v.reference, fl.figurative_text, fl.explanation
            FROM verses v
            JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE fl.type = 'metaphor'
            ORDER BY v.chapter, v.verse
            LIMIT 5
        ''')
        metaphors = cursor.fetchall()

        if metaphors:
            print(f"\nMetaphor examples found:")
            for ref, text, explanation in metaphors:
                print(f"  {ref}: '{text}' - {explanation[:100]}{'...' if len(explanation) > 100 else ''}")
        else:
            print(f"\nNo metaphors found in Genesis 1-3")

        db_manager.close()

    except Exception as e:
        print(f"Analysis error: {e}")

if __name__ == "__main__":
    main()