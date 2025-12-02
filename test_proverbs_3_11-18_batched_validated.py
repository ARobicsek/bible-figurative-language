#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Proverbs 3:11-18 with BATCHED PROCESSING + VALIDATION

This script tests the complete batched pipeline:
1. GPT-5.1 MEDIUM batched detection (all 8 verses in ONE API call)
2. GPT-5.1 MEDIUM batched validation (per verse batching)
3. Database storage with validation results

Expected results:
- Detection: ~10 instances (1.25/verse based on Session 8 testing)
- Validation: Validates all instances using GPT-5.1 MEDIUM
- Cost: ~$0.067 for detection + ~$0.01-0.02 per verse for validation
- Total cost: <$0.25
"""

import sys
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add source paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'private/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'private'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Load environment
load_dotenv()

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(output_dir, f'proverbs_3_11-18_batched_validated_{timestamp}_log.txt')
db_file = os.path.join(output_dir, f'proverbs_3_11-18_batched_validated_{timestamp}.db')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TEST: PROVERBS 3:11-18 WITH BATCHED PROCESSING + VALIDATION")
print("=" * 80)
print(f"Mode: GPT-5.1 MEDIUM (batched detection + batched validation)")
print(f"Verses: Proverbs 3:11-18 (8 verses)")
print(f"Log file: {log_file}")
print(f"Database: {db_file}")
print("=" * 80)

try:
    # Initialize components
    logger.info("Initializing Sefaria client...")
    sefaria = SefariaClient()

    logger.info("Fetching Proverbs 3 from Sefaria...")
    all_verses, api_time = sefaria.extract_hebrew_text("Proverbs.3")
    logger.info(f"Retrieved {len(all_verses)} verses in {api_time:.2f}s")

    # Filter to verses 11-18
    verses = [v for v in all_verses if 11 <= v['verse'] <= 18]
    logger.info(f"Filtered to verses 11-18: {len(verses)} verses")

    # Initialize database
    logger.info(f"Creating database: {db_file}")
    db_manager = DatabaseManager(db_file)
    db_manager.connect()
    db_manager.setup_database()

    # Initialize validator (GPT-5.1 MEDIUM)
    logger.info("Initializing MetaphorValidator with GPT-5.1 MEDIUM...")
    validator = MetaphorValidator(db_manager=db_manager, logger=logger)

    # Initialize divine names modifier
    logger.info("Initializing Hebrew Divine Names Modifier...")
    divine_names_modifier = HebrewDivineNamesModifier(logger=logger)

    # Import the batched processing function
    from interactive_parallel_processor import process_chapter_batched

    # Process verses with batched mode
    logger.info("\n" + "=" * 80)
    logger.info("STARTING BATCHED PROCESSING + VALIDATION")
    logger.info("=" * 80 + "\n")

    verses_stored, instances_stored, processing_time, total_attempted, total_cost = process_chapter_batched(
        verses, "Proverbs", 3, validator, divine_names_modifier, db_manager, logger
    )

    # Commit but don't close yet (we need to query results)
    db_manager.commit()

    # Print summary
    print("\n" + "=" * 80)
    print("TEST COMPLETE - RESULTS SUMMARY")
    print("=" * 80)
    print(f"Verses processed: {verses_stored}/{len(verses)}")
    print(f"Instances detected: {instances_stored}")
    print(f"Detection rate: {instances_stored/len(verses):.2f} instances/verse")
    print(f"Total cost: ${total_cost:.4f}")
    print(f"Total time: {processing_time:.1f}s")
    print(f"Average time per verse: {processing_time/len(verses):.2f}s")
    print("=" * 80)
    print(f"\nResults saved to:")
    print(f"  Database: {db_file}")
    print(f"  Log: {log_file}")
    print("=" * 80)

    # Query database for validation results
    logger.info("\nQuerying database for validation results...")

    # Get all instances with validation data
    cursor = db_manager.conn.cursor()
    cursor.execute("""
        SELECT
            v.reference,
            f.figurative_text,
            f.figurative_language,
            f.metaphor,
            f.simile,
            f.personification,
            f.validation_decision_metaphor,
            f.validation_decision_simile,
            f.validation_decision_personification,
            f.final_figurative_language,
            f.final_metaphor,
            f.final_simile,
            f.final_personification
        FROM figurative_language f
        JOIN verses v ON f.verse_id = v.id
        ORDER BY v.verse
    """)

    results = cursor.fetchall()

    print("\n" + "=" * 80)
    print("VALIDATION RESULTS")
    print("=" * 80)

    if results:
        for row in results:
            ref, text, fig, met, sim, per, val_met, val_sim, val_per, final_fig, final_met, final_sim, final_per = row
            print(f"\n{ref}: {text}")
            print(f"  Initial: fig={fig}, metaphor={met}, simile={sim}, personification={per}")
            print(f"  Validation: metaphor={val_met}, simile={val_sim}, personification={val_per}")
            print(f"  Final: fig={final_fig}, metaphor={final_met}, simile={final_sim}, personification={final_per}")
    else:
        print("No instances found in database.")

    print("=" * 80)

    db_manager.close()

    logger.info("\nTest completed successfully!")

except Exception as e:
    logger.error(f"Test failed with error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
