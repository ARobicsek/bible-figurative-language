#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process all of Deuteronomy with the improved pipeline system
Enhanced validator + strengthened initial annotator to reduce false positives
"""
import json
import time
from datetime import datetime
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def process_complete_deuteronomy():
    """Process all 34 chapters of Deuteronomy with improved system"""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_db = f"deuteronomy_improved_system_{timestamp}.db"

    print("=" * 70)
    print("DEUTERONOMY REPROCESSING WITH IMPROVED SYSTEM")
    print("=" * 70)
    print(f"Enhanced Features:")
    print(f"[DONE] Strengthened validator with comprehensive rejection criteria")
    print(f"[DONE] Enhanced initial annotator to reduce false positives")
    print(f"[DONE] Simile validation (historical precedent rejection)")
    print(f"[DONE] Metaphor vs personification reclassification")
    print(f"[DONE] Standard biblical language recognition")
    print(f"[DONE] ANE context consideration")
    print()
    print(f"Output database: {output_db}")
    print(f"Processing started: {datetime.now()}")
    print("=" * 70)

    # Initialize pipeline with enhanced system
    pipeline = FigurativeLanguagePipeline(
        db_path=output_db,
        use_llm_detection=True,
        use_actual_llm=True
    )

    # Process all 34 chapters of Deuteronomy
    start_time = time.time()

    try:
        # Process all 34 chapters individually
        all_results = {}
        total_verses = 0
        total_figurative = 0

        for chapter in range(1, 35):  # Chapters 1-34
            chapter_ref = f"Deuteronomy.{chapter}"
            print(f"\nProcessing {chapter_ref}...")

            try:
                chapter_results = pipeline.process_verses(chapter_ref)
                all_results[chapter_ref] = chapter_results

                if chapter_results:
                    total_verses += chapter_results.get('verses_processed', 0)
                    total_figurative += chapter_results.get('figurative_found', 0)

                print(f"  Completed: {chapter_results.get('verses_processed', 0)} verses, {chapter_results.get('figurative_found', 0)} figurative")

            except Exception as e:
                print(f"  ERROR in {chapter_ref}: {e}")
                all_results[chapter_ref] = {"error": str(e)}

        results = {
            "chapters_processed": len(all_results),
            "total_verses_processed": total_verses,
            "total_figurative_found": total_figurative,
            "chapter_details": all_results
        }

        processing_time = time.time() - start_time

        # Generate comprehensive summary
        summary = {
            "database_file": output_db,
            "processing_started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_processing_time": processing_time,
            "system_improvements": [
                "Enhanced validator with standard biblical language rejection",
                "Strengthened initial annotator with false positive prevention",
                "Simile validation for historical precedent filtering",
                "Metaphor vs personification reclassification capability",
                "ANE context consideration for literal vs figurative determination",
                "Comprehensive divine action/attribute recognition",
                "Theophanic manifestation literal classification",
                "Quantitative description literal classification"
            ],
            "results": results
        }

        # Save processing summary
        summary_file = f"deuteronomy_improved_system_summary_{timestamp}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 70)
        print("PROCESSING COMPLETE")
        print("=" * 70)
        print(f"Database: {output_db}")
        print(f"Summary: {summary_file}")
        print(f"Total time: {processing_time/60:.1f} minutes")
        print(f"Results: {results}")
        print("=" * 70)

        return summary

    except Exception as e:
        error_time = time.time() - start_time
        print(f"\nERROR after {error_time/60:.1f} minutes: {e}")
        print(f"Partial results may be available in: {output_db}")
        return None

if __name__ == "__main__":
    process_complete_deuteronomy()