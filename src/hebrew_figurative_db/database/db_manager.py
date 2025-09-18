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
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create figurative language table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS figurative_language (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                verse_id INTEGER NOT NULL,
                type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other')),
                subcategory TEXT,
                subcategory_level_1 TEXT,
                subcategory_level_2 TEXT,
                confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
                figurative_text TEXT,
                figurative_text_in_hebrew TEXT,
                explanation TEXT,
                speaker TEXT,
                purpose TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (verse_id) REFERENCES verses (id)
            )
        ''')

        # Create indexes for performance
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses (reference)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses (book, chapter)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_verses_llm_restriction ON verses (llm_restriction_error)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_type ON figurative_language (type)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_subcategory ON figurative_language (subcategory)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_subcategory_level_1 ON figurative_language (subcategory_level_1)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_subcategory_level_2 ON figurative_language (subcategory_level_2)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_confidence ON figurative_language (confidence)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_speaker ON figurative_language (speaker)')
        self.cursor.execute('CREATE INDEX IF NOT EXISTS idx_figurative_purpose ON figurative_language (purpose)')

        self.conn.commit()

    def insert_verse(self, verse_data: Dict) -> int:
        """Insert verse and return verse_id"""
        self.cursor.execute('''
            INSERT INTO verses (reference, book, chapter, verse, hebrew_text, hebrew_text_stripped, english_text, word_count, llm_restriction_error)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            verse_data['reference'],
            verse_data['book'],
            verse_data['chapter'],
            verse_data['verse'],
            verse_data['hebrew'],
            verse_data.get('hebrew_stripped'),
            verse_data['english'],
            verse_data['word_count'],
            verse_data.get('llm_restriction_error')
        ))

        return self.cursor.lastrowid

    def insert_figurative_language(self, verse_id: int, figurative_data: Dict):
        """Insert figurative language finding"""
        self.cursor.execute('''
            INSERT INTO figurative_language
            (verse_id, type, subcategory, subcategory_level_1, subcategory_level_2, confidence, figurative_text, figurative_text_in_hebrew, explanation, speaker, purpose)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            verse_id,
            figurative_data['type'],
            figurative_data.get('subcategory'),
            figurative_data.get('subcategory_level_1'),
            figurative_data.get('subcategory_level_2'),
            figurative_data['confidence'],
            figurative_data.get('figurative_text'),
            figurative_data.get('figurative_text_in_hebrew'),
            figurative_data.get('explanation'),
            figurative_data.get('speaker'),
            figurative_data.get('purpose')
        ))

    def get_statistics(self) -> Dict:
        """Get processing statistics"""
        # Count records
        self.cursor.execute('SELECT COUNT(*) FROM verses')
        verse_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM figurative_language')
        figurative_count = self.cursor.fetchone()[0]

        # Get type breakdown
        self.cursor.execute('SELECT type, COUNT(*) FROM figurative_language GROUP BY type')
        type_counts = dict(self.cursor.fetchall())

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
        """Get top figurative language findings by confidence"""
        self.cursor.execute('''
            SELECT v.reference, fl.type, fl.confidence, fl.figurative_text
            FROM figurative_language fl
            JOIN verses v ON fl.verse_id = v.id
            ORDER BY fl.confidence DESC
            LIMIT ?
        ''', (limit,))

        return self.cursor.fetchall()

    def get_verses_with_figurative_language(self) -> List[Dict]:
        """Get all verses with their figurative language findings"""
        self.cursor.execute('''
            SELECT
                v.reference,
                v.hebrew_text,
                v.english_text,
                v.word_count,
                fl.type,
                fl.confidence,
                fl.text_snippet,
                fl.pattern_matched,
                fl.ai_analysis
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