#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process Genesis chapter 50 with fixed conservative API
"""
import sys
import os
import logging
import traceback
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
import json
import time
from datetime import datetime

def setup_logging(log_file):
    """Setup comprehensive logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def process_genesis_50():
    """Process Genesis chapter 50 with fixed verse storage"""

    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"genesis_50_log_{timestamp}.txt"
    logger = setup_logging(log_file)

    logger.info("=== PROCESSING GENESIS CHAPTER 50 (FIXED VERSION) ===")
    start_time = time.time()

    try:
        # Initialize clients
        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info("Initializing Gemini conservative API...")
        conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

        # Create database with timestamp
        db_name = f"genesis_50_fixed_{timestamp}.db"
        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        total_verses = 0
        total_instances = 0
        errors = 0

        # Process Genesis 50
        chapter = 50
        logger.info(f"--- Processing Genesis {chapter} ---")

        # Get text
        logger.info(f"Fetching text for Genesis {chapter}...")
        verses_data, api_time = sefaria.extract_hebrew_text(f"Genesis.{chapter}")

        if not verses_data:
            logger.error(f"Failed to get text for Genesis {chapter}")
            return

        logger.info(f"Retrieved {len(verses_data)} verses for Genesis {chapter}")

        # Process each verse
        for i, verse_data in enumerate(verses_data):
            try:
                verse_ref = verse_data['reference']
                heb_verse = verse_data['hebrew']
                eng_verse = verse_data['english']
                total_verses += 1

                logger.info(f"  Processing {verse_ref} ({i+1}/{len(verses_data)})...")

                # Analyze with conservative API
                result_json, error = conservative_api.analyze_figurative_language(heb_verse, eng_verse)

                if error:
                    logger.error(f"API error for {verse_ref}: {error}")
                    errors += 1
                    continue

                # First insert verse regardless of figurative language detection
                verse_data_dict = {
                    'reference': verse_ref,
                    'book': 'Genesis',
                    'chapter': int(verse_ref.split(':')[0].split(' ')[1]),
                    'verse': int(verse_ref.split(':')[1]),
                    'hebrew': heb_verse,
                    'english': eng_verse,
                    'word_count': len(heb_verse.split())
                }
                verse_id = db_manager.insert_verse(verse_data_dict)
                logger.info(f"    Verse stored in database with ID: {verse_id}")

                if not result_json:
                    logger.warning(f"Empty result for {verse_ref}")
                    continue

                try:
                    # Clean up markdown formatting if present
                    clean_json = result_json.strip()
                    if clean_json.startswith('```json\n'):
                        clean_json = clean_json[8:]  # Remove ```json\n
                    if clean_json.endswith('\n```'):
                        clean_json = clean_json[:-4]  # Remove \n```

                    # Additional cleanup for analysis text after JSON
                    if '\n```\n' in clean_json:
                        clean_json = clean_json.split('\n```\n')[0]
                    elif '\n```' in clean_json:
                        clean_json = clean_json.split('\n```')[0]

                    results = json.loads(clean_json)
                    if results:  # Found figurative language
                        total_instances += len(results)
                        logger.info(f"    FOUND: {len(results)} figurative instances")

                        # Store each figurative language instance
                        for j, result in enumerate(results):
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

                            fig_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                            logger.info(f"      Instance {j+1}: {result.get('type', 'unknown')} - ID: {fig_id}")
                            logger.info(f"        Text: {result.get('english_text', 'N/A')}")
                            logger.info(f"        Explanation: {result.get('explanation', 'N/A')}")
                    else:
                        logger.info(f"    No figurative language detected")

                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error for {verse_ref}: {str(e)}")
                    try:
                        safe_output = result_json[:200] + "..." if len(result_json) > 200 else result_json
                        logger.error(f"Problematic JSON: {safe_output}")
                    except:
                        logger.error("Could not log problematic JSON due to encoding issues")
                    errors += 1

            except Exception as e:
                logger.error(f"Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                errors += 1

        total_time = time.time() - start_time

        # Final commit and close database
        db_manager.conn.commit()
        db_manager.conn.close()

        # Summary
        logger.info(f"\n=== GENESIS 50 PROCESSING COMPLETE ===")
        logger.info(f"Database: {db_name}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Total verses processed: {total_verses}")
        logger.info(f"Total figurative instances: {total_instances}")
        if total_verses > 0:
            logger.info(f"Instances per verse: {total_instances/total_verses:.3f}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Processing time: {total_time:.1f} seconds")

        # Verify database contents
        import sqlite3
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM verses")
        verse_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM figurative_language")
        fig_count = cursor.fetchone()[0]
        logger.info(f"Database verification: {verse_count} verses, {fig_count} figurative instances stored")

        # Show figurative language found
        if fig_count > 0:
            logger.info("\n=== FIGURATIVE LANGUAGE DETAILS ===")
            cursor.execute("""
                SELECT v.reference, fl.type, fl.figurative_text, fl.explanation, fl.confidence
                FROM figurative_language fl
                JOIN verses v ON fl.verse_id = v.id
                ORDER BY v.verse
            """)
            instances = cursor.fetchall()
            for ref, ftype, text, explanation, confidence in instances:
                logger.info(f"{ref}: {ftype} (confidence: {confidence:.2f})")
                logger.info(f"  Text: {text}")
                logger.info(f"  Explanation: {explanation}")

        conn.close()

        return db_name, total_verses, total_instances

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    process_genesis_50()