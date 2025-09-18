#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fresh validation run with Gemini 2.5 Flash and timestamped database
"""
import json
import time
from datetime import datetime
from process_individual_verses import process_individual_validation_verses

def run_fresh_validation():
    """Run fresh validation with timestamped database"""

    print("=== FRESH 200-VERSE VALIDATION WITH GEMINI 2.5 FLASH ===")

    # Load validation set
    try:
        with open("validation_set_200_verses.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        verse_refs = data.get('references', [])
        print(f"Loaded {len(verse_refs)} verse references")
    except Exception as e:
        print(f"Error loading validation set: {e}")
        return

    # Create timestamped database name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_db = f"validation_gemini25_{timestamp}.db"

    print(f"Using fresh database: {output_db}")
    print(f"Confirming Gemini 2.5 Flash model in use...")

    # Process all verses
    results = process_individual_validation_verses(verse_refs, output_db)

    # Print results
    print(f"\n{'='*60}")
    print(f"FRESH VALIDATION COMPLETE")
    print(f"{'='*60}")
    print(f"Database: {output_db}")
    print(f"Verses attempted: {results['total_verses_attempted']}")
    print(f"Verses processed: {results['total_processed']}")
    print(f"Figurative instances: {results['total_figurative_found']}")
    print(f"Detection rate: {results['detection_rate']:.1f}%")
    print(f"Error rate: {results['error_rate']:.1f}%")
    print(f"Processing time: {results['processing_time']:.1f}s")

    return results, output_db

if __name__ == "__main__":
    run_fresh_validation()