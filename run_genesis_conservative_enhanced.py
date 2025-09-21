#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Genesis processing with comprehensive error logging and monitoring
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

def process_genesis_conservative_enhanced():
    """Process complete Genesis with enhanced error handling and logging"""

    # Setup logging
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"genesis_conservative_log_{timestamp}.txt"
    logger = setup_logging(log_file)

    logger.info("=== PROCESSING COMPLETE GENESIS WITH CONSERVATIVE API (ENHANCED) ===")
    start_time = time.time()

    try:
        # Initialize clients with error handling
        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info("Initializing Gemini conservative API...")
        conservative_api = GeminiAPIClient("AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk")

        # Create database with timestamp
        db_name = f"genesis_conservative_{timestamp}.db"
        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        total_verses = 0
        total_instances = 0
        errors = 0
        chapter_progress = {}

        # Process all 50 chapters of Genesis
        for chapter in range(1, 51):
            chapter_start_time = time.time()
            logger.info(f"--- Processing Genesis {chapter} ---")

            try:
                # Get text with error handling
                logger.info(f"Fetching text for Genesis {chapter}...")
                verses_data, api_time = sefaria.extract_hebrew_text(f"Genesis.{chapter}")

                if not verses_data:
                    error_msg = f"Failed to get text for Genesis {chapter} - verses_data is None/empty"
                    logger.error(error_msg)
                    errors += 1
                    chapter_progress[chapter] = {"status": "failed", "error": "No text data", "verses": 0, "instances": 0}
                    continue

                logger.info(f"Retrieved {len(verses_data)} verses for Genesis {chapter}")
                chapter_instances = 0
                chapter_verses = 0

                # Process each verse
                for i, verse_data in enumerate(verses_data):
                    try:
                        verse_ref = verse_data['reference']
                        heb_verse = verse_data['hebrew']
                        eng_verse = verse_data['english']
                        total_verses += 1
                        chapter_verses += 1

                        logger.info(f"  Processing {verse_ref} ({i+1}/{len(verses_data)})...")

                        # Analyze with conservative API
                        result_json, error = conservative_api.analyze_figurative_language(heb_verse, eng_verse)

                        if error:
                            error_msg = f"API error for {verse_ref}: {error}"
                            logger.error(error_msg)
                            errors += 1
                            continue

                        if not result_json:
                            logger.warning(f"Empty result for {verse_ref}")
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
                                logger.info(f"    FOUND: {len(results)} instances")

                                # Store each figurative language instance
                                for result in results:
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
                                logger.debug(f"    No figurative language detected in {verse_ref}")

                        except json.JSONDecodeError as e:
                            error_msg = f"JSON decode error for {verse_ref}: {str(e)}"
                            logger.error(error_msg)
                            try:
                                # Log the problematic JSON (safely)
                                safe_output = result_json[:200] + "..." if len(result_json) > 200 else result_json
                                logger.error(f"Problematic JSON: {safe_output}")
                            except:
                                logger.error("Could not log problematic JSON due to encoding issues")
                            errors += 1

                    except Exception as e:
                        error_msg = f"Unexpected error processing verse {verse_data.get('reference', 'unknown')}: {str(e)}"
                        logger.error(error_msg)
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        errors += 1

                chapter_time = time.time() - chapter_start_time
                chapter_progress[chapter] = {
                    "status": "completed",
                    "verses": chapter_verses,
                    "instances": chapter_instances,
                    "time_minutes": chapter_time/60
                }

                logger.info(f"Genesis {chapter} COMPLETED: {chapter_instances} figurative instances from {chapter_verses} verses ({chapter_time/60:.1f} min)")

                # Commit after each chapter
                db_manager.conn.commit()

            except Exception as e:
                error_msg = f"Critical error processing Genesis {chapter}: {str(e)}"
                logger.error(error_msg)
                logger.error(f"Traceback: {traceback.format_exc()}")
                chapter_progress[chapter] = {"status": "failed", "error": str(e), "verses": 0, "instances": 0}
                errors += 1

        total_time = time.time() - start_time

        # Final commit and close database
        db_manager.conn.commit()
        db_manager.conn.close()

        # Create comprehensive summary
        logger.info(f"\n=== GENESIS CONSERVATIVE PROCESSING COMPLETE ===")
        logger.info(f"Database: {db_name}")
        logger.info(f"Log file: {log_file}")
        logger.info(f"Total verses processed: {total_verses}")
        logger.info(f"Total figurative instances: {total_instances}")
        if total_verses > 0:
            logger.info(f"Instances per verse: {total_instances/total_verses:.3f}")
        logger.info(f"Errors: {errors}")
        logger.info(f"Processing time: {total_time/60:.1f} minutes")

        # Chapter-by-chapter summary
        completed_chapters = sum(1 for ch in chapter_progress.values() if ch["status"] == "completed")
        failed_chapters = sum(1 for ch in chapter_progress.values() if ch["status"] == "failed")

        logger.info(f"Chapters completed: {completed_chapters}/50")
        logger.info(f"Chapters failed: {failed_chapters}/50")

        if failed_chapters > 0:
            logger.warning("Failed chapters:")
            for ch_num, progress in chapter_progress.items():
                if progress["status"] == "failed":
                    logger.warning(f"  Chapter {ch_num}: {progress.get('error', 'Unknown error')}")

        try:
            usage = conservative_api.get_usage_info()
            logger.info(f"API usage: {usage}")
        except Exception as e:
            logger.warning(f"Could not get API usage: {e}")

        # Write progress summary to JSON
        summary_file = f"genesis_processing_summary_{timestamp}.json"
        summary_data = {
            "database": db_name,
            "log_file": log_file,
            "start_time": datetime.fromtimestamp(start_time).isoformat(),
            "end_time": datetime.now().isoformat(),
            "total_time_minutes": total_time/60,
            "total_verses": total_verses,
            "total_instances": total_instances,
            "errors": errors,
            "chapters_completed": completed_chapters,
            "chapters_failed": failed_chapters,
            "chapter_progress": chapter_progress
        }

        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, indent=2, ensure_ascii=False)

        logger.info(f"Processing summary written to: {summary_file}")

        return db_name, total_verses, total_instances, log_file, summary_file

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    process_genesis_conservative_enhanced()