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
from claude_sonnet_client import ClaudeSonnetClient

class FlexibleTaggingGeminiClient(MultiModelGeminiClient):
    """Enhanced Gemini client with flexible tagging framework"""

    def __init__(self, api_key: str, validator=None, logger=None, db_manager=None):
        """Initialize with flexible tagging capabilities"""
        super().__init__(api_key, validator, logger, db_manager)
        self.flexible_rules = self._load_flexible_rules()

        # Additional tracking for Pro model fallbacks
        self.pro_fallback_count = 0

        # Initialize Claude Sonnet client for tertiary fallback
        try:
            # Pass our prompt generator to Claude so it uses the same instructions
            self.claude_client = ClaudeSonnetClient(
                logger=self.logger,
                prompt_generator=self._create_flexible_tagging_prompt
            )
            if self.logger:
                self.logger.info("Claude Sonnet 4 client initialized successfully with shared prompt generator")
        except Exception as e:
            self.claude_client = None
            if self.logger:
                self.logger.warning(f"Claude Sonnet 4 client initialization failed: {e}")

        # Claude fallback tracking
        self.claude_fallback_count = 0

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
            context_rules = """⚖️ **LEGAL/CEREMONIAL/RITUAL TEXT - MODERATE CONSERVATIVE** ⚖️

**NEVER MARK AS FIGURATIVE:**
• Technical religious terms: holy, clean, offering, covenant
• Procedural instructions and ritual descriptions
• Legal formulations and standard phrases
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger).
• Ritual procedural comparisons (e.g. כַּֽחַטָּאת֙ כָּֽאָשָׁ֔ם)

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

**THEN provide STRUCTURED JSON OUTPUT (REQUIRED):**

**CRITICAL JSON REQUIREMENTS:**
1. You MUST output a valid JSON array, even if empty: []
2. Each object MUST have ALL required fields
3. Use hierarchical arrays for target, vehicle, ground, and posture tags
4. Format exactly as shown below

**HIERARCHICAL TAGGING GUIDE - CRITICAL FOR SCHOLAR SEARCH:**
- TARGET = WHO/WHAT the figurative speech is ABOUT (generate hierarchical tags from specific to general)
- VEHICLE = WHAT the target is being LIKENED TO (generate hierarchical tags from specific to general)
- GROUND = WHAT QUALITY of the target is being described (generate hierarchical tags from specific to general)
- POSTURE = SPEAKER ATTITUDE/STANCE (generate hierarchical tags from specific to general)

**HIERARCHY SEARCH PRINCIPLES:**
Your tags MUST enable scholars to find instances at ANY level of specificity:
- SPECIFIC searches: "David as lion" → ["David", "king", "person"]
- CATEGORY searches: "king metaphors" → ["David", "king", "person"]
- BROAD searches: "person metaphors" → ["David", "king", "person"]

**HIERARCHICAL STRUCTURE REQUIREMENTS:**
- Array index 0: MOST SPECIFIC (exact subject/image/quality)
- Array index 1: CATEGORY LEVEL (type/class/group)
- Array index 2: BROADEST DOMAIN (general field/realm)
- Always provide 2-4 levels per dimension for maximum searchability
- MULTIPLE DESCRIPTORS: You CAN use multiple terms within each level when appropriate
  Example: ["David the king", "Israelite ruler", "human leader"] or ["fierce lion", "predatory animal", "living creature"]

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
                                           book: str = "", chapter: int = 0, model_override: str = None):
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
            if model_override:
                if self.logger:
                    self.logger.info(f"Using model override: {model_override}")

                # Handle gemini-2.5-pro as a special high-capacity fallback model
                if "2.5-pro" in model_override:
                    try:
                        import google.generativeai as genai
                        model_to_use = genai.GenerativeModel("gemini-2.5-pro")
                        config_to_use = {
                            'temperature': 0.10,  # Conservative for complex analysis
                            'top_p': 0.7,
                            'top_k': 20,
                            'max_output_tokens': 30000,  # Higher limit for Pro model
                        }
                        model_name_to_use = "gemini-2.5-pro"
                    except Exception as e:
                        if self.logger:
                            self.logger.error(f"Failed to initialize gemini-2.5-pro: {e}")
                        # Fallback to 1.5 flash if Pro not available
                        model_to_use = self.fallback_model
                        config_to_use = self.fallback_config
                        model_name_to_use = self.fallback_model_name
                elif "1.5" in model_override:
                    model_to_use = self.fallback_model
                    config_to_use = self.fallback_config
                    model_name_to_use = self.fallback_model_name
                else:
                    model_to_use = self.primary_model
                    config_to_use = self.primary_config
                    model_name_to_use = self.primary_model_name

                result, error, metadata = self._try_model_analysis_with_custom_prompt(
                    model_to_use, config_to_use, model_name_to_use,
                    prompt
                )
                metadata['fallback_used'] = "pro" in model_override or "1.5" in model_override
                metadata['pro_model_used'] = "2.5-pro" in model_override

                # Track Pro model fallbacks in usage statistics
                if "2.5-pro" in model_override:
                    self.fallback_count += 1
                    self.pro_fallback_count += 1
            else:
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

    def analyze_with_claude_fallback(self, hebrew_text: str, english_text: str,
                                     book: str = "", chapter: int = 0):
        """
        Claude Sonnet 4 fallback system for complex verses

        When both Gemini Flash and Pro models fail, use Claude Sonnet 4
        as the tertiary fallback with high token limits and different architecture.

        Returns: Tuple of (response_text, error, metadata)
        """
        if self.logger:
            self.logger.info(f"🤖 CLAUDE FALLBACK: Using Claude Sonnet 4 for complex verse analysis")

        if not self.claude_client:
            error_msg = "Claude Sonnet 4 client not available"
            if self.logger:
                self.logger.error(error_msg)

            metadata = {
                'model_used': 'claude-3-5-sonnet-20241022',
                'claude_fallback_used': True,
                'flexible_instances': [],
                'figurative_detection_deliberation': '',
                'tagging_analysis_deliberation': '',
                'instances_count': 0,
                'flexible_tagging_used': True,
                'truncation_detected': False
            }
            return "[]", error_msg, metadata

        try:
            # Track Claude fallback usage
            self.claude_fallback_count += 1

            # Use Claude Sonnet 4 with high token limit
            result_text, error, metadata = self.claude_client.analyze_figurative_language_flexible(
                hebrew_text, english_text, book, chapter, max_tokens=8000
            )

            if error:
                if self.logger:
                    self.logger.error(f"🤖 CLAUDE FALLBACK: Failed - {error}")

                fallback_metadata = {
                    'model_used': 'claude-3-5-sonnet-20241022',
                    'claude_fallback_used': True,
                    'flexible_instances': [],
                    'figurative_detection_deliberation': '',
                    'tagging_analysis_deliberation': '',
                    'instances_count': 0,
                    'flexible_tagging_used': True,
                    'truncation_detected': False
                }
                return "[]", error, fallback_metadata

            # Claude succeeded
            instances = metadata.get('flexible_instances', [])
            if self.logger:
                self.logger.info(f"🤖 CLAUDE FALLBACK: Successfully analyzed verse - {len(instances)} instances found")

            # Update metadata to reflect Claude usage
            metadata['claude_fallback_used'] = True
            metadata['flexible_tagging_used'] = True

            return result_text, None, metadata

        except Exception as e:
            error_msg = f"Claude fallback failed: {str(e)}"
            if self.logger:
                self.logger.error(error_msg)
            return "[]", error_msg, {
                'model_used': 'claude-3-5-sonnet-20241022',
                'claude_fallback_used': True,
                'claude_step_completed': 'failed',
                'error': True
            }

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

                # OPTIMIZED LOGGING - Only log detailed debug info in debug mode
                if self.logger and self.logger.level <= logging.DEBUG:
                    self.logger.debug(f"🔍 API Response Debug Info:")
                    self.logger.debug(f"  📊 Total candidates: {len(response.candidates)}")

                    # Log finish reason
                    finish_reason = getattr(candidate, 'finish_reason', 'NO_FINISH_REASON')
                    self.logger.debug(f"  🏁 Finish reason: {finish_reason}")
                    self.logger.debug(f"  📝 Finish reason type: {type(finish_reason)}")
                    self.logger.debug(f"  📝 Finish reason str: '{str(finish_reason)}'")

                    # Log usage metadata for token counts
                    if hasattr(response, 'usage_metadata'):
                        self.logger.debug(f"  🪙 Usage Metadata:")
                        self.logger.debug(f"    - Prompt Token Count: {getattr(response.usage_metadata, 'prompt_token_count', 'N/A')}")
                        self.logger.debug(f"    - Candidates Token Count: {getattr(response.usage_metadata, 'candidates_token_count', 'N/A')}")
                        self.logger.debug(f"    - Total Token Count: {getattr(response.usage_metadata, 'total_token_count', 'N/A')}")
                    else:
                        self.logger.debug(f"  🪙 Usage Metadata: Not available")

                    # Check for safety ratings
                    if hasattr(candidate, 'safety_ratings') and candidate.safety_ratings:
                        self.logger.debug(f"  🛡️ Safety ratings: {candidate.safety_ratings}")
                    else:
                        self.logger.debug(f"  🛡️ Safety ratings: None")

                    # Check content structure
                    if hasattr(candidate, 'content'):
                        self.logger.debug(f"  📄 Has content: True")
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            self.logger.debug(f"  📄 Content parts count: {len(candidate.content.parts)}")
                        else:
                            self.logger.debug(f"  📄 Content parts: None or empty")
                    else:
                        self.logger.debug(f"  📄 Has content: False")

                # Check for restriction and truncation
                if hasattr(candidate, 'finish_reason'):
                    if self._is_restriction_reason(candidate.finish_reason):
                        if self.logger:
                            self.logger.error(f"❌ CONTENT RESTRICTION DETECTED: {candidate.finish_reason}")
                        return None, f"Content restricted: {candidate.finish_reason}", {}
                    # Check for MAX_TOKENS truncation
                    elif str(candidate.finish_reason) == 'FinishReason.MAX_TOKENS' or str(candidate.finish_reason) == '2':
                        if self.logger:
                            self.logger.warning("⚠️ RESPONSE TRUNCATED DUE TO TOKEN LIMIT - will attempt fallback parsing")
                        # Continue to extract what we have and use fallback parsing
                    # Check for other concerning finish reasons
                    elif str(candidate.finish_reason) not in ['FinishReason.STOP', '1', 'STOP', None]:
                        if self.logger:
                            self.logger.warning(f"⚠️ UNUSUAL FINISH REASON: {candidate.finish_reason} - may indicate truncation or filtering")

                # Extract response text safely (using the same pattern as original)
                try:
                    if hasattr(candidate, 'content') and candidate.content:
                        if hasattr(candidate.content, 'parts') and candidate.content.parts:
                            response_text = candidate.content.parts[0].text
                            if self.logger and self.logger.level <= logging.DEBUG:
                                self.logger.debug(f"  📝 Response text length: {len(response_text)} characters")
                                self.logger.debug(f"  📝 Response ends with: '{response_text[-50:] if len(response_text) > 50 else response_text}'")
                                # Check for abrupt ending patterns
                                if not response_text.strip().endswith(('.', '!', '?', ']', '}')):
                                    self.logger.warning(f"  ⚠️ Response appears to end abruptly (no proper punctuation)")
                        else:
                            response_text = str(candidate.content)
                            if self.logger:
                                self.logger.warning(f"  ⚠️ No content parts - using string conversion")
                    else:
                        response_text = "[]"
                        if self.logger:
                            self.logger.warning(f"  ⚠️ No content found - using empty array")
                except Exception as e:
                    response_text = "[]"
                    if self.logger:
                        self.logger.error(f"  ❌ Exception extracting response text: {e}")

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
        should_trigger_fallback = False
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
                self.logger.debug(f"  📝 Detection ends with: '{figurative_detection[-100:] if len(figurative_detection) > 100 else figurative_detection}'")
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
        json_string = ""  # Initialize to prevent undefined variable errors
        if self.logger and self.logger.level <= logging.DEBUG:
            self.logger.debug(f"🔍 JSON EXTRACTION DEBUG:")

        try:
            # Use more sophisticated JSON extraction
            json_string = self._extract_json_array(response_text)

            if self.logger and self.logger.level <= logging.DEBUG:
                if json_string:
                    self.logger.debug(f"  📄 JSON string extracted: {len(json_string)} chars")
                    self.logger.debug(f"  📄 JSON preview: '{json_string[:200] if len(json_string) > 200 else json_string}'")
                    # Log the COMPLETE JSON for debugging malformed content
                    self.logger.debug(f"  📄 COMPLETE JSON CONTENT:")
                    self.logger.debug(f"---JSON-START---")
                    self.logger.debug(json_string)
                    self.logger.debug(f"---JSON-END---")
                    # Check for problematic characters only in debug mode
                    problematic_chars = []
                    for i, char in enumerate(json_string):
                        if ord(char) > 127 or char in ['🎯', '✅', '❌', '📊', '🔍', '⚠️']:
                            problematic_chars.append(f"'{char}' (ord={ord(char)}) at pos {i}")
                    if problematic_chars:
                        self.logger.warning(f"  ⚠️ Found problematic characters: {problematic_chars[:10]}")  # Show first 10
                else:
                    self.logger.debug(f"  ⚠️ No JSON string extracted from response")
            elif self.logger and json_string:
                # In INFO mode, just log basic success
                self.logger.info(f"JSON extracted: {len(json_string)} chars")

            if json_string and json_string != "[]":
                # First try to parse as-is
                try:
                    instances = json.loads(json_string)
                    if self.logger:
                        self.logger.info(f"  ✅ JSON parsing succeeded on first attempt")
                except json.JSONDecodeError as parse_error:
                    if self.logger:
                        self.logger.error(f"  ❌ Initial JSON parsing failed: {parse_error}")
                        self.logger.error(f"  ❌ Parse error position: {getattr(parse_error, 'pos', 'unknown')}")
                        self.logger.error(f"  ❌ Parse error line/col: {getattr(parse_error, 'lineno', 'unknown')}/{getattr(parse_error, 'colno', 'unknown')}")
                    # Try to fix common JSON issues
                    fixed_json = self._fix_json_format(json_string)
                    if fixed_json:
                        try:
                            instances = json.loads(fixed_json)
                            if self.logger:
                                self.logger.info("  ✅ JSON parsing succeeded after format repair")
                        except json.JSONDecodeError as repair_error:
                            if self.logger:
                                self.logger.error(f"  ❌ JSON format repair also failed: {repair_error}")
                            raise parse_error  # Re-raise the original error
                    else:
                        if self.logger:
                            self.logger.error(f"  ❌ JSON format repair returned None")
                        raise parse_error  # Re-raise the original error

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
            # Try fallback parsing from deliberation when JSON fails but figurative language is detected
            instances = self._fallback_parse_from_deliberation(figurative_detection, tagging_analysis)
            if instances and self.logger:
                self.logger.info(f"Fallback parsing recovered {len(instances)} instances from deliberation")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Unexpected error parsing flexible response: {e}")
            instances = []

        # Additional check: if no instances found but deliberation suggests figurative language was detected
        # Check both cases: JSON parsing failed OR we got empty array with analysis
        should_trigger_fallback = False
        if not instances and (figurative_detection or tagging_analysis):
            # Case 1: JSON parsing actually FAILED (not a valid empty array)
            json_parsing_failed = json_string.strip() != "[]"
            # Case 2: Got valid empty array but have substantial analysis (potential false negative)
            empty_array_with_analysis = json_string.strip() == "[]"

            if json_parsing_failed or empty_array_with_analysis:
                if self.logger:
                    self.logger.info(f"🔍 FALLBACK CHECK - No instances found but have deliberation text")

                # Check for signs of incomplete response or truncation
                combined_text = f"{figurative_detection} {tagging_analysis}".lower()
                truncation_indicators = [
                    "this is", "this phrase is", "is a", "is an", "idiom", "metaphor", "hyperbole", "metonymy",
                    "figurative", "non-literal", "set phrase", "biblical idiom"
                ]

                has_indicators = any(indicator in combined_text for indicator in truncation_indicators)
                ends_abruptly = (
                    figurative_detection.strip().endswith('...') or
                    not figurative_detection.strip().endswith('.') or
                    len(figurative_detection.strip()) > 100 and not any(punct in figurative_detection[-20:] for punct in ['.', '!', '?'])
                )

                if self.logger:
                    self.logger.info(f"  📝 Has figurative indicators: {has_indicators}")
                    self.logger.info(f"  📝 Appears to end abruptly: {ends_abruptly}")

                # Enhanced detection of LLM inconsistency - detailed analysis but empty JSON
                has_substantial_analysis = len(figurative_detection.strip()) > 500
                has_figurative_analysis = any(term in combined_text for term in [
                    "reasoning for inclusion", "marked as figurative", "classify", "include",
                    "this phrase", "this is", "functions as", "serves as", "represents"
                ])

                # Check for explicit POSITIVE conclusions about figurative language
                # Must exclude negative statements like "no figurative language"
                has_positive_figurative_conclusions = any(term in combined_text for term in [
                    "is a metaphor", "is an idiom", "is hyperbole", "is metonymy",
                    "biblical idiom", "this is figurative", "contains figurative", "uses figurative",
                    "classic case of", "fits the criteria", "clear case of", "example of",
                    "case of metonymy", "case of metaphor", "case of idiom", "case of hyperbole"
                ])

                # Check for negative conclusions that should NOT trigger fallback
                has_negative_figurative_conclusions = any(term in combined_text for term in [
                    "no figurative language", "not figurative", "no elements", "does not contain",
                    "not meet the criteria", "no metaphor", "no idiom", "no hyperbole",
                    "literal language", "straightforward language"
                ])

                # Final determination: only positive conclusions count
                has_figurative_conclusions = has_positive_figurative_conclusions and not has_negative_figurative_conclusions

                # Check for missing TAGGING_ANALYSIS section (indicates truncation)
                # FIXED: Only trigger when deliberation actually found figurative language
                missing_tagging_analysis = (
                    figurative_detection.strip() and  # Has FIGURATIVE_DETECTION
                    not tagging_analysis.strip() and  # But missing TAGGING_ANALYSIS
                    json_string.strip() == "[]" and   # And empty JSON result
                    has_figurative_conclusions         # AND deliberation concludes figurative language was found
                )

                # Multiple criteria for triggering fallback
                is_likely_truncated = ends_abruptly and has_indicators
                is_analysis_complete_but_json_empty = (
                    has_indicators and
                    has_figurative_conclusions and  # FIXED: Only trigger if positive conclusions found
                    has_figurative_analysis
                )

                should_trigger_fallback = is_likely_truncated or is_analysis_complete_but_json_empty or missing_tagging_analysis

                if self.logger:
                    self.logger.info(f"  📝 Has substantial analysis: {has_substantial_analysis}")
                    self.logger.info(f"  📝 Has figurative analysis: {has_figurative_analysis}")
                    self.logger.info(f"  📝 Has figurative conclusions: {has_figurative_conclusions}")
                    self.logger.info(f"  📝 Missing TAGGING_ANALYSIS: {missing_tagging_analysis}")
                    self.logger.info(f"  📝 Analysis complete but JSON empty: {is_analysis_complete_but_json_empty}")
                    self.logger.info(f"  📝 Should trigger fallback: {should_trigger_fallback}")

                if should_trigger_fallback:
                    if self.logger:
                        self.logger.error("❌ API response was truncated. No JSON was found and fallback parsing is disabled.")
                        self.logger.error("❌ This verse must be re-processed. Returning no instances.")
                    instances = [] # Explicitly set instances to empty
                else:
                    if self.logger:
                        self.logger.info(f"  📝 Truncation criteria not met - no fallback parsing attempted")

        result = {
            'flexible_instances': instances,
            'figurative_detection_deliberation': figurative_detection,
            'tagging_analysis_deliberation': tagging_analysis,
            'instances_count': len(instances),
            'flexible_tagging_used': True,
            'truncation_detected': should_trigger_fallback if 'should_trigger_fallback' in locals() else False
        }
        # NOTE: This method preserves the model_used field by not overwriting it
        # The model_used field is set in analyze_figurative_language_flexible and should not be overwritten
        return result

    def _extract_json_array(self, response_text: str) -> str:
        """Extract JSON array using robust logic adapted from multi-model system"""

        if self.logger:
            self.logger.info(f"    🔍 JSON Array Extraction:")

        # First try to find complete JSON array with proper bracket matching
        json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(0).strip()
            if self.logger:
                self.logger.info(f"      📄 Found JSON-like array: {len(json_str)} chars")
                self.logger.info(f"      📄 Array content: '{json_str}'")
            # Validate this looks like proper JSON with objects
            if '{' in json_str and '}' in json_str:
                if self.logger:
                    self.logger.info(f"      ✅ Array contains objects - using this match")
                return json_str
            elif self.logger:
                self.logger.info(f"      ⚠️ Array doesn't contain objects - continuing search")

        # Look for JSON OUTPUT section specifically
        json_output_match = re.search(r'(?:STRUCTURED )?JSON OUTPUT\s*:?\s*(.*?)(?:\s*$)', response_text, re.IGNORECASE | re.DOTALL)
        if json_output_match:
            json_section = json_output_match.group(1).strip()
            if self.logger:
                self.logger.info(f"      📄 Found JSON OUTPUT section: {len(json_section)} chars")
            # Extract array from this section with more robust bracket matching
            array_match = re.search(r'(\[[\s\S]*?\])', json_section)
            if array_match:
                candidate_json = array_match.group(1).strip()
                # Check if the JSON appears complete by looking for proper structure
                if self._is_json_complete(candidate_json):
                    if self.logger:
                        self.logger.info(f"      ✅ Found complete array in JSON OUTPUT section")
                    return candidate_json
                else:
                    if self.logger:
                        self.logger.warning(f"      ⚠️ JSON appears incomplete in OUTPUT section")
                    # Continue to other extraction methods
        elif self.logger:
            self.logger.info(f"      ⚠️ No JSON OUTPUT section found")

        # Use sophisticated bracket matching for standalone arrays
        start_bracket = response_text.find('[')
        if start_bracket != -1:
            if self.logger:
                self.logger.info(f"      📄 Attempting sophisticated bracket matching from position {start_bracket}")

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

            if self.logger:
                self.logger.info(f"      📄 Bracket matching found: {len(candidate_json)} chars")

            # Verify this contains objects
            if '{' in candidate_json and '}' in candidate_json:
                if self.logger:
                    self.logger.info(f"      ✅ Bracket-matched array contains objects")
                return candidate_json.strip()
            elif self.logger:
                self.logger.info(f"      ⚠️ Bracket-matched array doesn't contain objects")
        elif self.logger:
            self.logger.info(f"      ⚠️ No opening bracket '[' found in response")

        # Check if empty array is indicated
        if '[]' in response_text or 'no figurative language found' in response_text.lower():
            if self.logger:
                self.logger.info(f"      📄 Empty array pattern detected")
            return "[]"

        if self.logger:
            self.logger.warning(f"      ❌ No valid JSON array found - returning empty")
        return "[]"

    def _is_json_complete(self, json_str: str) -> bool:
        """Check if JSON string appears to be complete with required fields"""
        try:
            # Basic completeness check - must have required fields
            required_fields = ['figurative_language', 'confidence', 'target', 'vehicle', 'ground', 'posture']

            # Check if JSON ends with proper closing bracket
            if not json_str.strip().endswith(']'):
                return False

            # Check if it contains most required fields
            found_fields = sum(1 for field in required_fields if f'"{field}"' in json_str)

            # Consider complete if it has most required fields (allows for some flexibility)
            return found_fields >= 4
        except:
            return False

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

    def _fallback_parse_from_deliberation(self, figurative_detection: str, tagging_analysis: str) -> list:
        """
        Fallback method to extract basic figurative language info from deliberation text
        when JSON parsing fails but deliberation indicates figurative language was found
        """
        if not figurative_detection and not tagging_analysis:
            return []

        combined_text = f"{figurative_detection} {tagging_analysis}".lower()

        # Check if deliberation suggests figurative language was found
        positive_indicators = [
            "this is", "this phrase is", "is a", "is an", "classified as",
            "metaphor", "simile", "idiom", "hyperbole", "metonymy", "personification",
            "figurative", "non-literal", "set phrase", "biblical idiom"
        ]

        if not any(indicator in combined_text for indicator in positive_indicators):
            return []

        # Extract figurative types mentioned
        types_found = {
            'metaphor': 'no',
            'simile': 'no',
            'idiom': 'no',
            'hyperbole': 'no',
            'metonymy': 'no',
            'personification': 'no',
            'other': 'no'
        }

        # Look for explicit type mentions
        if 'metaphor' in combined_text:
            types_found['metaphor'] = 'yes'
        if 'simile' in combined_text:
            types_found['simile'] = 'yes'
        if any(term in combined_text for term in ['idiom', 'idiomatic', 'set phrase', 'biblical idiom']):
            types_found['idiom'] = 'yes'
        if 'hyperbole' in combined_text:
            types_found['hyperbole'] = 'yes'
        if 'metonymy' in combined_text:
            types_found['metonymy'] = 'yes'
        if 'personification' in combined_text:
            types_found['personification'] = 'yes'

        # Check if any figurative type was found
        if not any(val == 'yes' for val in types_found.values()):
            return []

        # Extract Hebrew and English text with better context awareness
        hebrew_text = ""
        english_text = ""

        # Look for Hebrew text patterns in context with figurative language mentions
        hebrew_patterns = [
            r'[*]{2,3}[^*]*([א-ת][א-ת\s־֑֖֤֣֥֛֪֚֭֮֙֜֗֝֩֫֬֯]*[א-ת])[^*]*[*]{2,3}',  # Hebrew in bold markers
            r'"([א-ת][א-ת\s־֑֖֤֣֥֛֪֚֭֮֙֜֗֝֩֫֬֯]*[א-ת])"',  # Hebrew in quotes
            r'([א-ת][א-ת\s־֑֖֤֣֥֛֪֚֭֮֙֜֗֝֩֫֬֯]*[א-ת])\s*\([^)]*\)',  # Hebrew followed by translation in parentheses
        ]

        for pattern in hebrew_patterns:
            matches = re.findall(pattern, figurative_detection + tagging_analysis)
            if matches:
                # Get the longest Hebrew match (likely more complete phrase)
                hebrew_text = max(matches, key=len).strip()
                break

        # Look for English text in quotes or after specific markers
        english_patterns = [
            r'"([^"\\]*(?:\\.[^"\\]*)*)"',
            r"'([^']*(?:\\.[^']*)*)'",
            r'english[:\s]+([^.]+)',  # After "English:"
            r'phrase[:\s]+([^.]+)',  # After "phrase:"
            r'\(([^)]+)\)',  # Text in parentheses (often translations)
        ]

        # Prioritize longer English matches (more descriptive)
        english_candidates = []
        for pattern in english_patterns:
            matches = re.findall(pattern, combined_text, re.IGNORECASE)
            english_candidates.extend(matches)

        if english_candidates:
            # Filter out very short matches and prefer longer ones
            filtered_candidates = [text.strip() for text in english_candidates if len(text.strip()) > 3]
            if filtered_candidates:
                english_text = max(filtered_candidates, key=len)

        # Create a basic fallback instance
        fallback_instance = {
            'figurative_language': 'yes',
            'hebrew_text': hebrew_text,
            'english_text': english_text,
            'explanation': 'Recovered from deliberation due to JSON parsing failure',
            'confidence': 0.7,  # Lower confidence for fallback parsing
            'speaker': 'Narrator',
            'purpose': 'Extracted from deliberation analysis',
            'target': [],
            'vehicle': [],
            'ground': [],
            'posture': []
        }

        # Add the detected types
        fallback_instance.update(types_found)

        if self.logger:
            detected_types = [k for k, v in types_found.items() if v == 'yes']
            self.logger.info(f"Fallback parsing detected types: {detected_types}")

        return [fallback_instance]

    def get_usage_info(self):
        """Override parent method to include Pro and Claude fallback statistics"""
        base_info = super().get_usage_info()

        # Add Pro model specific tracking
        base_info['Pro_Model_Fallbacks'] = self.pro_fallback_count
        base_info['Pro_Fallback_Rate'] = self.pro_fallback_count / max(self.request_count, 1)

        # Add Claude fallback tracking
        base_info['Claude_Fallbacks'] = self.claude_fallback_count
        base_info['Claude_Fallback_Rate'] = self.claude_fallback_count / max(self.request_count, 1)

        # Add Claude usage stats if available
        if self.claude_client:
            claude_stats = self.claude_client.get_usage_stats()
            base_info['Claude_Usage'] = claude_stats

        return base_info

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

    def _call_detection_only(self, hebrew_text: str, english_text: str, book: str, chapter: int):
        """
        Step 1: Detection only - simplified prompt for identifying figurative language
        """
        text_context = self._determine_text_context(book, chapter)

        # Create simplified detection-only prompt (no tagging instructions)
        context_rules = self._get_context_rules(text_context)

        prompt = f"""You are a biblical Hebrew scholar analyzing this text for figurative language.

Hebrew: {hebrew_text}
English: {english_text}

{context_rules}

**TASK: DETECTION ONLY**

**FIRST, provide your reasoning in a DETECTION_DELIBERATION section:**

DETECTION_DELIBERATION:
[Analyze EVERY potential figurative element in this verse. For each phrase/concept, explain:
- What you considered (e.g., "considered if 'X' might be metaphor, metonymy, etc")
- Your reasoning for including/excluding it
- Any borderline cases you debated]

**THEN provide STRUCTURED JSON OUTPUT (REQUIRED):**

You MUST output a valid JSON array. Use this exact format:

Example for figurative language found:
[{{"figurative_language": "yes", "simile": "no", "metaphor": "yes", "personification": "no", "idiom": "no", "hyperbole": "no", "metonymy": "no", "other": "no", "hebrew_text": "Hebrew phrase", "english_text": "English phrase", "explanation": "Brief explanation", "confidence": 0.8, "speaker": "Speaker name", "purpose": "Purpose"}}]

**CRITICAL**: Use only JSON format. No markdown, no bullet points, no prose.
**If no figurative language found, output exactly:** []

Analysis:"""

        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-2.5-pro")
            config = {
                'temperature': 0.05,  # Very conservative for detection
                'top_p': 0.7,
                'top_k': 20,
                'max_output_tokens': 8000,  # Smaller limit for simpler task
            }

            response = model.generate_content(prompt, generation_config=config)

            if not response.candidates or not response.candidates[0].content:
                return {'has_figurative_language': False, 'deliberation': ''}, "No response from model"

            response_text = response.candidates[0].content.parts[0].text

            # Extract deliberation
            deliberation = ""
            # Try multiple patterns to match different response formats
            patterns = [
                r'DETECTION_DELIBERATION\s*:?\s*(.*?)(?=JSON|Analysis|\[|$)',
                r'\*\*FIGURATIVE_DETECTION\*\*:?\s*(.*?)(?=JSON|Analysis|\[|$)',
                r'FIGURATIVE_DETECTION\s*:?\s*(.*?)(?=JSON|Analysis|\[|$)'
            ]

            for pattern in patterns:
                detection_match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if detection_match:
                    deliberation = detection_match.group(1).strip()
                    break

            # Extract JSON instances
            json_string = self._extract_json_array(response_text)
            instances = []
            if json_string and json_string != "[]":
                try:
                    instances = json.loads(json_string)
                except json.JSONDecodeError:
                    pass

            has_figurative = len(instances) > 0

            return {
                'has_figurative_language': has_figurative,
                'instances': instances,
                'deliberation': deliberation
            }, None

        except Exception as e:
            return {'has_figurative_language': False, 'deliberation': ''}, str(e)

    def _call_validation_only(self, detection_result, hebrew_text: str, english_text: str):
        """
        Step 2: Validation only - validate detected figurative language
        """
        instances = detection_result.get('instances', [])
        if not instances:
            return {'validated_instances': []}, None

        # Create validation-focused prompt
        instances_text = "\n".join([f"- {inst.get('english_text', '')}: {inst.get('explanation', '')}"
                                   for inst in instances])

        prompt = f"""You are a biblical Hebrew scholar validating figurative language detections.

Hebrew: {hebrew_text}
English: {english_text}

**DETECTED INSTANCES TO VALIDATE:**
{instances_text}

**TASK: VALIDATION ONLY**

**FIRST, provide your reasoning in a VALIDATION_DELIBERATION section:**

VALIDATION_DELIBERATION:
[For each detected instance, analyze:
- Is this truly figurative language?
- Is the classification (metaphor, simile, etc.) correct?
- Should it be reclassified to a different type?
- Should it be rejected as not figurative?]

**THEN provide JSON OUTPUT:**

Return only the VALID instances in JSON format. For each valid instance:
- Keep original fields: figurative_language, simile, metaphor, etc.
- Add validation_decision: "VALID", "RECLASSIFIED", or "INVALID"
- If RECLASSIFIED, correct the type fields
- Include all original metadata

**If no instances are valid, output:** []

Analysis:"""

        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-2.5-pro")
            config = {
                'temperature': 0.05,
                'top_p': 0.7,
                'top_k': 20,
                'max_output_tokens': 8000,
            }

            response = model.generate_content(prompt, generation_config=config)

            if not response.candidates or not response.candidates[0].content:
                return {'validated_instances': []}, "No response from model"

            response_text = response.candidates[0].content.parts[0].text

            # Extract validation deliberation
            validation_deliberation = ""
            validation_match = re.search(r'VALIDATION_DELIBERATION\s*:?\s*(.*?)(?=JSON|Analysis|\[|$)',
                                        response_text, re.IGNORECASE | re.DOTALL)
            if validation_match:
                validation_deliberation = validation_match.group(1).strip()

            # Extract validated instances
            json_string = self._extract_json_array(response_text)
            validated_instances = []
            if json_string and json_string != "[]":
                try:
                    validated_instances = json.loads(json_string)
                except json.JSONDecodeError:
                    pass

            return {
                'validated_instances': validated_instances,
                'validation_deliberation': validation_deliberation
            }, None

        except Exception as e:
            return {'validated_instances': []}, str(e)

    def _call_tagging_only(self, validation_result, hebrew_text: str, english_text: str):
        """
        Step 3: Tagging only - add hierarchical tags to validated instances
        """
        instances = validation_result.get('validated_instances', [])
        if not instances:
            return {'tagged_instances': []}, None

        # Create tagging-focused prompt
        instances_text = "\n".join([f"- {inst.get('english_text', '')}: {inst.get('explanation', '')}"
                                   for inst in instances])

        prompt = f"""You are a biblical Hebrew scholar adding hierarchical tags to validated figurative language.

Hebrew: {hebrew_text}
English: {english_text}

**VALIDATED INSTANCES TO TAG:**
{instances_text}

**TASK: HIERARCHICAL TAGGING ONLY**

**HIERARCHICAL TAGGING GUIDE:**
- TARGET = WHO/WHAT the figurative speech is ABOUT (specific → category → domain)
- VEHICLE = WHAT the target is being LIKENED TO (specific → category → domain)
- GROUND = WHAT QUALITY is being described (specific → type → aspect)
- POSTURE = SPEAKER ATTITUDE (specific → category → orientation)

**Examples:**
- target: ["David", "king", "person"]
- vehicle: ["lion", "predatory animal", "living creature"]
- ground: ["strength", "physical quality", "attribute"]
- posture: ["celebration", "praise", "positive sentiment"]

**FIRST, provide your reasoning in a TAGGING_DELIBERATION section:**

TAGGING_DELIBERATION:
[For each instance, explain your hierarchical tag choices:
- Why you chose each TARGET level
- Why you chose each VEHICLE level
- Why you chose each GROUND level
- Why you chose each POSTURE level]

**THEN provide JSON OUTPUT:**

Return all instances with added hierarchical tags:
- Keep ALL original fields unchanged
- Add: "target": ["specific", "category", "domain"]
- Add: "vehicle": ["specific", "category", "domain"]
- Add: "ground": ["specific", "type", "aspect"]
- Add: "posture": ["specific", "category", "orientation"]

Analysis:"""

        try:
            import google.generativeai as genai
            model = genai.GenerativeModel("gemini-2.5-pro")
            config = {
                'temperature': 0.05,
                'top_p': 0.7,
                'top_k': 20,
                'max_output_tokens': 8000,
            }

            response = model.generate_content(prompt, generation_config=config)

            if not response.candidates or not response.candidates[0].content:
                return {'tagged_instances': []}, "No response from model"

            response_text = response.candidates[0].content.parts[0].text

            # Extract tagging deliberation
            tagging_deliberation = ""
            tagging_match = re.search(r'TAGGING_DELIBERATION\s*:?\s*(.*?)(?=JSON|Analysis|\[|$)',
                                     response_text, re.IGNORECASE | re.DOTALL)
            if tagging_match:
                tagging_deliberation = tagging_match.group(1).strip()

            # Extract tagged instances
            json_string = self._extract_json_array(response_text)
            tagged_instances = []
            if json_string and json_string != "[]":
                try:
                    tagged_instances = json.loads(json_string)
                    # Ensure all instances have hierarchical tags
                    for instance in tagged_instances:
                        if 'target' not in instance:
                            instance['target'] = []
                        if 'vehicle' not in instance:
                            instance['vehicle'] = []
                        if 'ground' not in instance:
                            instance['ground'] = []
                        if 'posture' not in instance:
                            instance['posture'] = []
                except json.JSONDecodeError:
                    pass

            return {
                'tagged_instances': tagged_instances,
                'tagging_deliberation': tagging_deliberation
            }, None

        except Exception as e:
            return {'tagged_instances': []}, str(e)

    def _get_context_rules(self, context: str) -> str:
        """Get context-specific rules for the simplified prompts"""
        if context == TextContext.CREATION_NARRATIVE.value:
            return """**CREATION NARRATIVE - ULTRA CONSERVATIVE**
- NEVER mark divine creation verbs, procedural language, or primordial descriptions as figurative
- ONLY mark clear cross-domain metaphors"""
        elif context == TextContext.POETIC_BLESSING.value:
            return """**POETIC BLESSING - BALANCED DETECTION**
- MARK tribal animal characterizations, cross-domain comparisons
- BE CONSERVATIVE with genealogical and historical statements"""
        elif context == TextContext.LEGAL_CEREMONIAL.value:
            return """**LEGAL/CEREMONIAL - MODERATE CONSERVATIVE**
- NEVER mark technical religious terms or procedural instructions
- MARK clear cross-domain metaphors and obvious similes"""
        else:
            return """**NARRATIVE - STANDARD CONSERVATIVE**
- BE CONSERVATIVE with standard narrative language and divine anthropomorphisms
- MARK clear metaphors (e.g., "cleave to God" using physical attachment for spiritual devotion)
- MARK personification and obvious similes
- MARK physical verbs applied to spiritual/abstract concepts"""


if __name__ == "__main__":
    # Test functionality would go here
    print("FlexibleTaggingGeminiClient loaded successfully")
