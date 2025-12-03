#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Sonnet 4 Client for Hebrew Figurative Language Analysis
Serves as a high-quality fallback when Gemini models fail
"""
import anthropic
import os
import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable


class ClaudeSonnetClient:
    """Claude Sonnet 4 client for figurative language analysis"""

    def __init__(self, api_key: str = None, logger: logging.Logger = None, prompt_generator: Callable = None):
        """Initialize Claude Sonnet client

        Args:
            api_key: Anthropic API key
            logger: Logger instance
            prompt_generator: Function to generate prompts (should be the Gemini client's _create_flexible_tagging_prompt method)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logger or logging.getLogger(__name__)
        self.model_name = "claude-sonnet-4-20250514"
        self.prompt_generator = prompt_generator  # Function to generate prompts from Gemini client

        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0
        }

    def analyze_figurative_language_flexible(
        self,
        hebrew_text: str,
        english_text: str,
        book: str = "Unknown",
        chapter: int = 0,
        max_tokens: int = 8000
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """
        Analyze text for figurative language using Claude Sonnet 4
        Returns: (result_text, error, metadata)
        """

        # Use the shared prompt generator if available, otherwise fall back to local method
        if self.prompt_generator:
            prompt = self.prompt_generator(hebrew_text, english_text, self._determine_text_context(book, chapter))
        else:
            prompt = self._create_flexible_analysis_prompt(hebrew_text, english_text, book, chapter)

        try:
            self.usage_stats["total_requests"] += 1

            self.logger.info("Making request to Claude Sonnet 4 for figurative language analysis")

            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Update usage statistics
            if hasattr(message, 'usage'):
                self.usage_stats["total_input_tokens"] += message.usage.input_tokens
                self.usage_stats["total_output_tokens"] += message.usage.output_tokens
                self.usage_stats["total_tokens"] += message.usage.input_tokens + message.usage.output_tokens

            self.usage_stats["successful_requests"] += 1

            # Extract JSON and metadata from response using Gemini's parsing logic
            instances, deliberation, tagging_analysis = self._parse_flexible_response(response_text)

            metadata = {
                "flexible_instances": instances,
                "figurative_detection_deliberation": deliberation,
                "tagging_analysis_deliberation": tagging_analysis,
                "model_used": self.model_name,
                "truncation_detected": False,  # Claude Sonnet 4 with 8000 tokens should handle most cases
                "instances_count": len(instances)
            }

            self.logger.info(f"Claude Sonnet 4 analysis completed successfully: {len(instances)} instances found")

            return response_text, None, metadata

        except anthropic.APIError as e:
            self.usage_stats["failed_requests"] += 1
            error_msg = f"Claude Sonnet API error: {str(e)}"
            self.logger.error(error_msg)

            # Return empty result with error
            metadata = {
                "flexible_instances": [],
                "figurative_detection_deliberation": "",
                "tagging_analysis_deliberation": "",
                "model_used": self.model_name,
                "truncation_detected": False,
                "instances_count": 0
            }

            return "", error_msg, metadata

        except Exception as e:
            self.usage_stats["failed_requests"] += 1
            error_msg = f"Unexpected error in Claude Sonnet analysis: {str(e)}"
            self.logger.error(error_msg)

            metadata = {
                "flexible_instances": [],
                "figurative_detection_deliberation": "",
                "tagging_analysis_deliberation": "",
                "model_used": self.model_name,
                "truncation_detected": False,
                "instances_count": 0
            }

            return "", error_msg, metadata

    def _determine_text_context(self, book: str, chapter: int) -> str:
        """Determine text context for context-aware analysis (matching Gemini implementation)"""
        from hebrew_figurative_db.ai_analysis.gemini_api_multi_model import TextContext

        # Same logic as in the Gemini client
        book_lower = book.lower()

        # Creation narratives
        if book_lower == "genesis" and chapter == 1:
            return TextContext.CREATION_NARRATIVE.value

        # Poetic blessings
        if (book_lower == "genesis" and chapter in [9, 27, 49]) or \
           (book_lower == "deuteronomy" and chapter == 33):
            return TextContext.POETIC_BLESSING.value

        # Legal/ceremonial texts
        if book_lower in ["leviticus", "numbers"] or \
           (book_lower == "deuteronomy" and chapter in range(12, 27)) or \
           (book_lower == "exodus" and chapter in range(20, 32)):
            return TextContext.LEGAL_CEREMONIAL.value

        # Default to narrative
        return TextContext.NARRATIVE.value

    def _create_flexible_analysis_prompt(self, hebrew_text: str, english_text: str, book: str, chapter: int) -> str:
        """Create the analysis prompt for Claude Sonnet 4"""

        return f"""You are an expert in biblical Hebrew linguistics and figurative language analysis. I need you to analyze a verse from {book} {chapter} for figurative language using a CONSERVATIVE approach.

**Hebrew Text:** {hebrew_text}
**English Translation:** {english_text}

**TASK:** Identify ALL instances of figurative language in this verse using these guidelines:

**CONSERVATIVE DETECTION GUIDELINES:**
1. **MARK** physical verbs/concepts applied to spiritual/abstract concepts
2. **MARK** clear metaphors, similes, personification, idioms, hyperbole, metonymy
3. **BE CONSERVATIVE** with divine anthropomorphisms (only mark if clearly figurative beyond standard narrative language)
4. **EXCLUDE** proper names, standard titles, conventional expressions unless clearly figurative
5. **FOCUS** on Hebrew text primarily, use English for clarification

**OUTPUT FORMAT:**
First provide your **DETECTION DELIBERATION** - explain what you considered and why you included/excluded each potential figurative element.

Then provide **HIERARCHICAL TAGGING ANALYSIS** for any instances you found.

Finally, provide a **JSON array** with this structure for each instance:
```json
[
  {{
    "instance_id": 1,
    "figurative_language": "yes",
    "simile": "yes/no",
    "metaphor": "yes/no",
    "personification": "yes/no",
    "idiom": "yes/no",
    "hyperbole": "yes/no",
    "metonymy": "yes/no",
    "other": "yes/no",
    "confidence": 0.8,
    "english_text": "the relevant English phrase",
    "hebrew_text": "the relevant Hebrew phrase",
    "explanation": "detailed explanation of the figurative language",
    "speaker": "who is speaking",
    "purpose": "why this figurative language is used",
    "target": ["specific target", "target category", "general domain"],
    "vehicle": ["specific vehicle", "vehicle category", "general domain"],
    "ground": ["specific quality", "quality category", "general domain"],
    "posture": ["specific attitude", "attitude category", "general domain"]
  }}
]
```

**If NO figurative language is found, return an empty array: []**

Begin your analysis:"""

    def _parse_flexible_response(self, response_text: str) -> Tuple[List[Dict], str, str]:
        """Parse flexible tagging response format using Gemini's parsing logic"""
        should_trigger_fallback = False

        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(f"🔍 PARSING DEBUG - Starting response parsing:")
            self.logger.debug(f"  📏 Total response length: {len(response_text)}")
            self.logger.debug(f"  📄 Response preview (first 200 chars): '{response_text[:200]}'")
            self.logger.debug(f"  📄 Response ending (last 200 chars): '{response_text[-200:] if len(response_text) > 200 else response_text}'")

        # Extract figurative detection deliberation (improved pattern matching)
        figurative_detection = ""
        detection_match = re.search(r'FIGURATIVE_DETECTION\s*:?\s*(.*?)(?=TAGGING_ANALYSIS|STRUCTURED JSON OUTPUT|JSON OUTPUT|\[|$)',
                                   response_text, re.IGNORECASE | re.DOTALL)
        if detection_match:
            figurative_detection = detection_match.group(1).strip()
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(f"  📝 FIGURATIVE_DETECTION extracted: {len(figurative_detection)} chars")
        else:
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(f"  ⚠️ No FIGURATIVE_DETECTION section found")

        # Extract tagging analysis deliberation (improved pattern matching)
        tagging_analysis = ""
        tagging_match = re.search(r'TAGGING_ANALYSIS\s*:?\s*(.*?)(?=STRUCTURED JSON OUTPUT|JSON OUTPUT|\[|$)',
                                 response_text, re.IGNORECASE | re.DOTALL)
        if tagging_match:
            tagging_analysis = tagging_match.group(1).strip()
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(f"  📝 TAGGING_ANALYSIS extracted: {len(tagging_analysis)} chars")
        else:
            if self.logger and self.logger.level <= logging.DEBUG:
                self.logger.debug(f"  ⚠️ No TAGGING_ANALYSIS section found")

        # Extract JSON using Gemini's parsing logic
        instances = []
        json_string = ""
        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(f"🔍 JSON EXTRACTION DEBUG:")

        try:
            json_string = self._extract_json_array(response_text)

            if self.logger and self.logger.level <= logging.DEBUG:
                if json_string:
                    self.logger.debug(f"  📄 JSON string extracted: {len(json_string)} chars")
                    self.logger.debug(f"  📄 JSON preview: '{json_string[:200] if len(json_string) > 200 else json_string}'")

            if json_string and json_string != "[]":
                try:
                    instances = json.loads(json_string)
                    if self.logger:
                        self.logger.info(f"  ✅ JSON parsing succeeded")
                except json.JSONDecodeError as parse_error:
                    if self.logger:
                        self.logger.error(f"  ❌ JSON parsing failed: {parse_error}")
                    # Try to fix common JSON issues
                    fixed_json = self._fix_json_format(json_string)
                    if fixed_json:
                        try:
                            instances = json.loads(fixed_json)
                            if self.logger:
                                self.logger.info("  ✅ JSON parsing succeeded after format repair")
                        except json.JSONDecodeError:
                            instances = []
                    else:
                        instances = []
            else:
                instances = []

        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error parsing flexible response: {e}")
            instances = []

        return instances, figurative_detection, tagging_analysis

    def _extract_json_array(self, response_text: str) -> str:
        """Extract JSON array using robust logic adapted from Gemini system"""

        if self.logger:
            self.logger.info(f"    🔍 JSON Array Extraction:")

        # First try to find complete JSON array with proper bracket matching
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
            if self.logger:
                self.logger.info(f"      📄 Found JSON-like array: {len(json_str)} chars")
            # Validate this looks like proper JSON with objects
            if '{' in json_str and '}' in json_str:
                if self.logger:
                    self.logger.info(f"      ✅ Array contains objects - using this match")
                return json_str

        # Use sophisticated bracket matching for standalone arrays
        start_bracket = response_text.find('[')
        if start_bracket != -1:
            bracket_count = 0
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

            candidate_json = response_text[start_bracket:end_pos]

            # Verify this contains objects
            if '{' in candidate_json and '}' in candidate_json:
                if self.logger:
                    self.logger.info(f"      ✅ Bracket-matched array contains objects")
                return candidate_json.strip()

        # Check if empty array is indicated
        if '[]' in response_text or 'no figurative language found' in response_text.lower():
            if self.logger:
                self.logger.info(f"      📄 Empty array pattern detected")
            return "[]"

        if self.logger:
            self.logger.warning(f"      ❌ No valid JSON array found - returning empty")
        return "[]"

    def _fix_json_format(self, json_str: str) -> str:
        """Attempt to fix common JSON formatting issues"""
        try:
            # Remove any trailing commas before closing brackets/braces
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)

            # Fix missing quotes around field names
            json_str = re.sub(r'(\w+):', r'"\1":', json_str)

            # Try to parse again
            json.loads(json_str)
            return json_str
        except:
            return None

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0
        }


def test_claude_sonnet_client():
    """Test function for Claude Sonnet client"""
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    client = ClaudeSonnetClient(logger=logger)

    # Test with Genesis 14:20 (one of the problematic verses)
    hebrew_text = "וברוך אל עליון אשר־מגן צריך בידך ויתן־לו מעשר מכל"
    english_text = "And blessed be God Most High, Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."

    result, error, metadata = client.analyze_figurative_language_flexible(
        hebrew_text, english_text, "Genesis", 14
    )

    print(f"Error: {error}")
    print(f"Instances found: {len(metadata['flexible_instances'])}")
    print(f"Deliberation: {metadata['figurative_detection_deliberation'][:200]}...")
    print(f"Usage stats: {client.get_usage_stats()}")


if __name__ == "__main__":
    test_claude_sonnet_client()