#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Regenerate all three non-sacred fields in the database with the fixed Elohim modifier
that now handles all suffix forms (Elohekha, Eloheikhem, etc.)
"""

import sqlite3
import sys
import logging

sys.path.insert(0, 'private/src')
sys.stdout.reconfigure(encoding='utf-8')

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def regenerate_all_non_sacred_fields():
    """Regenerate all three non-sacred fields with the fixed modifier"""

    # Initialize the modifier
    modifier = HebrewDivineNamesModifier(logger=logger)

    # Connect to database
    conn = sqlite3.connect('database/Pentateuch_Psalms_fig_language.db')
    cursor = conn.cursor()

    # === FIELD 1: verses.hebrew_text_non_sacred ===
    logger.info("=" * 60)
    logger.info("REGENERATING: verses.hebrew_text_non_sacred")
    logger.info("=" * 60)

    cursor.execute('SELECT id, hebrew_text FROM verses')
    verses = cursor.fetchall()
    logger.info(f"Found {len(verses)} verses to process")

    modified_count = 0
    for idx, (verse_id, hebrew_text) in enumerate(verses, 1):
        if hebrew_text:
            non_sacred = modifier.modify_divine_names(hebrew_text)
            cursor.execute(
                'UPDATE verses SET hebrew_text_non_sacred = ? WHERE id = ?',
                (non_sacred, verse_id)
            )
            if non_sacred != hebrew_text:
                modified_count += 1

        # Commit every 500 verses
        if idx % 500 == 0:
            conn.commit()
            logger.info(f"  Progress: {idx}/{len(verses)} verses processed ({modified_count} modified)")

    conn.commit()
    logger.info(f"✓ COMPLETE: {len(verses)} verses processed, {modified_count} modified\n")

    # === FIELD 2: verses.english_text_non_sacred ===
    logger.info("=" * 60)
    logger.info("REGENERATING: verses.english_text_non_sacred")
    logger.info("=" * 60)

    cursor.execute('SELECT id, english_text FROM verses')
    verses = cursor.fetchall()
    logger.info(f"Found {len(verses)} verses to process")

    modified_count = 0
    for idx, (verse_id, english_text) in enumerate(verses, 1):
        if english_text:
            non_sacred = modifier.modify_english_with_hebrew_terms(english_text)
            cursor.execute(
                'UPDATE verses SET english_text_non_sacred = ? WHERE id = ?',
                (non_sacred, verse_id)
            )
            if non_sacred != english_text:
                modified_count += 1

        # Commit every 500 verses
        if idx % 500 == 0:
            conn.commit()
            logger.info(f"  Progress: {idx}/{len(verses)} verses processed ({modified_count} modified)")

    conn.commit()
    logger.info(f"✓ COMPLETE: {len(verses)} verses processed, {modified_count} modified\n")

    # === FIELD 3: figurative_language.figurative_text_in_hebrew_non_sacred ===
    logger.info("=" * 60)
    logger.info("REGENERATING: figurative_language.figurative_text_in_hebrew_non_sacred")
    logger.info("=" * 60)

    cursor.execute('SELECT id, figurative_text_in_hebrew FROM figurative_language')
    instances = cursor.fetchall()
    logger.info(f"Found {len(instances)} figurative language instances to process")

    modified_count = 0
    for idx, (instance_id, fig_hebrew) in enumerate(instances, 1):
        if fig_hebrew:
            non_sacred = modifier.modify_divine_names(fig_hebrew)
            cursor.execute(
                'UPDATE figurative_language SET figurative_text_in_hebrew_non_sacred = ? WHERE id = ?',
                (non_sacred, instance_id)
            )
            if non_sacred != fig_hebrew:
                modified_count += 1

        # Commit every 500 instances
        if idx % 500 == 0:
            conn.commit()
            logger.info(f"  Progress: {idx}/{len(instances)} instances processed ({modified_count} modified)")

    conn.commit()
    logger.info(f"✓ COMPLETE: {len(instances)} instances processed, {modified_count} modified\n")

    # Close connection
    conn.close()

    logger.info("=" * 60)
    logger.info("✓ ALL THREE FIELDS REGENERATED SUCCESSFULLY")
    logger.info("=" * 60)

if __name__ == '__main__':
    try:
        regenerate_all_non_sacred_fields()
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
