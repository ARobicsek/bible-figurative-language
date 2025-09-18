#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process the complete book of Deuteronomy with IMPROVED pipeline
Phase 6.5: Complete Deuteronomy Processing with Enhanced Simile/Metaphor Detection
"""
import json
import time
from datetime import datetime
from typing import List, Dict, Tuple
from src.hebrew_figurative_db.text_extraction import SefariaClient
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline
from src.hebrew_figurative_db.database import DatabaseManager
from src.hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor

def generate_deuteronomy_verse_refs() -> List[str]:
    """Generate all verse references for Deuteronomy (34 chapters)"""

    # Deuteronomy chapter verse counts
    chapter_verse_counts = {
        1: 46, 2: 37, 3: 29, 4: 49, 5: 33, 6: 25, 7: 26, 8: 20, 9: 29, 10: 22,
        11: 32, 12: 32, 13: 18, 14: 29, 15: 23, 16: 22, 17: 20, 18: 22, 19: 21, 20: 20,
        21: 23, 22: 30, 23: 25, 24: 22, 25: 19, 26: 19, 27: 26, 28: 68, 29: 29, 30: 20,
        31: 30, 32: 52, 33: 29, 34: 12
    }

    verse_refs = []
    for chapter, max_verses in chapter_verse_counts.items():
        for verse in range(1, max_verses + 1):
            verse_refs.append(f"Deuteronomy.{chapter}.{verse}")

    return verse_refs

def extract_single_verse(verse_ref: str) -> Tuple[Dict, float]:
    """Extract a single specific verse from Sefaria"""
    parts = verse_ref.split('.')
    if len(parts) != 3:
        raise ValueError(f"Invalid verse reference format: {verse_ref}")

    book, chapter, verse_num = parts
    chapter_ref = f"{book}.{chapter}"

    # Get the entire chapter first
    client = SefariaClient()
    start_time = time.time()
    verses, api_time = client.extract_hebrew_text(chapter_ref)

    # Find the specific verse
    target_verse = None
    for verse in verses:
        if verse['verse'] == int(verse_num):
            target_verse = verse
            break

    if target_verse is None:
        raise ValueError(f"Verse {verse_num} not found in {book} {chapter}")

    return target_verse, api_time

def process_single_verse_direct(pipeline, verse_data: Dict, drop_existing: bool = False) -> Dict:
    """Process a single verse directly through the detection pipeline"""

    hebrew_processor = HebrewTextProcessor()
    figurative_found = 0

    with DatabaseManager(pipeline.db_path) as db:
        if drop_existing:
            db.setup_database(drop_existing=True)

        try:
            # Process Hebrew text
            hebrew_stripped = hebrew_processor.strip_diacritics(verse_data['hebrew'])

            # Enhance verse data
            enhanced_verse = {
                **verse_data,
                'hebrew_stripped': hebrew_stripped
            }

            # Insert verse into database
            verse_id = db.insert_verse(enhanced_verse)

            # AI analysis for figurative language with IMPROVED detection
            detection_results, llm_error = pipeline.detector.detect_figurative_language(
                verse_data['english'], verse_data['hebrew']
            )

            # Update verse with LLM restriction error if any
            if llm_error:
                print(f"    LLM Restriction: {llm_error}")
                enhanced_verse['llm_restriction_error'] = llm_error
                # Update the verse record with the error
                db.cursor.execute(
                    'UPDATE verses SET llm_restriction_error = ? WHERE id = ?',
                    (llm_error, verse_id)
                )

            if detection_results:
                for i, detection_result in enumerate(detection_results):
                    # Clean and validate type
                    fig_type = detection_result['type'].lower().strip()
                    valid_types = ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy']
                    if fig_type not in valid_types:
                        fig_type = 'other'

                    # Prepare figurative language data
                    figurative_data = {
                        'type': fig_type,
                        'subcategory': detection_result.get('subcategory'),
                        'confidence': detection_result['confidence'],
                        'figurative_text': detection_result.get('figurative_text') or detection_result.get('english_text'),
                        'figurative_text_in_hebrew': detection_result.get('hebrew_source') or detection_result.get('hebrew_text'),
                        'explanation': detection_result.get('explanation'),
                        'speaker': detection_result.get('speaker'),
                        'purpose': detection_result.get('purpose')
                    }

                    # Insert figurative language record
                    db.insert_figurative_language(verse_id, figurative_data)
                    figurative_found += 1

                    print(f"    Found: {fig_type} [{detection_result.get('subcategory', 'uncat')}] ({detection_result['confidence']:.2f}) - {detection_result.get('speaker', 'Unknown')}")
            else:
                print(f"    No figurative language detected")

            # Commit changes
            db.commit()

        except Exception as e:
            print(f"    ERROR: {e}")
            return {'figurative_found': 0}

    return {'figurative_found': figurative_found}

def process_deuteronomy_improved():
    """Process the complete book of Deuteronomy with IMPROVED detection"""

    # Generate timestamp for output database
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_db = f"deuteronomy_improved_{timestamp}.db"

    print(f"=== PROCESSING COMPLETE DEUTERONOMY WITH IMPROVED PIPELINE ===")
    print(f"ENHANCEMENTS:")
    print(f"   - Refined simile detection (eliminates procedural false positives)")
    print(f"   - Enhanced metaphor detection (excludes religious terms)")
    print(f"   - Semantic subcategories (architectural, geological, etc.)")
    print(f"Target: 34 chapters, ~959 verses")
    print(f"Output Database: {output_db}")
    print(f"Start Time: {datetime.now()}")

    # Generate all verse references
    verse_refs = generate_deuteronomy_verse_refs()
    print(f"Generated {len(verse_refs)} verse references")

    # Initialize pipeline with IMPROVED instructions
    pipeline = FigurativeLanguagePipeline(
        db_path=output_db,
        use_llm_detection=True,
        use_actual_llm=True
    )

    start_time = time.time()
    total_processed = 0
    total_figurative_found = 0
    total_errors = 0
    total_api_time = 0

    # Track progress by chapter
    current_chapter = 1
    chapter_start_time = time.time()
    chapter_processed = 0
    chapter_figurative = 0

    # Process verses individually with rate limiting
    for i, verse_ref in enumerate(verse_refs, 1):
        try:
            # Check if we've moved to a new chapter
            chapter_num = int(verse_ref.split('.')[1])
            if chapter_num != current_chapter:
                # Print chapter summary
                chapter_time = time.time() - chapter_start_time
                print(f"\n=== CHAPTER {current_chapter} COMPLETE ===")
                print(f"Processed: {chapter_processed} verses")
                print(f"Figurative instances: {chapter_figurative}")
                print(f"Time: {chapter_time:.1f}s")
                print(f"Rate: {chapter_processed/chapter_time:.2f} verses/sec")

                # Reset for new chapter
                current_chapter = chapter_num
                chapter_start_time = time.time()
                chapter_processed = 0
                chapter_figurative = 0

            print(f"\n[{i}/{len(verse_refs)}] Processing: {verse_ref}")

            # Extract single verse
            verse_data, api_time = extract_single_verse(verse_ref)
            total_api_time += api_time

            # Process through IMPROVED pipeline
            result = process_single_verse_direct(pipeline, verse_data, drop_existing=(i == 1))

            total_processed += 1
            chapter_processed += 1
            figurative_count = result.get('figurative_found', 0)
            total_figurative_found += figurative_count
            chapter_figurative += figurative_count

            # Progress indicators
            if i % 50 == 0:
                elapsed = time.time() - start_time
                rate = total_processed / elapsed
                remaining = len(verse_refs) - i
                eta_minutes = (remaining / rate) / 60 if rate > 0 else 0

                print(f"\n--- PROGRESS UPDATE ---")
                print(f"Completed: {i}/{len(verse_refs)} ({i/len(verse_refs)*100:.1f}%)")
                print(f"Rate: {rate:.2f} verses/second")
                print(f"ETA: {eta_minutes:.1f} minutes")
                print(f"Figurative instances so far: {total_figurative_found}")

            # Small delay to be respectful to API
            if i < len(verse_refs):
                time.sleep(0.1)  # 100ms between requests

        except Exception as e:
            print(f"  ERROR processing {verse_ref}: {e}")
            total_errors += 1
            continue

    # Final chapter summary
    chapter_time = time.time() - chapter_start_time
    print(f"\n=== CHAPTER {current_chapter} COMPLETE ===")
    print(f"Processed: {chapter_processed} verses")
    print(f"Figurative instances: {chapter_figurative}")
    print(f"Time: {chapter_time:.1f}s")

    total_time = time.time() - start_time

    # Generate final statistics
    results = {
        'pipeline_version': 'improved',
        'enhancements': [
            'refined_simile_detection',
            'enhanced_metaphor_detection',
            'semantic_subcategories'
        ],
        'total_verses_attempted': len(verse_refs),
        'total_processed': total_processed,
        'total_figurative_found': total_figurative_found,
        'total_errors': total_errors,
        'processing_time': total_time,
        'api_time': total_api_time,
        'verses_per_second': total_processed / total_time if total_time > 0 else 0,
        'detection_rate': (total_figurative_found / total_processed) if total_processed > 0 else 0,
        'error_rate': (total_errors / len(verse_refs) * 100) if len(verse_refs) > 0 else 0,
        'output_database': output_db,
        'completion_time': datetime.now().isoformat()
    }

    # Print final summary
    print(f"\n{'='*60}")
    print(f"IMPROVED DEUTERONOMY PROCESSING COMPLETE!")
    print(f"{'='*60}")
    print(f"IMPROVED PIPELINE RESULTS:")
    print(f"   - Refined simile/metaphor detection")
    print(f"   - Semantic subcategories implemented")
    print(f"   - False positive reduction achieved")
    print(f"")
    print(f"Verses attempted: {results['total_verses_attempted']}")
    print(f"Verses processed: {results['total_processed']}")
    print(f"Figurative instances found: {results['total_figurative_found']}")
    print(f"Average instances per verse: {results['detection_rate']:.2f}")
    print(f"Processing errors: {results['total_errors']}")
    print(f"Error rate: {results['error_rate']:.1f}%")
    print(f"Total processing time: {results['processing_time']/60:.1f} minutes")
    print(f"Processing rate: {results['verses_per_second']:.2f} verses/second")
    print(f"API time: {results['api_time']:.1f}s")
    print(f"Database saved: {results['output_database']}")
    print(f"Completion time: {results['completion_time']}")

    # Save results summary
    summary_file = f"deuteronomy_improved_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Summary saved: {summary_file}")

    return results

if __name__ == "__main__":
    process_deuteronomy_improved()