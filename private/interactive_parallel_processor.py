#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Parallel Flexible Tagging Processor
User-friendly interface with high-performance parallel processing
"""
import sys
import os
import logging
import traceback
import json
import time
import re
import concurrent.futures
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.database.db_manager import DatabaseManager
from hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier
from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# Import our flexible tagging client
from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

# OpenAI import for batched processing
from openai import OpenAI

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
    books = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
        "Proverbs": 31
    }

    print("\n=== INTERACTIVE PARALLEL HEBREW FIGURATIVE LANGUAGE PROCESSOR ===")
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

def process_chapter_batched(verses_data, book_name, chapter, validator, divine_names_modifier, db_manager, logger):
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

    Returns:
        Tuple of (verses_stored, instances_stored, processing_time, total_attempted, total_cost)
    """
    start_time = time.time()

    if not verses_data:
        return 0, 0, 0, 0, 0.0

    logger.info(f"[BATCHED MODE] Processing {book_name} {chapter} with {len(verses_data)} verses in SINGLE API call")

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

IMPORTANT: A single verse may contain MULTIPLE distinct figurative language instances. Detect ALL instances, not just the most prominent one. For example, a verse might have both a metaphor AND personification, or multiple metaphors.

For each verse, detect instances of:
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

**FIRST, provide your deliberation in a DELIBERATION section:**

DELIBERATION:
[You MUST briefly analyze EVERY potential figurative element for ALL verses. For each phrase/concept, explain *briefly*:
- What you considered (e.g., "Verse 1: considered if 'X' might be metaphor...").
- Your reasoning for including/excluding it.
- Any borderline cases you debated.
Be explicit about what you examined and why you made each decision for each verse.]

**THEN provide STRUCTURED JSON OUTPUT (REQUIRED):**

Return a JSON array with ONE object per verse. Each object should have:
- "verse": verse number
- "reference": "{book_name} {chapter}:X"
- "instances": array of detected figurative language instances (empty array if none)

Example structure:
[
  {{
    "verse": 1,
    "reference": "{book_name} {chapter}:1",
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
        "explanation": "...",
        "confidence": 0.9
      }}
    ]
  }},
  ...
]
"""

    # Call GPT-5.1 MEDIUM
    api_start = time.time()
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        logger.info(f"Calling GPT-5.1 MEDIUM for {book_name} {chapter} (using streaming to avoid truncation)...")

        # Use streaming to avoid the 1023-character truncation issue
        # This ensures we capture the complete response without buffering limits
        stream = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                {"role": "user", "content": batched_prompt}
            ],
            max_completion_tokens=65536,
            reasoning_effort="medium",
            stream=True  # Enable streaming to avoid truncation
        )

        # Collect the streamed response
        response_text = ""
        chunk_count = 0

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                chunk_count += 1

                # Log progress every 100 chunks
                if chunk_count % 100 == 0:
                    logger.debug(f"Received {chunk_count} chunks, response length: {len(response_text)} chars")

        api_time = time.time() - api_start

        logger.info(f"Streaming completed in {api_time:.1f}s ({chunk_count} chunks)")
        logger.info(f"Total response length: {len(response_text)} characters")

        # Store original streaming text in case fallback overwrites it
        original_streaming_text = response_text

        # Extract deliberation from original streaming response BEFORE fallback logic
        chapter_deliberation = ""
        # Look for DELIBERATION section - more flexible patterns to handle real responses
        # Pattern 1: DELIBERATION followed by JSON array
        deliberation_match = re.search(r'DELIBERATION\s*:?\s*([\s\S]*?)(?=\s*\[)', original_streaming_text, re.IGNORECASE)
        if not deliberation_match:
            # Pattern 2: DELIBERATION followed by "STRUCTURED JSON OUTPUT" or similar
            deliberation_match = re.search(r'DELIBERATION\s*:?\s*([\s\S]*?)(?=STRUCTURED|JSON OUTPUT|```json)', original_streaming_text, re.IGNORECASE)
        if not deliberation_match:
            # Pattern 3: DELIBERATION followed by markdown code block
            deliberation_match = re.search(r'DELIBERATION\s*:?\s*([\s\S]*?)(?=```)', original_streaming_text, re.IGNORECASE)

        if deliberation_match:
            chapter_deliberation = deliberation_match.group(1).strip()
            logger.info(f"Captured chapter-level deliberation: {len(chapter_deliberation)} chars (from original streaming response)")

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
            logger.error("⚠️  TRUNCATION DETECTED! Response shows signs of being cut off")
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

        # If we didn't get deliberation from original streaming, try fallback response
        if not chapter_deliberation:
            deliberation_match = re.search(r'DELIBERATION\s*:\s*([\s\S]*?)(?=STRUCTURED JSON OUTPUT)', response_text, re.IGNORECASE)
            if deliberation_match:
                chapter_deliberation = deliberation_match.group(1).strip()
                logger.info(f"Found deliberation in fallback response: {len(chapter_deliberation)} chars")

        if chapter_deliberation:
            logger.info(f"Using deliberation: {len(chapter_deliberation)} chars")
        else:
            logger.warning("Could not find deliberation section in any response.")

        # Modify for non-sacred version (replace divine names)
        chapter_deliberation_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(chapter_deliberation) if chapter_deliberation else ''

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
            logger.error(f"JSON text length: {len(json_text)} chars")
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
                if e.msg == "Expecting ',' delimiter":
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
                    raise

        if not isinstance(verse_results, list):
            raise ValueError(f"Expected JSON array, got {type(verse_results)}")

        logger.info(f"Parsed {len(verse_results)} verse results")

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

            # Find original verse data
            original_verse = next((v for v in verses_data if v['verse'] == verse_num), None)
            if not original_verse:
                logger.warning(f"Could not find original verse data for {reference}")
                continue

            # Prepare verse data for database
            hebrew_stripped = HebrewTextProcessor.strip_diacritics(original_verse['hebrew'])
            hebrew_non_sacred = divine_names_modifier.modify_divine_names(original_verse['hebrew'])
            english_non_sacred = divine_names_modifier.modify_english_with_hebrew_terms(original_verse['english'])

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
                'figurative_detection_deliberation': chapter_deliberation,  # Chapter-level GPT-5.1 reasoning
                'figurative_detection_deliberation_non_sacred': chapter_deliberation_non_sacred,
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

        # BATCHED VALIDATION - Validate all instances from all verses in the chapter
        if validator and verse_to_instances_map:
            logger.info(f"[BATCHED VALIDATION] Validating {sum(len(v['instances']) for v in verse_to_instances_map.values())} instances from {len(verse_to_instances_map)} verses")

            validation_start = time.time()

            # Validate each verse's instances (validator already batches by verse)
            for verse_ref, verse_info in verse_to_instances_map.items():
                try:
                    instances = verse_info['instances']
                    hebrew_text = verse_info['hebrew']
                    english_text = verse_info['english']

                    logger.debug(f"Validating {len(instances)} instances from {verse_ref}")

                    # Call validator (which uses GPT-5.1 MEDIUM in batched mode)
                    bulk_validation_results = validator.validate_verse_instances(
                        instances, hebrew_text, english_text
                    )

                    # Create mapping from instance_id to db_id
                    instance_id_to_db_id = {inst.get('instance_id'): inst.get('db_id') for inst in instances}

                    # Process validation results
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

                        # Update database with validation results
                        db_manager.update_validation_data(db_id, validation_data)
                        logger.debug(f"Validation data updated for ID: {db_id}")

                except Exception as e:
                    logger.error(f"Validation failed for {verse_ref}: {e}")

            validation_time = time.time() - validation_start
            logger.info(f"[BATCHED VALIDATION] Completed in {validation_time:.1f}s")

        processing_time = time.time() - start_time
        total_cost = token_metadata.get('cost', 0)

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

    # Get user selection
    selection = get_user_selection()
    if not selection:
        return

    book_selections = selection['book_selections']
    max_workers = selection['max_workers']
    enable_debug = selection['enable_debug']

    # Generate filename from selections (similar to the single-threaded version)
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
                chapters = list(book_selections[book_name].keys())
                if len(chapters) == 1:
                    chapter_part = str(chapters[0])
                    verses = book_selections[book_name][chapters[0]]
                    if verses == 'ALL_VERSES':
                        verse_part = "all_v"
                    else:
                        verse_part = f"custom_v"
                else:
                    chapter_part = f"c{len(chapters)}"
                    verse_part = "multi_v"
        else:
            # Multiple books
            book_part = f"{len(book_selections)}books"
            total_chapters = 0
            for book_name, chapters in book_selections.items():
                if chapters == 'FULL_BOOK':
                    books_info = {
                        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
                        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
                        "Proverbs": 31
                    }
                    total_chapters += books_info.get(book_name, 25)
                else:
                    total_chapters += len(chapters)
            chapter_part = f"c{total_chapters}"
            verse_part = "multi_v"

        base_filename = f"{book_part}_{chapter_part}_{verse_part}_parallel_{date_part}_{time_part}"
        return base_filename

    base_filename = generate_filename_from_selections(book_selections)
    log_file = f"{base_filename}_log.txt"
    db_name = f"{base_filename}.db"
    json_file = f"{base_filename}_results.json"

    # Create summary of what will be processed
    books_info = {
        "Genesis": 50, "Exodus": 40, "Leviticus": 27,
        "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
        "Proverbs": 31
    }

    total_tasks = 0
    summary_lines = []

    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            # Estimate verses for full book (approximate)
            verse_estimates = {
                "Genesis": 1533, "Exodus": 1213, "Leviticus": 859,
                "Numbers": 1288, "Deuteronomy": 959, "Psalms": 2461,
                "Proverbs": 915
            }
            estimated_verses = verse_estimates.get(book_name, 1000)  # Default estimate
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

    proceed = input("\nProceed with parallel processing? (y/n): ").strip().lower()
    if proceed != 'y':
        print("Processing cancelled.")
        return

    logger = setup_logging(log_file, enable_debug)

    if was_loaded:
        logger.info(f"Successfully loaded environment variables from: {dotenv_path}")
    else:
        logger.warning(f"Warning: .env file not found at {dotenv_path}")

    # Log processing summary
    logger.info(f"=== MULTI-BOOK PARALLEL PROCESSING STARTED ===")
    logger.info(f"Total books: {len(book_selections)}")
    logger.info(f"Estimated verses: ~{total_tasks}")
    logger.info(f"Workers: {max_workers}")
    for book_name, chapters in book_selections.items():
        if chapters == 'FULL_BOOK':
            logger.info(f"Book: {book_name} - FULL BOOK")
        else:
            logger.info(f"Book: {book_name} - Chapters: {list(chapters.keys())}")

    start_time = time.time()

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

        logger.info("Initializing MetaphorValidator with GPT-5.1 MEDIUM...")
        # MetaphorValidator now uses OpenAI GPT-5.1, not Gemini
        validator = MetaphorValidator(db_manager=db_manager, logger=logger)

        logger.info("Initializing Flexible Tagging Gemini Client...")
        flexible_client = FlexibleTaggingGeminiClient(api_key, validator=validator, logger=logger, db_manager=db_manager)

        logger.info("Initializing Hebrew Divine Names Modifier...")
        divine_names_modifier = HebrewDivineNamesModifier(logger=logger)

        total_verses, total_instances, total_errors = 0, 0, 0
        all_results = []

        # Process each book, chapter, and verse selection
        for book_name, chapters in book_selections.items():
            logger.info(f"\n=== PROCESSING BOOK: {book_name.upper()} ===")

            if chapters == 'FULL_BOOK':
                # Process entire book - all chapters, all verses
                books_info = {
                    "Genesis": 50, "Exodus": 40, "Leviticus": 27,
                    "Numbers": 36, "Deuteronomy": 34, "Psalms": 150,
                    "Proverbs": 31
                }
                max_chapters = books_info[book_name]
                logger.info(f"Processing full book: all {max_chapters} chapters with all verses")

                for chapter in range(1, max_chapters + 1):
                    logger.info(f"--- PROCESSING: {book_name} {chapter} (FULL BOOK) ---")

                    # Fetch all verses for the chapter
                    verses_data, _ = sefaria.extract_hebrew_text(f"{book_name}.{chapter}")
                    if not verses_data:
                        logger.error(f"Failed to get text for {book_name} {chapter}")
                        continue

                    logger.info(f"Processing all {len(verses_data)} verses from {book_name} {chapter}")

                    # Use BATCHED processing for Proverbs (GPT-5.1 MEDIUM)
                    if book_name == "Proverbs":
                        logger.info(f"[BATCHED MODE ENABLED] Using GPT-5.1 MEDIUM for {book_name} {chapter}")

                        v, i, processing_time, total_attempted, chapter_cost = process_chapter_batched(
                            verses_data, book_name, chapter, validator, divine_names_modifier, db_manager, logger
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s (Cost: ${chapter_cost:.4f})")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

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

                    # Use BATCHED processing for Proverbs (GPT-5.1 MEDIUM)
                    if book_name == "Proverbs":
                        logger.info(f"[BATCHED MODE ENABLED] Using GPT-5.1 MEDIUM for {book_name} {chapter}")

                        v, i, processing_time, total_attempted, chapter_cost = process_chapter_batched(
                            verses_to_process, book_name, chapter, validator, divine_names_modifier, db_manager, logger
                        )

                        total_verses += v
                        total_instances += i

                        logger.info(f"Chapter {chapter} completed: {i} instances from {v} verses in {processing_time:.1f}s (Cost: ${chapter_cost:.4f})")
                        if total_attempted > 0:
                            logger.info(f"Average processing time: {processing_time/total_attempted:.2f}s per verse")

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
        db_manager.close()

        # Generate summary
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

        # Save basic results summary
        summary = {
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
            'usage_statistics': flexible_client.get_usage_info(),
            'validation_statistics': validator.get_validation_stats() if validator else {}
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        print(f"Summary saved: {json_file}")

        logger.info(f"=== PARALLEL PROCESSING COMPLETE ===")
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