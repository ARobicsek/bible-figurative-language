#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process complete book of Genesis with conservative API
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
import json
import time
from datetime import datetime

def process_genesis_conservative():
    """Process complete Genesis with conservative API"""

    print("=== PROCESSING COMPLETE GENESIS WITH CONSERVATIVE API ===")
    start_time = time.time()

    # Initialize clients
    sefaria = SefariaClient()
    conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

    # Create database with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f"genesis_conservative_{timestamp}.db"
    db_manager = DatabaseManager(db_name)
    db_manager.connect()
    db_manager.setup_database()

    print(f"Database: {db_name}")

    total_verses = 0
    total_instances = 0
    errors = 0

    # Process all 50 chapters of Genesis
    for chapter in range(1, 51):
        print(f"\n--- Processing Genesis {chapter} ---")

        # Get text
        verses_data, api_time = sefaria.extract_hebrew_text(f"Genesis.{chapter}")

        if not verses_data:
            print(f"Failed to get text for Genesis {chapter}")
            errors += 1
            continue

        chapter_instances = 0

        # Process each verse
        for verse_data in verses_data:
            verse_ref = verse_data['reference']
            heb_verse = verse_data['hebrew']
            eng_verse = verse_data['english']
            total_verses += 1

            print(f"  Processing {verse_ref}...")

            # Analyze with conservative API
            result_json, error = conservative_api.analyze_figurative_language(heb_verse, eng_verse)

            if error:
                print(f"    ERROR - {error}")
                errors += 1
                continue

            try:
                # Clean up markdown formatting if present
                clean_json = result_json.strip()
                if clean_json.startswith('```json\n'):
                    clean_json = clean_json[8:]  # Remove ```json\n
                if clean_json.endswith('\n```'):
                    clean_json = clean_json[:-4]  # Remove \n```

                results = json.loads(clean_json)
                if results:  # Found figurative language
                    chapter_instances += len(results)
                    total_instances += len(results)
                    print(f"    FOUND: {len(results)} instances")

                    # Store each instance in database
                    for result in results:
                        # First insert/get verse
                        verse_data = {
                            'reference': verse_ref,
                            'book': 'Genesis',
                            'chapter': int(verse_ref.split(':')[0].split(' ')[1]),
                            'verse': int(verse_ref.split(':')[1]),
                            'hebrew': heb_verse,
                            'english': eng_verse,
                            'word_count': len(heb_verse.split())
                        }
                        verse_id = db_manager.insert_verse(verse_data)

                        # Then insert figurative language data
                        figurative_data = {
                            'type': result.get('type', 'unknown'),
                            'vehicle_level_1': result.get('vehicle_level_1', ''),
                            'vehicle_level_2': result.get('vehicle_level_2', ''),
                            'tenor_level_1': result.get('tenor_level_1', ''),
                            'tenor_level_2': result.get('tenor_level_2', ''),
                            'confidence': result.get('confidence', 0.0),
                            'figurative_text': result.get('english_text', ''),
                            'figurative_text_in_hebrew': result.get('hebrew_text', ''),
                            'explanation': result.get('explanation', ''),
                            'speaker': result.get('speaker', ''),
                            'purpose': result.get('purpose', '')
                        }

                        db_manager.insert_figurative_language(verse_id, figurative_data)
                else:
                    print(f"    No figurative language detected")

            except json.JSONDecodeError:
                try:
                    # Safely handle Unicode in error output
                    safe_output = result_json.encode('ascii', 'replace').decode('ascii')
                    print(f"    JSON decode error - {safe_output}")
                except:
                    print(f"    JSON decode error - [Unicode content]")
                errors += 1

        print(f"Genesis {chapter}: {chapter_instances} figurative instances")

    total_time = time.time() - start_time

    # Commit and close database
    db_manager.conn.commit()
    db_manager.conn.close()

    print(f"\n=== GENESIS CONSERVATIVE PROCESSING COMPLETE ===")
    print(f"Database: {db_name}")
    print(f"Total verses processed: {total_verses}")
    print(f"Total figurative instances: {total_instances}")
    print(f"Instances per verse: {total_instances/total_verses:.3f}")
    print(f"Errors: {errors}")
    print(f"Processing time: {total_time/60:.1f} minutes")

    usage = conservative_api.get_usage_info()
    print(f"API usage: {usage}")

    return db_name, total_verses, total_instances

if __name__ == "__main__":
    process_genesis_conservative()