#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conservative Gemini API integration with improved false positive filtering
Based on feedback to reduce over-detection of figurative language
"""
import google.generativeai as genai
import json
import time
from typing import List, Dict, Optional


class GeminiAPIClient:
    """Conservative Gemini API client for figurative language analysis"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini API client

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)

        # Use Gemini 2.5 Flash primary with 1.5 Flash fallback
        try:
            self.model = genai.GenerativeModel('gemini-2.5-flash')
            self.model_name = 'gemini-2.5-flash'
        except Exception:
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.model_name = 'gemini-1.5-flash'

        # Generation config for consistent JSON output
        self.generation_config = {
            'temperature': 0.05,  # Very low temperature for conservative analysis
            'top_p': 0.7,
            'top_k': 20,
            'max_output_tokens': 2048,
        }

        # Usage tracking
        self.request_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def analyze_figurative_language(self, hebrew_text: str, english_text: str) -> tuple[str, Optional[str]]:
        """
        Analyze Hebrew text for figurative language using conservative Gemini approach

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation

        Returns:
            Tuple of (JSON string with analysis results, error message if restricted)
        """
        prompt = self._create_conservative_prompt(hebrew_text, english_text)

        try:
            # Make API call to Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Track usage
            self.request_count += 1
            if hasattr(response, 'usage_metadata'):
                self.total_input_tokens += getattr(response.usage_metadata, 'prompt_token_count', 0)
                self.total_output_tokens += getattr(response.usage_metadata, 'candidates_token_count', 0)

            # Check for safety restrictions or blocked content
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    # Check if content was blocked by safety filters or other restrictions
                    finish_reason = candidate.finish_reason
                    if hasattr(finish_reason, 'name') and finish_reason.name in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Content restricted: {finish_reason.name}"
                        return "[]", error_msg
                    elif str(finish_reason) in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Content restricted: {finish_reason}"
                        return "[]", error_msg

            # Extract text from response
            if response.text:
                return response.text.strip(), None
            else:
                return "[]", "No response text generated"  # Empty result

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            print(error_msg)
            return "[]", error_msg  # Return empty on error

    def _create_conservative_prompt(self, hebrew_text: str, english_text: str) -> str:
        """Create conservative analysis prompt prioritizing exclusions"""

        prompt = f"""You are a biblical Hebrew scholar. Analyze this text for figurative language using EXTREME CAUTION to avoid false positives.

Hebrew: {hebrew_text}
English: {english_text}

🚨 **CRITICAL: DO NOT MARK AS FIGURATIVE** 🚨

**CREATION NARRATIVES (Genesis 1-3) - BE EXTREMELY CONSERVATIVE:**
• "unformed and void" = LITERAL primordial state (NOT metaphor for chaos)
• "darkness over surface of deep" = LITERAL pre-creation description
• "lights" and "signs for times" = LITERAL celestial functions
• "earth brought forth" = LITERAL creation action (NOT personification)
• "breath of life" = TECHNICAL theological term (NOT metaphor)
• "living being" = TECHNICAL term for creature (NOT metaphor)
• "dominate/rule" by celestial bodies = LITERAL functional descriptions
• "flow from ground" = LITERAL irrigation (NOT figurative)
• Divine creating, speaking, blessing = STANDARD creation actions

**NEVER MARK AS FIGURATIVE:**
• Standard divine actions: spoke, blessed, created, made, saw, heard
• Technical religious terms: holy, clean, offering, covenant
• Historical statements: "we were slaves", "brought out of Egypt"
• Character actions with literal agency: "serpent duped me"
• Relationship descriptions: "enmity between you and woman"
• Physical descriptions: "delight to the eyes"
• Straightforward adjectives: "good land", "great nation"
• Geographic/physical descriptions: wilderness, mountain, land
• Standard biblical narrative language
• Procedural language using "as/like"

**BALANCED APPROACH:**
Avoid false positives but catch GENUINE figurative language.

📋 **MARK AS FIGURATIVE IF CLEARLY:**

**CLEAR METAPHORS (different domains compared):**
• "God is shepherd" = divine ↔ pastoral (CLEAR cross-domain)
• "mighty hand of God" = divine power ↔ human body part (CLEAR)
• "Israel is vine" = nation ↔ plant (CLEAR cross-domain)
• "fire is kindled in anger" = emotion ↔ physical fire (CLEAR)

**CLEAR PERSONIFICATION (non-human acting human):**
• "mountains sing" = geography ↔ human action (CLEAR)
• "earth reeled" = planet ↔ human movement (CLEAR)
• Divine emotions: "God angry", "God jealous", "God regretted" (CLEAR anthropomorphism)
• "land vomited out" = geography ↔ human action (CLEAR)

**CLEAR SIMILES (unlike things with "like/as"):**
• "like an eagle" = person ↔ bird (CLEAR unlike comparison)
• "numerous as stars" = people ↔ celestial (CLEAR unlike)
• "like consuming fire" = divine presence ↔ fire (CLEAR)

**BORDERLINE CASES - MARK IF CONFIDENT:**
• Divine anthropomorphic actions beyond standard creation/blessing
• Clear cross-domain imagery outside Creation narratives

**PRIORITIZE:** Genuine detection while avoiding Genesis 1-3 false positives.

**JSON OUTPUT (only if genuinely figurative):**
[{{"type": "metaphor/personification/simile", "hebrew_text": "Hebrew phrase", "english_text": "English phrase", "explanation": "Brief explanation", "vehicle_level_1": "nature/human/divine/abstract", "vehicle_level_2": "specific", "tenor_level_1": "God/people/covenant", "tenor_level_2": "specific", "confidence": 0.7-1.0, "speaker": "God/Moses/Narrator", "purpose": "brief purpose"}}]

If no figurative language found: []

Analysis:"""

        return prompt

    def get_usage_info(self) -> Dict:
        """Get current usage statistics"""
        return {
            'request_count': self.request_count,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens
        }

    def test_api_connection(self) -> bool:
        """Test if API connection is working"""
        try:
            response = self.model.generate_content("Test message", generation_config=self.generation_config)
            return response.text is not None
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False


if __name__ == "__main__":
    # Test with Genesis false positive examples
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    print("=== TESTING CONSERVATIVE GEMINI API ===")

    test_cases = [
        {
            "name": "Genesis 1:2 - should be LITERAL",
            "hebrew": "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם",
            "english": "Now the earth was unformed and void, and darkness was over the surface of the deep"
        },
        {
            "name": "Genesis 1:14 - should be LITERAL",
            "hebrew": "וְהָיוּ לְאֹתֹת וּלְמוֹעֲדִים",
            "english": "and let them be for signs and for seasons"
        },
        {
            "name": "Genesis 3:13 - should be LITERAL",
            "hebrew": "הַנָּחָשׁ הִשִּׁיאַנִי",
            "english": "The serpent duped me"
        }
    ]

    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        result, error = client.analyze_figurative_language(case['hebrew'], case['english'])
        print(f"Result: {result}")
        if error:
            print(f"Error: {error}")