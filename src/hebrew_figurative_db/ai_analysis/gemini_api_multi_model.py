#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-model Gemini API with Gemini 2.5 Flash → Gemini 1.5 Flash fallback
Context-aware conservative analysis addressing false negative issues
"""
import google.generativeai as genai
import os
import json
import time
from typing import List, Dict, Optional, Tuple
import re
from enum import Enum


class TextContext(Enum):
    CREATION_NARRATIVE = 'creation_narrative'
    POETIC_BLESSING = 'poetic_blessing'
    LEGAL_CEREMONIAL = 'legal_ceremonial'
    NARRATIVE = 'narrative'


class FinishReason(Enum):
    SAFETY = 'SAFETY'
    RECITATION = 'RECITATION'
    OTHER = 'OTHER'


PRIMARY_MODEL = 'gemini-2.5-flash'
FALLBACK_MODEL = 'gemini-1.5-flash'


class MultiModelGeminiClient:
    """Multi-model Gemini API client with context-aware conservative analysis"""

    def __init__(self, api_key: str, validator=None, logger=None, db_manager=None):
        """
        Initialize multi-model Gemini API client

        Args:
            api_key: Gemini API key
            validator: MetaphorValidator instance
            logger: Logger instance
            db_manager: DatabaseManager instance for logging
        """
        self.api_key = api_key
        self.validator = validator
        self.logger = logger
        self.db_manager = db_manager
        genai.configure(api_key=api_key)

        # Primary model: Gemini 2.5 Flash
        try:
            self.primary_model = genai.GenerativeModel(PRIMARY_MODEL)
            self.primary_model_name = PRIMARY_MODEL
        except Exception:
            # Fallback if 2.5 not available
            self.primary_model = genai.GenerativeModel(FALLBACK_MODEL)
            self.primary_model_name = FALLBACK_MODEL

        # Fallback model: Gemini 1.5 Flash
        self.fallback_model = genai.GenerativeModel(FALLBACK_MODEL)
        self.fallback_model_name = FALLBACK_MODEL

        # Generation configs
        self.primary_config = {
            'temperature': 0.15,  # Slightly higher for better detection
            'top_p': 0.8,
            'top_k': 25,
            'max_output_tokens': 10000,
        }

        self.fallback_config = {
            'temperature': 0.10,  # Conservative for fallback
            'top_p': 0.7,
            'top_k': 20,
            'max_output_tokens': 10000,
        }

        # Usage tracking
        self.request_count = 0
        self.primary_success_count = 0
        self.fallback_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.restriction_reasons = []

    def analyze_figurative_language(self, hebrew_text: str, english_text: str,
                                  book: str = "", chapter: int = 0) -> Tuple[str, Optional[str], Dict]:
        """
        Analyze Hebrew text for figurative language using multi-model approach

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation
            book: Book name for context-aware prompting
            chapter: Chapter number for context-aware prompting

        Returns:
            Tuple of (JSON string with analysis results, error message if restricted, metadata)
        """
        # Determine text context for appropriate prompting
        text_context = self._determine_text_context(book, chapter)

        # Try primary model first
        result, error, metadata = self._try_model_analysis(
            self.primary_model, self.primary_config, self.primary_model_name,
            hebrew_text, english_text, text_context
        )

        if error and self._is_restriction_error(error):
            # Fallback to secondary model for content restrictions
            if self.logger:
                self.logger.info(f"Primary model restricted ({error}), trying fallback...")
            self.restriction_reasons.append(f"{self.primary_model_name}: {error}")

            result, error, fallback_metadata = self._try_model_analysis(
                self.fallback_model, self.fallback_config, self.fallback_model_name,
                hebrew_text, english_text, text_context
            )

            # Update metadata
            metadata.update(fallback_metadata)
            metadata['fallback_used'] = True
            metadata['primary_restriction'] = self.restriction_reasons[-1]
            self.fallback_count += 1
        elif not error:
            # Only count as success if there was no error (including rate limit errors)
            self.primary_success_count += 1
            metadata['fallback_used'] = False

        self.request_count += 1
        return result, error, metadata

    def _try_model_analysis(self, model, config, model_name: str, hebrew_text: str,
                           english_text: str, context: str) -> Tuple[str, Optional[str], Dict]:
        """Try analysis with a specific model, with robust retry logic."""
        prompt = self._create_context_aware_prompt(hebrew_text, english_text, context)
        metadata = {'model_used': model_name, 'context': context, 'retries': 0}
        max_retries = 5
        backoff_factor = 2

        for attempt in range(max_retries):
            try:
                response = model.generate_content(prompt, generation_config=config)

                # Track usage
                if hasattr(response, 'usage_metadata'):
                    input_tokens = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    output_tokens = getattr(response.usage_metadata, 'candidates_token_count', 0)
                    self.total_input_tokens += input_tokens
                    self.total_output_tokens += output_tokens
                    metadata['input_tokens'] = input_tokens
                    metadata['output_tokens'] = output_tokens

                # Check for safety restrictions
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                        finish_reason = candidate.finish_reason
                        if self._is_restriction_reason(finish_reason):
                            error_msg = f"Content restricted: {finish_reason}"
                            return "[]", error_msg, metadata

                # Extract and validate response
                response_text = ""
                try:
                    response_text = response.text
                except Exception as e:
                    # This will catch the "Invalid operation" error
                    finish_reason_name = "Unknown"
                    if 'candidate' in locals() and hasattr(candidate, 'finish_reason') and hasattr(candidate.finish_reason, 'name'):
                        finish_reason_name = candidate.finish_reason.name
                    
                    error_msg = f"Could not access response.text (finish reason: {finish_reason_name}). Error: {e}"
                    if self.logger:
                        self.logger.warning(f"API WARNING: {error_msg}")
                    # We will return this as a non-fatal error and continue processing
                    return "[]", error_msg, metadata

                if response_text:
                    # Debug: Log response length and ending to check for truncation
                    if self.logger:
                        self.logger.debug(f"Raw response length: {len(response_text)} characters")
                        self.logger.debug(f"Response ends with: '{response_text[-100:]}'")

                    cleaned_response, all_instances, deliberation = self._clean_response(response_text.strip(), hebrew_text, english_text)
                    metadata['all_detected_instances'] = all_instances
                    metadata['llm_deliberation'] = deliberation
                    return cleaned_response, None, metadata
                else:
                    return "[]", "No response text generated", metadata

            except Exception as e:
                error_msg = f"{model_name} error: {str(e)}"
                wait_time = 0

                if "429" in error_msg and attempt < max_retries - 1:
                    # Try to parse the recommended retry delay from the error
                    retry_after_match = re.search(r'retry_delay {\s*seconds: (\d+)\s*}', error_msg)
                    if retry_after_match:
                        wait_time = int(retry_after_match.group(1))
                    else:
                        # Fallback to exponential backoff if delay is not specified
                        wait_time = (backoff_factor ** attempt) * 5

                    wait_time += (hash(time.time()) % 1000 / 1000) # Add jitter
                    if self.logger:
                        self.logger.info(f"Rate limit hit. Retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    metadata['retries'] = attempt + 1
                    continue

                if self.logger:
                    self.logger.error(f"API error (non-critical): {error_msg}")
                return "[]", error_msg, metadata

        return "[]", f"Failed after {max_retries} retries due to persistent API errors.", metadata

    def _determine_text_context(self, book: str, chapter: int) -> str:
        """Determine text context for appropriate prompting strategy"""

        # Genesis Creation Narratives (most conservative)
        if book.lower() == 'genesis' and chapter in {1, 2, 3}:
            return TextContext.CREATION_NARRATIVE.value

        # Poetic/Blessing texts (balanced approach)
        elif ((book.lower() == 'genesis' and chapter == 49) or
              (book.lower() == 'deuteronomy' and chapter in {32, 33})):
            return TextContext.POETIC_BLESSING.value

        # Legal/Ceremonial texts (moderate conservative)
        elif book.lower() in {'leviticus', 'numbers'}:
            return TextContext.LEGAL_CEREMONIAL.value

        # Narrative texts (standard approach)
        else:
            return TextContext.NARRATIVE.value

    def _create_context_aware_prompt(self, hebrew_text: str, english_text: str, context: str) -> str:
        """Create context-aware prompt based on text type"""

        base_prompt = f"""You are a biblical Hebrew scholar analyzing this text for figurative language.

Hebrew: {hebrew_text}
English: {english_text}

"""

        if context == TextContext.CREATION_NARRATIVE.value:
            # Ultra-conservative for Genesis 1-3
            context_rules = """🚨 **CREATION NARRATIVE - ULTRA CONSERVATIVE** 🚨

**NEVER MARK AS FIGURATIVE:**
• "unformed and void", "darkness over surface" = LITERAL primordial descriptions
• "lights for signs", "earth brought forth" = LITERAL creation functions
• Divine actions: spoke, blessed, created, made, saw = STANDARD creation verbs
• "breath of life", "living being" = TECHNICAL theological terms
• Geographic descriptions, procedural language

**ONLY MARK IF ABSOLUTELY CLEAR:**
• Obvious cross-domain metaphors"""

        elif context == TextContext.POETIC_BLESSING.value:
            # Balanced approach for poetic texts
            context_rules = """📜 **POETIC BLESSING TEXT - BALANCED DETECTION** 📜

**MARK AS FIGURATIVE:**
• Tribal characterizations using animals: "lion", "wolf", "serpent", "eagle"
• Cross-domain comparisons: "unstable as water", "like a hind let loose"
• Clear metaphorical relationships between people and nature/animals

**BE CONSERVATIVE WITH:**
• Standard genealogical language
• Geographic references
• Historical statements
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger).


**LOOK FOR:**
• Animal metaphors for human characteristics
• Nature imagery for human qualities"""

        elif context == TextContext.LEGAL_CEREMONIAL.value:
            # Moderate conservative for legal texts
            context_rules = """⚖️ **LEGAL/CEREMONIAL TEXT - MODERATE CONSERVATIVE** ⚖️

**NEVER MARK AS FIGURATIVE:**
• Technical religious terms: holy, clean, offering, covenant
• Procedural instructions and ritual descriptions
• Legal formulations and standard phrases
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger).

**MARK AS FIGURATIVE:**
• Clear cross-domain metaphors
• Obvious similes with "like/as" for unlike things"""

        else:  # narrative
            # Standard conservative approach
            context_rules = """📖 **NARRATIVE TEXT - STANDARD CONSERVATIVE** 📖

**BE CONSERVATIVE WITH:**
• Standard narrative language
• Character actions and dialogue
• Historical and genealogical information
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger).
• Biblical idions and set phrases (e.g. לְפִי־חָֽרֶב, פִֽי־יְהֹוָ֖ה,פְּנ֥י הָאֲדָמָֽה) - these are IDIOMS; classify figurative idioms as "idiom" type.

**NEVER MARK AS FIGURATIVE:**
• Comparisons of role or function, such as 'a prophet like myself' (כָּמֹנִי) or 'a prophet like yourself' (כָּמוֹךָ). These are literal statements of equivalence or similarity in function, not figurative similes.
• Proportional or behavioral comparisons, such as 'according to the blessing' or 'like all his fellow Levites'.

**MARK AS FIGURATIVE:**
• Clear metaphors with cross-domain comparisons
• Personification of non-human entities
• Obvious similes"""

        return base_prompt + context_rules + """

**FIRST, provide your deliberation in a DELIBERATION section:**

DELIBERATION:
[You MUST analyze EVERY potential figurative element in this verse. For each phrase/concept, explain briefly:
- What you considered (e.g., "considered if 'X' might be metaphor, metonymy, etc"). Note that synechdoche is a type of metonymy.
- Your reasoning for including/excluding it (e.g., "this is not metaphor, metonymy, etc because...")
- Any borderline cases you debated
Be explicit about what you examined and why you made each decision.
IMPORTANT: Include ALL phrases you marked as figurative in the JSON AND explain your reasoning for including them here.]

**THEN provide JSON OUTPUT (only if genuinely figurative):**
[{"figurative_language": "yes/no", "simile": "yes/no", "metaphor": "yes/no", "personification": "yes/no", "idiom": "yes/no", "hyperbole": "yes/no", "metonymy": "yes/no", "other": "yes/no", "hebrew_text": "Hebrew phrase", "english_text": "English phrase", "explanation": "Brief explanation", "vehicle_level_1": "nature/human/divine/abstract", "vehicle_level_2": "specific", "tenor_level_1": "God/people/covenant", "tenor_level_2": "specific", "confidence": 0.7-1.0, "speaker": "Narrator/name of character", "purpose": "brief purpose"}]

IMPORTANT: Mark each type field as "yes" or "no". A phrase can be multiple types (e.g., both metaphor and idiom). Set figurative_language to "yes" if ANY figurative language is detected.

If no figurative language found: []

Analysis:"""

    def _is_restriction_error(self, error_msg: str) -> bool:
        """Check if error indicates content restriction requiring fallback"""
        restriction_indicators = [
            'Content restricted',
            'SAFETY',
            'RECITATION',
            'OTHER',
            'blocked',
            'filtered'
        ]
        return any(indicator.lower() in error_msg.lower() for indicator in restriction_indicators)

    def _is_restriction_reason(self, finish_reason) -> bool:
        """Check if finish reason indicates content restriction"""
        restriction_reasons = {reason.value for reason in FinishReason}

        if hasattr(finish_reason, 'name'):
            return finish_reason.name in restriction_reasons
        else:
            return str(finish_reason).upper() in restriction_reasons

    def _clean_response(self, response_text: str, hebrew_text: str, english_text: str) -> Tuple[str, List[Dict], str]:
        """Clean and parse the JSON response, returning valid instances, all instances, and deliberation."""

        # Extract deliberation section (handle case variations and formatting)
        deliberation = ""
        # First try to extract deliberation properly, stopping at JSON OUTPUT or array start
        deliberation_match = re.search(r'(?:MY\s+)?DELIBERATION\s*(?:SECTION)?\s*:?\s*([\s\S]*?)(?=JSON OUTPUT:|---\s*$|\n\s*\[)', response_text, re.IGNORECASE)
        if deliberation_match:
            deliberation = deliberation_match.group(1).strip()
            # Clean up deliberation by removing any trailing incomplete content
            deliberation = re.sub(r'\n\s*\d+\.\s*\*\*[^*]*$', '', deliberation)  # Remove incomplete numbered items
        else:
            # Fallback: extract everything before JSON OUTPUT, --- separator, or the final JSON array
            fallback_match = re.search(r'^([\s\S]*?)(?=JSON OUTPUT:|---\s*$|\n\s*\[[\s\S]*\])', response_text)
            if fallback_match:
                deliberation = fallback_match.group(1).strip()
                # Clean up incomplete numbered content
                deliberation = re.sub(r'\n\s*\d+\.\s*\*\*[^*]*$', '', deliberation)

        # Count figurative language patterns for debugging
        excluding_count = len(re.findall(r'therefore.*?excluding.*?figurative', response_text.lower()))
        including_count = len(re.findall(r'therefore.*?including.*?(?:figurative|metaphor|idiom|simile)', response_text.lower()))

        # Use regex to find the JSON block, ignoring conversational text
        json_string = response_text
        match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if match:
            json_string = match.group(1).strip()
        else:
            # Look specifically for JSON OUTPUT: section first
            json_output_match = re.search(r'JSON OUTPUT:\s*([\s\S]*?)(?:\s*$)', response_text, re.IGNORECASE)
            if json_output_match:
                json_section = json_output_match.group(1).strip()
                # Extract the JSON array from this section
                array_match = re.search(r'(\[[\s\S]*?\])', json_section)
                if array_match:
                    json_string = array_match.group(1).strip()
                else:
                    # If no array found in JSON OUTPUT section, it might be empty
                    json_string = "[]"
            else:
                # Look for array after the deliberation section ends (marked by ---)
                # Find the last --- separator and look for JSON after it
                sections = response_text.split('---')
                if len(sections) > 1:
                    # Take the last section after --- separator
                    last_section = sections[-1].strip()
                    array_match = re.search(r'(\[[\s\S]*?\])', last_section)
                    if array_match:
                        json_string = array_match.group(1).strip()
                    else:
                        json_string = "[]"
                else:
                    # Check if response indicates no figurative language found
                    if excluding_count > 0 and including_count == 0:
                        json_string = "[]"
                    else:
                        # Look for standalone JSON array, but be very selective
                        # Find the start of a JSON array and extract it properly
                        start_bracket = response_text.find('[')
                        if start_bracket != -1:
                            # Use proper bracket matching to find the complete JSON
                            bracket_count = 0
                            brace_count = 0
                            in_string = False
                            escape_next = False
                            end_pos = len(response_text)

                            for i in range(start_bracket, len(response_text)):
                                char = response_text[i]

                                if escape_next:
                                    escape_next = False
                                    continue

                                if char == '\\' and in_string:
                                    escape_next = True
                                    continue

                                if char == '"' and not escape_next:
                                    in_string = not in_string
                                    continue

                                if not in_string:
                                    if char == '[':
                                        bracket_count += 1
                                    elif char == ']':
                                        bracket_count -= 1
                                        if bracket_count == 0:
                                            end_pos = i + 1
                                            break
                                    elif char == '{':
                                        brace_count += 1
                                    elif char == '}':
                                        brace_count -= 1

                            candidate_json = response_text[start_bracket:end_pos]

                            # Verify this looks like actual JSON with objects
                            if '{' in candidate_json and '}' in candidate_json:
                                json_string = candidate_json.strip()
                            else:
                                json_string = "[]"
                        else:
                            json_string = "[]"

        # Debug logging for JSON extraction
        if self.logger and json_string != "[]":
            self.logger.debug(f"Extracted JSON length: {len(json_string)} characters")
            if len(json_string) > 500:
                self.logger.debug(f"JSON extract (first 200 chars): {json_string[:200]}...")
                self.logger.debug(f"JSON extract (last 200 chars): ...{json_string[-200:]}")

        # If we still don't have valid JSON and the response contains figurative language analysis,
        # log this for debugging
        if json_string == "[]" and including_count > 0:
            if self.logger:
                self.logger.warning(f"LLM detected figurative language but no JSON found. Including count: {including_count}")
                self.logger.warning(f"Response snippet: {response_text[:500]}...")

        # Try to parse as JSON to validate
        try:
            data = json.loads(json_string)

            # Ensure data is a list
            if not isinstance(data, list):
                return "[]", [], deliberation

            all_instances = []
            validated_data = []

            for item in data:
                # Store original detection types for logging
                original_types = []
                for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    if item.get(fig_type) == 'yes':
                        original_types.append(fig_type)

                # Ensure all type fields are properly set to yes/no
                for fig_type in ['figurative_language', 'simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    if fig_type not in item or item[fig_type] not in ['yes', 'no']:
                        item[fig_type] = 'no'

                # Set figurative_language to 'yes' if any specific type is 'yes'
                if any(item.get(fig_type) == 'yes' for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']):
                    item['figurative_language'] = 'yes'

                # Set the original detection types
                item['original_detection_types'] = ','.join(original_types) if original_types else ''
                all_instances.append(item.copy())

                # Skip validation in this method - it will be done in insert_and_validate_instances
                validated_data.append(item)

            # Return the cleaned and sanitized data as a JSON string, plus all instances and deliberation
            return json.dumps(validated_data), all_instances, deliberation
        except json.JSONDecodeError as e:
            # If not valid JSON, try to repair it if it's just truncated
            if self.logger:
                self.logger.error(f"JSON decode error at position {e.pos}: {e.msg}")
                self.logger.error(f"JSON string length: {len(json_string)}")
                # Show context around the error position
                error_start = max(0, e.pos - 50)
                error_end = min(len(json_string), e.pos + 50)
                self.logger.error(f"JSON context around error: ...{json_string[error_start:error_end]}...")
                self.logger.error(f"Extracted JSON string (first 800 chars): {json_string[:800]}...")
                if len(json_string) > 800:
                    self.logger.error(f"Extracted JSON string (last 300 chars): ...{json_string[-300:]}")

            # Try to repair truncated JSON
            if "Unterminated string" in e.msg and json_string.startswith('['):
                if self.logger:
                    self.logger.info("Attempting to repair truncated JSON...")

                # Find the last complete object
                repaired_json = self._repair_truncated_json(json_string)
                if repaired_json:
                    try:
                        data = json.loads(repaired_json)
                        if isinstance(data, list):
                            if self.logger:
                                self.logger.info(f"Successfully repaired JSON, recovered {len(data)} items")

                            all_instances = []
                            validated_data = []

                            for item in data:
                                # Store original detection types for logging
                                original_types = []
                                for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                                    if item.get(fig_type) == 'yes':
                                        original_types.append(fig_type)

                                # Ensure all type fields are properly set to yes/no
                                for fig_type in ['figurative_language', 'simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                                    if fig_type not in item or item[fig_type] not in ['yes', 'no']:
                                        item[fig_type] = 'no'

                                # Set figurative_language to 'yes' if any specific type is 'yes'
                                if any(item.get(fig_type) == 'yes' for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']):
                                    item['figurative_language'] = 'yes'

                                # Set the original detection types
                                item['original_detection_types'] = ','.join(original_types) if original_types else ''
                                all_instances.append(item.copy())

                                # Skip validation in this method - it will be done in insert_and_validate_instances
                                validated_data.append(item)

                            return json.dumps(validated_data), all_instances, deliberation
                    except json.JSONDecodeError:
                        pass  # Fall through to return empty array

            return "[]", [], deliberation

    def _repair_truncated_json(self, json_string: str) -> Optional[str]:
        """Attempt to repair truncated JSON by finding the last complete object and closing the array"""
        try:
            # Find the last complete object by looking for the last complete closing brace
            last_complete_brace = -1
            brace_count = 0
            in_string = False
            escape_next = False

            for i, char in enumerate(json_string):
                if escape_next:
                    escape_next = False
                    continue

                if char == '\\' and in_string:
                    escape_next = True
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue

                if not in_string:
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            last_complete_brace = i

            if last_complete_brace > 0:
                # Extract up to the last complete object and close the array
                repaired = json_string[:last_complete_brace + 1] + '\n]'
                return repaired

            return None
        except Exception:
            return None

    def insert_and_validate_instances(self, verse_id: int, all_instances: List[Dict], hebrew_text: str, english_text: str) -> int:
        """Insert all detected instances into database with validation data"""
        if not self.db_manager:
            return 0

        valid_count = 0
        for item in all_instances:
            # Prepare figurative data with multi-type format
            figurative_data = {
                'figurative_language': item.get('figurative_language', 'no'),
                'simile': item.get('simile', 'no'),
                'metaphor': item.get('metaphor', 'no'),
                'personification': item.get('personification', 'no'),
                'idiom': item.get('idiom', 'no'),
                'hyperbole': item.get('hyperbole', 'no'),
                'metonymy': item.get('metonymy', 'no'),
                'other': item.get('other', 'no'),
                'vehicle_level_1': item.get('vehicle_level_1'),
                'vehicle_level_2': item.get('vehicle_level_2'),
                'tenor_level_1': item.get('tenor_level_1'),
                'tenor_level_2': item.get('tenor_level_2'),
                'confidence': item.get('confidence'),
                'figurative_text': item.get('english_text'),
                'figurative_text_in_hebrew': item.get('hebrew_text'),
                'explanation': item.get('explanation'),
                'speaker': item.get('speaker'),
                'purpose': item.get('purpose'),
                'original_detection_types': item.get('original_detection_types', '')
            }

            # Insert the figurative language record
            figurative_language_id = self.db_manager.insert_figurative_language(verse_id, figurative_data)

            # Perform validation for each detected type
            if self.validator:
                any_valid = False
                validation_data = {}

                # Initialize final fields to 'no'
                for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    validation_data[f'final_{fig_type}'] = 'no'

                for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    if item.get(fig_type) == 'yes':
                        is_valid, reason, error, reclassified_type = self.validator.validate_figurative_type(
                            fig_type,
                            hebrew_text,
                            english_text,
                            item.get('english_text'),
                            item.get('explanation'),
                            item.get('confidence')
                        )

                        if reclassified_type:
                            # This was reclassified to a different type
                            validation_data[f'validation_decision_{fig_type}'] = 'RECLASSIFIED'
                            validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"
                            # Don't set final field for original type
                            # Set final field for reclassified type
                            validation_data[f'final_{reclassified_type}'] = 'yes'
                            any_valid = True
                        elif is_valid:
                            # Validation confirmed the original type
                            validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                            validation_data[f'validation_reason_{fig_type}'] = reason
                            validation_data[f'final_{fig_type}'] = 'yes'
                            any_valid = True
                        else:
                            # Validation rejected the type
                            validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                            validation_data[f'validation_reason_{fig_type}'] = reason

                        if error:
                            validation_data['validation_error'] = error

                # Set final_figurative_language based on validation results
                validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'

                if any_valid:
                    valid_count += 1

                # Update validation data with final fields
                self.db_manager.update_validation_data(figurative_language_id, validation_data)

        return valid_count

    def get_usage_info(self) -> Dict:
        """Get comprehensive usage statistics"""
        return {
            'total_requests': self.request_count,
            'primary_success': self.primary_success_count,
            'fallback_used': self.fallback_count,
            'primary_success_rate': self.primary_success_count / max(1, self.request_count),
            'fallback_rate': self.fallback_count / max(1, self.request_count),
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens,
            'primary_model': self.primary_model_name,
            'fallback_model': self.fallback_model_name,
            'restriction_reasons': self.restriction_reasons
        }

    def test_api_connection(self) -> Dict:
        """Test both models"""
        results = {}

        # Test primary model
        try:
            response = self.primary_model.generate_content("Test message", generation_config=self.primary_config)
            results['primary'] = {'working': response.text is not None, 'model': self.primary_model_name}
        except Exception as e:
            results['primary'] = {'working': False, 'error': str(e), 'model': self.primary_model_name}

        # Test fallback model
        try:
            response = self.fallback_model.generate_content("Test message", generation_config=self.fallback_config)
            results['fallback'] = {'working': response.text is not None, 'model': self.fallback_model_name}
        except Exception as e:
            results['fallback'] = {'working': False, 'error': str(e), 'model': self.fallback_model_name}

        return results


if __name__ == "__main__":
    # Test the multi-model system
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running.")

    client = MultiModelGeminiClient(api_key)

    print("=== TESTING MULTI-MODEL GEMINI API ===")

    # Test API connections
    connections = client.test_api_connection()
    print(f"API Connection Tests: {connections}")

    # Test Genesis 49 verse (should detect figurative language)
    print("\n--- Genesis 49:9 Test (should detect metaphor) ---")
    hebrew = "גּוּר אַרְיֵה יְהוּדָה מִטֶּרֶף בְּנִי עָלִיתָ כָּרַע רָבַץ כְּאַרְיֵה וּכְלָבִיא מִי יְקִימֶנּוּ"
    english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness—who dare rouse him?"

    result, error, metadata = client.analyze_figurative_language(hebrew, english, "Genesis", 49)
    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    if error:
        print(f"Error: {error}")

    # Test Genesis 1:2 (should be conservative)
    print("\n--- Genesis 1:2 Test (should be literal) ---")
    hebrew = "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם"
    english = "Now the earth was unformed and void, and darkness was over the surface of the deep"

    result, error, metadata = client.analyze_figurative_language(hebrew, english, "Genesis", 1)
    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    if error:
        print(f"Error: {error}")

    print(f"\n--- Usage Statistics ---")
    print(client.get_usage_info())
