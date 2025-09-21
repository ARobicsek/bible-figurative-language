#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process complete Deuteronomy with multi-model API (Gemini 2.5 Flash → 1.5 Flash fallback)
Addresses false negative issues while maintaining zero false positives
"""
import sys
import os
import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from src.hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from src.hebrew_figurative_db.database.db_manager import DatabaseManager


def setup_logging(log_file: str):
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def create_database_tables(db_path: str):
    """Create database tables with enhanced schema"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Enhanced verses table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            reference TEXT NOT NULL,
            book TEXT NOT NULL,
            chapter INTEGER NOT NULL,
            verse INTEGER NOT NULL,
            hebrew_text TEXT NOT NULL,
            hebrew_text_stripped TEXT,
            english_text TEXT NOT NULL,
            word_count INTEGER,
            llm_restriction_error TEXT,
            model_used TEXT,
            fallback_used BOOLEAN DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Enhanced figurative language table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS figurative_language (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            verse_id INTEGER NOT NULL,
            type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other')),
            vehicle_level_1 TEXT,
            vehicle_level_2 TEXT,
            tenor_level_1 TEXT,
            tenor_level_2 TEXT,
            confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
            figurative_text TEXT,
            figurative_text_in_hebrew TEXT,
            explanation TEXT,
            speaker TEXT,
            purpose TEXT,
            model_used TEXT,
            fallback_used BOOLEAN DEFAULT 0,
            processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (verse_id) REFERENCES verses (id)
        )
    ''')

    # Processing metadata table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processing_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book TEXT NOT NULL,
            chapter INTEGER,
            total_verses INTEGER,
            figurative_instances INTEGER,
            primary_model_success INTEGER,
            fallback_used INTEGER,
            processing_time_seconds REAL,
            start_time TIMESTAMP,
            end_time TIMESTAMP,
            api_key_hash TEXT
        )
    ''')

    conn.commit()
    conn.close()


def process_chapter(sefaria_client: SefariaClient,
                   gemini_client: MultiModelGeminiClient,
                   book: str, chapter: int,
                   db_path: str) -> Dict:
    """Process a single chapter with multi-model API"""

    logging.info(f"--- Processing {book} {chapter} ---")

    # Fetch text
    logging.info(f"Fetching text for {book} {chapter}...")
    chapter_start = datetime.now()

    try:
        verses_data, api_time = sefaria_client.extract_hebrew_text(f"{book}.{chapter}")
    except Exception as e:
        logging.error(f"Failed to fetch {book} {chapter}: {e}")
        return {'error': str(e)}

    if not verses_data:
        logging.error(f"No verses retrieved for {book} {chapter}")
        return {'error': 'No verses retrieved'}

    logging.info(f"Retrieved {len(verses_data)} verses for {book} {chapter}")

    # Process verses
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    figurative_count = 0
    primary_success = 0
    fallback_used = 0

    for i, verse_data in enumerate(verses_data, 1):
        logging.info(f"  Processing {book} {chapter}:{i} ({i}/{len(verses_data)})...")

        hebrew_text = verse_data['hebrew']
        english_text = verse_data['english']
        reference = verse_data['reference']
        word_count = len(english_text.split())

        # Analyze with multi-model API
        result_json, restriction_error, metadata = gemini_client.analyze_figurative_language(
            hebrew_text, english_text, book, chapter
        )

        # Track model usage
        model_used = metadata.get('model_used', 'unknown')
        was_fallback = metadata.get('fallback_used', False)

        if was_fallback:
            fallback_used += 1
        else:
            primary_success += 1

        # Insert verse record
        cursor.execute('''
            INSERT INTO verses (reference, book, chapter, verse, hebrew_text, hebrew_text_stripped,
                              english_text, word_count, llm_restriction_error, model_used, fallback_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (reference, book, chapter, i, hebrew_text, hebrew_text.strip(),
              english_text, word_count, restriction_error, model_used, was_fallback))

        verse_id = cursor.lastrowid

        # Process figurative language results
        try:
            figurative_instances = json.loads(result_json) if result_json else []

            if figurative_instances:
                logging.info(f"    FOUND: {len(figurative_instances)} figurative instances")

                for idx, instance in enumerate(figurative_instances, 1):
                    logging.info(f"      Instance {idx}: {instance.get('type', 'unknown')} - '{instance.get('english_text', 'N/A')}'")

                    cursor.execute('''
                        INSERT INTO figurative_language
                        (verse_id, type, vehicle_level_1, vehicle_level_2, tenor_level_1, tenor_level_2,
                         confidence, figurative_text, figurative_text_in_hebrew, explanation, speaker, purpose,
                         model_used, fallback_used)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        verse_id,
                        instance.get('type', 'unknown'),
                        instance.get('vehicle_level_1'),
                        instance.get('vehicle_level_2'),
                        instance.get('tenor_level_1'),
                        instance.get('tenor_level_2'),
                        instance.get('confidence', 0.0),
                        instance.get('english_text'),
                        instance.get('hebrew_text'),
                        instance.get('explanation'),
                        instance.get('speaker'),
                        instance.get('purpose'),
                        model_used,
                        was_fallback
                    ))
                    figurative_count += 1

        except json.JSONDecodeError as e:
            logging.warning(f"Invalid JSON for {reference}: {result_json}")

    # Record chapter metadata
    chapter_end = datetime.now()
    processing_time = (chapter_end - chapter_start).total_seconds()

    cursor.execute('''
        INSERT INTO processing_metadata
        (book, chapter, total_verses, figurative_instances, primary_model_success,
         fallback_used, processing_time_seconds, start_time, end_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (book, chapter, len(verses_data), figurative_count, primary_success,
          fallback_used, processing_time, chapter_start, chapter_end))

    conn.commit()
    conn.close()

    logging.info(f"{book} {chapter} COMPLETED: {figurative_count} figurative instances from {len(verses_data)} verses")
    logging.info(f"Model usage: {primary_success} primary success, {fallback_used} fallback used")

    return {
        'chapter': chapter,
        'verses': len(verses_data),
        'figurative': figurative_count,
        'primary_success': primary_success,
        'fallback_used': fallback_used,
        'processing_time': processing_time
    }


def main():
    """Main processing function"""

    # Setup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    db_name = f"deuteronomy_multi_model_{timestamp}.db"
    log_name = f"deuteronomy_multi_model_log_{timestamp}.txt"

    setup_logging(log_name)

    logging.info("=== PROCESSING DEUTERONOMY WITH MULTI-MODEL API ===")
    logging.info(f"Database: {db_name}")
    logging.info(f"Log file: {log_name}")

    # Initialize clients
    logging.info("Initializing Sefaria client...")
    sefaria_client = SefariaClient()

    logging.info("Initializing Gemini multi-model API...")
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    gemini_client = MultiModelGeminiClient(api_key)

    # Test API connections
    logging.info("Testing API connections...")
    connections = gemini_client.test_api_connection()
    logging.info(f"API status: {connections}")

    # Create database
    logging.info(f"Creating database: {db_name}")
    create_database_tables(db_name)

    # Process all Deuteronomy chapters (1-34)
    total_start = datetime.now()
    total_verses = 0
    total_figurative = 0
    total_primary_success = 0
    total_fallback = 0

    for chapter in range(1, 35):  # Deuteronomy has 34 chapters
        try:
            result = process_chapter(sefaria_client, gemini_client, "Deuteronomy", chapter, db_name)

            if 'error' not in result:
                total_verses += result['verses']
                total_figurative += result['figurative']
                total_primary_success += result['primary_success']
                total_fallback += result['fallback_used']
            else:
                logging.error(f"Chapter {chapter} failed: {result['error']}")

        except Exception as e:
            logging.error(f"Exception processing Deuteronomy {chapter}: {e}")

    # Final summary
    total_end = datetime.now()
    total_time = (total_end - total_start).total_seconds()

    logging.info("\n=== DEUTERONOMY MULTI-MODEL PROCESSING COMPLETE ===")
    logging.info(f"Database: {db_name}")
    logging.info(f"Log file: {log_name}")
    logging.info(f"Total processing time: {total_time:.1f} seconds")
    logging.info(f"Total verses processed: {total_verses:,}")
    logging.info(f"Total figurative instances: {total_figurative:,}")
    logging.info(f"Primary model success: {total_primary_success} ({total_primary_success/max(1,total_verses)*100:.1f}%)")
    logging.info(f"Fallback used: {total_fallback} ({total_fallback/max(1,total_verses)*100:.1f}%)")

    # API usage statistics
    usage_stats = gemini_client.get_usage_info()
    logging.info(f"\nAPI Usage Statistics:")
    logging.info(f"Primary model: {usage_stats['primary_model']}")
    logging.info(f"Fallback model: {usage_stats['fallback_model']}")
    logging.info(f"Total requests: {usage_stats['total_requests']:,}")
    logging.info(f"Primary success rate: {usage_stats['primary_success_rate']*100:.1f}%")
    logging.info(f"Fallback rate: {usage_stats['fallback_rate']*100:.1f}%")
    logging.info(f"Total tokens: {usage_stats['total_tokens']:,}")

    if usage_stats['restriction_reasons']:
        logging.info("Restriction reasons encountered:")
        for reason in usage_stats['restriction_reasons']:
            logging.info(f"  - {reason}")

    # Save summary
    summary_file = f"deuteronomy_multi_model_summary_{timestamp}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            'processing_summary': {
                'database': db_name,
                'log_file': log_name,
                'start_time': total_start.isoformat(),
                'end_time': total_end.isoformat(),
                'total_time_seconds': total_time,
                'total_verses': total_verses,
                'total_figurative': total_figurative,
                'primary_success': total_primary_success,
                'fallback_used': total_fallback
            },
            'api_usage': usage_stats
        }, f, indent=2, ensure_ascii=False)

    logging.info(f"Summary saved to: {summary_file}")


if __name__ == "__main__":
    main()