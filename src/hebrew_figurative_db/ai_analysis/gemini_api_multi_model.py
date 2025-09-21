#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-model Gemini API with Gemini 2.5 Flash → Gemini 1.5 Flash fallback
Context-aware conservative analysis addressing false negative issues
"""
import google.generativeai as genai
import json
import time
from typing import List, Dict, Optional, Tuple
import re


class MultiModelGeminiClient:
    """Multi-model Gemini API client with context-aware conservative analysis"""

    def __init__(self, api_key: str):
        """
        Initialize multi-model Gemini API client

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)

        # Primary model: Gemini 2.5 Flash
        try:
            self.primary_model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.primary_model_name = 'gemini-2.0-flash-exp'
        except Exception:
            # Fallback if 2.5 not available
            self.primary_model = genai.GenerativeModel('gemini-1.5-flash')
            self.primary_model_name = 'gemini-1.5-flash'

        # Fallback model: Gemini 1.5 Flash
        self.fallback_model = genai.GenerativeModel('gemini-1.5-flash')
        self.fallback_model_name = 'gemini-1.5-flash'

        # Generation configs
        self.primary_config = {
            'temperature': 0.15,  # Slightly higher for better detection
            'top_p': 0.8,
            'top_k': 25,
            'max_output_tokens': 2048,
        }

        self.fallback_config = {
            'temperature': 0.10,  # Conservative for fallback
            'top_p': 0.7,
            'top_k': 20,
            'max_output_tokens': 2048,
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
            # Fallback to secondary model
            print(f"Primary model restricted ({error}), trying fallback...")
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
        else:
            self.primary_success_count += 1
            metadata['fallback_used'] = False

        self.request_count += 1
        return result, error, metadata

    def _try_model_analysis(self, model, config, model_name: str, hebrew_text: str,
                           english_text: str, context: str) -> Tuple[str, Optional[str], Dict]:
        """Try analysis with a specific model"""

        prompt = self._create_context_aware_prompt(hebrew_text, english_text, context)
        metadata = {'model_used': model_name, 'context': context}

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
            if response.text:
                cleaned_response = self._clean_response(response.text.strip())
                return cleaned_response, None, metadata
            else:
                return "[]", "No response text generated", metadata

        except Exception as e:
            error_msg = f"{model_name} error: {str(e)}"
            print(f"API error (non-critical): {error_msg}")
            return "[]", error_msg, metadata

    def _determine_text_context(self, book: str, chapter: int) -> str:
        """Determine text context for appropriate prompting strategy"""

        # Genesis Creation Narratives (most conservative)
        if book.lower() == 'genesis' and chapter in [1, 2, 3]:
            return 'creation_narrative'

        # Poetic/Blessing texts (balanced approach)
        elif ((book.lower() == 'genesis' and chapter == 49) or  # Jacob's blessings
              (book.lower() == 'deuteronomy' and chapter == 32) or  # Song of Moses
              (book.lower() == 'deuteronomy' and chapter == 33)):  # Moses' blessing
            return 'poetic_blessing'

        # Legal/Ceremonial texts (moderate conservative)
        elif book.lower() in ['leviticus', 'numbers']:
            return 'legal_ceremonial'

        # Narrative texts (standard approach)
        else:
            return 'narrative'

    def _create_context_aware_prompt(self, hebrew_text: str, english_text: str, context: str) -> str:
        """Create context-aware prompt based on text type"""

        base_prompt = f"""You are a biblical Hebrew scholar analyzing this text for figurative language.

Hebrew: {hebrew_text}
English: {english_text}

"""

        if context == 'creation_narrative':
            # Ultra-conservative for Genesis 1-3
            context_rules = """🚨 **CREATION NARRATIVE - ULTRA CONSERVATIVE** 🚨

**NEVER MARK AS FIGURATIVE:**
• "unformed and void", "darkness over surface" = LITERAL primordial descriptions
• "lights for signs", "earth brought forth" = LITERAL creation functions
• Divine actions: spoke, blessed, created, made, saw = STANDARD creation verbs
• "breath of life", "living being" = TECHNICAL theological terms
• Geographic descriptions, procedural language

**ONLY MARK IF ABSOLUTELY CLEAR:**
• Obvious cross-domain metaphors
• Clear anthropomorphism beyond standard creation actions"""

        elif context == 'poetic_blessing':
            # Balanced approach for poetic texts
            context_rules = """📜 **POETIC BLESSING TEXT - BALANCED DETECTION** 📜

**MARK AS FIGURATIVE:**
• Tribal characterizations using animals: "lion", "wolf", "serpent", "eagle"
• Cross-domain comparisons: "unstable as water", "like a hind let loose"
• Divine anthropomorphism: emotions, human actions attributed to God
• Clear metaphorical relationships between people and nature/animals

**BE CONSERVATIVE WITH:**
• Standard genealogical language
• Geographic references
• Historical statements

**LOOK FOR:**
• Animal metaphors for human characteristics
• Nature imagery for human qualities
• Divine emotions and actions"""

        elif context == 'legal_ceremonial':
            # Moderate conservative for legal texts
            context_rules = """⚖️ **LEGAL/CEREMONIAL TEXT - MODERATE CONSERVATIVE** ⚖️

**NEVER MARK AS FIGURATIVE:**
• Technical religious terms: holy, clean, offering, covenant
• Procedural instructions and ritual descriptions
• Legal formulations and standard phrases

**MARK AS FIGURATIVE:**
• Clear cross-domain metaphors
• Divine anthropomorphism (emotions, human characteristics)
• Obvious similes with "like/as" for unlike things"""

        else:  # narrative
            # Standard conservative approach
            context_rules = """📖 **NARRATIVE TEXT - STANDARD CONSERVATIVE** 📖

**BE CONSERVATIVE WITH:**
• Standard narrative language
• Character actions and dialogue
• Historical and genealogical information

**MARK AS FIGURATIVE:**
• Clear metaphors with cross-domain comparisons
• Personification of non-human entities
• Divine anthropomorphism
• Obvious similes"""

        return base_prompt + context_rules + """

**JSON OUTPUT (only if genuinely figurative):**
[{"type": "metaphor/personification/simile", "hebrew_text": "Hebrew phrase", "english_text": "English phrase", "explanation": "Brief explanation", "vehicle_level_1": "nature/human/divine/abstract", "vehicle_level_2": "specific", "tenor_level_1": "God/people/covenant", "tenor_level_2": "specific", "confidence": 0.7-1.0, "speaker": "God/Moses/Narrator", "purpose": "brief purpose"}]

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
        restriction_reasons = ['SAFETY', 'RECITATION', 'OTHER']

        if hasattr(finish_reason, 'name'):
            return finish_reason.name in restriction_reasons
        else:
            return str(finish_reason) in restriction_reasons

    def _clean_response(self, response_text: str) -> str:
        """Clean and validate JSON response"""
        # Remove markdown wrapper if present
        response_text = re.sub(r'^```json\s*', '', response_text)
        response_text = re.sub(r'\s*```$', '', response_text)

        # Try to parse as JSON to validate
        try:
            json.loads(response_text)
            return response_text
        except json.JSONDecodeError:
            # If not valid JSON, return empty array
            print(f"Invalid JSON response: {response_text}")
            return "[]"

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
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
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