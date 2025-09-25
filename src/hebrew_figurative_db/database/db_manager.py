#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Database manager for figurative language storage and retrieval
"""
import sqlite3
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class DatabaseManager:
    """SQLite database manager for Hebrew figurative language data"""

    def __init__(self, db_path: str = 'figurative_language_pipeline.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        if self.conn:
            self.conn.close()

    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def setup_database(self, drop_existing: bool = False):
        """Set up database schema"""
        if drop_existing:
            self.cursor.execute('DROP TABLE IF EXISTS figurative_language')
            self.cursor.execute('DROP TABLE IF EXISTS verses')

        # Create verses table
        self.cursor.execute('''
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
                llm_deliberation TEXT,
                instances_detected INTEGER,
                instances_recovered INTEGER,
                instances_lost_to_truncation INTEGER,
                truncation_occurred TEXT CHECK(truncation_occurred IN ('yes', 'no')) DEFAULT 'no',
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create figurative language table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS figurative_language (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verse_id INTEGER NOT NULL,
                figurative_language TEXT CHECK(figurative_language IN ('yes', 'no')) DEFAULT 'no',
                simile TEXT CHECK(simile IN ('yes', 'no')) DEFAULT 'no',
                metaphor TEXT CHECK(metaphor IN ('yes', 'no')) DEFAULT 'no',
                personification TEXT CHECK(personification IN ('yes', 'no')) DEFAULT 'no',
                idiom TEXT CHECK(idiom IN ('yes', 'no')) DEFAULT 'no',
                hyperbole TEXT CHECK(hyperbole IN ('yes', 'no')) DEFAULT 'no',
                metonymy TEXT CHECK(metonymy IN ('yes', 'no')) DEFAULT 'no',
                other TEXT CHECK(other IN ('yes', 'no')) DEFAULT 'no',
                final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')) DEFAULT 'no',
                final_simile TEXT CHECK(final_simile IN ('yes', 'no')) DEFAULT 'no',
                final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')) DEFAULT 'no',
                final_personification TEXT CHECK(final_personification IN ('yes', 'no')) DEFAULT 'no',
                final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')) DEFAULT 'no',
                final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')) DEFAULT 'no',
                final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')) DEFAULT 'no',
                final_other TEXT CHECK(final_other IN ('yes', 'no')) DEFAULT 'no',
                target TEXT,  -- Hierarchical tag array as JSON
                vehicle TEXT,  -- Hierarchical tag array as JSON
                ground TEXT,  -- Hierarchical tag array as JSON
                posture TEXT,  -- Hierarchical tag array as JSON
                confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
                figurative_text TEXT,
                figurative_text_in_hebrew TEXT,
                figurative_text_in_hebrew_stripped TEXT,
                explanation TEXT,
                speaker TEXT,
                purpose TEXT,
                original_detection_types TEXT,
                figurative_detection_deliberation TEXT,  -- LLM reasoning about figurative language detection and typing
                tagging_analysis_deliberation TEXT,      -- LLM reasoning about hierarchical tag selection
                validation_decision_simile TEXT CHECK(validation_decision_simile IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_metaphor TEXT CHECK(validation_decision_metaphor IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_personification TEXT CHECK(validation_decision_personification IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_idiom TEXT CHECK(validation_decision_idiom IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_hyperbole TEXT CHECK(validation_decision_hyperbole IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_metonymy TEXT CHECK(validation_decision_metonymy IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_decision_other TEXT CHECK(validation_decision_other IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
                validation_reason_simile TEXT,
                validation_reason_metaphor TEXT,
                validation_reason_personification TEXT,
                validation_reason_idiom TEXT,
                validation_reason_hyperbole TEXT,
                validation_reason_metonymy TEXT,
                validation_reason_other TEXT,
                validation_response TEXT,
                validation_error TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (verse_id) REFERENCES verses (id)
            )
        ''')

        # Create indexes for performance
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses (reference)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses (book, chapter)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_llm_restriction ON verses (llm_restriction_error)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_language ON figurative_language (figurative_language)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_simile ON figurative_language (simile)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_metaphor ON figurative_language (metaphor)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_personification ON figurative_language (personification)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_idiom ON figurative_language (idiom)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_hyperbole ON figurative_language (hyperbole)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_metonymy ON figurative_language (metonymy)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_other ON figurative_language (other)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_figurative_language ON figurative_language (final_figurative_language)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_simile ON figurative_language (final_simile)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_metaphor ON figurative_language (final_metaphor)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_personification ON figurative_language (final_personification)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_idiom ON figurative_language (final_idiom)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_hyperbole ON figurative_language (final_hyperbole)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_metonymy ON figurative_language (final_metonymy)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_final_other ON figurative_language (final_other)')
        # Note: JSON fields (target, vehicle, ground, posture) are searchable but don't need simple indexes
        # Advanced JSON querying would require JSON1 extension for complex searches
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_confidence ON figurative_language (confidence)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_speaker ON figurative_language (speaker)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_purpose ON figurative_language (purpose)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_original_detection_types ON figurative_language (original_detection_types)')

        self.conn.commit()

    def insert_verse(self, verse_data: Dict) -> int:
        """Insert verse and return verse_id"""
        self.cursor.execute('''
            INSERT INTO verses (reference, book, chapter, verse, hebrew_text, hebrew_text_stripped, english_text, word_count, llm_restriction_error, llm_deliberation, instances_detected, instances_recovered, instances_lost_to_truncation, truncation_occurred)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            verse_data['reference'],
            verse_data['book'],
            verse_data['chapter'],
            verse_data['verse'],
            verse_data['hebrew'],
            verse_data.get('hebrew_stripped'),
            verse_data['english'],
            verse_data['word_count'],
            verse_data.get('llm_restriction_error'),
            verse_data.get('llm_deliberation'),
            verse_data.get('instances_detected'),
            verse_data.get('instances_recovered'),
            verse_data.get('instances_lost_to_truncation'),
            verse_data.get('truncation_occurred', 'no')
        ))

        return self.cursor.lastrowid

    def insert_figurative_language(self, verse_id: int, figurative_data: Dict) -> int:
        """Insert figurative language finding and return figurative_language_id"""
        self.cursor.execute('''
            INSERT INTO figurative_language
            (verse_id, figurative_language, simile, metaphor, personification, idiom, hyperbole, metonymy, other,
             final_figurative_language, final_simile, final_metaphor, final_personification, final_idiom,
             final_hyperbole, final_metonymy, final_other,
             target, vehicle, ground, posture,
             confidence, figurative_text, figurative_text_in_hebrew, figurative_text_in_hebrew_stripped,
             explanation, speaker, purpose, original_detection_types,
             figurative_detection_deliberation, tagging_analysis_deliberation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            verse_id,
            figurative_data.get('figurative_language', 'no'),
            figurative_data.get('simile', 'no'),
            figurative_data.get('metaphor', 'no'),
            figurative_data.get('personification', 'no'),
            figurative_data.get('idiom', 'no'),
            figurative_data.get('hyperbole', 'no'),
            figurative_data.get('metonymy', 'no'),
            figurative_data.get('other', 'no'),
            figurative_data.get('final_figurative_language', 'no'),
            figurative_data.get('final_simile', 'no'),
            figurative_data.get('final_metaphor', 'no'),
            figurative_data.get('final_personification', 'no'),
            figurative_data.get('final_idiom', 'no'),
            figurative_data.get('final_hyperbole', 'no'),
            figurative_data.get('final_metonymy', 'no'),
            figurative_data.get('final_other', 'no'),
            figurative_data.get('target', '[]'),  # Hierarchical JSON array
            figurative_data.get('vehicle', '[]'),  # Hierarchical JSON array
            figurative_data.get('ground', '[]'),  # Hierarchical JSON array
            figurative_data.get('posture', '[]'),  # Hierarchical JSON array
            figurative_data['confidence'],
            figurative_data.get('figurative_text'),
            figurative_data.get('figurative_text_in_hebrew'),
            figurative_data.get('figurative_text_in_hebrew_stripped'),
            figurative_data.get('explanation'),
            figurative_data.get('speaker'),
            figurative_data.get('purpose'),
            figurative_data.get('original_detection_types'),
            figurative_data.get('figurative_detection_deliberation', ''),
            figurative_data.get('tagging_analysis_deliberation', '')
        ))

        return self.cursor.lastrowid

    def update_validation_data(self, figurative_language_id: int, validation_data: Dict):
        """Update validation data for an existing figurative language entry"""
        self.cursor.execute('''
            UPDATE figurative_language
            SET validation_decision_simile = ?, validation_decision_metaphor = ?, validation_decision_personification = ?,
                validation_decision_idiom = ?, validation_decision_hyperbole = ?, validation_decision_metonymy = ?, validation_decision_other = ?,
                validation_reason_simile = ?, validation_reason_metaphor = ?, validation_reason_personification = ?,
                validation_reason_idiom = ?, validation_reason_hyperbole = ?, validation_reason_metonymy = ?, validation_reason_other = ?,
                final_figurative_language = ?, final_simile = ?, final_metaphor = ?, final_personification = ?,
                final_idiom = ?, final_hyperbole = ?, final_metonymy = ?, final_other = ?,
                validation_response = ?, validation_error = ?
            WHERE id = ?
        ''', (
            validation_data.get('validation_decision_simile'),
            validation_data.get('validation_decision_metaphor'),
            validation_data.get('validation_decision_personification'),
            validation_data.get('validation_decision_idiom'),
            validation_data.get('validation_decision_hyperbole'),
            validation_data.get('validation_decision_metonymy'),
            validation_data.get('validation_decision_other'),
            validation_data.get('validation_reason_simile'),
            validation_data.get('validation_reason_metaphor'),
            validation_data.get('validation_reason_personification'),
            validation_data.get('validation_reason_idiom'),
            validation_data.get('validation_reason_hyperbole'),
            validation_data.get('validation_reason_metonymy'),
            validation_data.get('validation_reason_other'),
            validation_data.get('final_figurative_language'),
            validation_data.get('final_simile'),
            validation_data.get('final_metaphor'),
            validation_data.get('final_personification'),
            validation_data.get('final_idiom'),
            validation_data.get('final_hyperbole'),
            validation_data.get('final_metonymy'),
            validation_data.get('final_other'),
            validation_data.get('validation_response'),
            validation_data.get('validation_error'),
            figurative_language_id
        ))

    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        # Count records
        self.cursor.execute('SELECT COUNT(*) FROM verses')
        verse_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM figurative_language')
        figurative_count = self.cursor.fetchone()[0]

        # Get type breakdown (count of each figurative language type - using final validated results)
        type_counts = {}
        for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
            self.cursor.execute(f'SELECT COUNT(*) FROM figurative_language WHERE final_{fig_type} = "yes"')
            type_counts[fig_type] = self.cursor.fetchone()[0]

        # Get average confidence
        self.cursor.execute('SELECT AVG(confidence) FROM figurative_language')
        avg_confidence = self.cursor.fetchone()[0] or 0.0

        return {
            'total_verses': verse_count,
            'total_figurative': figurative_count,
            'detection_rate': (figurative_count / verse_count * 100) if verse_count > 0 else 0,
            'avg_confidence': avg_confidence,
            'type_breakdown': type_counts
        }

    def get_top_findings(self, limit: int = 5) -> List[Tuple]:
        """Get top figurative language findings by confidence (using final validated results)"""
        self.cursor.execute('''
            SELECT v.reference, fl.final_figurative_language, fl.final_simile, fl.final_metaphor, fl.final_personification,
                   fl.final_idiom, fl.final_hyperbole, fl.final_metonymy, fl.final_other, fl.confidence, fl.figurative_text
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            WHERE fl.final_figurative_language = 'yes'
            ORDER BY fl.confidence DESC
            LIMIT ?
        ''', (limit,))

        return self.cursor.fetchall()

    def get_verses_with_figurative_language(self) -> List[Dict]:
        """Get all verses with their figurative language findings (both initial and final)"""
        self.cursor.execute('''
            SELECT
                v.reference,
                v.hebrew_text,
                v.english_text,
                v.word_count,
                fl.figurative_language,
                fl.simile, fl.metaphor, fl.personification,
                fl.idiom, fl.hyperbole, fl.metonymy, fl.other,
                fl.final_figurative_language,
                fl.final_simile, fl.final_metaphor, fl.final_personification,
                fl.final_idiom, fl.final_hyperbole, fl.final_metonymy, fl.final_other,
                fl.confidence,
                fl.figurative_text,
                fl.explanation
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            ORDER BY v.chapter, v.verse
        ''')

        return self.cursor.fetchall()

    def commit(self):
        """Commit changes"""
        if self.conn:
            self.conn.commit()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None