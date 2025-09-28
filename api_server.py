#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask API server for Biblical Figurative Language Interface
Serves data from the SQLite database with advanced filtering and search capabilities
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sqlite3
import json
import re
from typing import List, Dict, Any, Optional
import os
import sys
import traceback

# Ensure proper Unicode handling
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration
app.config['JSON_AS_ASCII'] = False  # Ensure proper Unicode in JSON responses

# Database configuration
DB_PATH = r"C:\Users\ariro\OneDrive\Documents\Bible\2books_c63_multi_v_parallel_20250928_0934.db"

class DatabaseManager:
    """Handles all database operations with proper error handling"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        """Create database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        return conn

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and return results as list of dictionaries"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise  # Re-raise to be handled by Flask error handler
        except Exception as e:
            print(f"Unexpected error in execute_query: {e}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            raise

# Initialize database manager
db_manager = DatabaseManager(DB_PATH)

class SearchProcessor:
    """Handles complex search logic and filtering"""

    @staticmethod
    def parse_range_string(range_str: str) -> List[int]:
        """Parse range strings like '1,3,5-7,10' into list of integers"""
        if not range_str or range_str.lower() == 'all':
            return []

        result = []
        parts = range_str.split(',')

        for part in parts:
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                result.extend(range(start, end + 1))
            else:
                result.append(int(part))

        return sorted(list(set(result)))  # Remove duplicates and sort

    @staticmethod
    def build_figurative_filter(types: List[str]) -> str:
        """Build SQL filter for figurative language types"""
        if not types:
            return "1=1"

        conditions = []
        for fig_type in types:
            if fig_type in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                conditions.append(f"fl.final_{fig_type} = 'yes'")

        return f"({' OR '.join(conditions)})" if conditions else "1=1"

    @staticmethod
    def build_metadata_search(target: str, vehicle: str, ground: str, posture: str, operator: str) -> tuple:
        """Build SQL conditions for metadata search with AND/OR logic"""
        conditions = []
        params = []

        if target:
            conditions.append("fl.target LIKE ?")
            params.append(f"%{target}%")

        if vehicle:
            conditions.append("fl.vehicle LIKE ?")
            params.append(f"%{vehicle}%")

        if ground:
            conditions.append("fl.ground LIKE ?")
            params.append(f"%{ground}%")

        if posture:
            conditions.append("fl.posture LIKE ?")
            params.append(f"%{posture}%")

        if not conditions:
            return "1=1", []

        joiner = " AND " if operator.upper() == "AND" else " OR "
        return f"({joiner.join(conditions)})", params

# API Routes

@app.route('/')
def serve_frontend():
    """Serve the main HTML interface"""
    return send_from_directory('.', 'biblical_figurative_interface.html')

@app.route('/api/verses')
def get_verses():
    """
    Get verses with optional filtering
    """
    try:
        # Get query parameters
        books = request.args.get('books', '').split(',') if request.args.get('books') else []
        chapters_str = request.args.get('chapters', '')
        verses_str = request.args.get('verses', '')
        figurative_types = request.args.get('figurative_types', '').split(',') if request.args.get('figurative_types') else []
        search_hebrew = request.args.get('search_hebrew', '')
        search_target = request.args.get('search_target', '')
        search_vehicle = request.args.get('search_vehicle', '')
        search_ground = request.args.get('search_ground', '')
        search_posture = request.args.get('search_posture', '')
        search_operator = request.args.get('search_operator', 'AND')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Build base query
        base_query = """
        SELECT DISTINCT
            v.id, v.reference, v.book, v.chapter, v.verse,
            v.hebrew_text, v.hebrew_text_non_sacred,
            v.english_text, v.english_text_non_sacred,
            v.figurative_detection_deliberation, v.model_used
        FROM verses v
        LEFT JOIN figurative_language fl ON v.id = fl.verse_id
        WHERE 1=1
        """

        conditions = []
        params = []

        # Book filter
        if books and books != ['']:
            book_conditions = []
            for book in books:
                book = book.strip()
                if book.lower() in ['leviticus', 'numbers']:
                    book_conditions.append("v.book = ?")
                    params.append(book.title())
                elif book.isdigit():
                    # Handle numeric book references (3=Leviticus, 4=Numbers)
                    book_map = {'3': 'Leviticus', '4': 'Numbers'}
                    if book in book_map:
                        book_conditions.append("v.book = ?")
                        params.append(book_map[book])

            if book_conditions:
                conditions.append(f"({' OR '.join(book_conditions)})")

        # Chapter filter
        if chapters_str and chapters_str.lower() != 'all':
            chapters = SearchProcessor.parse_range_string(chapters_str)
            if chapters:
                placeholders = ','.join(['?' for _ in chapters])
                conditions.append(f"v.chapter IN ({placeholders})")
                params.extend(chapters)

        # Verse filter
        if verses_str and verses_str.lower() != 'all':
            verses = SearchProcessor.parse_range_string(verses_str)
            if verses:
                placeholders = ','.join(['?' for _ in verses])
                conditions.append(f"v.verse IN ({placeholders})")
                params.extend(verses)

        # Hebrew text search
        if search_hebrew:
            conditions.append("v.hebrew_text_stripped LIKE ?")
            params.append(f"%{search_hebrew}%")

        # Figurative type filter (only show verses with figurative language if types specified)
        if figurative_types and figurative_types != ['']:
            figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
            conditions.append(figurative_filter)
            conditions.append("fl.id IS NOT NULL")  # Only verses with figurative language

        # Metadata search
        metadata_condition, metadata_params = SearchProcessor.build_metadata_search(
            search_target, search_vehicle, search_ground, search_posture, search_operator
        )
        if metadata_params:
            conditions.append(metadata_condition)
            params.extend(metadata_params)
            conditions.append("fl.id IS NOT NULL")  # Only verses with figurative language

        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        # Add ordering and pagination
        base_query += " ORDER BY v.book, v.chapter, v.verse LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        # Execute query
        verses = db_manager.execute_query(base_query, tuple(params))

        # Get annotations for each verse
        for verse in verses:
            annotations_query = """
            SELECT
                figurative_text, figurative_text_in_hebrew, figurative_text_in_hebrew_non_sacred,
                final_metaphor, final_simile, final_personification, final_idiom,
                final_hyperbole, final_metonymy, final_other,
                target, vehicle, ground, posture,
                explanation, speaker, confidence,
                validation_reason_metaphor, validation_reason_simile, validation_reason_personification,
                validation_reason_idiom, validation_reason_hyperbole, validation_reason_metonymy,
                validation_reason_other
            FROM figurative_language
            WHERE verse_id = ?
            """

            # Apply figurative type filter to annotations if specified
            if figurative_types and figurative_types != ['']:
                # Note: no 'fl.' alias needed here since we're querying figurative_language directly
                fig_conditions = []
                for fig_type in figurative_types:
                    if fig_type in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                        fig_conditions.append(f"final_{fig_type} = 'yes'")

                if fig_conditions:
                    annotations_query += f" AND ({' OR '.join(fig_conditions)})"

            annotations = db_manager.execute_query(annotations_query, (verse['id'],))

            # Process annotations
            processed_annotations = []
            for annotation in annotations:
                # Determine which types are present
                types = []
                if annotation['final_metaphor'] == 'yes':
                    types.append('metaphor')
                if annotation['final_simile'] == 'yes':
                    types.append('simile')
                if annotation['final_personification'] == 'yes':
                    types.append('personification')
                if annotation['final_idiom'] == 'yes':
                    types.append('idiom')
                if annotation['final_hyperbole'] == 'yes':
                    types.append('hyperbole')
                if annotation['final_metonymy'] == 'yes':
                    types.append('metonymy')
                if annotation['final_other'] == 'yes':
                    types.append('other')

                # Parse JSON fields safely
                try:
                    target = json.loads(annotation['target']) if annotation['target'] else []
                    vehicle = json.loads(annotation['vehicle']) if annotation['vehicle'] else []
                    ground = json.loads(annotation['ground']) if annotation['ground'] else []
                    posture = json.loads(annotation['posture']) if annotation['posture'] else []
                except (json.JSONDecodeError, TypeError):
                    target = annotation['target'] or []
                    vehicle = annotation['vehicle'] or []
                    ground = annotation['ground'] or []
                    posture = annotation['posture'] or []

                # Collect validation reasons
                validation_reasons = {}
                for type_name in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    reason = annotation.get(f'validation_reason_{type_name}')
                    if reason:
                        validation_reasons[type_name] = reason

                processed_annotations.append({
                    'figurative_text': annotation['figurative_text'] or '',
                    'figurative_text_in_hebrew': annotation['figurative_text_in_hebrew'] or '',
                    'figurative_text_in_hebrew_non_sacred': annotation['figurative_text_in_hebrew_non_sacred'] or '',
                    'types': types,
                    'target': target,
                    'vehicle': vehicle,
                    'ground': ground,
                    'posture': posture,
                    'explanation': annotation['explanation'] or '',
                    'speaker': annotation['speaker'] or '',
                    'confidence': annotation['confidence'] or 0.0,
                    'validation_reasons': validation_reasons
                })

            verse['annotations'] = processed_annotations

        # Get total count for pagination
        count_query = base_query.replace(
            "SELECT DISTINCT\n            v.id, v.reference, v.book, v.chapter, v.verse,\n            v.hebrew_text, v.hebrew_text_non_sacred,\n            v.english_text, v.english_text_non_sacred,\n            v.figurative_detection_deliberation, v.model_used",
            "SELECT COUNT(DISTINCT v.id) as count"
        ).replace(" ORDER BY v.book, v.chapter, v.verse LIMIT ? OFFSET ?", "")

        # Remove limit and offset from params for count query
        count_params = params[:-2]
        count_result = db_manager.execute_query(count_query, tuple(count_params))
        total_count = count_result[0]['count'] if count_result else 0

        return jsonify({
            'verses': verses,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total_count,
                'has_more': offset + limit < total_count
            }
        })

    except Exception as e:
        print(f"Error in get_verses: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.route('/api/statistics')
def get_statistics():
    """Get database statistics"""
    try:
        # Total verses
        total_verses = db_manager.execute_query("SELECT COUNT(*) as count FROM verses")[0]['count']

        # Total figurative instances
        total_instances = db_manager.execute_query("SELECT COUNT(*) as count FROM figurative_language")[0]['count']

        # Books
        books = db_manager.execute_query("SELECT DISTINCT book FROM verses ORDER BY book")

        # Figurative type counts
        type_counts = {}
        for type_name in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
            count = db_manager.execute_query(
                f"SELECT COUNT(*) as count FROM figurative_language WHERE final_{type_name} = 'yes'"
            )[0]['count']
            type_counts[type_name] = count

        # Model usage
        model_usage = db_manager.execute_query("""
            SELECT model_used, COUNT(*) as count
            FROM figurative_language
            WHERE model_used IS NOT NULL
            GROUP BY model_used
        """)

        return jsonify({
            'total_verses': total_verses,
            'total_instances': total_instances,
            'books': [book['book'] for book in books],
            'type_counts': type_counts,
            'model_usage': {item['model_used']: item['count'] for item in model_usage}
        })

    except Exception as e:
        print(f"Error in get_statistics: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@app.route('/api/search/suggestions')
def get_search_suggestions():
    """Get autocomplete suggestions for search fields"""
    try:
        field = request.args.get('field')
        query = request.args.get('query', '')

        if not field or len(query) < 2:
            return jsonify([])

        suggestions = []

        if field in ['target', 'vehicle', 'ground', 'posture']:
            # Get unique values from JSON arrays
            results = db_manager.execute_query(f"SELECT DISTINCT {field} FROM figurative_language WHERE {field} IS NOT NULL")

            for result in results:
                try:
                    json_data = json.loads(result[field])
                    if isinstance(json_data, list):
                        for item in json_data:
                            if query.lower() in item.lower() and item not in suggestions:
                                suggestions.append(item)
                except (json.JSONDecodeError, TypeError):
                    # Handle non-JSON data
                    if result[field] and query.lower() in result[field].lower() and result[field] not in suggestions:
                        suggestions.append(result[field])

        return jsonify(suggestions[:10])  # Limit to 10 suggestions

    except Exception as e:
        print(f"Error in get_search_suggestions: {e}")
        return jsonify([])

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Check if database exists
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        print("Please ensure the database file exists and the path is correct.")
        exit(1)

    print("Starting Biblical Figurative Language API Server...")
    print(f"Database: {DB_PATH}")
    print("Access the interface at: http://localhost:5000")
    print("API Statistics: http://localhost:5000/api/statistics")

    app.run(debug=True, host='0.0.0.0', port=5000)