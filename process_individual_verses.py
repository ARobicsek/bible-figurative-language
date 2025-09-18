#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process individual verses (not entire chapters) for validation
"""
import json
import time
from typing import List, Dict, Tuple
from src.hebrew_figurative_db.text_extraction import SefariaClient
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

def extract_single_verse(verse_ref: str) -> Tuple[Dict, float]:
    """
    Extract a single specific verse from Sefaria

    Args:
        verse_ref: Reference like "Genesis.41.4" for Genesis 41:4

    Returns:
        Tuple of (verse_data, api_time)
    """
    # Parse the reference
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

def process_individual_validation_verses(verse_refs: List[str], output_db: str = "validation_200_verses.db") -> Dict:
    """Process exactly the specified individual verses"""

    print(f"=== PROCESSING {len(verse_refs)} INDIVIDUAL VERSES FOR VALIDATION ===")

    # Initialize pipeline
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

    # Process verses individually with rate limiting
    for i, verse_ref in enumerate(verse_refs, 1):
        try:
            print(f"\n[{i}/{len(verse_refs)}] Processing: {verse_ref}")

            # Extract single verse
            verse_data, api_time = extract_single_verse(verse_ref)
            total_api_time += api_time

            # Process through pipeline (create individual "chapter" for single verse)
            temp_range = f"{verse_data['book']}.{verse_data['chapter']}.{verse_data['verse']}"

            # Use direct processing instead of pipeline to avoid duplicate API calls
            result = process_single_verse_direct(pipeline, verse_data, drop_existing=(i == 1))

            total_processed += 1
            total_figurative_found += result.get('figurative_found', 0)

            # Small delay to be respectful to API
            if i < len(verse_refs):
                time.sleep(0.1)  # 100ms between requests (reduced from 500ms)

        except Exception as e:
            print(f"  ERROR processing {verse_ref}: {e}")
            total_errors += 1
            continue

    total_time = time.time() - start_time

    # Generate final statistics
    results = {
        'total_verses_attempted': len(verse_refs),
        'total_processed': total_processed,
        'total_figurative_found': total_figurative_found,
        'total_errors': total_errors,
        'processing_time': total_time,
        'api_time': total_api_time,
        'verses_per_second': total_processed / total_time if total_time > 0 else 0,
        'detection_rate': (total_figurative_found / total_processed * 100) if total_processed > 0 else 0,
        'error_rate': (total_errors / len(verse_refs) * 100) if len(verse_refs) > 0 else 0,
        'output_database': output_db
    }

    return results

def process_single_verse_direct(pipeline, verse_data: Dict, drop_existing: bool = False) -> Dict:
    """Process a single verse directly through the detection pipeline"""

    from src.hebrew_figurative_db.database import DatabaseManager
    from src.hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor

    hebrew_processor = HebrewTextProcessor()
    figurative_found = 0

    with DatabaseManager(pipeline.db_path) as db:
        if drop_existing:
            db.setup_database(drop_existing=True)

        try:
            # Process Hebrew text
            hebrew_stripped = hebrew_processor.strip_diacritics(verse_data['hebrew'])
            speaker = hebrew_processor.identify_speaker_patterns(verse_data['english'], verse_data['hebrew'])

            # Enhance verse data
            enhanced_verse = {
                **verse_data,
                'hebrew_stripped': hebrew_stripped,
                'speaker': speaker
            }

            # Insert verse into database
            verse_id = db.insert_verse(enhanced_verse)

            # AI analysis for figurative language
            detection_results = pipeline.detector.detect_figurative_language(
                verse_data['english'], verse_data['hebrew']
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
                        'explanation': detection_result.get('explanation')
                    }

                    # Insert figurative language record
                    db.insert_figurative_language(verse_id, figurative_data)
                    figurative_found += 1

                    print(f"    Found: {fig_type} [{detection_result.get('subcategory', 'uncat')}] ({detection_result['confidence']:.2f})")
            else:
                print(f"    No figurative language detected")

            # Commit changes
            db.commit()

        except Exception as e:
            print(f"    ERROR: {e}")
            return {'figurative_found': 0}

    return {'figurative_found': figurative_found}

def main():
    """Main validation script for individual verses"""

    print("=== INDIVIDUAL VERSE VALIDATION ===")

    # Load validation set
    try:
        with open("validation_set_200_verses.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        verse_refs = data.get('references', [])
        print(f"Loaded {len(verse_refs)} verse references")
    except Exception as e:
        print(f"Error loading validation set: {e}")
        return

    if not verse_refs:
        print("No verses to process.")
        return

    # Show sample
    print(f"\nSample verses (individual processing):")
    for i, ref in enumerate(verse_refs[:5]):
        print(f"  {i+1}. {ref} -> will extract only this specific verse")

    print(f"\nProcessing {len(verse_refs)} individual verses...")
    print(f"Estimated time: {len(verse_refs) * 3 / 60:.1f} minutes")

    # Process all verses
    results = process_individual_validation_verses(verse_refs)

    # Print summary
    print(f"\n{'='*60}")
    print(f"VALIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"Verses attempted: {results['total_verses_attempted']}")
    print(f"Verses processed: {results['total_processed']}")
    print(f"Figurative instances found: {results['total_figurative_found']}")
    print(f"Processing errors: {results['total_errors']}")
    print(f"Detection rate: {results['detection_rate']:.1f}%")
    print(f"Error rate: {results['error_rate']:.1f}%")
    print(f"Processing time: {results['processing_time']:.1f}s")
    print(f"API time: {results['api_time']:.1f}s")
    print(f"Results saved to: {results['output_database']}")

    return results

if __name__ == "__main__":
    main()