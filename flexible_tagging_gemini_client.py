#!/usr/bin/env python3
"""
Enhanced MultiModelGeminiClient with Flexible Tagging Framework Integration

This extends the existing MultiModelGeminiClient to use our revolutionary
flexible tag-based taxonomy instead of rigid categorical classifications.
"""

import sys
import os
import json
import logging
import re

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient, TextContext

class FlexibleTaggingGeminiClient(MultiModelGeminiClient):
    """Enhanced Gemini client with flexible tagging framework"""

    def __init__(self, api_key: str, validator=None, logger=None, db_manager=None):
        """Initialize with flexible tagging capabilities"""
        super().__init__(api_key, validator, logger, db_manager)
        self.flexible_rules = self._load_flexible_rules()

    def _load_flexible_rules(self):
        """Load the flexible tagging rules"""
        try:
            with open('tag_taxonomy_rules.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            if self.logger:
                self.logger.warning("tag_taxonomy_rules.json not found, using default rules")
            return {}

    def _create_flexible_tagging_prompt(self, hebrew_text: str, english_text: str, context: str) -> str:
        """Create enhanced prompt using proven multi-model instructions adapted for flexible tagging"""

        base_prompt = f"""You are a biblical Hebrew scholar analyzing this text for figurative language.

Hebrew: {hebrew_text}
English: {english_text}

"""

        # Use EXACT proven context rules from multi-model system
        if context == TextContext.CREATION_NARRATIVE.value:
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
            context_rules = """📖 **NARRATIVE TEXT - STANDARD CONSERVATIVE** 📖

**BE CONSERVATIVE WITH:**
• Standard narrative language
• Character actions and dialogue
• Historical and genealogical information
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger).
• Biblical idioms and set phrases (e.g. לְפִי־חָֽרֶב, פִֽי־יְהֹוָ֖ה,פְּנ֥י הָאֲדָמָֽה) - these are IDIOMS; classify figurative idioms as "idiom" type.

**NEVER MARK AS FIGURATIVE:**
• Comparisons of role or function, such as 'a prophet like myself' (כָּמֹנִי) or 'a prophet like yourself' (כָּמוֹךָ). These are literal statements of equivalence or similarity in function, not figurative similes.
• Proportional or behavioral comparisons, such as 'according to the blessing' or 'like all his fellow Levites'.

**MARK AS FIGURATIVE:**
• Clear metaphors with cross-domain comparisons
• Personification of non-human entities
• Obvious similes"""

        flexible_instructions = """
**FIRST, provide your deliberation in a FIGURATIVE_DETECTION section:**

FIGURATIVE_DETECTION:
[You MUST briefly analyze EVERY potential figurative element in this verse. For each phrase/concept, explain briefly:
- What you considered (e.g., "considered if 'X' might be metaphor, metonymy, etc"). Note that synechdoche is a type of metonymy.
- Your reasoning for including/excluding it (e.g., "this is not metaphor, metonymy, etc because...")
- Any borderline cases you debated
Be explicit about what you examined and why you made each decision.
IMPORTANT: Include ALL phrases you marked as figurative in the JSON AND explain your reasoning for including them here.]

**THEN provide your deliberation in a TAGGING_ANALYSIS section:**

TAGGING_ANALYSIS:
[For each figurative instance you identified, explain your thinking about:
- The TARGET of the figurative speech (the core subject being described)
- The VEHICLE (the image or idea used to convey something about the target)
- The GROUND (the underlying characteristic/quality of the target that the figurative language illuminates)
- The SPEAKER POSTURE (the speaker attitude, stance, or emotional orientation)]

**THEN provide STRUCTURED JSON OUTPUT (REQUIRED):**

**CRITICAL JSON REQUIREMENTS:**
1. You MUST output a valid JSON array, even if empty: []
2. Each object MUST have ALL required fields
3. Use hierarchical arrays for target, vehicle, ground, and posture tags
4. Format exactly as shown below

**HIERARCHICAL TAGGING GUIDE:**
- TARGET = WHO/WHAT the figurative speech is ABOUT (generate hierarchical tags from specific to general)
- VEHICLE = WHAT the target is being LIKENED TO (generate hierarchical tags from specific to general)
- GROUND = WHAT QUALITY of the target is being described (generate hierarchical tags from specific to general)
- POSTURE = SPEAKER ATTITUDE/STANCE (generate hierarchical tags from specific to general)
- note - always bear in mind that the purpose of the tags is to allow scholars to search for instances of figurative language; thing of these as search or index terms.

**POSTURE HIERARCHY EXAMPLES:**
- Positive: ["celebration", "praise", "positive sentiment"] or ["blessing", "approval", "positive stance"]
- Negative: ["condemnation", "anger", "negative sentiment"] or ["frustration", "disappointment", "negative stance"]
- Neutral: ["instruction", "teaching", "neutral stance"] or ["description", "explanation", "neutral stance"]

**REQUIRED JSON FORMAT:**
[
{
  "figurative_language": "yes",
  "simile": "no",
  "metaphor": "yes",
  "personification": "no",
  "idiom": "no",
  "hyperbole": "no",
  "metonymy": "no",
  "other": "no",
  "hebrew_text": "Hebrew phrase here",
  "english_text": "English phrase here",
  "explanation": "Brief explanation of the figurative language",
  "target": ["specific target", "target category", "general domain"],
  "vehicle": ["specific vehicle", "vehicle category", "source domain"],
  "ground": ["specific quality", "quality type", "broad aspect"],
  "posture": ["specific attitude", "attitude category", "general orientation"],
  "confidence": 0.9,
  "speaker": "Speaker name or Narrator",
  "purpose": "Purpose of the figurative language"
}
]

**If no figurative language found, output exactly:** []

IMPORTANT: Mark each type field as "yes" or "no". A phrase can be multiple types (e.g., both metaphor and idiom). Set figurative_language to "yes" if ANY figurative language is detected.

Analysis:"""

        return base_prompt + context_rules + flexible_instructions

    def analyze_figurative_language_flexible(self, hebrew_text: str, english_text: str,
                                           book: str = "", chapter: int = 0):
        """
        Analyze using flexible tagging framework

        Returns: Tuple of (response_text, raw_json, parsed_flexible_data)
        """
        # Determine text context
        text_context = self._determine_text_context(book, chapter)

        # Generate flexible tagging prompt
        prompt = self._create_flexible_tagging_prompt(hebrew_text, english_text, text_context)

        # Use existing model infrastructure but with new prompt
        try:
            # Try primary model
            result, error, metadata = self._try_model_analysis_with_custom_prompt(
                self.primary_model, self.primary_config, self.primary_model_name,
                prompt
            )

            if error and (self._is_restriction_error(error) or self._is_server_error(error)):
                # Fallback to secondary model
                if self.logger:
                    self.logger.info(f"Primary model failed, trying fallback...")

                result, error, fallback_metadata = self._try_model_analysis_with_custom_prompt(
                    self.fallback_model, self.fallback_config, self.fallback_model_name,
                    prompt
                )

                metadata.update(fallback_metadata)
                metadata['fallback_used'] = True
            else:
                metadata['fallback_used'] = False
                self.primary_success_count += 1

            return result, error, metadata

        except Exception as e:
            error_msg = str(e)
            if self.logger:
                self.logger.error(f"Flexible analysis failed: {error_msg}")
            return None, error_msg, {'error': True}

    def _try_model_analysis_with_custom_prompt(self, model, config, model_name, prompt):
        """Try analysis with custom flexible tagging prompt"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=config
                )

                self.request_count += 1
                self.total_input_tokens += getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0
                self.total_output_tokens += getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0

                if not response.candidates:
                    return "[]", "No candidates generated", {}

                candidate = response.candidates[0]

                # Check for restriction
                if hasattr(candidate, 'finish_reason'):
                    if self._is_restriction_reason(candidate.finish_reason):
                        return None, f"Content restricted: {candidate.finish_reason}", {}

                # Extract response text safely (using the same pattern as original)
                try:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            response_text = candidate.content.parts[0].text
                        else:
                            response_text = str(candidate.content)
                    else:
                        response_text = "[]"
                except Exception:
                    response_text = "[]"

                # Parse flexible response
                parsed_data = self._parse_flexible_response(response_text)

                # Create metadata matching original format
                metadata = {
                    'model_used': model_name,
                    'retries': attempt,
                    'input_tokens': getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    'output_tokens': getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                }
                metadata.update(parsed_data)

                return response_text, None, metadata

            except Exception as e:
                error_msg = str(e)
                if self.logger:
                    self.logger.warning(f"Attempt {attempt + 1} failed: {error_msg}")

                if attempt == max_retries - 1:
                    return "[]", error_msg, {'retries': max_retries}

        return "[]", "Failed after retries", {'retries': max_retries}

    def _parse_flexible_response(self, response_text: str):
        """Parse flexible tagging response format with dual deliberation and robust JSON extraction"""

        # Extract figurative detection deliberation (improved pattern matching)
        figurative_detection = ""
        detection_match = re.search(r'FIGURATIVE_DETECTION\s*:?\s*(.*?)(?=TAGGING_ANALYSIS|STRUCTURED JSON OUTPUT|JSON OUTPUT|\[|$)',
                                   response_text, re.IGNORECASE | re.DOTALL)
        if detection_match:
            figurative_detection = detection_match.group(1).strip()

        # Extract tagging analysis deliberation (improved pattern matching)
        tagging_analysis = ""
        tagging_match = re.search(r'TAGGING_ANALYSIS\s*:?\s*(.*?)(?=STRUCTURED JSON OUTPUT|JSON OUTPUT|\[|$)',
                                 response_text, re.IGNORECASE | re.DOTALL)
        if tagging_match:
            tagging_analysis = tagging_match.group(1).strip()

        # Combine both deliberations for backward compatibility
        combined_deliberation = ""
        if figurative_detection and tagging_analysis:
            combined_deliberation = f"FIGURATIVE_DETECTION:\n{figurative_detection}\n\nTAGGING_ANALYSIS:\n{tagging_analysis}"
        elif figurative_detection:
            combined_deliberation = f"FIGURATIVE_DETECTION:\n{figurative_detection}"
        elif tagging_analysis:
            combined_deliberation = f"TAGGING_ANALYSIS:\n{tagging_analysis}"

        # Extract JSON using improved parsing logic from multi-model system
        instances = []
        try:
            # Use more sophisticated JSON extraction
            json_string = self._extract_json_array(response_text)

            if json_string and json_string != "[]":
                instances = json.loads(json_string)

                # Validate that instances are properly formatted dictionaries
                if isinstance(instances, list):
                    valid_instances = []
                    for instance in instances:
                        if isinstance(instance, dict):
                            # Ensure all required fields exist
                            self._validate_instance_format(instance)
                            valid_instances.append(instance)
                        elif isinstance(instance, str):
                            if self.logger:
                                self.logger.warning(f"Skipping string instance: {instance[:100]}...")
                    instances = valid_instances
                else:
                    instances = []
            else:
                instances = []

        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"JSON parsing failed: {e}")
                self.logger.error(f"Response text (first 500 chars): {response_text[:500]}")
            instances = []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error parsing flexible response: {e}")
            instances = []

        return {
            'flexible_instances': instances,
            'figurative_detection_deliberation': figurative_detection,
            'tagging_analysis_deliberation': tagging_analysis,
            'llm_deliberation': combined_deliberation,  # For backward compatibility
            'instances_count': len(instances),
            'flexible_tagging_used': True
        }

    def _extract_json_array(self, response_text: str) -> str:
        """Extract JSON array using robust logic adapted from multi-model system"""

        # First try to find complete JSON array with proper bracket matching
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
            # Validate this looks like proper JSON with objects
            if '{' in json_str and '}' in json_str:
                return json_str

        # Look for JSON OUTPUT section specifically
        json_output_match = re.search(r'(?:STRUCTURED )?JSON OUTPUT\s*:?\s*(.*?)(?:\s*$)', response_text, re.IGNORECASE | re.DOTALL)
        if json_output_match:
            json_section = json_output_match.group(1).strip()
            # Extract array from this section
            array_match = re.search(r'(\[[\s\S]*?\])', json_section)
            if array_match:
                return array_match.group(1).strip()

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
                return candidate_json.strip()

        # Check if empty array is indicated
        if '[]' in response_text or 'no figurative language found' in response_text.lower():
            return "[]"

        return "[]"

    def _validate_instance_format(self, instance: dict):
        """Ensure instance has all required fields with proper defaults"""
        required_fields = {
            'figurative_language': 'no',
            'simile': 'no',
            'metaphor': 'no',
            'personification': 'no',
            'idiom': 'no',
            'hyperbole': 'no',
            'metonymy': 'no',
            'other': 'no',
            'hebrew_text': '',
            'english_text': '',
            'explanation': '',
            'target': [],
            'vehicle': [],
            'ground': [],
            'posture': [],
            'confidence': 0.8,
            'speaker': 'Narrator',
            'purpose': ''
        }

        for field, default_value in required_fields.items():
            if field not in instance:
                instance[field] = default_value

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


if __name__ == "__main__":
    # Test functionality would go here
    print("FlexibleTaggingGeminiClient loaded successfully")