#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run the 200 random verses through the LLM pipeline for validation
"""
import json
import time
from typing import List, Dict
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def load_validation_set(filename: str = "validation_set_200_verses.json") -> List[str]:
    """Load the validation verse references"""

    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        references = data.get('references', [])
        print(f"Loaded {len(references)} verse references from {filename}")

        return references

    except FileNotFoundError:
        print(f"Error: {filename} not found. Run generate_random_validation_set.py first.")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        return []

def process_validation_verses(verse_refs: List[str], output_db: str = "validation_llm_results.db") -> Dict:
    """Process all validation verses through LLM pipeline"""

    print(f"=== PROCESSING {len(verse_refs)} VALIDATION VERSES ===")

    # Initialize pipeline with LLM detection
    pipeline = FigurativeLanguagePipeline(
        db_path=output_db,
        use_llm_detection=True,
        use_actual_llm=True
    )

    start_time = time.time()
    total_processed = 0
    total_figurative_found = 0
    total_errors = 0

    # Process verses in small batches to avoid overwhelming the API
    batch_size = 10
    batches = [verse_refs[i:i + batch_size] for i in range(0, len(verse_refs), batch_size)]

    print(f"Processing {len(batches)} batches of {batch_size} verses each...")

    for batch_num, batch in enumerate(batches, 1):
        print(f"\n--- BATCH {batch_num}/{len(batches)} ---")

        for verse_ref in batch:
            try:
                print(f"Processing: {verse_ref}")

                # Process single verse
                result = pipeline.process_verses(verse_ref, drop_existing=(batch_num == 1 and verse_ref == batch[0]))

                total_processed += result.get('processed_verses', 0)
                total_figurative_found += result.get('figurative_found', 0)
                total_errors += result.get('processing_errors', 0)

                # Small delay to be respectful to API
                time.sleep(0.1)

            except Exception as e:
                print(f"  ERROR processing {verse_ref}: {e}")
                total_errors += 1

        # Longer pause between batches
        if batch_num < len(batches):
            print(f"  Batch {batch_num} complete. Pausing...")
            time.sleep(2)

    total_time = time.time() - start_time

    # Final statistics
    results = {
        'total_verses_attempted': len(verse_refs),
        'total_processed': total_processed,
        'total_figurative_found': total_figurative_found,
        'total_errors': total_errors,
        'processing_time': total_time,
        'verses_per_second': total_processed / total_time if total_time > 0 else 0,
        'detection_rate': (total_figurative_found / total_processed * 100) if total_processed > 0 else 0,
        'error_rate': (total_errors / len(verse_refs) * 100) if len(verse_refs) > 0 else 0,
        'output_database': output_db
    }

    return results

def print_validation_summary(results: Dict):
    """Print summary of validation run"""

    print(f"\n{'='*60}")
    print(f"🎯 VALIDATION RUN COMPLETE")
    print(f"{'='*60}")

    print(f"Verses attempted: {results['total_verses_attempted']}")
    print(f"Verses processed: {results['total_processed']}")
    print(f"Figurative instances found: {results['total_figurative_found']}")
    print(f"Processing errors: {results['total_errors']}")
    print(f"")
    print(f"Detection rate: {results['detection_rate']:.1f}%")
    print(f"Error rate: {results['error_rate']:.1f}%")
    print(f"Processing speed: {results['verses_per_second']:.2f} verses/second")
    print(f"Total time: {results['processing_time']:.1f} seconds")
    print(f"")
    print(f"📁 Results saved to: {results['output_database']}")

    if results['error_rate'] < 5:
        print(f"✅ Validation run completed successfully!")
    else:
        print(f"⚠️ Validation run completed with warnings (high error rate)")

def main():
    """Main validation script"""

    print("=== LLM VALIDATION SET PROCESSING ===")

    # Load validation set
    verse_refs = load_validation_set()

    if not verse_refs:
        print("No verses to process. Exiting.")
        return

    # Show sample of what will be processed
    print(f"\nSample verses to be processed:")
    for i, ref in enumerate(verse_refs[:5]):
        print(f"  {i+1}. {ref}")
    print(f"  ... and {len(verse_refs) - 5} more")

    # Confirm processing
    print(f"\nAbout to process {len(verse_refs)} verses with real LLM analysis.")
    print(f"This will make ~{len(verse_refs)} API calls to Gemini.")
    print(f"Estimated time: {len(verse_refs) * 2 / 60:.1f} minutes")

    # Process all verses
    results = process_validation_verses(verse_refs)

    # Print summary
    print_validation_summary(results)

    # Instructions for manual review
    print(f"\n📋 NEXT STEPS FOR MANUAL REVIEW:")
    print(f"1. Open the database: {results['output_database']}")
    print(f"2. Use query_non_figurative_verses.sql to find verses WITHOUT figurative language")
    print(f"3. Manually review a sample of both detected and non-detected verses")
    print(f"4. Look for patterns in false positives and false negatives")

    return results

if __name__ == "__main__":
    main()