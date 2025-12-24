#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Parallel Flexible Tagging Processor
User-friendly interface with high-performance parallel processing

Version: 2.1.0
Last Updated: December 2024
"""
import sys
import os
import logging
import traceback
import json
import time
import re
import uuid
import hashlib
import concurrent.futures
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional, Any

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Pipeline version for tracking
PIPELINE_VERSION = "2.1.0"

# Books configuration - centralized definition
SUPPORTED_BOOKS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27,
    "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
    "Proverbs": 31, "Isaiah": 66, "Jeremiah": 52
}

# Books that use batched processing (prophetic/wisdom literature)
BATCHED_PROCESSING_BOOKS = ["Proverbs", "Isaiah", "Jeremiah"]

# Verse count estimates for progress reporting
VERSE_ESTIMATES = {
    "Genesis": 1533, "Exodus": 1213, "Leviticus": 859,
    "Numbers": 1288, "Deuteronomy": 959, "Psalms": 2461,
    "Proverbs": 915, "Isaiah": 1292, "Jeremiah": 1364
}

# Token limits - increased for prophetic books with longer chapters
MAX_COMPLETION_TOKENS_DEFAULT = 65536
MAX_COMPLETION_TOKENS_PROPHETIC = 100000  # Higher limit for Jeremiah, Isaiah

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Import our flexible tagging client
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

# OpenAI import for batched processing
from openai import OpenAI

# Pydantic for JSON schema validation
try:
    from pydantic import BaseModel, Field, ValidationError
    from typing import Literal
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False


# JSON Schema Models for LLM Response Validation
if PYDANTIC_AVAILABLE:
    class FigurativeInstance(BaseModel):
        """Schema for a single figurative language instance from LLM."""
        verse: int = Field(..., ge=1, description="Verse number")
        figurative_text: str = Field(..., min_length=1, description="The figurative expression")
        explanation: str = Field(..., min_length=10, description="Explanation of the figurative language")
        confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
        metaphor: Optional[Literal["yes", "no"]] = Field(default="no")
        simile: Optional[Literal["yes", "no"]] = Field(default="no")
        personification: Optional[Literal["yes", "no"]] = Field(default="no")
        idiom: Optional[Literal["yes", "no"]] = Field(default="no")
        hyperbole: Optional[Literal["yes", "no"]] = Field(default="no")
        metonymy: Optional[Literal["yes", "no"]] = Field(default="no")
        other: Optional[Literal["yes", "no"]] = Field(default="no")

    class ChapterResponse(BaseModel):
        """Schema for the complete chapter response from LLM."""
        instances: List[FigurativeInstance] = Field(default_factory=list)

    def validate_llm_response(response_data: List[Dict], logger=None) -> Tuple[List[Dict], List[str]]:
        """
        Validate LLM response against Pydantic schema.

        Returns:
            Tuple of (valid_instances, validation_errors)
        """
        valid_instances = []
        errors = []

        for i, item in enumerate(response_data):
            try:
                validated = FigurativeInstance(**item)
                valid_instances.append(validated.model_dump())
            except ValidationError as e:
                error_msg = f"Instance {i}: {e.errors()}"
                errors.append(error_msg)
                if logger:
                    logger.warning(f"[SCHEMA VALIDATION] {error_msg}")

        return valid_instances, errors
else:
    def validate_llm_response(response_data: List[Dict], logger=None) -> Tuple[List[Dict], List[str]]:
        """Fallback validation when pydantic is not available."""
        # Basic validation without pydantic
        valid_instances = []
        errors = []

        for i, item in enumerate(response_data):
            if not isinstance(item, dict):
                errors.append(f"Instance {i}: Not a dictionary")
                continue

            # Check required fields
            if 'verse' not in item:
                errors.append(f"Instance {i}: Missing 'verse' field")
                continue

            if 'figurative_text' not in item or not item.get('figurative_text'):
                errors.append(f"Instance {i}: Missing or empty 'figurative_text'")
                continue

            # Normalize confidence
            if 'confidence' in item:
                try:
                    conf = float(item['confidence'])
                    if conf < 0 or conf > 1:
                        item['confidence'] = max(0.0, min(1.0, conf))
                except (TypeError, ValueError):
                    item['confidence'] = 0.5

            valid_instances.append(item)

        return valid_instances, errors


class RunContext:
    """Context object for tracking a processing run's state and failures."""

    def __init__(self, book_selections: Dict, output_dir: str = "."):
        self.run_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        self.started_at = datetime.now().isoformat()
        self.book_selections = book_selections
        self.output_dir = output_dir

        # Failure tracking
        self.failed_chapters: List[Dict] = []
        self.failed_verses: List[Dict] = []
        self.validation_issues: List[Dict] = []
        self.streaming_corruptions: List[Dict] = []

        # Success tracking
        self.processed_chapters: List[Dict] = []
        self.total_verses_processed = 0
        self.total_instances_detected = 0
        self.total_cost = 0.0

        # Model tracking
        self.models_used: Dict[str, int] = {}

    def add_chapter_failure(self, book: str, chapter: int, reason: str,
                           verses_attempted: int = 0, raw_response_file: str = None,
                           error_type: str = "unknown"):
        """Record a chapter-level failure."""
        self.failed_chapters.append({
            "type": "chapter_complete_failure",
            "book": book,
            "chapter": chapter,
            "reason": reason,
            "error_type": error_type,
            "verses_attempted": verses_attempted,
            "raw_response_file": raw_response_file,
            "retry_command": f"python interactive_parallel_processor.py {book} {chapter}",
            "timestamp": datetime.now().isoformat()
        })

    def add_verse_failure(self, book: str, chapter: int, verse: int, reason: str,
                         error_type: str = "unknown"):
        """Record a verse-level failure."""
        self.failed_verses.append({
            "type": "verse_failure",
            "book": book,
            "chapter": chapter,
            "verse": verse,
            "reason": reason,
            "error_type": error_type,
            "timestamp": datetime.now().isoformat()
        })

    def add_streaming_corruption(self, book: str, chapter: int,
                                 corrupted_chunks: int, affected_verses: List[int]):
        """Record streaming corruption events."""
        self.streaming_corruptions.append({
            "book": book,
            "chapter": chapter,
            "corrupted_chunks": corrupted_chunks,
            "affected_verses": affected_verses,
            "timestamp": datetime.now().isoformat()
        })

    def add_validation_issue(self, book: str, chapter: int,
                            coverage_rate: float, total_instances: int,
                            validated_instances: int):
        """Record validation coverage issues."""
        self.validation_issues.append({
            "book": book,
            "chapter": chapter,
            "coverage_rate": coverage_rate,
            "total_instances": total_instances,
            "validated_instances": validated_instances,
            "missing_count": total_instances - validated_instances,
            "timestamp": datetime.now().isoformat()
        })

    def record_chapter_success(self, book: str, chapter: int,
                               verses_stored: int, instances_stored: int,
                               processing_time: float, cost: float,
                               model_used: str):
        """Record successful chapter processing."""
        self.processed_chapters.append({
            "book": book,
            "chapter": chapter,
            "verses_stored": verses_stored,
            "instances_stored": instances_stored,
            "processing_time": processing_time,
            "cost": cost,
            "model_used": model_used,
            "timestamp": datetime.now().isoformat()
        })
        self.total_verses_processed += verses_stored
        self.total_instances_detected += instances_stored
        self.total_cost += cost

        # Track model usage
        self.models_used[model_used] = self.models_used.get(model_used, 0) + 1

    def track_model_usage(self, model: str):
        """Track which models were used."""
        self.models_used[model] = self.models_used.get(model, 0) + 1

    def get_failure_manifest(self) -> Dict:
        """Generate the structured failure manifest."""
        return {
            "run_id": self.run_id,
            "pipeline_version": PIPELINE_VERSION,
            "started_at": self.started_at,
            "completed_at": datetime.now().isoformat(),
            "summary": {
                "total_chapters_attempted": len(self.processed_chapters) + len(self.failed_chapters),
                "successful_chapters": len(self.processed_chapters),
                "failed_chapters": len(self.failed_chapters),
                "failed_verses": len(self.failed_verses),
                "validation_issues": len(self.validation_issues),
                "streaming_corruptions": len(self.streaming_corruptions),
                "total_verses_processed": self.total_verses_processed,
                "total_instances_detected": self.total_instances_detected,
                "total_cost": round(self.total_cost, 4),
                "models_used": self.models_used
            },
            "failed_items": self.failed_chapters + self.failed_verses,
            "validation_issues": self.validation_issues,
            "streaming_corruptions": self.streaming_corruptions,
            "retry_commands": [f["retry_command"] for f in self.failed_chapters]
        }

    def save_failure_manifest(self, base_filename: str) -> str:
        """Save the failure manifest to a JSON file."""
        manifest = self.get_failure_manifest()
        manifest_file = f"{base_filename}_failures.json"
        manifest_path = os.path.join(self.output_dir, manifest_file)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest_path

    def get_processing_manifest(self) -> Dict:
        """Generate the processing manifest for documentation."""
        return {
            "run_id": self.run_id,
            "pipeline_version": PIPELINE_VERSION,
            "started_at": self.started_at,
            "completed_at": datetime.now().isoformat(),
            "configuration": {
                "book_selections": {
                    k: "FULL_BOOK" if v == "FULL_BOOK" else list(v.keys())
                    for k, v in self.book_selections.items()
                },
                "max_completion_tokens_default": MAX_COMPLETION_TOKENS_DEFAULT,
                "max_completion_tokens_prophetic": MAX_COMPLETION_TOKENS_PROPHETIC,
                "batched_processing_books": BATCHED_PROCESSING_BOOKS
            },
            "results": {
                "total_verses_processed": self.total_verses_processed,
                "total_instances_detected": self.total_instances_detected,
                "detection_rate": round(self.total_instances_detected / max(1, self.total_verses_processed), 3),
                "total_cost": round(self.total_cost, 4),
                "models_used": self.models_used,
                "success_rate": round(
                    len(self.processed_chapters) /
                    max(1, len(self.processed_chapters) + len(self.failed_chapters)) * 100,
                    1
                )
            },
            "chapters_processed": self.processed_chapters,
            "failures_summary": {
                "chapter_failures": len(self.failed_chapters),
                "verse_failures": len(self.failed_verses),
                "validation_issues": len(self.validation_issues)
            }
        }

    def save_processing_manifest(self, base_filename: str) -> str:
        """Save the processing manifest to a JSON file."""
        manifest = self.get_processing_manifest()
        manifest_file = f"{base_filename}_manifest.json"
        manifest_path = os.path.join(self.output_dir, manifest_file)

        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        return manifest_path


class SefariaCache:
    """Simple file-based cache for Sefaria API responses."""

    def __init__(self, cache_dir: str = ".sefaria_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, reference: str) -> str:
        """Generate a cache key from a reference."""
        return hashlib.md5(reference.encode()).hexdigest()

    def _get_cache_path(self, reference: str) -> Path:
        """Get the cache file path for a reference."""
        return self.cache_dir / f"{self._get_cache_key(reference)}.json"

    def get(self, reference: str) -> Optional[Tuple[List[Dict], Any]]:
        """Get cached data for a reference."""
        cache_path = self._get_cache_path(reference)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('verses_data'), data.get('metadata')
            except (json.JSONDecodeError, KeyError):
                return None
        return None

    def set(self, reference: str, verses_data: List[Dict], metadata: Any = None):
        """Cache data for a reference."""
        cache_path = self._get_cache_path(reference)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump({
                'reference': reference,
                'verses_data': verses_data,
                'metadata': metadata,
                'cached_at': datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)

    def has(self, reference: str) -> bool:
        """Check if a reference is cached."""
        return self._get_cache_path(reference).exists()


def get_recommended_batches(book_name: str, total_chapters: int = None, batch_size: int = 10) -> List[Tuple[int, int]]:
    """
    Get recommended chapter batches for processing a book.

    For large books like Jeremiah (52 chapters), returns batches of ~10 chapters
    to reduce risk of complete run failure.

    Args:
        book_name: Name of the book
        total_chapters: Override chapter count (uses SUPPORTED_BOOKS if None)
        batch_size: Target chapters per batch (default 10)

    Returns:
        List of (start_chapter, end_chapter) tuples
    """
    if total_chapters is None:
        total_chapters = SUPPORTED_BOOKS.get(book_name, 1)

    batches = []
    start = 1
    while start <= total_chapters:
        end = min(start + batch_size - 1, total_chapters)
        batches.append((start, end))
        start = end + 1

    return batches


def print_batch_recommendations(book_name: str):
    """Print recommended batching strategy for a book."""
    total_chapters = SUPPORTED_BOOKS.get(book_name, 0)
    if total_chapters == 0:
        print(f"Book '{book_name}' not found in supported books.")
        return

    batches = get_recommended_batches(book_name)
    estimated_verses = VERSE_ESTIMATES.get(book_name, total_chapters * 25)

    print(f"\n=== RECOMMENDED BATCHING FOR {book_name.upper()} ===")
    print(f"Total chapters: {total_chapters}")
    print(f"Estimated verses: ~{estimated_verses}")
    print(f"Recommended batches: {len(batches)}")
    print()

    for i, (start, end) in enumerate(batches, 1):
        chapters_in_batch = end - start + 1
        estimated_batch_verses = int(estimated_verses * chapters_in_batch / total_chapters)
        print(f"  Batch {i}: Chapters {start}-{end} ({chapters_in_batch} chapters, ~{estimated_batch_verses} verses)")

    print(f"\nEstimated cost: ${len(batches) * 0.8:.2f} - ${len(batches) * 1.5:.2f}")
    print(f"Estimated time: {len(batches) * 15}-{len(batches) * 30} minutes")
    print()


def has_corrupted_hebrew(text):
    """Check if Hebrew text contains corruption patterns"""
    # Look for common corruption patterns seen in the logs
    corruption_patterns = [
        'x�',      # x followed by replacement character
        '\x00',    # Null bytes
        'x\\',     # x followed by backslash (incomplete escape)
        'x"',      # x followed by quote (incomplete sequence)
        'x\x7f',   # x followed by control characters
    ]

    # Also check for sequences that look like corrupted UTF-8
    # Hebrew text should be in the range \u0590-\u05FF
    # Corrupted sequences often have x followed by non-Hebrew chars
    # Pattern: x followed by any combination of non-Hebrew chars and special symbols
    corrupted_pattern = re.compile(r'x[^\u0590-\u05FFa-zA-Z0-9\s\.,;:\'"!?()\[\]{}\-]*[^\u0590-\u05FFa-zA-Z0-9\s\.,;:\'"!?()\[\]{}\-]')

    # Check for known corruption patterns
    for pattern in corruption_patterns:
        if pattern in text:
            return True

    # Check for the corrupted Hebrew pattern
    if corrupted_pattern.search(text):
        return True

    # Check for excessive non-printable characters (except newlines and tabs)
    non_printable = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
    if non_printable > len(text) * 0.1:  # More than 10% non-printable
        return True

    return False

def setup_logging(log_file, enable_debug=False):
    """Setup optimized logging with level filtering"""
    log_level = logging.DEBUG if enable_debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def parse_selection(input_str, max_value, selection_type="item"):
    """Parse user input for flexible selection (e.g., '5', '10-15', '1,3,5-7', 'all')."""
    input_str = input_str.strip().lower()
    if input_str == 'all':
        return list(range(1, max_value + 1))

    selected = set()

    # Split by commas for multiple selections
    parts = [part.strip() for part in input_str.split(',')]

    for part in parts:
        if not part:
            continue

        # Range (e.g., 10-15)
        range_match = re.match(r'^(\d+)-(\d+)$', part)
        if range_match:
            start = int(range_match.group(1))
            end = int(range_match.group(2))
            if 1 <= start <= end <= max_value:
                selected.update(range(start, end + 1))
            else:
                print(f"Invalid range {part}: must be between 1 and {max_value}")
                return None
        # Single number
        elif part.isdigit():
            num = int(part)
            if 1 <= num <= max_value:
                selected.add(num)
            else:
                print(f"Invalid {selection_type} {num}: must be between 1 and {max_value}")
                return None
        else:
            print(f"Invalid format: {part}")
            return None

    return sorted(list(selected)) if selected else None

def get_user_selection():
    """Get flexible book, chapter, and verse selection from user with parallel settings"""
    # Use centralized books configuration
    books = SUPPORTED_BOOKS

    print(f"\n=== INTERACTIVE PARALLEL HEBREW FIGURATIVE LANGUAGE PROCESSOR v{PIPELINE_VERSION} ===")
    print("Enhanced version with flexible multi-book, multi-chapter, multi-verse selection + parallel processing")
    print("\nAvailable books:")
    for i, (book, chapters) in enumerate(books.items(), 1):
        print(f"  {i}. {book} ({chapters} chapters)")

    # Get book selection
    selected_books = []
    while True:
        try:
            print("\nBook Selection Examples:")
            print("  - Single: 'Genesis' or '1'")
            print("  - Multiple: 'Genesis,Exodus' or '1,2'")
            print("  - Range: '1-3' (Genesis through Leviticus)")
            print("  - Mixed: '1,3,5' (Genesis, Leviticus, Deuteronomy)")
            print("  - All: 'all'")

            choice = input(f"\nSelect books: ").strip()

            if choice.lower() == 'all':
                selected_books = list(books.keys())
                break

            # Parse book selection
            book_parts = [part.strip() for part in choice.split(',')]
            temp_books = []

            for part in book_parts:
                if not part:
                    continue

                # Range of book numbers (e.g., 1-3)
                range_match = re.match(r'^(\d+)-(\d+)$', part)
                if range_match:
                    start = int(range_match.group(1))
                    end = int(range_match.group(2))
                    if 1 <= start <= end <= len(books):
                        book_list = list(books.keys())
                        temp_books.extend(book_list[start-1:end])
                    else:
                        print(f"Invalid book range {part}: must be between 1 and {len(books)}")
                        temp_books = []
                        break
                # Single book number
                elif part.isdigit():
                    book_num = int(part)
                    if 1 <= book_num <= len(books):
                        temp_books.append(list(books.keys())[book_num - 1])
                    else:
                        print(f"Invalid book number {book_num}: must be between 1 and {len(books)}")
                        temp_books = []
                        break
                # Book name
                else:
                    matched_book = next((b for b in books if b.lower() == part.lower()), None)
                    if matched_book:
                        temp_books.append(matched_book)
                    else:
                        print(f"Invalid book name: {part}")
                        temp_books = []
                        break

            if temp_books:
                # Remove duplicates and maintain order
                seen = set()
                selected_books = []
                for book in temp_books:
                    if book not in seen:
                        selected_books.append(book)
                        seen.add(book)
                break
            else:
                print("Please try again with valid book selection.")

        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            return None

    print(f"\nSelected books: {', '.join(selected_books)}")

    # Get chapter and verse selections for each book
    book_selections = {}

    for book_name in selected_books:
        max_chapters = books[book_name]
        print(f"\n--- {book_name} ({max_chapters} chapters available) ---")

        # Get chapter selection for this book
        while True:
            try:
                print("Chapter Selection Examples:")
                print(f"  - Single: '5'")
                print(f"  - Multiple: '1,3,7'")
                print(f"  - Range: '5-10'")
                print(f"  - Mixed: '1,3,5-7,10'")
                print(f"  - All chapters: 'all'")
                print(f"  - ALL CHAPTERS & VERSES: 'full' (processes entire book)")

                chapter_input = input(f"Enter chapters for {book_name} (1-{max_chapters}): ").strip().lower()

                if chapter_input == 'full':
                    # Process entire book - all chapters, all verses
                    print(f"Selected: FULL BOOK ({book_name} - all chapters, all verses)")
                    print(f"  Will process all {max_chapters} chapters with all verses")

                    # Use special marker 'ALL' to indicate full book processing
                    book_selections[book_name] = 'FULL_BOOK'
                    break

                selected_chapters = parse_selection(chapter_input, max_chapters, "chapter")

                if selected_chapters is not None:
                    break
                else:
                    print(f"Please enter valid chapters (1-{max_chapters})")

            except KeyboardInterrupt:
                print("\nExiting...")
                return None

        # Skip individual chapter processing if 'full' was selected
        if chapter_input == 'full':
            continue

        print(f"Selected chapters for {book_name}: {selected_chapters}")

        # Get verse selection for each chapter
        chapter_verse_map = {}

        # Ask if user wants all verses for all selected chapters
        if len(selected_chapters) > 1:
            all_verses_choice = input(f"\nProcess ALL verses for all {len(selected_chapters)} chapters? (y/n): ").strip().lower()
            if all_verses_choice == 'y':
                # Use special marker for all chapters/all verses
                chapter_verse_map = {chapter: 'ALL_VERSES' for chapter in selected_chapters}
                print(f"  Will process all verses for all {len(selected_chapters)} chapters")
                book_selections[book_name] = chapter_verse_map
                continue

        for chapter in selected_chapters:
            print(f"\n  Chapter {chapter}:")
            print("    Verse Selection Examples:")
            print(f"      - Single: '5'")
            print(f"      - Multiple: '1,3,7'")
            print(f"      - Range: '5-10'")
            print(f"      - Mixed: '1,3,5-7,10'")
            print(f"      - All: 'all'")

            verse_input = input(f"    Enter verses for {book_name} {chapter}: ").strip()

            if verse_input.lower() == 'all':
                selected_verses = 'ALL_VERSES'
            else:
                # We'll validate actual verse ranges during processing
                # For now, just store the input for later processing
                selected_verses = verse_input

            chapter_verse_map[chapter] = selected_verses
            print(f"    Selected verses for {book_name} {chapter}: {selected_verses}")

        book_selections[book_name] = chapter_verse_map

    # Get parallelization settings
    print(f"\nPARALLEL PROCESSING SETTINGS:")
    print(f"Recommended: 6-8 workers (balance of speed vs API limits)")
    print(f"Conservative: 2-4 workers (slower but more reliable)")
    print(f"Aggressive: 8-12 workers (faster but may hit rate limits)")

    while True:
        try:
            max_workers_input = input(f"\nEnter max parallel workers (1-12, default: 6): ").strip()
            if not max_workers_input:
                max_workers = 6  # Default
                break
            elif max_workers_input.isdigit():
                max_workers = int(max_workers_input)
                if 1 <= max_workers <= 12:
                    break
                else:
                    print("Max workers must be between 1 and 12")
            else:
                print("Please enter a number or press Enter for default (6)")
        except KeyboardInterrupt:
            print("\nExiting...")
            return None

    # Get logging level preference
    debug_choice = input("\nEnable detailed debug logging? (y/N): ").strip().lower()
    enable_debug = debug_choice in ['y', 'yes']

    return {
        'book_selections': book_selections,
        'max_workers': max_workers,
        'enable_debug': enable_debug
    }

def save_raw_response(response_text, book_name, chapter):
    """Save raw API response for debugging"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"debug_response_{book_name}_{chapter}_{timestamp}.json"
    filepath = os.path.join("debug", filename)

    os.makedirs("debug", exist_ok=True)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(response_text)

    return filepath

def extract_individual_verses(json_text, logger):
    """Extract individual verse objects from malformed JSON"""
    verses = []

    # Look for verse patterns in the JSON
    verse_pattern = r'"verse":\s*(\d+)'
    verse_matches = list(re.finditer(verse_pattern, json_text))

    logger.info(f"Found {len(verse_matches)} verse patterns in malformed JSON")

    for i, match in enumerate(verse_matches):
        verse_num = match.group(1)
        start_pos = match.start()

        # Find the start of this verse object
        obj_start = json_text.rfind('{', 0, start_pos)

        # Find the end of this verse object
        if i < len(verse_matches) - 1:
            next_match = verse_matches[i + 1]
            obj_end = json_text.rfind('}', 0, next_match.start())
        else:
            obj_end = json_text.rfind('}', start_pos)

        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            verse_json = json_text[obj_start:obj_end + 1]

            # Try to complete this object
            open_braces = verse_json.count('{')
            close_braces = verse_json.count('}')

            for _ in range(open_braces - close_braces):
                verse_json += '}'

            try:
                verse_obj = json.loads(verse_json)
                verses.append(verse_obj)
                logger.debug(f"Successfully extracted verse {verse_num}")
            except json.JSONDecodeError:
                # Try to repair common issues
                verse_json = verse_json.rstrip(',').rstrip()
                try:
                    verse_obj = json.loads(verse_json)
                    verses.append(verse_obj)
                    logger.debug(f"Successfully extracted verse {verse_num} after repair")
                except:
                    logger.warning(f"Could not parse verse {verse_num} object")

    return verses

def process_validation_result(validation_result: Dict, instance_id_to_db_id: Dict,
                               db_manager, logger) -> Tuple[bool, Optional[int]]:
    """
    Process a single validation result and update the database.

    Args:
        validation_result: Dict with 'instance_id' and 'validation_results'
        instance_id_to_db_id: Mapping from instance_id to database ID
        db_manager: DatabaseManager instance
        logger: Logger instance

    Returns:
        Tuple of (success: bool, db_id: Optional[int])
    """
    instance_id = validation_result.get('instance_id')
    results = validation_result.get('validation_results', {})

    db_id = instance_id_to_db_id.get(instance_id)
    if not db_id:
        logger.error(f"Could not find DB ID for instance_id {instance_id}")
        return False, None

    any_valid = False
    validation_data = {}

    # Initialize all final fields to 'no'
    for fig_type in ['simile', 'metaphor', 'personification', 'idiom',
                     'hyperbole', 'metonymy', 'other']:
        validation_data[f'final_{fig_type}'] = 'no'

    # Process each figurative type result
    for fig_type, result in results.items():
        decision = result.get('decision')
        reason = result.get('reason', '')
        reclassified_type = result.get('reclassified_type')

        if decision == 'RECLASSIFIED' and reclassified_type:
            validation_data[f'validation_decision_{fig_type}'] = 'RECLASSIFIED'
            validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"
            validation_data[f'final_{reclassified_type}'] = 'yes'
            any_valid = True
            logger.debug(f"RECLASSIFIED: {fig_type} → {reclassified_type}")
        elif decision == 'VALID':
            validation_data[f'validation_decision_{fig_type}'] = 'VALID'
            validation_data[f'validation_reason_{fig_type}'] = reason
            validation_data[f'final_{fig_type}'] = 'yes'
            any_valid = True
            logger.debug(f"VALID: {fig_type}")
        else:  # INVALID
            validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
            validation_data[f'validation_reason_{fig_type}'] = reason
            logger.debug(f"INVALID: {fig_type}")

    validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'
    validation_data['validation_response'] = json.dumps({
        'instance_id': instance_id,
        'validation_results': results,
        'timestamp': datetime.now().isoformat()
    })
    validation_data['validation_error'] = None

    # Update database
    db_manager.update_validation_data(db_id, validation_data)
    logger.debug(f"Validation data updated for DB ID: {db_id}")

    return True, db_id


def recover_missing_validations(db_manager, validator, book_name: str, chapter: int,
                                 logger) -> Dict:
    """
    Identify and recover missing validation data for a chapter.

    Args:
        db_manager: DatabaseManager instance
        validator: MetaphorValidator instance
        book_name: Book name
        chapter: Chapter number
        logger: Logger instance

    Returns:
        Dict with recovery statistics
    """
    stats = {
        'total_missing': 0,
        'recovered': 0,
        'failed': 0
    }

    logger.info(f"[RECOVERY] Checking for missing validations in {book_name} {chapter}")

    # Query for instances missing validation
    db_manager.cursor.execute("""
        SELECT fl.id, fl.verse_id, fl.figurative_text, fl.figurative_text_in_hebrew,
               fl.explanation, fl.confidence,
               fl.simile, fl.metaphor, fl.personification,
               fl.idiom, fl.hyperbole, fl.metonymy, fl.other,
               v.hebrew_text, v.english_text, v.reference
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE v.book = ? AND v.chapter = ?
        AND (
            fl.validation_decision_simile IS NULL AND
            fl.validation_decision_metaphor IS NULL AND
            fl.validation_decision_personification IS NULL AND
            fl.validation_decision_idiom IS NULL AND
            fl.validation_decision_hyperbole IS NULL AND
            fl.validation_decision_metonymy IS NULL AND
            fl.validation_decision_other IS NULL
        )
    """, (book_name, chapter))

    missing_instances = db_manager.cursor.fetchall()
    stats['total_missing'] = len(missing_instances)

    if not missing_instances:
        logger.info(f"[RECOVERY] No missing validations found for {book_name} {chapter}")
        return stats

    logger.warning(f"[RECOVERY] Found {len(missing_instances)} instances missing validation")

    # Prepare instances for validation
    instances_to_validate = []
    id_mapping = {}  # instance_id -> db_id

    for i, row in enumerate(missing_instances):
        instance_id = i + 1
        id_mapping[instance_id] = row['id']

        instance = {
            'instance_id': instance_id,
            'verse_reference': row['reference'],
            'hebrew_text': row['hebrew_text'],
            'english_text': row['english_text'],
            'figurative_text': row['figurative_text'] or '',
            'explanation': row['explanation'] or '',
            'simile': row['simile'],
            'metaphor': row['metaphor'],
            'personification': row['personification'],
            'idiom': row['idiom'],
            'hyperbole': row['hyperbole'],
            'metonymy': row['metonymy'],
            'other': row['other']
        }
        instances_to_validate.append(instance)

    # Validate in batches of 10
    batch_size = 10
    for i in range(0, len(instances_to_validate), batch_size):
        batch = instances_to_validate[i:i + batch_size]
        logger.info(f"[RECOVERY] Validating batch {i//batch_size + 1} ({len(batch)} instances)")

        try:
            validation_results = validator.validate_chapter_instances(batch)

            for result in validation_results:
                success, db_id = process_validation_result(
                    result, id_mapping, db_manager, logger
                )
                if success:
                    stats['recovered'] += 1
                else:
                    stats['failed'] += 1

        except Exception as e:
            logger.error(f"[RECOVERY] Batch validation failed: {e}")
            stats['failed'] += len(batch)

    db_manager.commit()

    logger.info(f"[RECOVERY] Complete: {stats['recovered']} recovered, {stats['failed']} failed")
    return stats


def process_chapter_batched(verses_data, book_name, chapter, validator, divine_names_modifier, db_manager, logger, run_context: RunContext = None):
    """Process an entire chapter in a single batched API call (GPT-5.1 MEDIUM)

    This approach sends all verses in ONE API call, achieving 95% token savings
    compared to per-verse processing.

    Args:
        verses_data: List of verse dictionaries with 'hebrew', 'english', 'reference', 'verse'
        book_name: Name of the book
        chapter: Chapter number
        validator: MetaphorValidator instance (uses GPT-5.1 MEDIUM)
        divine_names_modifier: HebrewDivineNamesModifier instance
        db_manager: DatabaseManager instance
        logger: Logger instance
        run_context: Optional RunContext for failure tracking

    Returns:
        Tuple of (verses_stored, instances_stored, processing_time, total_attempted, total_cost)
    """
    start_time = time.time()

    if not verses_data:
        return 0, 0, 0, 0, 0.0

    # Use increased token limit for prophetic books (Jeremiah, Isaiah)
    max_tokens = MAX_COMPLETION_TOKENS_PROPHETIC if book_name in BATCHED_PROCESSING_BOOKS else MAX_COMPLETION_TOKENS_DEFAULT

    logger.info(f"[BATCHED MODE] Processing {book_name} {chapter} with {len(verses_data)} verses in SINGLE API call")
    logger.info(f"[BATCHED MODE] Using max_completion_tokens={max_tokens}")

    # Build full chapter context (Hebrew + English)
    chapter_hebrew = "\n".join([f"{v['verse']}. {v['hebrew']}" for v in verses_data])
    chapter_english = "\n".join([f"{v['verse']}. {v['english']}" for v in verses_data])
    full_chapter_context = f"""=== {book_name} Chapter {chapter} (FULL CHAPTER for context) ===

Hebrew:
{chapter_hebrew}

English:
{chapter_english}
"""

    logger.info(f"Chapter context: {len(full_chapter_context)} chars")

    # Build verses to analyze section
    verses_to_analyze = ""
    for v in verses_data:
        verses_to_analyze += f"\nVerse {v['verse']}:\n"
        verses_to_analyze += f"Hebrew: {v['hebrew']}\n"
        verses_to_analyze += f"English: {v['english']}\n"

    # Build batched prompt
    batched_prompt = f"""You are a biblical Hebrew scholar specializing in figurative language analysis. Your task is to analyze all verses from {book_name} Chapter {chapter} for figurative language.

{full_chapter_context}

=== VERSES TO ANALYZE ===
{verses_to_analyze}

=== TASK ===

Analyze EACH of the {len(verses_data)} verses above for figurative language.

CRITICAL MULTI-INSTANCE DETECTION REQUIREMENTS:

For EACH verse, you MUST explicitly determine and report:
1. ZERO instances: No figurative language detected - provide EMPTY "instances" array []
2. ONE instance: Single figurative language expression - provide ONE object in "instances" array
3. MULTIPLE instances: Multiple DISTINCT expressions - provide MULTIPLE objects in "instances" array

ESSENTIAL GUIDELINES:
- Do NOT default to finding exactly one instance per verse
- Some verses may have ZERO figurative language instances - this is VALID
- Some verses may have SEVERAL figurative language instances - this is VALID
- Each instance must represent a DISTINCT figurative expression, NOT different aspects of the same expression
- Multiple expressions in the same verse can be of the same type (e.g., two metaphors) or different types

For each verse, briefly analyze what you considered and include it in the "deliberation" field of the JSON. Then detect instances of:
- Metaphor
- Simile
- Personification
- Merism
- Synecdoche
- Metonymy
- Hyperbole
- Irony

For each detected instance, provide:
1. **figurative_language**: "yes" or "no"
2. **metaphor**: "yes" or "no" (specific to metaphor)
3. **simile**: "yes" or "no"
4. **personification**: "yes" or "no"
5. **idiom**: "yes" or "no"
6. **hyperbole**: "yes" or "no"
7. **metonymy**: "yes" or "no"
8. **other**: "yes" or "no"
9. **hebrew_text**: The Hebrew text of the figurative expression
10. **english_text**: The English translation of the figurative expression
11. **target**: JSON array with 3 levels - [specific, category, domain]
12. **vehicle**: JSON array with 3 levels - [specific, category, domain]
13. **ground**: JSON array with 3 levels - [specific, category, domain]
14. **posture**: JSON array with 3 levels - [specific, category, domain]
15. **explanation**: Brief explanation of the figurative language
16. **confidence**: Confidence score (0.0-1.0)

=== OUTPUT FORMAT ===

**Provide STRUCTURED JSON OUTPUT (REQUIRED):**

Return a JSON array with ONE object per verse. Each object should have:
- "verse": verse number
- "reference": "{book_name} {chapter}:X"
- "deliberation": Your brief analysis for THIS VERSE ONLY - what you considered and your reasoning
- "instances": array of detected figurative language instances (empty array if none)

Example structure showing ZERO, ONE, and MULTIPLE instances:
[
  {{
    "verse": 1,
    "reference": "{book_name} {chapter}:1",
    "deliberation": "Analyzed verse for figurative language. Found no metaphors, similes, or other figurative expressions. The language appears to be literal and straightforward.",
    "instances": []  // ZERO instances - empty array when no figurative language detected
  }},
  {{
    "verse": 2,
    "reference": "{book_name} {chapter}:2",
    "deliberation": "Identified one clear metaphor comparing divine discipline to a shepherd's guidance. No other figurative expressions present.",
    "instances": [
      {{
        "figurative_language": "yes",
        "metaphor": "yes",
        "simile": "no",
        "personification": "no",
        "idiom": "no",
        "hyperbole": "no",
        "metonymy": "no",
        "other": "no",
        "hebrew_text": "...",
        "english_text": "...",
        "target": ["specific", "category", "domain"],
        "vehicle": ["specific", "category", "domain"],
        "ground": ["specific", "category", "domain"],
        "posture": ["specific", "category", "domain"],
        "explanation": "Divine guidance compared to shepherd's care",
        "confidence": 0.9
      }}
    ]
  }},
  {{
    "verse": 3,
    "reference": "{book_name} {chapter}:3",
    "deliberation": "Found two distinct figurative expressions: 1) wisdom personified as a woman calling out, and 2) the heart described as a pathway. Both are separate figurative devices in the same verse.",
    "instances": [
      {{
        "figurative_language": "yes",
        "metaphor": "no",
        "simile": "no",
        "personification": "yes",
        "idiom": "no",
        "hyperbole": "no",
        "metonymy": "no",
        "other": "no",
        "hebrew_text": "...",
        "english_text": "...",
        "target": ["specific", "category", "domain"],
        "vehicle": ["specific", "category", "domain"],
        "ground": ["specific", "category", "domain"],
        "posture": ["specific", "category", "domain"],
        "explanation": "Wisdom personified as calling woman",
        "confidence": 0.95
      }},
      {{
        "figurative_language": "yes",
        "metaphor": "yes",
        "simile": "no",
        "personification": "no",
        "idiom": "no",
        "hyperbole": "no",
        "metonymy": "no",
        "other": "no",
        "hebrew_text": "...",
        "english_text": "...",
        "target": ["specific", "category", "domain"],
        "vehicle": ["specific", "category", "domain"],
        "ground": ["specific", "category", "domain"],
        "posture": ["specific", "category", "domain"],
        "explanation": "Heart described metaphorically as a pathway",
        "confidence": 0.85
      }}
    ]
  }}
]

IMPORTANT: Each verse's "deliberation" field should contain ONLY the analysis for that specific verse, not for other verses.
"""

    # Call GPT-5.1 MEDIUM
    api_start = time.time()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        logger.info(f"Calling GPT-5.1 MEDIUM for {book_name} {chapter} (using streaming to avoid truncation)...")

        # Use streaming to avoid the 1023-character truncation issue
        # This ensures we capture the complete response without buffering limits
        # Enhanced with corruption detection and recovery
        max_stream_retries = 3
        response_text = ""
        skipped_verses = set()  # Track which verses had corruption
        corrupted_chunks = 0    # Count total corrupted chunks

        for stream_attempt in range(max_stream_retries):
            try:
                logger.info(f"Stream attempt {stream_attempt + 1}/{max_stream_retries}")
                stream = openai_client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[
                        {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis. Always return valid JSON."},
                        {"role": "user", "content": batched_prompt}
                    ],
                    max_completion_tokens=max_tokens,  # Use dynamic token limit
                    reasoning_effort="medium",
                    stream=True  # Enable streaming to avoid truncation
                )

                # Collect the streamed response with corruption detection
                response_text = ""
                chunk_count = 0
                last_valid_content = ""
                current_verse = None  # Track which verse we're currently parsing

                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content

                        # Check for corruption patterns
                        if '\x00' in content or '�' in content or 'x�' in content:
                            logger.warning(f"Detected corrupted chunk at chunk {chunk_count} - skipping")
                            corrupted_chunks += 1

                            # Try to identify which verse was affected
                            # Look for verse patterns in recent content
                            verse_match = re.search(r'"verse":\s*(\d+)', last_valid_content[-200:] if last_valid_content else "")
                            if verse_match:
                                current_verse = int(verse_match.group(1))
                                skipped_verses.add(current_verse)
                                logger.warning(f"Marked verse {current_verse} as potentially corrupted")
                            continue  # Skip corrupted chunk

                        # Validate UTF-8 encoding
                        try:
                            content.encode('utf-8').decode('utf-8')

                            # Additional Hebrew text validation
                            if has_corrupted_hebrew(content):
                                logger.warning(f"Hebrew corruption detected in chunk {chunk_count} - skipping")
                                corrupted_chunks += 1
                                continue

                            response_text += content
                            last_valid_content = response_text
                            chunk_count += 1

                            # Track current verse for better error reporting
                            verse_match = re.search(r'"verse":\s*(\d+)', content)
                            if verse_match:
                                current_verse = int(verse_match.group(1))

                        except UnicodeError as e:
                            logger.warning(f"Unicode error in chunk {chunk_count}: {e}")
                            corrupted_chunks += 1
                            if current_verse:
                                skipped_verses.add(current_verse)
                            continue

                        # Log progress every 100 chunks
                        if chunk_count % 100 == 0:
                            logger.debug(f"Received {chunk_count} chunks, response length: {len(response_text)} chars")

                # If we get here, streaming completed successfully
                logger.info(f"Streaming completed in attempt {stream_attempt + 1}")
                break  # Exit retry loop on success

            except Exception as e:
                logger.error(f"Streaming error on attempt {stream_attempt + 1}: {e}")
                if stream_attempt < max_stream_retries - 1:
                    logger.info(f"Retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    # All retries failed, try non-streaming fallback
                    logger.warning("All streaming attempts failed - falling back to non-streaming mode")
                    try:
                        logger.info("Making non-streaming API call as fallback...")
                        response = openai_client.chat.completions.create(
                            model="gpt-5.1",
                            messages=[
                                {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis. Always return valid JSON."},
                                {"role": "user", "content": batched_prompt}
                            ],
                            max_completion_tokens=max_tokens,  # Use dynamic token limit
                            reasoning_effort="medium",
                            stream=False
                        )
                        response_text = response.choices[0].message.content
                        logger.info("Non-streaming fallback successful")
                    except Exception as fallback_error:
                        logger.error(f"Non-streaming fallback also failed: {fallback_error}")
                        response_text = last_valid_content if last_valid_content else ""
                        logger.warning(f"Using last known good state ({len(response_text)} chars)")

        api_time = time.time() - api_start

        logger.info(f"Streaming completed in {api_time:.1f}s ({chunk_count} chunks)")
        logger.info(f"Total response length: {len(response_text)} characters")

        # Save raw response for debugging
        saved_file = save_raw_response(response_text, book_name, chapter)
        logger.info(f"Saved raw response to {saved_file}")

        # Store original streaming text in case fallback overwrites it
        original_streaming_text = response_text

        # Deliberation is now extracted from verse-specific JSON fields, no need to extract separate deliberation section
        logger.info("Deliberation will be extracted from verse-specific JSON fields")

        # For streaming responses, we need to make a separate call to get usage data
        # or estimate based on typical patterns
        token_metadata = {
            'input_tokens': len(batched_prompt) // 4,  # Rough estimate: 1 token ≈ 4 chars
            'output_tokens': len(response_text) // 4,  # Rough estimate: 1 token ≈ 4 chars
            'reasoning_tokens': 0,  # Not available in streaming mode
            'total_tokens': (len(batched_prompt) + len(response_text)) // 4,
            'streaming': True
        }

        # GPT-5.1 pricing: $1.25/M input + $10.00/M output
        cost = (token_metadata['input_tokens'] / 1_000_000 * 1.25 +
               token_metadata['output_tokens'] / 1_000_000 * 10.0)
        token_metadata['cost'] = cost

        logger.info(f"Estimated token usage: {token_metadata.get('input_tokens', 0):,} input, "
                   f"{token_metadata.get('output_tokens', 0):,} output")
        logger.info(f"Estimated cost: ${token_metadata.get('cost', 0):.4f}")

        # Verify we got a complete response (check for truncation indicators)
        if len(response_text) < 1500:
            logger.warning(f"Response seems short ({len(response_text)} chars) - possible truncation still occurring")
        else:
            logger.info(f"Good response length ({len(response_text)} chars) - streaming likely avoided truncation")

        # Parse JSON response
        logger.debug(f"Response text preview: {response_text[:200]}...{response_text[-200:] if len(response_text) > 400 else response_text[-200:]}")

        # TRUNCATION DETECTION: Check for common truncation patterns
        # Clean response text by removing markdown code block markers for detection
        clean_response = response_text.strip()
        if clean_response.startswith('```'):
            clean_response = '\n'.join(clean_response.split('\n')[1:])  # Remove first line with ```
        if clean_response.endswith('```'):
            clean_response = clean_response[:-3].rstrip()  # Remove trailing ```

        truncation_indicators = [
            clean_response.endswith('...'),  # Incomplete sentence
            clean_response.endswith(',"'),   # Mid-JSON field
            clean_response.endswith(':{'),   # Mid-JSON object
            len(clean_response) < 1000,      # Suspiciously short response
            'confidence' in clean_response and not clean_response.rstrip().endswith(']') and not clean_response.rstrip().endswith('}'),  # Cut in confidence field
        ]

        if any(truncation_indicators):
            logger.error("TRUNCATION DETECTED! Response shows signs of being cut off")
            logger.error(f"Response length: {len(response_text)} characters")
            logger.error(f"Ends with: {repr(response_text[-50:])}")

            # Try fallback with non-streaming request as backup
            logger.info("Attempting fallback with non-streaming request...")
            try:
                fallback_response = openai_client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[
                        {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                        {"role": "user", "content": batched_prompt}
                    ],
                    max_completion_tokens=16384,  # Use smaller limit for fallback
                    reasoning_effort="medium"
                )

                fallback_text = fallback_response.choices[0].message.content
                if len(fallback_text) > len(response_text):
                    logger.info(f"Fallback successful! Got {len(fallback_text)} chars vs {len(response_text)} chars")
                    response_text = fallback_text

                    # Update token estimates with fallback data
                    if hasattr(fallback_response, 'usage'):
                        token_metadata['input_tokens'] = getattr(fallback_response.usage, 'prompt_tokens', 0)
                        token_metadata['output_tokens'] = getattr(fallback_response.usage, 'completion_tokens', 0)
                        token_metadata['reasoning_tokens'] = getattr(fallback_response.usage, 'reasoning_tokens', 0)
                        cost = (token_metadata['input_tokens'] / 1_000_000 * 1.25 +
                               token_metadata['output_tokens'] / 1_000_000 * 10.0)
                        token_metadata['cost'] = cost
                        logger.info(f"Updated token usage from fallback: {token_metadata.get('input_tokens', 0):,} input, "
                                   f"{token_metadata.get('output_tokens', 0):,} output")
                else:
                    logger.warning("Fallback response also short or similar length")

            except Exception as fallback_error:
                logger.error(f"Fallback request failed: {fallback_error}")
                logger.warning("Proceeding with possibly truncated response")

        # Deliberation extraction is now handled per-verse in JSON parsing

        # Modify for non-sacred version (replace divine names)
        # chapter_deliberation_non_sacred is no longer needed since deliberation is now verse-specific

        # Extract JSON array from response (handle markdown wrappers)
        json_text = response_text.strip()

        # First, try to find the JSON array using regex pattern
        # Look for JSON array that starts with [ and ends with ]
        # FIX: Use greedy matching to capture the COMPLETE array, not just the first object
        json_pattern = r'\[\s*\{.*\}\s*\]'  # Changed from .*? to .* for greedy matching
        json_match = re.search(json_pattern, response_text, re.DOTALL)

        if json_match:
            json_text = json_match.group(0)
            logger.debug(f"Found JSON array using regex pattern: {len(json_text)} chars")
        else:
            # Fallback: Handle markdown wrappers
            if json_text.startswith("```json"):
                json_text = json_text[7:]
            if json_text.startswith("```"):
                json_text = json_text[3:]
            if json_text.endswith("```"):
                json_text = json_text[:-3]
            json_text = json_text.strip()
            logger.debug(f"Extracted JSON using markdown wrapper removal: {len(json_text)} chars")

        # If still empty, try to find JSON brackets directly with proper bracket matching
        if not json_text:
            # Find the first [ and use bracket counting to find the matching ]
            first_bracket = response_text.find('[')
            if first_bracket != -1:
                # Count brackets to find the matching closing bracket
                bracket_count = 1
                pos = first_bracket + 1
                while pos < len(response_text) and bracket_count > 0:
                    if response_text[pos] == '[':
                        bracket_count += 1
                    elif response_text[pos] == ']':
                        bracket_count -= 1
                    pos += 1

                if bracket_count == 0:
                    # Found matching bracket
                    json_text = response_text[first_bracket:pos]
                    logger.debug(f"Extracted JSON using bracket counting: {len(json_text)} chars")
                else:
                    # Fallback: use simple search but warn
                    last_bracket = response_text.rfind(']')
                    if last_bracket > first_bracket:
                        json_text = response_text[first_bracket:last_bracket + 1]
                        logger.warning(f"Extracted JSON using simple bracket search (uncounted brackets): {len(json_text)} chars")
                    else:
                        logger.error("Could not find matching JSON brackets")

        # Debug logging if JSON is still empty
        if not json_text:
            logger.error("JSON extraction failed - no content found")
            logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            logger.error(f"Response text (last 500 chars): {response_text[-500:]}")
            raise ValueError("Could not extract JSON from response")

        logger.debug(f"Final JSON text length: {len(json_text)} chars")
        logger.debug(f"JSON text preview: {json_text[:200]}...{json_text[-200:] if len(json_text) > 400 else json_text[-200:]}")

        # Parse JSON with error handling
        try:
            verse_results = json.loads(json_text)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Error at line {e.lineno}, column {e.colno}")
            logger.error(f"JSON text length: {len(json_text)} chars")

            # Show context around error
            error_pos = e.colno - 1
            context_start = max(0, error_pos - 100)
            context_end = min(len(json_text), error_pos + 100)

            logger.error(f"Context around error:")
            logger.error(f"...{json_text[context_start:error_pos]}<ERROR>{json_text[error_pos:context_end]}...")
            logger.error(f"JSON text (first 1000 chars): {json_text[:1000]}")
            logger.error(f"JSON text (last 1000 chars): {json_text[-1000:] if len(json_text) > 1000 else json_text}")

            # Try to repair and complete truncated JSON
            logger.info("Attempting to repair and complete truncated JSON...")
            repaired_json = json_text

            # If JSON appears to be truncated, try to complete it
            if e.msg in ["Expecting ',' delimiter", "Expecting property name enclosed in double quotes", "Unterminated string"]:
                logger.info("JSON appears truncated - attempting intelligent completion...")

                # Count braces and brackets to understand structure
                open_braces = repaired_json.count('{')
                close_braces = repaired_json.count('}')
                open_brackets = repaired_json.count('[')
                close_brackets = repaired_json.count(']')

                logger.info(f"Structure analysis: {open_braces} {{ vs {close_braces} }}, {open_brackets} [ vs {close_brackets} ]")

                # Find the last valid position in the JSON
                if e.msg == "Unterminated string":
                    logger.info("Attempting to fix unterminated string...")
                    error_pos = e.colno - 1

                    # Simple fix: just insert a quote at the error position
                    # This is a common issue where the closing quote is missing
                    repaired_json = repaired_json[:error_pos] + '"' + repaired_json[error_pos:]
                    logger.info(f"Inserted quote at position {error_pos} to fix unterminated string")

                    # Now close the structure
                    missing_braces = open_braces - close_braces
                    missing_brackets = open_brackets - close_brackets

                    # Add closing brackets first (inner structures)
                    for _ in range(missing_brackets):
                        repaired_json += ']'

                    # Add closing braces (outer structures)
                    for _ in range(missing_braces):
                        repaired_json += '}'

                elif e.msg == "Expecting ',' delimiter":
                    # Try to complete the current object/array
                    pos = e.colno - 1  # Adjust for 0-based indexing
                    # Look for the last complete property or value
                    truncated_text = repaired_json[:pos]

                    # Add missing comma and try to close the structure
                    # First, try to find the last complete value
                    last_complete = truncated_text.rstrip()
                    if not last_complete.endswith(',') and not last_complete.endswith('[') and not last_complete.endswith('{'):
                        # Likely need a comma
                        truncated_text += ','

                    # Add missing closing brackets and braces
                    missing_braces = open_braces - close_braces
                    missing_brackets = open_brackets - close_brackets

                    # Add closing brackets first (inner structures)
                    for _ in range(missing_brackets):
                        truncated_text += ']'

                    # Add closing braces (outer structures)
                    for _ in range(missing_braces):
                        truncated_text += '}'

                    repaired_json = truncated_text
                    logger.info(f"Added {missing_brackets} missing ] and {missing_braces} missing }}")

                # Try parsing the repaired JSON
                try:
                    verse_results = json.loads(repaired_json)
                    logger.info("JSON repair successful!")
                    logger.info(f"Successfully parsed JSON with {len(verse_results)} verse results")
                except json.JSONDecodeError as e2:
                    logger.error(f"JSON repair failed: {e2}")
                    logger.error(f"Repaired JSON (first 1000 chars): {repaired_json[:1000]}")
                    logger.error(f"Repaired JSON (last 1000 chars): {repaired_json[-1000:] if len(repaired_json) > 1000 else repaired_json}")
                    raise
            else:
                # For other JSON errors, try basic repair
                logger.info("Trying basic JSON repair...")

                # Fix missing commas between array elements and object properties
                repaired_json = re.sub(r'\]\s*\n\s*\[', '], [', repaired_json)
                repaired_json = re.sub(r'}\s*\n\s*{', '}, {', repaired_json)

                # Fix missing commas in nested structures
                repaired_json = re.sub(r'"\]\s*\n\s*"', '"],\n    "', repaired_json)

                # Fix common trailing comma issues
                repaired_json = re.sub(r',\s*}', '}', repaired_json)
                repaired_json = re.sub(r',\s*\]', ']', repaired_json)

                # Try parsing the repaired JSON
                try:
                    verse_results = json.loads(repaired_json)
                    logger.info("Basic JSON repair successful!")
                except json.JSONDecodeError as e2:
                    logger.error(f"Basic JSON repair failed: {e2}")
                    logger.error(f"Repaired JSON (first 1000 chars): {repaired_json[:1000]}")
                    logger.error(f"Repaired JSON (last 1000 chars): {repaired_json[-1000:] if len(repaired_json) > 1000 else repaired_json}")

                    # If all repair attempts fail, try verse-level extraction
                    logger.warning("JSON repair failed, attempting verse-level extraction...")
                    verse_results = extract_individual_verses(json_text, logger)

                    if verse_results:
                        logger.info(f"Successfully extracted {len(verse_results)} verses using fallback method")
                    else:
                        logger.error("All JSON parsing strategies failed")
                        raise ValueError("Could not parse JSON response with any strategy")

        if not isinstance(verse_results, list):
            raise ValueError(f"Expected JSON array, got {type(verse_results)}")

        logger.info(f"Parsed {len(verse_results)} verse results")

        # Validate verse results before processing
        if not verse_results:
            raise ValueError("No verse results parsed from response")

        # Validate verse structure with enhanced pydantic validation
        valid_verses = []
        schema_errors = []
        for vr in verse_results:
            if 'verse' in vr and isinstance(vr['verse'], int):
                # Validate instances within each verse using pydantic
                if 'instances' in vr and vr['instances']:
                    validated_instances, instance_errors = validate_llm_response(vr['instances'], logger)
                    if instance_errors:
                        schema_errors.extend(instance_errors)
                    vr['instances'] = validated_instances
                valid_verses.append(vr)
            else:
                logger.warning(f"Skipping invalid verse result: {vr}")
                schema_errors.append(f"Verse missing 'verse' field: {vr}")

        verse_results = valid_verses

        if schema_errors:
            logger.warning(f"[SCHEMA VALIDATION] {len(schema_errors)} validation errors found")
            for err in schema_errors[:5]:  # Log first 5 errors
                logger.warning(f"  - {err}")
            if len(schema_errors) > 5:
                logger.warning(f"  ... and {len(schema_errors) - 5} more errors")

        if not verse_results:
            raise ValueError("No valid verse results found after filtering")

        logger.info(f"After validation: {len(verse_results)} valid verses (schema errors: {len(schema_errors)})")

        # Calculate detection statistics
        total_instances = sum(len(vr.get('instances', [])) for vr in verse_results)
        detection_rate = total_instances / len(verse_results) if verse_results else 0

        logger.info(f"Detected {total_instances} instances ({detection_rate:.2f} instances/verse)")

        # Collect all instances for batched validation
        all_instances_for_validation = []
        verse_to_instances_map = {}  # Map verse_ref to list of instances

        # Store results in database
        verses_stored = 0
        instances_stored = 0

        for vr in verse_results:
            verse_num = vr.get('verse')
            reference = vr.get('reference', f'{book_name} {chapter}:{verse_num}')
            instances = vr.get('instances', [])

            # Extract verse-specific deliberation from JSON
            verse_specific_deliberation = vr.get('deliberation', '')
            if verse_specific_deliberation:
                logger.debug(f"Found verse-specific deliberation for {reference}: {len(verse_specific_deliberation)} chars")
            else:
                logger.warning(f"No deliberation found for {reference}, using empty string")
                verse_specific_deliberation = None  # Use null as requested

            # Find original verse data
            original_verse = next((v for v in verses_data if v['verse'] == verse_num), None)
            if not original_verse:
                logger.warning(f"Could not find original verse data for {reference}")
                continue

            # Prepare verse data for database
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(original_verse['hebrew'])
            hebrew_non_sacred = divine_names_modifier.modify_divine_names(original_verse['hebrew'])
            english_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(original_verse['english'])

            # Apply divine names modification to deliberation if present
            verse_specific_deliberation_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(verse_specific_deliberation) if verse_specific_deliberation else None

            # Calculate word count
            hebrew_words = original_verse['hebrew'].split()
            word_count = len([w for w in hebrew_words if w.strip()])

            verse_data = {
                'reference': reference,
                'book': book_name,
                'chapter': chapter,
                'verse': verse_num,
                'hebrew': original_verse['hebrew'],
                'hebrew_stripped': hebrew_stripped,
                'hebrew_text_non_sacred': hebrew_non_sacred,  # Fixed: Match db_manager field name
                'english': original_verse['english'],
                'english_text_non_sacred': english_non_sacred,  # Fixed: Match db_manager field name
                'word_count': word_count,
                'instances_detected': len(instances),
                'figurative_detection_deliberation': verse_specific_deliberation,  # Verse-specific deliberation
                'figurative_detection_deliberation_non_sacred': verse_specific_deliberation_non_sacred,
                'model_used': 'gpt-5.1-medium-batched',
                'truncation_occurred': 'no',  # Batched mode doesn't have truncation issues
                'pro_model_used': 'no',
                'both_models_truncated': 'no',
                'tertiary_decomposed': 'no'
            }

            logger.debug(f"Verse data for insertion: {json.dumps(verse_data, indent=2, ensure_ascii=False)}")
            # Insert verse into database
            verse_id = db_manager.insert_verse(verse_data)
            verses_stored += 1

            # Process instances for this verse
            instances_with_db_ids = []

            for j, instance in enumerate(instances):
                # Prepare instance data for database
                figurative_data = {
                    'figurative_language': instance.get('figurative_language', 'no'),
                    'simile': instance.get('simile', 'no'),
                    'metaphor': instance.get('metaphor', 'no'),
                    'personification': instance.get('personification', 'no'),
                    'idiom': instance.get('idiom', 'no'),
                    'hyperbole': instance.get('hyperbole', 'no'),
                    'metonymy': instance.get('metonymy', 'no'),
                    'other': instance.get('other', 'no'),
                    'confidence': instance.get('confidence', 0.5),
                    'figurative_text': instance.get('english_text', ''),
                    'figurative_text_in_hebrew': instance.get('hebrew_text', ''),
                    'figurative_text_in_hebrew_stripped': HebrewTextProcessor.strip_diacritics(instance.get('hebrew_text', '')),
                    'figurative_text_in_hebrew_non_sacred': divine_names_modifier.modify_divine_names(instance.get('hebrew_text', '')),
                    'explanation': instance.get('explanation', ''),
                    'speaker': instance.get('speaker', ''),
                    'purpose': instance.get('purpose', ''),
                    'target': json.dumps(instance.get('target', [])) if instance.get('target') else '[]',
                    'vehicle': json.dumps(instance.get('vehicle', [])) if instance.get('vehicle') else '[]',
                    'ground': json.dumps(instance.get('ground', [])) if instance.get('ground') else '[]',
                    'posture': json.dumps(instance.get('posture', [])) if instance.get('posture') else '[]',
                    'tagging_analysis_deliberation': '',  # No per-instance deliberation in batched mode
                    'model_used': 'gpt-5.1-medium-batched'
                }

                # Insert instance into database
                figurative_language_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                instances_stored += 1

                # Keep track for validation
                instance_copy = instance.copy()
                instance_copy['db_id'] = figurative_language_id
                instance_copy['verse_ref'] = reference
                instance_copy['instance_id'] = j + 1
                instances_with_db_ids.append(instance_copy)

            # Map this verse to its instances for batched validation
            if instances_with_db_ids:
                verse_to_instances_map[reference] = {
                    'hebrew': original_verse['hebrew'],
                    'english': original_verse['english'],
                    'instances': instances_with_db_ids
                }

        # BATCHED VALIDATION - Validate all instances from all verses in a single API call
        if validator and verse_to_instances_map:
            total_instances = sum(len(v['instances']) for v in verse_to_instances_map.values())
            logger.info(f"[BATCHED VALIDATION] Validating {total_instances} instances from {len(verse_to_instances_map)} verses in ONE API call")

            validation_start = time.time()

            # Collect all instances from all verses with their context
            all_chapter_instances = []

            for verse_ref, verse_info in verse_to_instances_map.items():
                instances = verse_info['instances']
                hebrew_text = verse_info['hebrew']
                english_text = verse_info['english']

                logger.debug(f"Preparing {len(instances)} instances from {verse_ref} for batch validation")

                for instance in instances:
                    # Add verse context to each instance
                    instance['verse_reference'] = verse_ref
                    instance['hebrew_text'] = hebrew_text
                    instance['english_text'] = english_text
                    all_chapter_instances.append(instance)

            # Make a single validation call for all instances in the chapter
            try:
                logger.info(f"Making single validation API call for {len(all_chapter_instances)} instances")
                bulk_validation_results = validator.validate_chapter_instances(all_chapter_instances)

                # VALIDATION PREVENTION MEASURES: Check for validation system failures
                validation_success_count = 0
                validation_failure_count = 0
                validation_bypass_detected = False

                if len(bulk_validation_results) == 0:
                    logger.error(f"VALIDATION FAILURE: No validation results returned for {len(all_chapter_instances)} instances")
                    validation_bypass_detected = True
                elif len(bulk_validation_results) != len(all_chapter_instances):
                    logger.error(f"VALIDATION MISMATCH: Expected {len(all_chapter_instances)} results, got {len(bulk_validation_results)}")
                    validation_bypass_detected = True

                # Check for structured error results
                for result in bulk_validation_results:
                    if 'error' in result or 'fallback_validation' in result:
                        validation_failure_count += 1
                        logger.warning(f"Validation error detected for instance {result.get('instance_id', 'unknown')}")
                    else:
                        validation_success_count += 1

                # Log validation health metrics
                logger.info(f"VALIDATION HEALTH: Successes: {validation_success_count}, Failures: {validation_failure_count}, Total expected: {len(all_chapter_instances)}")

                if validation_bypass_detected or validation_failure_count > 0:
                    logger.error(f"VALIDATION SYSTEM ISSUE DETECTED - Consider running universal_validation_recovery.py on this database")
                    # Don't fail processing, but log the issue for later recovery

                # Create mapping from instance_id to db_id (validator assigns instance_id)
                instance_id_to_db_id = {}
                for instance in all_chapter_instances:
                    instance_id_to_db_id[instance.get('instance_id')] = instance.get('db_id')

                # Track validation processing using shared function
                processed_validation_ids = set()

                # Process validation results using shared function
                for validation_result in bulk_validation_results:
                    success, db_id = process_validation_result(
                        validation_result, instance_id_to_db_id, db_manager, logger
                    )
                    if success:
                        processed_validation_ids.add(validation_result.get('instance_id'))

                # Check for missing validation IDs
                expected_instance_ids = set(instance_id_to_db_id.keys())
                missing_validation_ids = expected_instance_ids - processed_validation_ids

                if missing_validation_ids:
                    logger.error(f"VALIDATION GAP: {len(missing_validation_ids)} instances missing validation results")
                    logger.error(f"Missing instance IDs: {sorted(missing_validation_ids)}")
                    logger.error(f"This indicates a validation API response parsing issue")

                    # Log details for debugging
                    for missing_id in sorted(missing_validation_ids):
                        db_id = instance_id_to_db_id.get(missing_id)
                        logger.error(f"  Instance ID {missing_id} (DB ID: {db_id}) did not receive validation")

                logger.info(f"[BATCHED VALIDATION] Completed single API call for {total_instances} instances")
                logger.info(f"[BATCHED VALIDATION] Processed {len(processed_validation_ids)} validation results")
                if missing_validation_ids:
                    logger.error(f"[BATCHED VALIDATION] WARNING: {len(missing_validation_ids)} instances did not receive validation")
                    logger.info(f"[BATCHED VALIDATION] Auto-recovery will run at end of processing session")

                # VALIDATION PREVENTION MEASURES: Post-update verification checkpoint
                try:
                    # Quick verification that validation data was actually written to database
                    verification_results = db_manager.verify_validation_data_for_chapter(book_name, chapter)

                    # Check if we got valid results
                    if 'error' in verification_results:
                        logger.error(f"Verification failed: {verification_results['error']}")
                    else:
                        # Use decision coverage as primary metric, response coverage as secondary
                        coverage_rate = max(
                            verification_results.get('validation_coverage_rate', 0),  # Based on validation_response
                            verification_results.get('decision_coverage_rate', 0)      # Based on validation_decision_*
                        )

                        if coverage_rate < 95.0:
                            logger.error(f"VALIDATION COVERAGE WARNING: Only {coverage_rate:.1f}% of instances have validation data")
                            logger.error(f"Expected: {len(all_chapter_instances)} instances, With validation: {verification_results.get('instances_with_decisions', verification_results.get('instances_with_validation', 0))}")
                            logger.error(f"RECOMMENDATION: Run universal_validation_recovery.py --database {{db_path}} --chapters {chapter}")
                        else:
                            logger.info(f"VALIDATION VERIFICATION PASSED: {coverage_rate:.1f}% coverage")

                except Exception as verify_error:
                    logger.warning(f"Could not perform validation verification checkpoint: {verify_error}")

            except Exception as e:
                logger.error(f"Batch validation failed for chapter {chapter}: {e}")
                logger.error(f"RECOMMENDATION: Run universal_validation_recovery.py on this database after processing completes")

            validation_time = time.time() - validation_start
            logger.info(f"[BATCHED VALIDATION] Completed in {validation_time:.1f}s")

        processing_time = time.time() - start_time
        total_cost = token_metadata.get('cost', 0)

        # Log corruption and skipped verses summary
        if corrupted_chunks > 0:
            logger.warning(f"STREAM CORRUPTION DETECTED: {corrupted_chunks} corrupted chunks were skipped during streaming")

        if skipped_verses:
            sorted_skipped = sorted(skipped_verses)
            logger.warning(f"VERSES WITH CORRUPTION: The following verses may have incomplete data due to corrupted chunks: {sorted_skipped}")
            logger.warning(f"   Total affected verses: {len(sorted_skipped)} out of {len(verses_data)}")
            logger.info("   Recommendation: Review these verses manually or reprocess this chapter")
        elif corrupted_chunks == 0:
            logger.info("No corruption detected - all verses processed successfully")

        return verses_stored, instances_stored, processing_time, len(verses_data), total_cost

    except Exception as e:
        logger.error(f"Error during batched processing of {book_name} {chapter}: {e}")
        import traceback
        traceback.print_exc()
        return 0, 0, time.time() - start_time, len(verses_data), 0.0

def process_single_verse(verse_data, book_name, chapter, flexible_client, validator, divine_names_modifier, logger, worker_id, chapter_context=None):
    """Process a single verse for parallel execution

    Args:
        verse_data: Dict with verse reference, hebrew, and english text
        book_name: Name of the book being processed
        chapter: Chapter number
        flexible_client: FlexibleTaggingGeminiClient instance
        validator: MetaphorValidator instance
        divine_names_modifier: HebrewDivineNamesModifier instance
        logger: Logger instance
        worker_id: Worker thread ID
        chapter_context: Optional full chapter text for context (used for Proverbs and other wisdom literature)
    """
    try:
        verse_ref = verse_data['reference']
        heb_verse = verse_data['hebrew']
        eng_verse = verse_data['english']

        if logger.level <= logging.INFO:
            logger.info(f"Worker {worker_id}: Processing {verse_ref}")

        # Use flexible tagging analysis (with chapter context for Proverbs)
        result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
            heb_verse, eng_verse, book=book_name, chapter=chapter, chapter_context=chapter_context
        )

        # Handle truncation fallback
        truncation_occurred = metadata.get('truncation_detected', False)
        pro_model_used = False
        both_models_truncated = False
        tertiary_decomposed = False

        if truncation_occurred:
            if logger.level <= logging.WARNING:
                logger.warning(f"Worker {worker_id}: Truncation detected in {verse_ref}, retrying with Pro model")

            result_text, error, metadata = flexible_client.analyze_figurative_language_flexible(
                heb_verse, eng_verse, book=book_name, chapter=chapter, model_override="gemini-2.5-pro",
                chapter_context=chapter_context
            )
            pro_model_used = True

            # Check if Pro model also truncated
            pro_truncation_occurred = metadata.get('truncation_detected', False)
            both_models_truncated = pro_truncation_occurred
            if pro_truncation_occurred:
                if logger.level <= logging.WARNING:
                    logger.warning(f"Worker {worker_id}: Pro model also truncated for {verse_ref} - trying Claude Sonnet 4 fallback")

                # Claude Sonnet 4 fallback
                try:
                    result_text, error, metadata = flexible_client.analyze_with_claude_fallback(
                        heb_verse, eng_verse, book=book_name, chapter=chapter, chapter_context=chapter_context
                    )
                    tertiary_decomposed = True

                    claude_success = not error and metadata.get('instances_count', 0) >= 0
                    instances_found = metadata.get('instances_count', 0)

                    if logger.level <= logging.INFO:
                        logger.info(f"Worker {worker_id}: Claude fallback completed for {verse_ref} - "
                                   f"Success: {claude_success}, Instances: {instances_found}")

                    # Keep both_models_truncated as True since both Gemini models failed
                    # Don't overwrite - both Gemini models actually truncated regardless of Claude success

                except Exception as claude_error:
                    if logger.level <= logging.ERROR:
                        logger.error(f"Worker {worker_id}: Claude fallback failed for {verse_ref}: {claude_error}")
                    # both_models_truncated stays True - both Gemini models truncated

                # Keep truncation_occurred as True to indicate the verse had truncation issues
                truncation_occurred = True

        # Prepare verse data
        hebrew_stripped = HebrewTextProcessor.strip_diacritics(heb_verse)
        hebrew_non_sacred = divine_names_modifier.modify_divine_names(heb_verse)
        english_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(eng_verse)
        instances_count = len(metadata.get('flexible_instances', []))
        figurative_detection = metadata.get('figurative_detection_deliberation', '')
        figurative_detection_non_sacred = divine_names_modifier.modify_divine_names(figurative_detection) if figurative_detection else ''

        # SAFEGUARD: Ensure we don't have truncated deliberation from fallback scenarios
        # If we used Pro model or Claude fallback, verify the deliberation is complete
        if (pro_model_used or tertiary_decomposed) and figurative_detection:
            # Check for known truncation patterns that indicate incomplete deliberation
            truncation_patterns = [
                'I have included this in the',
                'It is included in the',
                'marked it as such in the',
                'I have marked it as such in the',
                'included in the'
            ]

            if any(figurative_detection.endswith(pattern) for pattern in truncation_patterns):
                if logger.level <= logging.WARNING:
                    logger.warning(f"Worker {worker_id}: Detected truncated deliberation in {verse_ref} despite fallback model usage")
                    logger.warning(f"Worker {worker_id}: Deliberation ends with: '{figurative_detection[-100:]}'")

                # Mark as potentially incomplete
                figurative_detection += " [TRUNCATION DETECTED DESPITE FALLBACK]"

        # Determine final model used
        final_model_used = metadata.get('model_used', 'gemini-2.5-flash')
        if tertiary_decomposed and metadata.get('claude_fallback_used'):
            final_model_used = 'claude-sonnet-4-20250514'
        elif pro_model_used:
            final_model_used = 'gemini-2.5-pro'

        verse_result = {
            'reference': verse_ref,
            'book': book_name,
            'chapter': chapter,
            'verse': int(verse_ref.split(':')[1]),
            'hebrew': heb_verse,
            'hebrew_stripped': hebrew_stripped,
            'hebrew_text_non_sacred': hebrew_non_sacred,
            'english': eng_verse,
            'english_text_non_sacred': english_non_sacred,
            'word_count': len(heb_verse.split()),
            'llm_restriction_error': error,
            'figurative_detection_deliberation': figurative_detection,
            'figurative_detection_deliberation_non_sacred': figurative_detection_non_sacred,
            'instances_detected': instances_count,
            'instances_recovered': instances_count,
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'yes' if truncation_occurred else 'no',
            'both_models_truncated': 'yes' if both_models_truncated else 'no',
            'model_used': final_model_used,  # Add to verse-level tracking
            'worker_id': worker_id,
            'instances': metadata.get('flexible_instances', []),
            'tagging_analysis': metadata.get('tagging_analysis_deliberation', ''),
            'tertiary_decomposed': tertiary_decomposed
        }

        if logger.level <= logging.INFO:
            logger.info(f"Worker {worker_id}: Completed {verse_ref} - {instances_count} instances")

        return verse_result, None

    except Exception as e:
        error_msg = f"Worker {worker_id}: Error processing {verse_data.get('reference', 'unknown')}: {str(e)}"
        if logger.level <= logging.ERROR:
            logger.error(error_msg)
        return None, error_msg

def process_verses_parallel(verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context=None):
    """Process verses in parallel and store results

    Args:
        verses_to_process: List of verse data dicts
        book_name: Name of the book
        chapter: Chapter number
        flexible_client: FlexibleTaggingGeminiClient instance
        validator: MetaphorValidator instance
        divine_names_modifier: HebrewDivineNamesModifier instance
        db_manager: DatabaseManager instance
        logger: Logger instance
        max_workers: Number of parallel workers
        chapter_context: Optional full chapter text for context (used for Proverbs)
    """

    logger.info(f"Starting parallel processing: {len(verses_to_process)} verses with {max_workers} workers")
    if chapter_context:
        logger.info(f"Using chapter context for {book_name} {chapter} (wisdom literature mode)")

    all_verse_results = []
    all_instance_results = []

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all verse processing tasks
        future_to_verse = {}
        for i, verse_data in enumerate(verses_to_process):
            worker_id = (i % max_workers) + 1
            future = executor.submit(
                process_single_verse, verse_data, book_name, chapter,
                flexible_client, validator, divine_names_modifier, logger, worker_id, chapter_context
            )
            future_to_verse[future] = verse_data

        # Collect results as they complete
        completed_count = 0
        for future in concurrent.futures.as_completed(future_to_verse):
            verse_data = future_to_verse[future]
            try:
                verse_result, error = future.result()
                completed_count += 1

                if verse_result:
                    all_verse_results.append(verse_result)

                    # Process instances for this verse
                    instances = verse_result.get('instances', [])
                    for j, instance in enumerate(instances):
                        if isinstance(instance, dict):
                            instance_result = {
                                'verse_ref': verse_result['reference'],
                                'instance_number': j + 1,
                                'instance_data': instance,
                                'tagging_analysis': verse_result.get('tagging_analysis', ''),
                                'model_used': verse_result.get('model_used', 'gemini-2.5-flash'),
                                'tertiary_decomposed': verse_result.get('tertiary_decomposed', False)
                            }
                            all_instance_results.append(instance_result)

                # Progress update
                if completed_count % 5 == 0 or completed_count == len(verses_to_process):
                    logger.info(f"Progress: {completed_count}/{len(verses_to_process)} verses completed")

            except Exception as e:
                logger.error(f"Failed to process verse {verse_data.get('reference', 'unknown')}: {e}")

    processing_time = time.time() - start_time

    # Store results in database
    logger.info("Storing results in database...")

    verses_stored = 0
    instances_stored = 0

    for verse_result in all_verse_results:
        try:
            # Store verse
            verse_data = {k: v for k, v in verse_result.items()
                         if k not in ['instances', 'tagging_analysis', 'worker_id', 'tertiary_decomposed']}
            verse_id = db_manager.insert_verse(verse_data)
            verses_stored += 1

            # Store instances for this verse
            verse_instances = [inst for inst in all_instance_results
                             if inst['verse_ref'] == verse_result['reference']]

            # Store instances first, then validate
            instances_with_db_ids = []

            for instance_result in verse_instances:
                instance_data = instance_result['instance_data']

                # Prepare instance data for database
                figurative_data = {
                    'figurative_language': instance_data.get('figurative_language', 'no'),
                    'simile': instance_data.get('simile', 'no'),
                    'metaphor': instance_data.get('metaphor', 'no'),
                    'personification': instance_data.get('personification', 'no'),
                    'idiom': instance_data.get('idiom', 'no'),
                    'hyperbole': instance_data.get('hyperbole', 'no'),
                    'metonymy': instance_data.get('metonymy', 'no'),
                    'other': instance_data.get('other', 'no'),
                    'confidence': instance_data.get('confidence', 0.5),
                    'figurative_text': instance_data.get('english_text', ''),
                    'figurative_text_in_hebrew': instance_data.get('hebrew_text', ''),
                    'figurative_text_in_hebrew_stripped': HebrewTextProcessor.strip_diacritics(instance_data.get('hebrew_text', '')),
                    'figurative_text_in_hebrew_non_sacred': divine_names_modifier.modify_divine_names(instance_data.get('hebrew_text', '')),
                    'explanation': instance_data.get('explanation', ''),
                    'speaker': instance_data.get('speaker', ''),
                    'purpose': instance_data.get('purpose', ''),
                    'target': json.dumps(instance_data.get('target', [])) if instance_data.get('target') else '[]',
                    'vehicle': json.dumps(instance_data.get('vehicle', [])) if instance_data.get('vehicle') else '[]',
                    'ground': json.dumps(instance_data.get('ground', [])) if instance_data.get('ground') else '[]',
                    'posture': json.dumps(instance_data.get('posture', [])) if instance_data.get('posture') else '[]',
                    'tagging_analysis_deliberation': instance_result.get('tagging_analysis', ''),
                    'model_used': instance_result.get('model_used', 'gemini-2.5-flash')
                }

                figurative_language_id = db_manager.insert_figurative_language(verse_id, figurative_data)
                instances_stored += 1

                # Keep track of instance and its new DB ID for validation
                instance_data['db_id'] = figurative_language_id
                instances_with_db_ids.append(instance_data)

            # VALIDATION STEP - Add bulk validation for all instances in this verse
            if validator and instances_with_db_ids:
                try:
                    logger.debug(f"Starting validation for {len(instances_with_db_ids)} instances in {verse_result['reference']}")
                    bulk_validation_results = validator.validate_verse_instances(instances_with_db_ids, verse_result['hebrew'], verse_result['english'])

                    # Create a mapping from instance_id to db_id for easy lookup
                    instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances_with_db_ids}

                    # Process the bulk validation results
                    for validation_result in bulk_validation_results:
                        instance_id = validation_result.get('instance_id')
                        results = validation_result.get('validation_results', {})

                        db_id = instance_id_to_db_id.get(instance_id)

                        if not db_id:
                            logger.error(f"Could not find DB ID for validation result with instance_id {instance_id}")
                            continue

                        any_valid = False
                        validation_data = {}
                        for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                            validation_data[f'final_{fig_type}'] = 'no'

                        for fig_type, result in results.items():
                            decision = result.get('decision')
                            reason = result.get('reason', '')
                            reclassified_type = result.get('reclassified_type')

                            if decision == 'RECLASSIFIED' and reclassified_type:
                                validation_data[f'validation_decision_{fig_type}'] = 'RECLASSIFIED'
                                validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"
                                validation_data[f'final_{reclassified_type}'] = 'yes'
                                any_valid = True
                                logger.debug(f"RECLASSIFIED: {fig_type} → {reclassified_type} - {reason}")
                            elif decision == 'VALID':
                                validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                validation_data[f'final_{fig_type}'] = 'yes'
                                any_valid = True
                                logger.debug(f"VALID: {fig_type} - {reason}")
                            else: # INVALID
                                validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                                validation_data[f'validation_reason_{fig_type}'] = reason
                                logger.debug(f"INVALID: {fig_type} - {reason}")

                        validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'

                    # Store the complete validation response for verification
                    validation_data['validation_response'] = json.dumps({
                        'instance_id': instance_id,
                        'validation_results': results,
                        'timestamp': datetime.now().isoformat()
                    })
                    validation_data['validation_error'] = None  # Explicitly set to None when successful

                    db_manager.update_validation_data(db_id, validation_data)
                    logger.debug(f"Validation data updated for ID: {db_id}")

                except Exception as e:
                    logger.error(f"Validation failed for {verse_result['reference']}: {e}")

        except Exception as e:
            logger.error(f"Error storing {verse_result['reference']}: {e}")

    return verses_stored, instances_stored, processing_time, len(verses_to_process)

def main():
    """Main execution function"""
    # Look for .env in parent directory (project root), not in private/
    project_root = os.path.dirname(os.path.dirname(__file__))
    dotenv_path = os.path.join(project_root, '.env')
    was_loaded = load_dotenv(dotenv_path=dotenv_path)

    # Check for command-line arguments
    if len(sys.argv) == 3:
        # Command-line mode: python script.py BookName ChapterNumber
        book_name = sys.argv[1]
        chapter_num = int(sys.argv[2])

        # Use centralized books configuration
        valid_books = SUPPORTED_BOOKS

        if book_name not in valid_books:
            print(f"Error: Book '{book_name}' not supported. Valid books: {', '.join(valid_books.keys())}")
            return

        if not 1 <= chapter_num <= valid_books[book_name]:
            print(f"Error: Chapter {chapter_num} not valid for {book_name} (1-{valid_books[book_name]})")
            return

        # Create selection structure for command-line mode
        selection = {
            'book_selections': {book_name: {chapter_num: 'ALL_VERSES'}},
            'max_workers': 6,
            'enable_debug': False
        }

        # Special database name for Proverbs 3
        if book_name == "Proverbs" and chapter_num == 3:
            db_name = "Proverbs.db"
        else:
            # Generate filename as usual
            base_filename = f"{book_name.lower()}_c{chapter_num}_all_v_batched_{datetime.now().strftime('%Y%m%d_%H%M')}"
            db_name = f"{base_filename}.db"
    else:
        # Interactive mode
        selection = get_user_selection()
        if not selection:
            return

        # Will generate filename later in interactive mode
        db_name = None

    book_selections = selection['book_selections']
    max_workers = selection['max_workers']
    enable_debug = selection['enable_debug']

    # Generate filename from selections (for interactive mode or if not set above)
    def generate_filename_from_selections(book_selections):
        now = datetime.now()
        date_part = now.strftime("%Y%m%d")
        time_part = now.strftime("%H%M")

        if len(book_selections) == 1:
            # Single book
            book_name = list(book_selections.keys())[0]
            book_part = book_name.lower()

            if book_selections[book_name] == 'FULL_BOOK':
                chapter_part = "full"
                verse_part = "full"
            else:
                chapters = sorted(list(book_selections[book_name].keys()))
                if len(chapters) == 1:
                    chapter_part = f"ch{chapters[0]}"
                    verses = book_selections[book_name][chapters[0]]
                    if verses == 'ALL_VERSES':
                        verse_part = "all_v"
                    else:
                        verse_part = f"custom_v"
                else:
                    # Use range format: ch1-10 instead of c10
                    chapter_part = f"ch{chapters[0]}-{chapters[-1]}"
                    verse_part = "all_v"
        else:
            # Multiple books
            book_part = f"{len(book_selections)}books"
            total_chapters = 0
            for book_name, chapters in book_selections.items():
                if chapters == 'FULL_BOOK':
                    total_chapters += SUPPORTED_BOOKS.get(book_name, 25)
                else:
                    total_chapters += len(chapters)
            chapter_part = f"c{total_chapters}"
            verse_part = "multi_v"

        base_filename = f"{book_part}_{chapter_part}_{verse_part}_parallel_{date_part}_{time_part}"
        return base_filename

    # Use provided db_name or generate one
    if db_name is None:
        base_filename = generate_filename_from_selections(book_selections)
        db_name = f"{base_filename}.db"
        log_file = f"{base_filename}_log.txt"
        json_file = f"{base_filename}_results.json"
    else:
        # For command-line mode with specific db_name
        base_filename = db_name.replace('.db', '')
        log_file = f"{base_filename}_log.txt"
        json_file = f"{base_filename}_results.json"

    # Create summary of what will be processed (use centralized configs)
    books_info = SUPPORTED_BOOKS

    total_tasks = 0
    summary_lines = []

    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            # Use centralized verse estimates
            estimated_verses = VERSE_ESTIMATES.get(book_name, 1000)  # Default estimate
            total_tasks += estimated_verses
            summary_lines.append(f"  {book_name}: FULL BOOK (~{estimated_verses} verses)")
        else:
            for chapter, verses in chapters.items():
                if verses == 'ALL_VERSES':
                    # Estimate verses per chapter (approximate)
                    estimated_verses = 25  # Average verses per chapter
                    total_tasks += estimated_verses
                    summary_lines.append(f"  {book_name} {chapter}: all verses (~{estimated_verses})")
                else:
                    # For specific verse selections, we'll count during processing
                    total_tasks += 20  # Rough estimate
                    summary_lines.append(f"  {book_name} {chapter}: selected verses")

    print(f"\n=== PARALLEL PROCESSING SUMMARY ===")
    print(f"Books: {len(book_selections)}")
    print(f"Estimated verses to process: ~{total_tasks}")
    for line in summary_lines[:10]:  # Show first 10 for brevity
        print(line)
    if len(summary_lines) > 10:
        print(f"  ... and {len(summary_lines) - 10} more chapter/verse combinations")
    print(f"\nParallel workers: {max_workers}")
    print(f"Debug logging: {'enabled' if enable_debug else 'disabled'}")
    print(f"Output files: {base_filename}.*")
    print(f"Database: {db_name}")

    # Skip confirmation for command-line mode
    if len(sys.argv) == 3:
        print(f"\nProcessing {book_name} {chapter_num} (command-line mode)...")
    else:
        proceed = input("\nProceed with parallel processing? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Processing cancelled.")
            return

    logger = setup_logging(log_file, enable_debug)

    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}")

    # Initialize run context for tracking
    run_context = RunContext(book_selections, output_dir=os.path.dirname(db_name) if db_name else ".")

    # Log processing summary with run ID
    logger.info(f"=== MULTI-BOOK PARALLEL PROCESSING STARTED ===")
    logger.info(f"Run ID: {run_context.run_id}")
    logger.info(f"Pipeline Version: {PIPELINE_VERSION}")
    logger.info(f"Total books: {len(book_selections)}")
    logger.info(f"Estimated verses: ~{total_tasks}")
    logger.info(f"Workers: {max_workers}")
    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            logger.info(f"Book: {book_name} - FULL BOOK")
        else:
            logger.info(f"Book: {book_name} - Chapters: {list(chapters.keys())}")

    start_time = time.time()

    # Initialize Sefaria cache for faster reruns
    sefaria_cache = SefariaCache()

    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found")

        logger.info("Initializing Sefaria client...")
        sefaria = SefariaClient()

        logger.info(f"Creating database: {db_name}")
        db_manager = DatabaseManager(db_name)
        db_manager.connect()
        db_manager.setup_database()

        # Add processing_runs table for tracking
        db_manager.cursor.execute("""
            CREATE TABLE IF NOT EXISTS processing_runs (
                id INTEGER PRIMARY KEY,
                run_id TEXT,
                book TEXT,
                chapter_start INTEGER,
                chapter_end INTEGER,
                started_at TEXT,
                completed_at TEXT,
                model_used TEXT,
                reasoning_effort TEXT,
                verses_processed INTEGER,
                instances_detected INTEGER,
                validation_coverage_rate REAL,
                estimated_cost REAL,
                failures_count INTEGER,
                pipeline_version TEXT
            )
        """)
        db_manager.commit()

        logger.info("Initializing MetaphorValidator with GPT-5.1 MEDIUM...")
        # MetaphorValidator now uses OpenAI GPT-5.1, not Gemini
        validator = MetaphorValidator(db_manager=db_manager, logger=logger)

        logger.info("Initializing Flexible Tagging Gemini Client...")
        flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

        logger.info("Initializing Hebrew Divine Names Modifier...")
        divine_names_modifier = HebrewDivineNamesModifier(logger=logger)

        total_verses, total_instances, total_errors = 0, 0, 0
        all_results = []
        failed_chapters = []  # Track chapters that failed processing

        # Process each book, chapter, and verse selection
        for book_name, chapters in book_selections.items():
            logger.info(f"\n=== PROCESSING BOOK: {book_name.upper()} ===")

            if chapters == 'FULL_BOOK':
                # Use centralized config
                max_chapters = SUPPORTED_BOOKS[book_name]
                logger.info(f"Processing full book: all {max_chapters} chapters with all verses")

                for chapter in range(1, max_chapters + 1):
                    logger.info(f"--- PROCESSING: {book_name} {chapter} (FULL BOOK) ---")

                    # Fetch all verses for the chapter (with caching)
                    reference = f"{book_name}.{chapter}"
                    cached = sefaria_cache.get(reference)
                    if cached and cached[0]:
                        verses_data = cached[0]
                        logger.info(f"Using cached Sefaria data for {reference}")
                    else:
                        verses_data, _ = sefaria.extract_hebrew_text(reference)
                        if verses_data:
                            sefaria_cache.set(reference, verses_data)
                            logger.debug(f"Cached Sefaria data for {reference}")

                    if not verses_data:
                        logger.error(f"Failed to get text for {book_name} {chapter}")
                        failed_chapters.append({
                            'book': book_name,
                            'chapter': chapter,
                            'verses_attempted': 0,
                            'reason': 'Sefaria API failed to return text'
                        })
                        run_context.add_chapter_failure(
                            book_name, chapter,
                            'Sefaria API failed to return text',
                            error_type='sefaria_api_failure'
                        )
                        continue

                    logger.info(f"Processing all {len(verses_data)} verses from {book_name} {chapter}")

                    # Use BATCHED processing for prophetic/wisdom books
                    if book_name in BATCHED_PROCESSING_BOOKS:
                        logger.info(f"[BATCHED MODE ENABLED] Using GPT-5.1 MEDIUM for {book_name} {chapter}")

                        v, i, processing_time, total_attempted, chapter_cost = process_chapter_batched(
                            verses_data, book_name, chapter, validator, divine_names_modifier, db_manager, logger, run_context
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s (Cost: ${chapter_cost:.4f})")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                        # Track failed chapters
                        if v == 0 and total_attempted > 0:
                            failed_chapters.append({
                                'book': book_name,
                                'chapter': chapter,
                                'verses_attempted': total_attempted,
                                'reason': 'Batched processing returned 0 verses (likely JSON parsing failure)'
                            })
                            run_context.add_chapter_failure(
                                book_name, chapter,
                                'Batched processing returned 0 verses (likely JSON parsing failure)',
                                verses_attempted=total_attempted,
                                error_type='json_parsing_failure'
                            )
                            logger.error(f"CHAPTER FAILED: {book_name} {chapter} - 0 verses stored from {total_attempted} attempted")
                        else:
                            # Record success
                            run_context.record_chapter_success(
                                book_name, chapter, v, i,
                                processing_time, chapter_cost,
                                'gpt-5.1-medium-batched'
                            )

                        db_manager.commit()
                    else:
                        # Use per-verse parallel processing for other books
                        # Generate chapter context for Proverbs (wisdom literature needs full chapter context)
                        chapter_context_text = None
                        if book_name == "Proverbs":
                            # Build full chapter text from all verses
                            hebrew_chapter = "\n".join([v['hebrew'] for v in verses_data])
                            english_chapter = "\n".join([v['english'] for v in verses_data])
                            chapter_context_text = f"=== {book_name} Chapter {chapter} ===\n\nHebrew:\n{hebrew_chapter}\n\nEnglish:\n{english_chapter}"
                            logger.info(f"Generated chapter context for Proverbs {chapter} ({len(chapter_context_text)} chars)")

                        # Process verses in parallel
                        v, i, processing_time, total_attempted = process_verses_parallel(
                            verses_data, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context_text
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                        db_manager.commit()
            else:
                # Process specific chapters and verses
                for chapter, verse_selection in chapters.items():
                    logger.info(f"--- PROCESSING: {book_name} {chapter} ---")

                    # Fetch verses for the chapter
                    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
                    if not verses_data:
                        logger.error(f"Failed to get text for {book_name} {chapter}")
                        failed_chapters.append({
                            'book': book_name,
                            'chapter': chapter,
                            'verses_attempted': 0,
                            'reason': 'Sefaria API failed to return text'
                        })
                        continue

                    # Filter verses based on user selection
                    if verse_selection == 'ALL_VERSES':
                        verses_to_process = verses_data
                        logger.info(f"Processing all {len(verses_to_process)} verses from {book_name} {chapter}")
                    else:
                        # Parse the verse selection string
                        max_verses = len(verses_data)
                        if isinstance(verse_selection, str) and verse_selection.lower() != 'all':
                            parsed_verses = parse_selection(verse_selection, max_verses, "verse")
                            if parsed_verses:
                                verses_to_process = [v for v in verses_data if int(v['reference'].split(':')[1]) in parsed_verses]
                                logger.info(f"Processing {len(verses_to_process)} selected verses: {parsed_verses}")
                            else:
                                logger.error(f"Invalid verse selection: {verse_selection}")
                                continue
                        else:
                            verses_to_process = verses_data
                            logger.info(f"Processing all {len(verses_to_process)} verses from {book_name} {chapter}")

                    # Use BATCHED processing for Proverbs and Isaiah (GPT-5.1 MEDIUM)
                    if book_name in ["Proverbs", "Isaiah", "Jeremiah"]:
                        logger.info(f"[BATCHED MODE ENABLED] Using GPT-5.1 MEDIUM for {book_name} {chapter}")

                        v, i, processing_time, total_attempted, chapter_cost = process_chapter_batched(
                            verses_to_process, book_name, chapter, validator, divine_names_modifier, db_manager, logger
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s (Cost: ${chapter_cost:.4f})")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                        # Track failed chapters
                        if v == 0 and total_attempted > 0:
                            failed_chapters.append({
                                'book': book_name,
                                'chapter': chapter,
                                'verses_attempted': total_attempted,
                                'reason': 'Batched processing returned 0 verses (likely JSON parsing failure)'
                            })
                            logger.error(f"CHAPTER FAILED: {book_name} {chapter} - 0 verses stored from {total_attempted} attempted")

                        db_manager.commit()
                    else:
                        # Use per-verse parallel processing for other books
                        # Generate chapter context for other wisdom literature if needed
                        chapter_context_text = None

                        # Process verses in parallel
                        v, i, processing_time, total_attempted = process_verses_parallel(
                            verses_to_process, book_name, chapter, flexible_client, validator, divine_names_modifier, db_manager, logger, max_workers, chapter_context_text
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

                        db_manager.commit()

        total_time = time.time() - start_time

        # Generate summary - keep database open for validation check
        print(f"\n=== PARALLEL PROCESSING COMPLETE ===")
        print(f"Database: {db_name}")
        print(f"Log file: {log_file}")
        print(f"Books processed: {len(book_selections)}")
        print(f"Total verses processed: {total_verses}")
        print(f"Total instances found: {total_instances}")
        print(f"Total processing time: {total_time:.1f} seconds")
        if total_verses > 0:
            print(f"Average time per verse: {total_time/total_verses:.2f} seconds")
            detection_rate = (total_instances / total_verses) * 100
            print(f"Figurative language detection rate: {detection_rate:.1f}%")
        else:
            print(f"Average time per verse: N/A (no verses processed)")
            print(f"Figurative language detection rate: N/A")
        print(f"Workers used: {max_workers}")
        print(f"\n==> Processed {total_verses} verses from {len(book_selections)} books")
        print(f"** Total time: {total_time:.1f} seconds with {max_workers} parallel workers")

        # Display validation error summary
        validation_issues = []

        # Check validation coverage for all processed chapters
        if validator and db_manager and total_verses > 0:
            print(f"\n{'='*60}")
            print(f"VALIDATION COVERAGE CHECK")
            print(f"{'='*60}")

            for book_name, chapters in book_selections.items():
                if chapters == 'FULL_BOOK':
                    max_chapters = SUPPORTED_BOOKS[book_name]
                    chapters_to_check = range(1, max_chapters + 1)
                else:
                    chapters_to_check = chapters.keys()

                for chapter in chapters_to_check:
                    try:
                        verification = db_manager.verify_validation_data_for_chapter(book_name, chapter)
                        if verification.get('needs_recovery', False):
                            # Use decision coverage as primary metric, response coverage as secondary
                            coverage_rate = max(
                                verification.get('validation_coverage_rate', 0),  # Based on validation_response
                                verification.get('decision_coverage_rate', 0)      # Based on validation_decision_*
                            )
                            validation_issues.append({
                                'book': book_name,
                                'chapter': chapter,
                                'coverage': coverage_rate,
                                'total': verification.get('total_instances', 0),
                                'validated': verification.get('instances_with_decisions', verification.get('instances_with_validation', 0))
                            })
                    except:
                        # Skip chapters that couldn't be verified
                        pass

            if validation_issues:
                print(f"\nVALIDATION ISSUES FOUND IN {len(validation_issues)} CHAPTER(S)")
                print(f"{'='*60}")
                for issue in validation_issues[:10]:
                    print(f"  {issue['book']} Chapter {issue['chapter']}:")
                    print(f"     Coverage: {issue['coverage']:.1f}% ({issue['validated']}/{issue['total']} instances)")
                if len(validation_issues) > 10:
                    print(f"  ... and {len(validation_issues) - 10} more")

                # AUTOMATIC RECOVERY
                print(f"\n[AUTO-RECOVERY] Attempting to recover missing validations...")
                print(f"{'='*60}")

                total_recovered = 0
                total_failed = 0

                for issue in validation_issues:
                    recovery_stats = recover_missing_validations(
                        db_manager, validator, issue['book'], issue['chapter'], logger
                    )
                    total_recovered += recovery_stats['recovered']
                    total_failed += recovery_stats['failed']

                print(f"\n[AUTO-RECOVERY] Results:")
                print(f"   Recovered: {total_recovered}")
                print(f"   Failed: {total_failed}")

                # Re-verify after recovery
                if total_recovered > 0:
                    print(f"\n[POST-RECOVERY VERIFICATION]")
                    still_missing = 0
                    for issue in validation_issues:
                        recheck = db_manager.verify_validation_data_for_chapter(
                            issue['book'], issue['chapter']
                        )
                        if recheck.get('needs_recovery', False):
                            coverage = max(
                                recheck.get('validation_coverage_rate', 0),
                                recheck.get('decision_coverage_rate', 0)
                            )
                            print(f"   {issue['book']} {issue['chapter']}: {coverage:.1f}% coverage")
                            still_missing += 1

                    if still_missing == 0:
                        print(f"   All validation issues resolved!")
                    else:
                        print(f"\n   WARNING: {still_missing} chapters still have issues")
                        print(f"   Manual intervention may be required")

                print(f"{'='*60}")

                logger.info(f"AUTO-RECOVERY: {total_recovered} recovered, {total_failed} failed")
            else:
                print(f"All processed chapters have healthy validation coverage (>95%)")
                print(f"{'='*60}")

        # Display failed chapters summary
        if failed_chapters:
            print(f"\n{'='*60}")
            print(f"WARNING: {len(failed_chapters)} CHAPTER(S) FAILED TO PROCESS")
            print(f"{'='*60}")
            for failure in failed_chapters:
                print(f"  • {failure['book']} Chapter {failure['chapter']}")
                print(f"    Verses attempted: {failure['verses_attempted']}")
                print(f"    Reason: {failure['reason']}")
            print(f"{'='*60}")
            print(f"To retry failed chapters, run the processor again with:")
            for failure in failed_chapters:
                print(f"  python interactive_parallel_processor.py {failure['book']} {failure['chapter']}")
            print(f"{'='*60}")
            logger.error(f"FAILED CHAPTERS SUMMARY: {len(failed_chapters)} chapter(s) failed")
            for failure in failed_chapters:
                logger.error(f"  - {failure['book']} {failure['chapter']}: {failure['reason']}")
        else:
            print(f"\nAll chapters processed successfully!")

        # Save basic results summary (enhanced with run context)
        summary = {
            'run_id': run_context.run_id,
            'pipeline_version': PIPELINE_VERSION,
            'processing_info': {
                'books_processed': len(book_selections),
                'book_selections': {k: 'FULL_BOOK' if v == 'FULL_BOOK' else list(v.keys()) for k, v in book_selections.items()},
                'max_workers': max_workers,
                'timestamp': datetime.now().isoformat(),
                'total_verses': total_verses,
                'total_instances': total_instances,
                'processing_time_seconds': total_time,
                'avg_time_per_verse': total_time/total_verses if total_verses > 0 else 0
            },
            'failed_chapters': failed_chapters,
            'usage_statistics': flexible_client.get_usage_info(),
            'validation_statistics': validator.get_validation_stats() if validator else {}
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Summary saved: {json_file}")

        # Save failure manifest (always save, even if no failures, for documentation)
        failure_manifest_path = run_context.save_failure_manifest(base_filename)
        print(f"Failure manifest saved: {failure_manifest_path}")
        logger.info(f"Failure manifest saved: {failure_manifest_path}")

        # Save processing manifest for documentation
        processing_manifest_path = run_context.save_processing_manifest(base_filename)
        print(f"Processing manifest saved: {processing_manifest_path}")
        logger.info(f"Processing manifest saved: {processing_manifest_path}")

        # Record processing run in database
        try:
            db_manager.cursor.execute("""
                INSERT INTO processing_runs (
                    run_id, book, chapter_start, chapter_end,
                    started_at, completed_at, model_used, reasoning_effort,
                    verses_processed, instances_detected, validation_coverage_rate,
                    estimated_cost, failures_count, pipeline_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_context.run_id,
                list(book_selections.keys())[0] if len(book_selections) == 1 else 'multiple',
                min([c for book_chapters in book_selections.values()
                     for c in (range(1, SUPPORTED_BOOKS.get(book, 1) + 1) if book_chapters == 'FULL_BOOK' else book_chapters.keys())
                     for book in book_selections.keys()], default=1),
                max([c for book_chapters in book_selections.values()
                     for c in (range(1, SUPPORTED_BOOKS.get(book, 1) + 1) if book_chapters == 'FULL_BOOK' else book_chapters.keys())
                     for book in book_selections.keys()], default=1),
                run_context.started_at,
                datetime.now().isoformat(),
                'gpt-5.1-medium-batched',
                'medium',
                total_verses,
                total_instances,
                100.0 if not validation_issues else (100.0 - len(validation_issues) * 5),  # Rough estimate
                run_context.total_cost,
                len(failed_chapters),
                PIPELINE_VERSION
            ))
            db_manager.commit()
            logger.info(f"Processing run recorded in database with run_id: {run_context.run_id}")
        except Exception as db_error:
            logger.warning(f"Could not record processing run in database: {db_error}")

        # Close database connection
        if db_manager:
            db_manager.close()

        logger.info(f"=== PARALLEL PROCESSING COMPLETE ===")
        logger.info(f"Run ID: {run_context.run_id}")
        logger.info(f"Final stats: {total_instances} instances from {total_verses} verses")

    except Exception as e:
        logger.error(f"CRITICAL FAILURE: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Check the log file for detailed error information.")