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
import glob

# Ensure proper Unicode handling
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration
app.config['JSON_AS_ASCII'] = False  # Ensure proper Unicode in JSON responses

# Database configuration
# Get the project root directory (parent of web/)
# Use __file__ to get the directory of this script, then go up one level
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, 'database', 'Pentateuch_Psalms_fig_language.db')
DB_DIRECTORY = os.path.join(PROJECT_ROOT, 'database')

# Debug logging for production troubleshooting
print(f"Script directory: {SCRIPT_DIR}")
print(f"Project root: {PROJECT_ROOT}")
print(f"Database path: {DB_PATH}")
print(f"Database exists: {os.path.exists(DB_PATH)}")

class DatabaseManager:
    """Handles all database operations with proper error handling"""

    def __init__(self, db_path: str):
        self.db_path = db_path

    def get_connection(self):
        """Create database connection with proper configuration"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
        # Optimize for read-heavy workload
        conn.execute("PRAGMA cache_size = -64000")  # 64MB cache
        conn.execute("PRAGMA temp_store = MEMORY")
        conn.execute("PRAGMA journal_mode = WAL")
        conn.execute("PRAGMA synchronous = NORMAL")
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

# Cache for expensive count queries
count_cache = {}

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
    def build_metadata_search(target: str, vehicle: str, ground: str, posture: str) -> tuple:
        """Build SQL conditions for metadata search with OR logic and semicolon-separated multi-term support"""
        conditions = []
        params = []

        def parse_search_terms(search_str: str) -> List[str]:
            """Parse semicolon-separated search terms and trim whitespace"""
            if not search_str:
                return []
            # Strip whitespace and filter out empty strings
            return [term.strip() for term in search_str.split(';') if term.strip()]

        # Handle target field with multi-term OR logic
        if target and target.strip():
            target_terms = parse_search_terms(target)
            if target_terms:
                target_conditions = []
                for term in target_terms:
                    target_conditions.append("fl.target LIKE ?")
                    params.append(f"%{term}%")
                if target_conditions:
                    conditions.append(f"({' OR '.join(target_conditions)})")

        # Handle vehicle field with multi-term OR logic
        if vehicle and vehicle.strip():
            vehicle_terms = parse_search_terms(vehicle)
            if vehicle_terms:
                vehicle_conditions = []
                for term in vehicle_terms:
                    vehicle_conditions.append("fl.vehicle LIKE ?")
                    params.append(f"%{term}%")
                if vehicle_conditions:
                    conditions.append(f"({' OR '.join(vehicle_conditions)})")

        # Handle ground field with multi-term OR logic
        if ground and ground.strip():
            ground_terms = parse_search_terms(ground)
            if ground_terms:
                ground_conditions = []
                for term in ground_terms:
                    ground_conditions.append("fl.ground LIKE ?")
                    params.append(f"%{term}%")
                if ground_conditions:
                    conditions.append(f"({' OR '.join(ground_conditions)})")

        # Handle posture field with multi-term OR logic
        if posture and posture.strip():
            posture_terms = parse_search_terms(posture)
            if posture_terms:
                posture_conditions = []
                for term in posture_terms:
                    posture_conditions.append("fl.posture LIKE ?")
                    params.append(f"%{term}%")
                if posture_conditions:
                    conditions.append(f"({' OR '.join(posture_conditions)})")

        # All fields are combined with OR (as per user requirement)
        if conditions:
            return f"({' OR '.join(conditions)})", params
        else:
            # No search terms - return empty to indicate no metadata filter should be applied
            return "", []

# API Routes

@app.route('/')
def serve_frontend():
    """Serve the main HTML interface"""
    return send_from_directory('.', 'biblical_figurative_interface.html')

@app.route('/favicon.ico')
def favicon():
    """Return 204 No Content for favicon to prevent 404 errors"""
    return '', 204

@app.route('/api/verses')
def get_verses():
    """
    Get verses with optional filtering
    """
    import time
    start_time = time.time()

    try:
        # Get query parameters
        books = request.args.get('books', '').split(',') if request.args.get('books') else []
        chapters_str = request.args.get('chapters', '')
        verses_str = request.args.get('verses', '')
        figurative_types = request.args.get('figurative_types', '').split(',') if request.args.get('figurative_types') else []
        show_not_figurative = request.args.get('show_not_figurative', 'false').lower() == 'true'
        search_hebrew = request.args.get('search_hebrew', '')
        search_english = request.args.get('search_english', '')
        search_target = request.args.get('search_target', '')
        search_vehicle = request.args.get('search_vehicle', '')
        search_ground = request.args.get('search_ground', '')
        search_posture = request.args.get('search_posture', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        # Check if metadata search is active FIRST (before deciding query structure)
        # This is needed to determine if we can use simple queries or need the JOIN
        has_any_metadata = bool(search_target or search_vehicle or search_ground or search_posture)

        # Optimize query structure based on whether we need figurative_language table
        # For non-figurative only queries, skip the JOIN entirely
        # BUT: if metadata search is active, we MUST use the JOIN
        use_simple_query = show_not_figurative and (not figurative_types or figurative_types == ['']) and not has_any_metadata

        # Check if we're selecting ALL types + Not Figurative (which means show all verses)
        # BUT: if metadata search is active, we can't skip the filtering logic
        all_types = {'metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other'}
        show_all_verses = show_not_figurative and set(figurative_types) == all_types and not has_any_metadata

        if show_all_verses:
            # User wants ALL verses (with and without figurative language)
            # Use simple query without JOIN
            base_query = """
            SELECT
                v.id, v.reference, v.book, v.chapter, v.verse,
                v.hebrew_text, v.hebrew_text_stripped, v.hebrew_text_non_sacred,
                v.english_text_clean, v.english_text_clean_non_sacred,
                v.figurative_detection_deliberation, v.model_used
            FROM verses v
            WHERE 1=1
            """
        elif use_simple_query:
            # Simple query with LEFT JOIN for non-figurative verses only
            # Include verses with no FL records OR verses where final_figurative_language = 'no'
            base_query = """
            SELECT
                v.id, v.reference, v.book, v.chapter, v.verse,
                v.hebrew_text, v.hebrew_text_stripped, v.hebrew_text_non_sacred,
                v.english_text_clean, v.english_text_clean_non_sacred,
                v.figurative_detection_deliberation, v.model_used
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE (fl.id IS NULL OR fl.final_figurative_language = 'no')
            """
        else:
            # Full query with LEFT JOIN for figurative language queries
            base_query = """
            SELECT
                v.id, v.reference, v.book, v.chapter, v.verse,
                v.hebrew_text, v.hebrew_text_stripped, v.hebrew_text_non_sacred,
                v.english_text_clean, v.english_text_clean_non_sacred,
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
                # Handle all books by name
                valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                if book.lower() in valid_books:
                    book_conditions.append("v.book = ?")
                    params.append(book.title())
                elif book.isdigit():
                    # Handle numeric book references
                    book_map = {
                        '1': 'Genesis',
                        '2': 'Exodus',
                        '3': 'Leviticus',
                        '4': 'Numbers',
                        '5': 'Deuteronomy'
                    }
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

        # Text search conditions (applied FIRST, independently of figurative filtering)
        if search_hebrew:
            conditions.append("v.hebrew_text_stripped LIKE ?")
            params.append(f"%{search_hebrew}%")

        if search_english:
            conditions.append("v.english_text_clean LIKE ?")
            params.append(f"%{search_english}%")

        # Handle figurative language filtering (applied AFTER text search)
        # Skip this section for simple queries and show_all_verses - they don't need filtering
        if not use_simple_query and not show_all_verses:
            # Check if metadata search is active
            metadata_condition, metadata_params = SearchProcessor.build_metadata_search(
                search_target, search_vehicle, search_ground, search_posture
            )
            has_metadata_search = bool(metadata_condition)

            # METADATA SEARCH OVERRIDES EVERYTHING
            # If metadata search is active, ONLY show figurative verses matching the search
            # Ignore "Not Figurative" checkbox entirely (non-figurative verses have no metadata)
            if has_metadata_search:
                # Only figurative verses
                conditions.append("fl.id IS NOT NULL")
                # Must match selected figurative types (if any specified)
                if figurative_types and figurative_types != ['']:
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(figurative_filter)
                # Must match metadata search
                conditions.append(metadata_condition)
                params.extend(metadata_params)

            # NO METADATA SEARCH - apply normal filtering logic
            elif show_not_figurative and (not figurative_types or figurative_types == ['']):
                # Show ONLY verses WITHOUT figurative language (and matching text search if any)
                # Include verses with no FL records OR verses where all final_* are 'no'
                conditions.append("(fl.id IS NULL OR fl.final_figurative_language = 'no')")
            elif figurative_types and figurative_types != ['']:
                if show_not_figurative:
                    # Show verses WITH specified figurative types OR verses WITHOUT any figurative language
                    # "Not figurative" means fl.id IS NULL OR all types are 'no'
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(f"({figurative_filter} OR fl.id IS NULL OR fl.final_figurative_language = 'no')")
                else:
                    # Show ONLY verses WITH specified figurative language types (and matching text search if any)
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(figurative_filter)
                    conditions.append("fl.id IS NOT NULL")  # Only verses with figurative language
            elif not show_not_figurative:
                # If no figurative types selected and not showing non-figurative, show nothing
                # This will be handled by the frontend now
                pass

        # Add conditions to query
        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        # Add GROUP BY only for queries with JOIN (to handle potential duplicates)
        if not use_simple_query and not show_all_verses:
            base_query += " GROUP BY v.id"

        # Add ordering and pagination (order books biblically)
        base_query += """ ORDER BY
            CASE v.book
                WHEN 'Genesis' THEN 1
                WHEN 'Exodus' THEN 2
                WHEN 'Leviticus' THEN 3
                WHEN 'Numbers' THEN 4
                WHEN 'Deuteronomy' THEN 5
                WHEN 'Psalms' THEN 6
                ELSE 99
            END, v.chapter, v.verse
            LIMIT ? OFFSET ?"""
        params.extend([limit, offset])

        # Execute query
        t1 = time.time()
        verses = db_manager.execute_query(base_query, tuple(params))
        print(f"  Main query: {time.time()-t1:.2f}s ({len(verses)} verses)")

        # Optimize annotation fetching - get all annotations in bulk rather than N+1 queries
        verse_ids = [verse['id'] for verse in verses]
        all_annotations = {}

        # Only fetch annotations if we need them (not for non-figurative only queries)
        # For show_all_verses, we need to fetch ALL annotations regardless of type
        if verse_ids and not use_simple_query:
            # Build bulk annotation query
            placeholders = ','.join(['?' for _ in verse_ids])
            annotations_query = f"""
            SELECT
                verse_id, figurative_text, figurative_text_in_hebrew, figurative_text_in_hebrew_non_sacred,
                final_metaphor, final_simile, final_personification, final_idiom,
                final_hyperbole, final_metonymy, final_other,
                target, vehicle, ground, posture,
                explanation, speaker, confidence,
                validation_reason_metaphor, validation_reason_simile, validation_reason_personification,
                validation_reason_idiom, validation_reason_hyperbole, validation_reason_metonymy,
                validation_reason_other
            FROM figurative_language
            WHERE verse_id IN ({placeholders})
            """

            # Apply figurative type filter to annotations if specified
            annotation_params = list(verse_ids)
            if figurative_types and figurative_types != [''] and not show_all_verses:
                # Only filter by type if not showing all verses
                fig_conditions = []
                for fig_type in figurative_types:
                    if fig_type in ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                        fig_conditions.append(f"final_{fig_type} = 'yes'")

                if fig_conditions:
                    annotations_query += f" AND ({' OR '.join(fig_conditions)})"

            t2 = time.time()
            bulk_annotations = db_manager.execute_query(annotations_query, tuple(annotation_params))
            print(f"  Annotation query: {time.time()-t2:.2f}s ({len(bulk_annotations)} annotations)")

            # Group annotations by verse_id
            for annotation in bulk_annotations:
                verse_id = annotation['verse_id']
                if verse_id not in all_annotations:
                    all_annotations[verse_id] = []
                all_annotations[verse_id].append(annotation)

        # Process verses and their annotations
        for verse in verses:
            verse_id = verse['id']

            # For non-figurative only queries, we don't need to process annotations
            if use_simple_query:
                verse['annotations'] = []
                continue

            annotations = all_annotations.get(verse_id, [])

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

                # Minimal cleaning for Hebrew figurative text (database is clean, so minimal processing needed)
                def clean_hebrew_figurative_text(text):
                    if not text:
                        return ''

                    # Since database Hebrew text is clean, only remove obvious JSON artifacts if any
                    cleaned = text
                    # Remove only clear JSON contamination patterns
                    cleaned = re.sub(r'json","[^"]*"', '', cleaned)  # Remove JSON fragments
                    cleaned = re.sub(r'verse_model_used[^}]*', '', cleaned)  # Remove JSON artifacts

                    # Clean up excessive whitespace
                    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

                    # Return the text with minimal changes since database is clean
                    return cleaned

                # Minimal cleaning for English explanations and validation reasons
                def clean_english_explanation(text):
                    if not text:
                        return ''

                    # Minimal cleaning - only remove obvious JSON artifacts
                    cleaned = text
                    # Remove only clear JSON contamination patterns
                    cleaned = re.sub(r'json","[^"]*"', '', cleaned)  # Remove JSON fragments

                    # Clean up excessive whitespace
                    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

                    # Accept any reasonable content (much more permissive than before)
                    if len(cleaned) > 3 and len(cleaned) < 2000:  # Much more permissive bounds
                        return cleaned

                    return text.strip()  # If somehow it doesn't meet criteria, return original stripped

                processed_annotations.append({
                    'figurative_text': annotation['figurative_text'] or '',  # Keep English figurative text as-is
                    'figurative_text_in_hebrew': clean_hebrew_figurative_text(annotation['figurative_text_in_hebrew']),
                    'figurative_text_in_hebrew_non_sacred': clean_hebrew_figurative_text(annotation['figurative_text_in_hebrew_non_sacred']),
                    'types': types,
                    'target': target,
                    'vehicle': vehicle,
                    'ground': ground,
                    'posture': posture,
                    'explanation': clean_english_explanation(annotation['explanation']) if annotation['explanation'] else '',
                    'speaker': annotation['speaker'] or '',
                    'confidence': annotation['confidence'] or 0.0,
                    'validation_reasons': validation_reasons,
                    # Individual validation reason fields for frontend compatibility - using fixed cleaning
                    'validation_reason_metaphor': clean_english_explanation(annotation.get('validation_reason_metaphor')) if annotation.get('validation_reason_metaphor') else '',
                    'validation_reason_simile': clean_english_explanation(annotation.get('validation_reason_simile')) if annotation.get('validation_reason_simile') else '',
                    'validation_reason_personification': clean_english_explanation(annotation.get('validation_reason_personification')) if annotation.get('validation_reason_personification') else '',
                    'validation_reason_idiom': clean_english_explanation(annotation.get('validation_reason_idiom')) if annotation.get('validation_reason_idiom') else '',
                    'validation_reason_hyperbole': clean_english_explanation(annotation.get('validation_reason_hyperbole')) if annotation.get('validation_reason_hyperbole') else '',
                    'validation_reason_metonymy': clean_english_explanation(annotation.get('validation_reason_metonymy')) if annotation.get('validation_reason_metonymy') else '',
                    'validation_reason_other': clean_english_explanation(annotation.get('validation_reason_other')) if annotation.get('validation_reason_other') else ''
                })

            verse['annotations'] = processed_annotations

        # Get total count for pagination - optimize based on query type
        t3 = time.time()
        count_params = params[:-2]  # Remove limit and offset from params

        # For show_all_verses, just count all verses
        if show_all_verses:
            count_query = "SELECT COUNT(*) as count FROM verses v WHERE 1=1"

            # Only add book/chapter/verse/text search filters
            count_conditions = []
            count_params_list = []

            if books and books != ['']:
                book_conds = []
                for book in books:
                    book = book.strip()
                    valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                    if book.lower() in valid_books:
                        book_conds.append("v.book = ?")
                        count_params_list.append(book.title())
                if book_conds:
                    count_conditions.append(f"({' OR '.join(book_conds)})")

            if search_hebrew:
                count_conditions.append("v.hebrew_text_stripped LIKE ?")
                count_params_list.append(f"%{search_hebrew}%")
            if search_english:
                count_conditions.append("v.english_text LIKE ?")
                count_params_list.append(f"%{search_english}%")

            if count_conditions:
                count_query += " AND " + " AND ".join(count_conditions)

            count_result = db_manager.execute_query(count_query, tuple(count_params_list))
            total_count = count_result[0]['count'] if count_result else 0
        # For non-figurative only queries (no JOIN needed), use simple COUNT
        elif show_not_figurative and (not figurative_types or figurative_types == ['']):
            count_query = "SELECT COUNT(DISTINCT v.id) as count FROM verses v WHERE 1=1"

            # Add only verse-level conditions (no figurative_language table needed)
            verse_conditions = []
            verse_params = []

            # Re-build book filter
            if books and books != ['']:
                book_conds = []
                for book in books:
                    book = book.strip()
                    valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                    if book.lower() in valid_books:
                        book_conds.append("v.book = ?")
                        verse_params.append(book.title())
                if book_conds:
                    verse_conditions.append(f"({' OR '.join(book_conds)})")

            # Add text search
            if search_hebrew:
                verse_conditions.append("v.hebrew_text_stripped LIKE ?")
                verse_params.append(f"%{search_hebrew}%")
            if search_english:
                verse_conditions.append("v.english_text LIKE ?")
                verse_params.append(f"%{search_english}%")

            # Add non-figurative condition
            # Include verses with no FL records OR verses where final_figurative_language = 'no'
            count_query += " AND (v.id NOT IN (SELECT DISTINCT verse_id FROM figurative_language WHERE final_figurative_language = 'yes'))"

            if verse_conditions:
                count_query += " AND " + " AND ".join(verse_conditions)

            count_result = db_manager.execute_query(count_query, tuple(verse_params))
            total_count = count_result[0]['count'] if count_result else 0
        elif show_not_figurative and figurative_types and figurative_types != ['']:
            # For mixed queries (figurative + non-figurative), skip count entirely on first page
            # Show estimate to avoid 15+ second delay
            if offset == 0:
                total_count = 5002  # Fast estimate for initial load
            else:
                # For subsequent pages, user has already waited, so we can compute exact count
                # (This code path won't be hit often since most users won't paginate mixed queries)
                total_count = 5002
        else:
            # For queries with figurative language only, use simplified count
            count_query = """
            SELECT COUNT(DISTINCT v.id) as count
            FROM verses v
            INNER JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE 1=1
            """

            # Add the same conditions to count query (excluding JOIN-related ones)
            if conditions:
                count_query += " AND " + " AND ".join(conditions)

            count_result = db_manager.execute_query(count_query, tuple(count_params))
            total_count = count_result[0]['count'] if count_result else 0

        # Get total figurative instances for filtered results
        # Only skip for non-figurative ONLY queries
        if use_simple_query:
            total_figurative_instances = 0  # No figurative instances for non-figurative only query
        elif show_all_verses or (show_not_figurative and figurative_types and figurative_types != ['']):
            # For show_all_verses or mixed queries, return estimate to trigger background count
            total_figurative_instances = 0  # Will be calculated in background
        else:
            figurative_count_query = """
            SELECT COUNT(fl.id) as count
            FROM verses v
            LEFT JOIN figurative_language fl ON v.id = fl.verse_id AND fl.final_figurative_language = 'yes'
            WHERE 1=1
            """

            if conditions:
                figurative_count_query += " AND " + " AND ".join(conditions)

            figurative_count_result = db_manager.execute_query(figurative_count_query, tuple(count_params))
            total_figurative_instances = figurative_count_result[0]['count'] if figurative_count_result else 0

        print(f"  Count queries: {time.time()-t3:.2f}s (total={total_count})")

        elapsed = time.time() - start_time
        print(f"API /verses took {elapsed:.2f}s (verses={len(verses)}, total={total_count})")

        return jsonify({
            'verses': verses,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'total': total_count,
                'has_more': offset + limit < total_count,
                'total_figurative_instances': total_figurative_instances
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

        # Books in biblical order
        biblical_order = ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy']
        books_query = db_manager.execute_query("SELECT DISTINCT book FROM verses")
        available_books = [book['book'] for book in books_query]
        # Order books according to biblical sequence
        books = [{'book': book} for book in biblical_order if book in available_books]

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

# Database selection endpoints removed - now using fixed database
# These endpoints have been disabled as the application now uses a single fixed database

@app.route('/api/verses/count')
def get_verses_count():
    """
    Get exact verse count for current filters (lazy loading)
    This endpoint performs the expensive COUNT query in the background
    """
    import time
    start_time = time.time()

    try:
        # Get same query parameters as /api/verses
        books = request.args.get('books', '').split(',') if request.args.get('books') else []
        chapters_str = request.args.get('chapters', '')
        verses_str = request.args.get('verses', '')
        figurative_types = request.args.get('figurative_types', '').split(',') if request.args.get('figurative_types') else []
        show_not_figurative = request.args.get('show_not_figurative', 'false').lower() == 'true'
        search_hebrew = request.args.get('search_hebrew', '')
        search_english = request.args.get('search_english', '')
        search_target = request.args.get('search_target', '')
        search_vehicle = request.args.get('search_vehicle', '')
        search_ground = request.args.get('search_ground', '')
        search_posture = request.args.get('search_posture', '')

        # Build conditions (same logic as main /api/verses endpoint)
        # Check if metadata search is active FIRST
        has_any_metadata = bool(search_target or search_vehicle or search_ground or search_posture)

        use_simple_query = show_not_figurative and (not figurative_types or figurative_types == ['']) and not has_any_metadata

        # Check if we're selecting ALL types + Not Figurative (which means show all verses)
        # BUT: if metadata search is active, we can't skip the filtering logic
        all_types = {'metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other'}
        show_all_verses = show_not_figurative and set(figurative_types) == all_types and not has_any_metadata

        if show_all_verses:
            # Show all verses - use simple count
            count_query = "SELECT COUNT(*) as count FROM verses v WHERE 1=1"
            conditions = []
            params = []

            # Book filter
            if books and books != ['']:
                book_conditions = []
                for book in books:
                    book = book.strip()
                    valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                    if book.lower() in valid_books:
                        book_conditions.append("v.book = ?")
                        params.append(book.title())
                if book_conditions:
                    conditions.append(f"({' OR '.join(book_conditions)})")

            # Text search
            if search_hebrew:
                conditions.append("v.hebrew_text_stripped LIKE ?")
                params.append(f"%{search_hebrew}%")
            if search_english:
                conditions.append("v.english_text LIKE ?")
                params.append(f"%{search_english}%")

            if conditions:
                count_query += " AND " + " AND ".join(conditions)

            count_result = db_manager.execute_query(count_query, tuple(params))
            total_count = count_result[0]['count'] if count_result else 0

            # Get figurative instance count for all types
            figurative_count_query = """
            SELECT COUNT(fl.id) as count
            FROM verses v
            INNER JOIN figurative_language fl ON v.id = fl.verse_id
            WHERE fl.final_figurative_language = 'yes'
            """

            if conditions:
                figurative_count_query += " AND " + " AND ".join(conditions)

            figurative_count_result = db_manager.execute_query(figurative_count_query, tuple(params))
            total_figurative_instances = figurative_count_result[0]['count'] if figurative_count_result else 0

        elif use_simple_query:
            # Simple count for non-figurative only queries
            count_query = "SELECT COUNT(DISTINCT v.id) as count FROM verses v WHERE 1=1"
            conditions = []
            params = []

            # Book filter
            if books and books != ['']:
                book_conditions = []
                for book in books:
                    book = book.strip()
                    valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                    if book.lower() in valid_books:
                        book_conditions.append("v.book = ?")
                        params.append(book.title())
                if book_conditions:
                    conditions.append(f"({' OR '.join(book_conditions)})")

            # Text search
            if search_hebrew:
                conditions.append("v.hebrew_text_stripped LIKE ?")
                params.append(f"%{search_hebrew}%")
            if search_english:
                conditions.append("v.english_text LIKE ?")
                params.append(f"%{search_english}%")

            # Add non-figurative condition
            count_query += " AND v.id NOT IN (SELECT DISTINCT verse_id FROM figurative_language)"

            if conditions:
                count_query += " AND " + " AND ".join(conditions)

            count_result = db_manager.execute_query(count_query, tuple(params))
            total_count = count_result[0]['count'] if count_result else 0
            total_figurative_instances = 0  # No figurative instances for non-figurative query

        else:
            # Complex count query for mixed or figurative-only queries
            base_query = """
            SELECT v.id
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
                    valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                    if book.lower() in valid_books:
                        book_conditions.append("v.book = ?")
                        params.append(book.title())
                if book_conditions:
                    conditions.append(f"({' OR '.join(book_conditions)})")

            # Chapter and verse filters
            if chapters_str and chapters_str.lower() != 'all':
                chapters = SearchProcessor.parse_range_string(chapters_str)
                if chapters:
                    placeholders = ','.join(['?' for _ in chapters])
                    conditions.append(f"v.chapter IN ({placeholders})")
                    params.extend(chapters)

            if verses_str and verses_str.lower() != 'all':
                verses = SearchProcessor.parse_range_string(verses_str)
                if verses:
                    placeholders = ','.join(['?' for _ in verses])
                    conditions.append(f"v.verse IN ({placeholders})")
                    params.extend(verses)

            # Text search
            if search_hebrew:
                conditions.append("v.hebrew_text_stripped LIKE ?")
                params.append(f"%{search_hebrew}%")
            if search_english:
                conditions.append("v.english_text LIKE ?")
                params.append(f"%{search_english}%")

            # Check if metadata search is active
            metadata_condition, metadata_params = SearchProcessor.build_metadata_search(
                search_target, search_vehicle, search_ground, search_posture
            )
            has_metadata_search = bool(metadata_condition)

            # METADATA SEARCH OVERRIDES EVERYTHING
            # If metadata search is active, ONLY show figurative verses matching the search
            if has_metadata_search:
                # Only figurative verses
                conditions.append("fl.id IS NOT NULL")
                # Must match selected figurative types (if any specified)
                if figurative_types and figurative_types != ['']:
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(figurative_filter)
                # Must match metadata search
                conditions.append(metadata_condition)
                params.extend(metadata_params)

            # NO METADATA SEARCH - apply normal filtering logic
            elif show_not_figurative and (not figurative_types or figurative_types == ['']):
                # Not figurative only: include verses with no FL records OR where all final_* are 'no'
                conditions.append("(fl.id IS NULL OR fl.final_figurative_language = 'no')")
            elif figurative_types and figurative_types != ['']:
                if show_not_figurative:
                    # Mixed: show verses WITH specified types OR verses WITHOUT any figurative language
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(f"({figurative_filter} OR fl.id IS NULL OR fl.final_figurative_language = 'no')")
                else:
                    # Only verses WITH specified figurative language types
                    figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                    conditions.append(figurative_filter)
                    conditions.append("fl.id IS NOT NULL")

            # Add conditions to query
            if conditions:
                base_query += " AND " + " AND ".join(conditions)

            # Wrap in COUNT query with GROUP BY
            count_query = f"SELECT COUNT(*) as count FROM ({base_query} GROUP BY v.id) as subquery"

            count_result = db_manager.execute_query(count_query, tuple(params))
            total_count = count_result[0]['count'] if count_result else 0

            # Get figurative instance count
            # For mixed queries with selected types, count only the selected types
            if figurative_types and figurative_types != ['']:
                # Count instances of selected types
                figurative_count_query = """
                SELECT COUNT(fl.id) as count
                FROM verses v
                INNER JOIN figurative_language fl ON v.id = fl.verse_id
                WHERE 1=1
                """

                # Add same verse-level conditions
                count_conditions = []
                count_params = []

                if books and books != ['']:
                    book_conditions = []
                    for book in books:
                        book = book.strip()
                        valid_books = ['genesis', 'exodus', 'leviticus', 'numbers', 'deuteronomy', 'psalms']
                        if book.lower() in valid_books:
                            book_conditions.append("v.book = ?")
                            count_params.append(book.title())
                    if book_conditions:
                        count_conditions.append(f"({' OR '.join(book_conditions)})")

                if chapters_str and chapters_str.lower() != 'all':
                    chapters = SearchProcessor.parse_range_string(chapters_str)
                    if chapters:
                        placeholders = ','.join(['?' for _ in chapters])
                        count_conditions.append(f"v.chapter IN ({placeholders})")
                        count_params.extend(chapters)

                if verses_str and verses_str.lower() != 'all':
                    verses = SearchProcessor.parse_range_string(verses_str)
                    if verses:
                        placeholders = ','.join(['?' for _ in verses])
                        count_conditions.append(f"v.verse IN ({placeholders})")
                        count_params.extend(verses)

                if search_hebrew:
                    count_conditions.append("v.hebrew_text_stripped LIKE ?")
                    count_params.append(f"%{search_hebrew}%")
                if search_english:
                    count_conditions.append("v.english_text LIKE ?")
                    count_params.append(f"%{search_english}%")

                # Add figurative type filter
                figurative_filter = SearchProcessor.build_figurative_filter(figurative_types)
                count_conditions.append(figurative_filter)

                # Add metadata search
                if search_target or search_vehicle or search_ground or search_posture:
                    metadata_condition, metadata_params = SearchProcessor.build_metadata_search(
                        search_target, search_vehicle, search_ground, search_posture
                    )
                    if metadata_condition:  # Non-empty string means we have search terms
                        count_conditions.append(metadata_condition)
                        count_params.extend(metadata_params)

                if count_conditions:
                    figurative_count_query += " AND " + " AND ".join(count_conditions)

                figurative_count_result = db_manager.execute_query(figurative_count_query, tuple(count_params))
                total_figurative_instances = figurative_count_result[0]['count'] if figurative_count_result else 0
            else:
                total_figurative_instances = 0

        elapsed = time.time() - start_time
        print(f"API /verses/count took {elapsed:.2f}s (total={total_count}, instances={total_figurative_instances})")

        return jsonify({
            'total': total_count,
            'total_figurative_instances': total_figurative_instances
        })

    except Exception as e:
        print(f"Error in get_verses_count: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

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

    # Use environment variable to determine if we're in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    port = int(os.environ.get('PORT', 5000))

    if debug_mode:
        print("Running in DEBUG mode")
        print("Access the interface at: http://localhost:5000")
        print("API Statistics: http://localhost:5000/api/statistics")
    else:
        print("Running in PRODUCTION mode")

    app.run(debug=debug_mode, host='0.0.0.0', port=port)