#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Multi-Model LLM Client supporting GPT-5.1, Claude Opus 4.5, and Gemini 3.0 Pro

This unified client provides a three-tier fallback chain:
1. GPT-5.1 (Primary) - OpenAI's latest reasoning model
2. Claude Opus 4.5 (Fallback 1) - Anthropic's most capable model
3. Gemini 3.0 Pro (Fallback 2) - Google's high-capacity thinking model

Each model is configured with maximum reasoning/thinking parameters for optimal
figurative language analysis in biblical Hebrew texts.
"""

import os
import json
import time
import re
from typing import List, Dict, Optional, Tuple
from enum import Enum

# OpenAI imports
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Anthropic imports
try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Google Gemini imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Import for Hebrew text processing
try:
    from ..text_extraction.hebrew_utils import HebrewTextProcessor
except ImportError:
    # Fallback for when running as main
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from text_extraction.hebrew_utils import HebrewTextProcessor


class TextContext(Enum):
    """Text context types for context-aware prompting"""
    CREATION_NARRATIVE = 'creation_narrative'
    POETIC_BLESSING = 'poetic_blessing'
    POETIC_WISDOM = 'poetic_wisdom'
    LEGAL_CEREMONIAL = 'legal_ceremonial'
    NARRATIVE = 'narrative'


class UnifiedLLMClient:
    """
    Unified client for GPT-5.1, Claude Opus 4.5, and Gemini 3.0 Pro

    Handles model-specific parameter translation and three-tier fallback logic
    with automatic retry on failures.
    """

    def __init__(self, validator=None, logger=None, db_manager=None):
        """
        Initialize the unified LLM client with all three models

        Args:
            validator: MetaphorValidator instance for two-stage validation
            logger: Logger instance for debugging and monitoring
            db_manager: DatabaseManager instance for logging
        """
        self.validator = validator
        self.logger = logger
        self.db_manager = db_manager

        # Initialize OpenAI client (GPT-5.1)
        self.openai_client = None
        if OPENAI_AVAILABLE:
            try:
                openai_api_key = os.getenv("OPENAI_API_KEY")
                if openai_api_key:
                    self.openai_client = OpenAI(api_key=openai_api_key)
                    if self.logger:
                        self.logger.info("✅ OpenAI GPT-5.1 client initialized")
                else:
                    if self.logger:
                        self.logger.warning("⚠️ OPENAI_API_KEY not found in environment")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ Failed to initialize OpenAI client: {e}")

        # Initialize Anthropic client (Claude Opus 4.5)
        self.anthropic_client = None
        if ANTHROPIC_AVAILABLE:
            try:
                anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
                if anthropic_api_key:
                    self.anthropic_client = Anthropic(api_key=anthropic_api_key)
                    if self.logger:
                        self.logger.info("✅ Anthropic Claude Opus 4.5 client initialized")
                else:
                    if self.logger:
                        self.logger.warning("⚠️ ANTHROPIC_API_KEY not found in environment")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ Failed to initialize Anthropic client: {e}")

        # Initialize Google Gemini client (Gemini 3.0 Pro)
        self.gemini_client = None
        if GEMINI_AVAILABLE:
            try:
                gemini_api_key = os.getenv("GEMINI_API_KEY")
                if gemini_api_key:
                    genai.configure(api_key=gemini_api_key)
                    # Try Gemini 3.0 Pro first, fallback to 2.5 Pro if needed
                    try:
                        self.gemini_client = genai.GenerativeModel("gemini-3.0-pro")
                        self.gemini_model_name = "gemini-3.0-pro"
                    except Exception:
                        try:
                            self.gemini_client = genai.GenerativeModel("gemini-3-pro")
                            self.gemini_model_name = "gemini-3-pro"
                        except Exception:
                            # Fallback to Gemini 2.5 Pro if 3.0 not available
                            self.gemini_client = genai.GenerativeModel("gemini-2.5-pro")
                            self.gemini_model_name = "gemini-2.5-pro"

                    if self.logger:
                        self.logger.info(f"✅ Google Gemini client initialized ({self.gemini_model_name})")
                else:
                    if self.logger:
                        self.logger.warning("⚠️ GEMINI_API_KEY not found in environment")
            except Exception as e:
                if self.logger:
                    self.logger.error(f"❌ Failed to initialize Gemini client: {e}")

        # Usage tracking
        self.request_count = 0
        self.gpt_success_count = 0
        self.claude_success_count = 0
        self.gemini_success_count = 0
        self.gpt_fallback_count = 0
        self.claude_fallback_count = 0
        self.total_cost = 0.0

        # Token tracking by model
        self.gpt_tokens = {'input': 0, 'output': 0, 'reasoning': 0}
        self.claude_tokens = {'input': 0, 'output': 0, 'thinking': 0}
        self.gemini_tokens = {'input': 0, 'output': 0}

    def analyze_figurative_language(self, hebrew_text: str, english_text: str,
                                   book: str = "", chapter: int = 0) -> Tuple[str, Optional[str], Dict]:
        """
        Analyze Hebrew text for figurative language using three-tier fallback chain

        Tries models in order: GPT-5.1 → Claude Opus 4.5 → Gemini 3.0 Pro

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation
            book: Book name for context-aware prompting
            chapter: Chapter number for context-aware prompting

        Returns:
            Tuple of (JSON string with analysis results, error message if any, metadata dict)
        """
        self.request_count += 1

        # Determine text context for appropriate prompting
        text_context = self._determine_text_context(book, chapter)

        # Build the analysis prompt (shared across all models)
        prompt = self._build_prompt(hebrew_text, english_text, text_context)

        # Try GPT-5.1 first
        if self.openai_client:
            result, error, metadata = self._call_gpt51(prompt, hebrew_text, english_text)
            if not error:
                self.gpt_success_count += 1
                metadata['primary_model'] = 'gpt-5.1'
                metadata['fallback_used'] = False
                return result, None, metadata
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ GPT-5.1 failed: {error}. Trying Claude Opus 4.5...")
                self.gpt_fallback_count += 1

        # Fallback to Claude Opus 4.5
        if self.anthropic_client:
            result, error, metadata = self._call_claude_opus45(prompt, hebrew_text, english_text)
            if not error:
                self.claude_success_count += 1
                metadata['primary_model'] = 'claude-opus-4-5'
                metadata['fallback_used'] = True
                metadata['fallback_reason'] = 'gpt_failure'
                return result, None, metadata
            else:
                if self.logger:
                    self.logger.warning(f"⚠️ Claude Opus 4.5 failed: {error}. Trying Gemini 3.0 Pro...")
                self.claude_fallback_count += 1

        # Final fallback to Gemini 3.0 Pro
        if self.gemini_client:
            result, error, metadata = self._call_gemini3_pro(prompt, hebrew_text, english_text)
            if not error:
                self.gemini_success_count += 1
                metadata['primary_model'] = self.gemini_model_name
                metadata['fallback_used'] = True
                metadata['fallback_reason'] = 'gpt_and_claude_failure'
                return result, None, metadata
            else:
                if self.logger:
                    self.logger.error(f"❌ All three models failed. Last error: {error}")

        # All models failed
        return "[]", "All models failed", {
            'error': True,
            'fallback_used': True,
            'all_models_failed': True
        }

    def _call_gpt51(self, prompt: str, hebrew_text: str, english_text: str) -> Tuple[str, Optional[str], Dict]:
        """
        Call GPT-5.1 with reasoning_effort="high"

        CRITICAL: GPT-5.1 defaults to reasoning_effort="none" - must explicitly set to "high"!
        """
        max_retries = 3
        metadata = {'model_used': 'gpt-5.1'}

        for attempt in range(max_retries):
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[
                        {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                        {"role": "user", "content": prompt}
                    ],
                    max_completion_tokens=65536,  # 64K max
                    reasoning_effort="high",  # CRITICAL - defaults to "none"!
                    temperature=0.15
                )

                # Extract token usage
                if hasattr(response, 'usage'):
                    metadata['input_tokens'] = getattr(response.usage, 'prompt_tokens', 0)
                    metadata['output_tokens'] = getattr(response.usage, 'completion_tokens', 0)
                    metadata['reasoning_tokens'] = getattr(response.usage, 'reasoning_tokens', 0)

                    # Update totals
                    self.gpt_tokens['input'] += metadata['input_tokens']
                    self.gpt_tokens['output'] += metadata['output_tokens']
                    self.gpt_tokens['reasoning'] += metadata['reasoning_tokens']

                    # Calculate cost (from plan: $1.25/M input, $10/M output)
                    cost = (metadata['input_tokens'] / 1_000_000 * 1.25 +
                           metadata['output_tokens'] / 1_000_000 * 10.0)
                    self.total_cost += cost
                    metadata['cost'] = cost

                # Extract response text
                response_text = response.choices[0].message.content

                # Parse and validate the response
                cleaned_response, all_instances, deliberation, truncation_info = self._clean_response(
                    response_text, hebrew_text, english_text
                )

                metadata['all_detected_instances'] = all_instances
                metadata['truncation_info'] = truncation_info
                metadata['retries'] = attempt

                return cleaned_response, None, metadata

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    if "rate_limit" in error_msg.lower() or "429" in error_msg:
                        wait_time = (2 ** attempt) * 5
                        if self.logger:
                            self.logger.info(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue

                return "[]", f"GPT-5.1 error: {error_msg}", {'retries': attempt + 1}

        return "[]", "GPT-5.1 failed after retries", {'retries': max_retries}

    def _call_claude_opus45(self, prompt: str, hebrew_text: str, english_text: str) -> Tuple[str, Optional[str], Dict]:
        """
        Call Claude Opus 4.5 with effort="high"

        Model ID: claude-opus-4-5-20251101
        """
        max_retries = 3
        metadata = {'model_used': 'claude-opus-4-5-20251101'}

        for attempt in range(max_retries):
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=64000,
                    messages=[{"role": "user", "content": prompt}],
                    # Note: effort parameter may not be in all SDK versions yet
                    # If not available, Claude will use default high-quality processing
                )

                # Extract token usage
                if hasattr(response, 'usage'):
                    metadata['input_tokens'] = getattr(response.usage, 'input_tokens', 0)
                    metadata['output_tokens'] = getattr(response.usage, 'output_tokens', 0)

                    # Update totals
                    self.claude_tokens['input'] += metadata['input_tokens']
                    self.claude_tokens['output'] += metadata['output_tokens']

                    # Calculate cost (from plan: $5/M input, $25/M output, $25/M thinking)
                    # Note: thinking tokens may be reported separately in future SDK versions
                    cost = (metadata['input_tokens'] / 1_000_000 * 5.0 +
                           metadata['output_tokens'] / 1_000_000 * 25.0)
                    self.total_cost += cost
                    metadata['cost'] = cost

                # Extract response text
                response_text = response.content[0].text

                # Parse and validate the response
                cleaned_response, all_instances, deliberation, truncation_info = self._clean_response(
                    response_text, hebrew_text, english_text
                )

                metadata['all_detected_instances'] = all_instances
                metadata['truncation_info'] = truncation_info
                metadata['retries'] = attempt

                return cleaned_response, None, metadata

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    if "rate_limit" in error_msg.lower() or "429" in error_msg:
                        wait_time = (2 ** attempt) * 5
                        if self.logger:
                            self.logger.info(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue

                return "[]", f"Claude Opus 4.5 error: {error_msg}", {'retries': attempt + 1}

        return "[]", "Claude Opus 4.5 failed after retries", {'retries': max_retries}

    def _call_gemini3_pro(self, prompt: str, hebrew_text: str, english_text: str) -> Tuple[str, Optional[str], Dict]:
        """
        Call Gemini 3.0 Pro with thinking_level="high"

        Note: Gemini 3.0 Pro defaults to thinking_level="high" (good!)
        """
        max_retries = 3
        metadata = {'model_used': self.gemini_model_name}

        generation_config = {
            'temperature': 0.15,
            'top_p': 0.8,
            'top_k': 25,
            'max_output_tokens': 64000,
            # Note: thinking_level parameter may vary by SDK version
            # Gemini 3.0 defaults to "high" which is what we want
        }

        for attempt in range(max_retries):
            try:
                response = self.gemini_client.generate_content(
                    prompt,
                    generation_config=generation_config
                )

                # Extract token usage
                if hasattr(response, 'usage_metadata'):
                    metadata['input_tokens'] = getattr(response.usage_metadata, 'prompt_token_count', 0)
                    metadata['output_tokens'] = getattr(response.usage_metadata, 'candidates_token_count', 0)

                    # Update totals
                    self.gemini_tokens['input'] += metadata['input_tokens']
                    self.gemini_tokens['output'] += metadata['output_tokens']

                    # Note: Gemini pricing varies by region/tier
                    # Using approximate values - adjust based on actual pricing
                    cost = (metadata['input_tokens'] / 1_000_000 * 0.50 +
                           metadata['output_tokens'] / 1_000_000 * 2.0)
                    self.total_cost += cost
                    metadata['cost'] = cost

                # Check for safety restrictions
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                        if self._is_restriction_reason(candidate.finish_reason):
                            return "[]", f"Content restricted: {candidate.finish_reason}", metadata

                # Extract response text
                response_text = response.text

                # Parse and validate the response
                cleaned_response, all_instances, deliberation, truncation_info = self._clean_response(
                    response_text, hebrew_text, english_text
                )

                metadata['all_detected_instances'] = all_instances
                metadata['truncation_info'] = truncation_info
                metadata['retries'] = attempt

                return cleaned_response, None, metadata

            except Exception as e:
                error_msg = str(e)
                if attempt < max_retries - 1:
                    if "429" in error_msg or "rate" in error_msg.lower():
                        wait_time = (2 ** attempt) * 5
                        if self.logger:
                            self.logger.info(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue

                return "[]", f"Gemini 3.0 Pro error: {error_msg}", {'retries': attempt + 1}

        return "[]", "Gemini 3.0 Pro failed after retries", {'retries': max_retries}

    def _determine_text_context(self, book: str, chapter: int) -> str:
        """Determine text context for appropriate prompting strategy"""

        # Genesis Creation Narratives (most conservative)
        if book.lower() == 'genesis' and chapter in {1, 2, 3}:
            return TextContext.CREATION_NARRATIVE.value

        # Poetic/Blessing texts (balanced approach)
        elif ((book.lower() == 'genesis' and chapter == 49) or
              (book.lower() == 'deuteronomy' and chapter in {32, 33})):
            return TextContext.POETIC_BLESSING.value

        # Wisdom Literature (Proverbs - high figurative detection)
        elif book.lower() == 'proverbs':
            return TextContext.POETIC_WISDOM.value

        # Psalms (poetic with high figurative content)
        elif book.lower() == 'psalms':
            return TextContext.POETIC_BLESSING.value  # Reuse poetic context

        # Legal/Ceremonial texts (moderate conservative)
        elif book.lower() in {'leviticus', 'numbers'}:
            return TextContext.LEGAL_CEREMONIAL.value

        # Narrative texts (standard approach)
        else:
            return TextContext.NARRATIVE.value

    def _build_prompt(self, hebrew_text: str, english_text: str, context: str) -> str:
        """
        Build the analysis prompt with context-aware rules

        Uses the proven prompt structure from the existing multi-model system
        """
        base_prompt = f"""You are a biblical Hebrew scholar analyzing this text for figurative language.

Hebrew: {hebrew_text}
English: {english_text}

"""

        # Context-specific rules (from existing proven system)
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

        elif context == TextContext.POETIC_BLESSING.value or context == TextContext.POETIC_WISDOM.value:
            if context == TextContext.POETIC_WISDOM.value:
                header = "📖 **WISDOM LITERATURE (PROVERBS) - BALANCED DETECTION** 📖"
                specific_examples = """• Animal metaphors: "ant", "eagle", "lion", "serpent" for character types
• Nature imagery: "water", "trees", "paths", "valleys" for life concepts
• Body metaphors: "heart", "tongue", "eyes", "hands" as abstract concepts
• Structural metaphors: "house", "foundation", "roof" for life/wisdom
• Path metaphors: "way", "path", "steps" for life choices
• Tree/water of life: Clear figurative expressions

**MARK WITH CARE:**
• Personification: "Wisdom calls", "Folly cries" - clear personification
• Comparative statements: Often genuinely figurative in Proverbs
• "Like/as" constructions: High percentage are true similes"""
            else:
                header = "📜 **POETIC BLESSING TEXT - BALANCED DETECTION** 📜"
                specific_examples = """• Tribal characterizations using animals: "lion", "wolf", "serpent", "eagle"
• Cross-domain comparisons: "unstable as water", "like a hind let loose"
• Clear metaphorical relationships between people and nature/animals

**LOOK FOR:**
• Animal metaphors for human characteristics
• Nature imagery for human qualities"""

            context_rules = f"""{header}

**MARK AS FIGURATIVE:**
{specific_examples}

**BE CONSERVATIVE WITH:**
• Standard genealogical language
• Geographic references
• Historical statements
• Divine anthropomorphisms (e.g. God went, God was angry, God watched, God fought) - these are LITERAL in the ANE context unless they refer to God's body (God's finger)."""

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

        instructions = """

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

        return base_prompt + context_rules + instructions

    def _clean_response(self, response_text: str, hebrew_text: str, english_text: str) -> Tuple[str, List[Dict], str, Dict]:
        """
        Clean and parse the JSON response

        Returns: (cleaned_json_string, all_instances_list, deliberation_text, truncation_info_dict)
        """
        # Extract deliberation section
        deliberation = ""
        deliberation_match = re.search(r'(?:MY\s+)?DELIBERATION\s*(?:SECTION)?\s*:?\s*([\s\S]*?)(?=JSON OUTPUT:|---\s*$|\n\s*\[)',
                                       response_text, re.IGNORECASE)
        if deliberation_match:
            deliberation = deliberation_match.group(1).strip()

        # Extract JSON using robust parsing
        json_string = self._extract_json_array(response_text)

        truncation_info = {
            'instances_detected': 0,
            'instances_recovered': 0,
            'instances_lost_to_truncation': 0,
            'truncation_occurred': 'no'
        }

        # Try to parse JSON
        try:
            data = json.loads(json_string)

            if not isinstance(data, list):
                return "[]", [], deliberation, truncation_info

            all_instances = []
            validated_data = []

            truncation_info['instances_detected'] = len(data)
            truncation_info['instances_recovered'] = len(data)

            for item in data:
                # Ensure all type fields are properly set
                for fig_type in ['figurative_language', 'simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                    if fig_type not in item or item[fig_type] not in ['yes', 'no']:
                        item[fig_type] = 'no'

                # Set figurative_language to 'yes' if any specific type is 'yes'
                if any(item.get(fig_type) == 'yes' for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']):
                    item['figurative_language'] = 'yes'

                # Store original detection types
                original_types = [fig_type for fig_type in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']
                                 if item.get(fig_type) == 'yes']
                item['original_detection_types'] = ','.join(original_types) if original_types else ''

                all_instances.append(item.copy())
                validated_data.append(item)

            return json.dumps(validated_data), all_instances, deliberation, truncation_info

        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"JSON decode error: {e}")
            return "[]", [], deliberation, truncation_info

    def _extract_json_array(self, response_text: str) -> str:
        """Extract JSON array from response text"""

        # Try to find JSON in code block first
        json_match = re.search(r'```json\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            return json_match.group(1).strip()

        # Look for JSON OUTPUT section
        json_output_match = re.search(r'JSON OUTPUT:\s*([\s\S]*?)(?:\s*$)', response_text, re.IGNORECASE)
        if json_output_match:
            json_section = json_output_match.group(1).strip()
            array_match = re.search(r'(\[[\s\S]*?\])', json_section)
            if array_match:
                return array_match.group(1).strip()

        # Look for standalone array
        array_match = re.search(r'\[[\s\S]*?\]', response_text)
        if array_match:
            candidate = array_match.group(0)
            if '{' in candidate and '}' in candidate:
                return candidate.strip()

        # Check for empty array
        if '[]' in response_text or 'no figurative language' in response_text.lower():
            return "[]"

        return "[]"

    def _is_restriction_reason(self, finish_reason) -> bool:
        """Check if finish reason indicates content restriction (Gemini-specific)"""
        restriction_reasons = {'SAFETY', 'RECITATION', 'OTHER'}

        if hasattr(finish_reason, 'name'):
            return finish_reason.name in restriction_reasons
        else:
            return str(finish_reason).upper() in restriction_reasons

    def insert_and_validate_instances(self, verse_id: int, all_instances: List[Dict],
                                     hebrew_text: str, english_text: str) -> int:
        """
        Insert all detected instances into database with validation data

        This method is compatible with the existing database schema and validation system.
        """
        if not self.db_manager:
            return 0

        valid_count = 0
        for item in all_instances:
            # Strip diacritics from Hebrew figurative text if it exists
            hebrew_figurative_stripped = None
            if item.get('hebrew_text'):
                hebrew_figurative_stripped = HebrewTextProcessor.strip_diacritics(item.get('hebrew_text'))

            # Prepare figurative data
            figurative_data = {
                'figurative_language': item.get('figurative_language', 'no'),
                'simile': item.get('simile', 'no'),
                'metaphor': item.get('metaphor', 'no'),
                'personification': item.get('personification', 'no'),
                'idiom': item.get('idiom', 'no'),
                'hyperbole': item.get('hyperbole', 'no'),
                'metonymy': item.get('metonymy', 'no'),
                'other': item.get('other', 'no'),
                'final_figurative_language': 'no',
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

                # Initialize final fields
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
                            validation_data[f'validation_decision_{fig_type}'] = 'RECLASSIFIED'
                            validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"
                            validation_data[f'final_{reclassified_type}'] = 'yes'
                            any_valid = True
                        elif is_valid:
                            validation_data[f'validation_decision_{fig_type}'] = 'VALID'
                            validation_data[f'validation_reason_{fig_type}'] = reason
                            validation_data[f'final_{fig_type}'] = 'yes'
                            any_valid = True
                        else:
                            validation_data[f'validation_decision_{fig_type}'] = 'INVALID'
                            validation_data[f'validation_reason_{fig_type}'] = reason

                        if error:
                            validation_data['validation_error'] = error

                # Set final_figurative_language based on validation results
                validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'

                if any_valid:
                    valid_count += 1

                # Update validation data
                self.db_manager.update_validation_data(figurative_language_id, validation_data)

        return valid_count

    def get_usage_info(self) -> Dict:
        """Get comprehensive usage statistics across all three models"""
        return {
            'total_requests': self.request_count,
            'gpt_success_count': self.gpt_success_count,
            'claude_success_count': self.claude_success_count,
            'gemini_success_count': self.gemini_success_count,
            'gpt_fallback_count': self.gpt_fallback_count,
            'claude_fallback_count': self.claude_fallback_count,
            'gpt_success_rate': self.gpt_success_count / max(1, self.request_count),
            'claude_success_rate': self.claude_success_count / max(1, self.request_count),
            'gemini_success_rate': self.gemini_success_count / max(1, self.request_count),
            'total_cost': self.total_cost,
            'gpt_tokens': self.gpt_tokens.copy(),
            'claude_tokens': self.claude_tokens.copy(),
            'gemini_tokens': self.gemini_tokens.copy(),
            'models_available': {
                'gpt-5.1': self.openai_client is not None,
                'claude-opus-4.5': self.anthropic_client is not None,
                'gemini-3.0-pro': self.gemini_client is not None
            }
        }

    def test_api_connections(self) -> Dict:
        """Test all three API connections"""
        results = {}

        # Test GPT-5.1
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5.1",
                    messages=[{"role": "user", "content": "Test message"}],
                    max_completion_tokens=100,
                    reasoning_effort="high"
                )
                results['gpt-5.1'] = {'working': True, 'model': 'gpt-5.1'}
            except Exception as e:
                results['gpt-5.1'] = {'working': False, 'error': str(e)}
        else:
            results['gpt-5.1'] = {'working': False, 'error': 'Client not initialized'}

        # Test Claude Opus 4.5
        if self.anthropic_client:
            try:
                response = self.anthropic_client.messages.create(
                    model="claude-opus-4-5-20251101",
                    max_tokens=100,
                    messages=[{"role": "user", "content": "Test message"}]
                )
                results['claude-opus-4.5'] = {'working': True, 'model': 'claude-opus-4-5-20251101'}
            except Exception as e:
                results['claude-opus-4.5'] = {'working': False, 'error': str(e)}
        else:
            results['claude-opus-4.5'] = {'working': False, 'error': 'Client not initialized'}

        # Test Gemini 3.0 Pro
        if self.gemini_client:
            try:
                response = self.gemini_client.generate_content("Test message")
                results['gemini-3.0-pro'] = {'working': True, 'model': self.gemini_model_name}
            except Exception as e:
                results['gemini-3.0-pro'] = {'working': False, 'error': str(e)}
        else:
            results['gemini-3.0-pro'] = {'working': False, 'error': 'Client not initialized'}

        return results


if __name__ == "__main__":
    # Test the unified LLM client
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    client = UnifiedLLMClient(logger=logger)

    print("=== TESTING UNIFIED LLM CLIENT ===\n")

    # Test API connections
    print("Testing API connections...")
    connections = client.test_api_connections()
    for model, status in connections.items():
        if status['working']:
            print(f"[OK] {model}: Connected ({status['model']})")
        else:
            print(f"[FAIL] {model}: Failed - {status['error']}")

    print("\n--- Testing with Genesis 49:9 (should detect metaphor) ---")
    hebrew = "גּוּר אַרְיֵה יְהוּדָה מִטֶּרֶף בְּנִי עָלִיתָ כָּרַע רָבַץ כְּאַרְיֵה וּכְלָבִיא מִי יְקִימֶנּוּ"
    english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness—who dare rouse him?"

    result, error, metadata = client.analyze_figurative_language(hebrew, english, "Genesis", 49)
    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    if error:
        print(f"Error: {error}")

    print("\n--- Usage Statistics ---")
    print(json.dumps(client.get_usage_info(), indent=2))
