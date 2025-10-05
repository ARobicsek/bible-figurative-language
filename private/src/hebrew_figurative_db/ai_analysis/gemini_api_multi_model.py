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

# Import for Hebrew text processing
try:
    from ..text_extraction.hebrew_utils import HebrewTextProcessor
except ImportError:
    # Fallback for when running as main
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from text_extraction.hebrew_utils import HebrewTextProcessor


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
FALLBACK_MODEL = 'gemini-2.5-pro'


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

        # Generation configs (increased token limits for detailed flexible tagging deliberations)
        self.primary_config = {
            'temperature': 0.15,  # Slightly higher for better detection
            'top_p': 0.8,
            'top_k': 25,
            'max_output_tokens': 15000,  # Increased to prevent truncation of detailed deliberations
        }

        self.fallback_config = {
            'temperature': 0.10,  # Conservative for fallback
            'top_p': 0.7,
            'top_k': 20,
            'max_output_tokens': 15000,  # Increased to prevent truncation of detailed deliberations
        }

        # Usage tracking
        self.request_count = 0
        self.primary_success_count = 0
        self.fallback_count = 0
        self.server_error_fallback_count = 0  # Track 500 error fallbacks
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

        if error and (self._is_restriction_error(error) or self._is_server_error(error) or self._is_truncation_error(error)):
            # Determine fallback reason
            if self._is_restriction_error(error):
                fallback_reason = "content restriction"
            elif self._is_truncation_error(error):
                fallback_reason = "deliberation truncation"
            else:
                fallback_reason = "server error"

            # Fallback to secondary model for content restrictions, truncation, or persistent server errors
            if self.logger:
                self.logger.info(f"Primary model failed ({fallback_reason}: {error}), trying fallback...")

            if self._is_restriction_error(error):
                self.restriction_reasons.append(f"{self.primary_model_name}: {error}")
                self.fallback_count += 1
            elif self._is_truncation_error(error):
                self.fallback_count += 1
            else:
                self.server_error_fallback_count += 1

            result, error, fallback_metadata = self._try_model_analysis(
                self.fallback_model, self.fallback_config, self.fallback_model_name,
                hebrew_text, english_text, text_context
            )

            # Update metadata
            metadata.update(fallback_metadata)
            metadata['fallback_used'] = True
            metadata['fallback_reason'] = fallback_reason
            if self._is_restriction_error(error):
                metadata['primary_restriction'] = self.restriction_reasons[-1]
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
        start_time = time.time()  # Track total elapsed time

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

                    cleaned_response, all_instances, deliberation, truncation_info = self._clean_response(response_text.strip(), hebrew_text, english_text)
                    metadata['all_detected_instances'] = all_instances
                    metadata['truncation_info'] = truncation_info

                    # Check for deliberation truncation
                    if self._is_deliberation_truncated(deliberation, len(all_instances)):
                        error_msg = f"Deliberation truncation detected (length: {len(deliberation)}, instances: {len(all_instances)})"
                        if self.logger:
                            self.logger.warning(f"{model_name}: {error_msg}")
                            self.logger.warning(f"Deliberation content: {deliberation[:200]}")
                        # Return error to trigger fallback
                        return "[]", error_msg, metadata

                    return cleaned_response, None, metadata
                else:
                    return "[]", "No response text generated", metadata

            except Exception as e:
                error_msg = f"{model_name} error: {str(e)}"
                elapsed_time = time.time() - start_time

                # Check if we should retry (different logic for 429 vs 500 errors)
                should_retry = attempt < max_retries - 1

                if "429" in error_msg and should_retry:
                    # Rate limit error - use recommended delay or exponential backoff
                    retry_after_match = re.search(r'retry_delay {\s*seconds: (\d+)\s*}', error_msg)
                    if retry_after_match:
                        wait_time = int(retry_after_match.group(1))
                    else:
                        wait_time = (backoff_factor ** attempt) * 5

                    wait_time += (hash(time.time()) % 1000 / 1000)  # Add jitter
                    if self.logger:
                        self.logger.info(f"Rate limit hit. Retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    metadata['retries'] = attempt + 1
                    continue

                elif "500" in error_msg and should_retry:
                    # Server error - exponential backoff with 30-second timeout check
                    if elapsed_time >= 30:
                        # After 30 seconds of 500 errors, give up and let caller try fallback model
                        if self.logger:
                            self.logger.warning(f"Server errors for {elapsed_time:.1f} seconds, giving up on {model_name}")
                        return "[]", f"Server error timeout after {elapsed_time:.1f}s: {error_msg}", metadata

                    wait_time = min((backoff_factor ** attempt) * 2, 10)  # Cap at 10 seconds per retry
                    wait_time += (hash(time.time()) % 1000 / 1000)  # Add jitter
                    if self.logger:
                        self.logger.info(f"Server error, retrying in {wait_time:.2f} seconds... (Attempt {attempt + 1}/{max_retries}, elapsed: {elapsed_time:.1f}s)")
                    time.sleep(wait_time)
                    metadata['retries'] = attempt + 1
                    continue

                # Non-retryable error or max retries reached
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
[You MUST briefly analyze EVERY potential figurative element in this verse. For each phrase/concept, explain *briefly*:
- What you considered (e.g., "considered if 'X' might be metaphor, metonymy, etc"). Note that synechdoche is a type of metonymy.
- Your reasoning for including/excluding it (e.g., "this is not metaphor, metonymy, etc because...")
- Any borderline cases you debated
- Your thinking about the TARGET of the figurative speech (this is the core subject of the figurative language. It's the literal person, object, action or concept being described), the VEHICLE (This is the image or idea used to convey something about the target. It's the "what it's like" part of the comparison) and the GROUND (This is the underlying characteristic of the target that the figurative language is intended to describe. The vehicle tells you that target is [ground]).
Be explicit about what you examined and why you made each decision.
IMPORTANT: Include ALL phrases you marked as figurative in the JSON AND explain your reasoning for including them here.]

**THEN provide JSON OUTPUT (only if genuinely figurative):**

**TARGET/VEHICLE/GROUND CLASSIFICATION GUIDE:**
- **TARGET** = WHO/WHAT the figurative speech is ABOUT (the subject being described, e.g. "follow these laws with all your heart and soul" --> target_level_1="Social Group", target_specific="The Israelites")
- **VEHICLE** = WHAT the target is being LIKENED TO (the comparison/image used, e.g. "do not deviate right or left" --> vehicle_level_1 = "spatial", vehicle_specific = "directions")
- **GROUND** = WHAT QUALITY of the target is being described (the quality of the target that the vehicle sheds light on, e.g. "I carried you on eagle's wings" --> ground_level_1 = "physical quality", ground_specific = "with comfort and safety")

Example: "Judah is a lion" → TARGET (i.e. who the metaphor is about): target_level_1 = Specific person, target_specific = Judah; VEHICLE (i.e. what Judah is likened to): vehicle_level_1=natural world, vehicle_specific =lion; GROUND (i.e. this figurative speech tells us that the target has [x] quality): ground_level_1=physical quality, ground_specific=strength

[{"figurative_language": "yes/no", "simile": "yes/no", "metaphor": "yes/no", "personification": "yes/no", "idiom": "yes/no", "hyperbole": "yes/no", "metonymy": "yes/no", "other": "yes/no", "hebrew_text": "Hebrew phrase", "english_text": "English phrase", "explanation": "Brief explanation", "target_level_1": "God/social group/action/geographical or political entity/natural world/created objects/specific person/time/state of being/legal, religious or moral concept/other", "target_specific": "specific target", "vehicle_level_1": "natural world/human parts/human action/relationships/spatial/the ancient workplace/warfare/wordplay/abstract/other", "vehicle_specific": "specific vehicle", "ground_level_1": "moral quality/physical quality/psychological quality/status/essential nature or identity/other", "ground_specific": "specific ground", "confidence": 0.7-1.0, "speaker": "Narrator/name of character", "purpose": "brief purpose"}]
You **must** use **one of categories specified above** for target_level_1, vehicle_level_1, and ground_level_1.

IMPORTANT: Mark each type field as "yes" or "no". A phrase can be multiple types (e.g., both metaphor and idiom). Set figurative_language to "yes" if ANY figurative language is detected.

If no figurative language found: []

Analysis:"""

    def _is_restriction_error(self, error_msg: str) -> bool:
        """Check if error indicates content restriction requiring fallback"""
        if not error_msg:
            return False
        restriction_indicators = [
            'Content restricted',
            'SAFETY',
            'RECITATION',
            'OTHER',
            'blocked',
            'filtered'
        ]
        return any(indicator.lower() in error_msg.lower() for indicator in restriction_indicators)

    def _is_truncation_error(self, error_msg: str) -> bool:
        """Check if error message indicates deliberation truncation"""
        if not error_msg:
            return False
        return "Deliberation truncation detected" in error_msg

    def _is_server_error(self, error_msg: str) -> bool:
        """Check if error indicates persistent server issues requiring fallback"""
        if not error_msg:
            return False
        server_error_indicators = [
            'Server error timeout after',
            '500 An internal error',
            'Failed after .* retries due to persistent API errors'
        ]
        return any(re.search(indicator, error_msg) for indicator in server_error_indicators)

    def _is_restriction_reason(self, finish_reason) -> bool:
        """Check if finish reason indicates content restriction"""
        restriction_reasons = {reason.value for reason in FinishReason}

        if hasattr(finish_reason, 'name'):
            return finish_reason.name in restriction_reasons
        else:
            return str(finish_reason).upper() in restriction_reasons

    def _is_deliberation_truncated(self, deliberation: str, instances_found: int) -> bool:
        """
        Check if deliberation appears to be truncated.

        A deliberation is considered truncated if:
        1. It's very short (< 100 chars) AND no instances were found
        2. It ends mid-sentence or mid-word
        3. It's empty but we expected analysis
        4. It ends with incomplete instructions like "THEN provide" or "JSON OUTPUT:"

        Args:
            deliberation: The extracted deliberation text
            instances_found: Number of figurative language instances found

        Returns:
            True if deliberation appears truncated
        """
        # Empty deliberation is suspicious if no instances found
        if not deliberation:
            return True

        # Check for mid-instruction truncation (applies regardless of length)
        # These patterns indicate the LLM was cut off while giving instructions
        mid_instruction_patterns = [
            r'THEN provide\s*$',  # Ends with "THEN provide"
            r'(?:now|then|finally)\s+(?:provide|output|return)\s*$',  # Ends with instruction start
            r'JSON OUTPUT:\s*$',  # Ends with JSON OUTPUT: but no JSON
            r'(?:provide|output|return)\s+(?:the|a|an)\s+\w*$',  # Ends mid-instruction
        ]

        if any(re.search(pattern, deliberation, re.IGNORECASE) for pattern in mid_instruction_patterns):
            return True

        # Very short deliberation with no instances is likely truncated
        if len(deliberation) < 100 and instances_found == 0:
            # Check if it ends mid-sentence or mid-word
            # Common truncation patterns:
            # - Ends with incomplete markdown: **"
            # - Ends mid-word without punctuation
            # - Ends with just a number and formatting: "1.  **"
            truncation_patterns = [
                r'\*\*["\']?\s*$',  # Ends with ** or **" or **'
                r'\d+\.\s+\*\*\s*$',  # Ends with number and **
                r'[a-zA-Z]\s*$',  # Ends mid-word
                r'^\s*$',  # Empty or whitespace only
            ]

            if any(re.search(pattern, deliberation) for pattern in truncation_patterns):
                return True

            # Also check if deliberation is suspiciously short without proper conclusion
            # A complete "no figurative language" analysis should be at least a few sentences
            if len(deliberation) < 150 and instances_found == 0:
                # Check if it lacks typical completion markers
                has_completion = any(marker in deliberation.lower() for marker in [
                    'therefore', 'thus', 'in conclusion', 'no figurative',
                    'excluding', 'literal', 'none found'
                ])
                if not has_completion:
                    return True

        return False

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

        # Initialize truncation tracking
        truncation_info = {
            'instances_detected': 0,
            'instances_recovered': 0,
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'no'
        }

        # Try to parse as JSON to validate
        try:
            data = json.loads(json_string)

            # Ensure data is a list
            if not isinstance(data, list):
                return "[]", [], deliberation

            all_instances = []
            validated_data = []

            # Update truncation info for successful parsing
            truncation_info['instances_detected'] = len(data)
            truncation_info['instances_recovered'] = len(data)
            truncation_info['instances_lost_to_truncation'] = 0
            truncation_info['truncation_occurred'] = 'no'

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

            # Return the cleaned and sanitized data as a JSON string, plus all instances, deliberation, and truncation info
            return json.dumps(validated_data), all_instances, deliberation, truncation_info
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

                # Find complete objects and try to repair incomplete ones
                repaired_json = self._repair_truncated_json(json_string)
                if repaired_json:
                    try:
                        data = json.loads(repaired_json)
                        if isinstance(data, list):
                            if self.logger:
                                # Check original truncated JSON for potential lost data
                                truncated_object_count = json_string.count('"figurative_language":')
                                recovered_count = len(data)

                                # Update truncation info
                                truncation_info['instances_detected'] = truncated_object_count
                                truncation_info['instances_recovered'] = recovered_count
                                truncation_info['instances_lost_to_truncation'] = max(0, truncated_object_count - recovered_count)
                                truncation_info['truncation_occurred'] = 'yes'

                                if truncated_object_count > recovered_count:
                                    self.logger.warning(f"JSON repair: recovered {recovered_count} of {truncated_object_count} detected instances - {truncated_object_count - recovered_count} instances lost to truncation")
                                else:
                                    self.logger.info(f"Successfully repaired JSON, recovered {recovered_count} items")

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

                            return json.dumps(validated_data), all_instances, deliberation, truncation_info
                    except json.JSONDecodeError:
                        pass  # Fall through to return empty array

            return "[]", [], deliberation, truncation_info

    def _repair_truncated_json(self, json_string: str) -> Optional[str]:
        """Attempt to repair truncated JSON by finding complete objects and reconstructing partial ones"""
        try:
            # First, try to find all complete objects
            complete_objects = []
            current_object = ""
            brace_count = 0
            in_string = False
            escape_next = False
            in_object = False

            for i, char in enumerate(json_string):
                if escape_next:
                    escape_next = False
                    current_object += char
                    continue

                if char == '\\' and in_string:
                    escape_next = True
                    current_object += char
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    current_object += char
                    continue

                current_object += char

                if not in_string:
                    if char == '{':
                        brace_count += 1
                        if not in_object:
                            in_object = True
                            current_object = '{'
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0 and in_object:
                            # Found a complete object
                            complete_objects.append(current_object)
                            current_object = ""
                            in_object = False

            # If we have complete objects, great!
            if complete_objects:
                repaired = '[\n' + ',\n'.join(complete_objects) + '\n]'
                return repaired

            # If no complete objects, try to find the last incomplete object and see if we can salvage it
            if in_object and current_object and brace_count == 1:
                # We have one incomplete object - try to close it gracefully
                # Look for the last complete field
                lines = current_object.split('\n')
                salvageable_lines = []

                for line in lines:
                    line = line.strip()
                    if not line or line == '{':
                        salvageable_lines.append(line)
                        continue

                    # Check if this line looks like a complete field
                    if (line.endswith(',') or line.endswith('"') or
                        line.endswith('}') or line.endswith('0') or
                        line.endswith('1') or line.endswith('true') or
                        line.endswith('false')):
                        salvageable_lines.append(line)
                    else:
                        # This line is incomplete, stop here
                        break

                if len(salvageable_lines) > 1:  # More than just the opening brace
                    # Remove trailing comma if present
                    if salvageable_lines[-1].endswith(','):
                        salvageable_lines[-1] = salvageable_lines[-1][:-1]

                    salvaged_object = '\n'.join(salvageable_lines) + '\n}'
                    repaired = '[\n' + salvaged_object + '\n]'
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
            # Strip diacritics from Hebrew figurative text if it exists
            hebrew_figurative_stripped = None
            if item.get('hebrew_text'):
                hebrew_figurative_stripped = HebrewTextProcessor.strip_diacritics(item.get('hebrew_text'))

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
                'final_figurative_language': 'no',  # Will be set by validation
                'final_simile': 'no',
                'final_metaphor': 'no',
                'final_personification': 'no',
                'final_idiom': 'no',
                'final_hyperbole': 'no',
                'final_metonymy': 'no',
                'final_other': 'no',
                'target_level_1': item.get('target_level_1'),
                'target_specific': item.get('target_specific'),
                'vehicle_level_1': item.get('vehicle_level_1'),
                'vehicle_specific': item.get('vehicle_specific'),
                'ground_level_1': item.get('ground_level_1'),
                'ground_specific': item.get('ground_specific'),
                'confidence': item.get('confidence'),
                'figurative_text': item.get('english_text'),
                'figurative_text_in_hebrew': item.get('hebrew_text'),
                'figurative_text_in_hebrew_stripped': hebrew_figurative_stripped,
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
        total_fallbacks = self.fallback_count + self.server_error_fallback_count
        return {
            'total_requests': self.request_count,
            'primary_success': self.primary_success_count,
            'content_restriction_fallbacks': self.fallback_count,
            'server_error_fallbacks': self.server_error_fallback_count,
            'total_fallbacks': total_fallbacks,
            'primary_success_rate': self.primary_success_count / max(1, self.request_count),
            'content_restriction_rate': self.fallback_count / max(1, self.request_count),
            'server_error_fallback_rate': self.server_error_fallback_count / max(1, self.request_count),
            'total_fallback_rate': total_fallbacks / max(1, self.request_count),
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
