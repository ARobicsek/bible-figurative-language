#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two-stage metaphor validation system to reduce false positives
"""
import google.generativeai as genai
import json
import time
from typing import List, Dict, Optional, Tuple


class MetaphorValidator:
    """Stage 2 validator for metaphor detection to eliminate false positives"""

    def __init__(self, api_key: str):
        """
        Initialize the validator with Gemini API

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)

        # Use same model as main detection
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Conservative generation config for validation
        self.generation_config = {
            'temperature': 0.05,  # Very low temperature for consistency
            'top_p': 0.7,
            'top_k': 20,
            'max_output_tokens': 1024,
        }

        self.validation_count = 0

    def validate_metaphor(self,
                         hebrew_text: str,
                         english_text: str,
                         figurative_text: str,
                         explanation: str,
                         confidence: float) -> Tuple[bool, str, Optional[str]]:
        """
        Validate whether a detected metaphor is truly figurative

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation
            figurative_text: The detected figurative expression
            explanation: Original explanation from stage 1
            confidence: Original confidence score

        Returns:
            Tuple of (is_valid_metaphor: bool, reason: str, error: Optional[str])
        """

        prompt = self._create_validation_prompt(
            hebrew_text, english_text, figurative_text, explanation, confidence
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            self.validation_count += 1

            # Check for safety restrictions
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    finish_reason = candidate.finish_reason
                    if hasattr(finish_reason, 'name') and finish_reason.name in ['SAFETY', 'RECITATION', 'OTHER']:
                        return False, "Content restricted by safety filters", f"Safety restriction: {finish_reason.name}"
                    elif str(finish_reason) in ['SAFETY', 'RECITATION', 'OTHER']:
                        return False, "Content restricted by safety filters", f"Safety restriction: {finish_reason}"

            if response.text:
                # Parse the validation response
                response_text = response.text.strip()

                # Expected format: "VALID: reason" or "INVALID: reason"
                if response_text.startswith("VALID:"):
                    reason = response_text[6:].strip()
                    return True, reason, None
                elif response_text.startswith("INVALID:"):
                    reason = response_text[8:].strip()
                    return False, reason, None
                else:
                    # Fallback parsing
                    if "VALID" in response_text.upper():
                        return True, response_text, None
                    else:
                        return False, response_text, None
            else:
                return False, "No response generated", "Empty response"

        except Exception as e:
            error_msg = f"Validation API error: {str(e)}"
            return False, "API error during validation", error_msg

    def _create_validation_prompt(self,
                                 hebrew_text: str,
                                 english_text: str,
                                 figurative_text: str,
                                 explanation: str,
                                 confidence: float) -> str:
        """Create the validation prompt"""

        prompt = f"""You are a biblical Hebrew scholar conducting a FINAL VALIDATION of metaphor detection. Your task is to determine if this detected "metaphor" is genuinely figurative or if it's actually literal language.

CONTEXT:
Hebrew: {hebrew_text}
English: {english_text}

DETECTED "METAPHOR":
Text: "{figurative_text}"
Explanation: {explanation}
Original Confidence: {confidence}

🔍 CRITICAL ANALYSIS NEEDED: Distinguish between literal language and genuine metaphorical transfers across conceptual domains.

✅ ACCEPT AS VALID METAPHOR:

🔥 DIVINE ANTHROPOMORPHISM (Always metaphorical - God is incorporeal):
- God's body parts: "mighty hand", "outstretched arm", "God's shoulders", "hide My face"
- Divine physical actions: "God's sword devours", "My arrows drunk with blood"
- These are ALWAYS metaphorical since God has no literal body

🌍 CROSS-DOMAIN COMPARISONS:
- Places as other things: "Egypt = iron blast furnace" (nation as industrial equipment)
- People as animals: "Dan = lion's whelp", "stiff-necked people"
- People as objects: "descendants = stars", "Israel = vine"
- Abstract as concrete: "anger = fire", "protection = shield"

🌱 METAPHORICAL LANGUAGE TRANSFERS:
- Agricultural → Human: "first fruit of vigor" (child as harvest)
- Spatial → Moral: "turn right/left" (physical direction for spiritual deviation)
- Military → Divine: divine weapons, battles (God's warfare is metaphorical)
- Commercial → Spiritual: when economic terms describe non-economic relationships

🛑 REJECT AS LITERAL:

📜 STANDARD RELIGIOUS FORMULAS:
- "holy people" = technical covenantal status
- "I make this covenant" = legal terminology
- "signs and proofs" = standard covenant language

⚔️ HUMAN MILITARY ACTIONS (but NOT divine warfare):
- Human soldiers' actions: "defeat them", "march against"
- Literal human weapons and tactics

🏪 LITERAL COMMERCIAL/LEGAL ACTIONS:
- "honest weights" = actual trade regulation
- "pull off sandal" = actual legal ritual
- "pay wages" = literal economic transaction

📍 LITERAL GEOGRAPHIC/HISTORICAL REFERENCES:
- Actual place names and historical events
- Literal population descriptions without comparison

EXAMPLES OF VALID METAPHORS TO ACCEPT:
✅ "mighty hand of God" = divine power (God has no literal hand)
✅ "sword devours flesh" = divine judgment (God's sword is metaphorical)
✅ "Egypt = iron blast furnace" = nation compared to industrial equipment
✅ "first fruit of vigor" = child compared to agricultural harvest
✅ "turn right or left" = moral deviation using spatial metaphor
✅ "arrows drunk with blood" = divine weapons (God's arrows are metaphorical)

EXAMPLES TO REJECT:
❌ "honest weights" = literal commercial regulation (no domain transfer)
❌ "we were slaves" = literal historical statement
❌ "holy people" = technical religious status (not comparative)
❌ "signs and proofs" = standard covenant terminology

RESPONSE FORMAT:
If this is a valid metaphor: "VALID: [brief reason why it crosses domains or involves divine anthropomorphism]"
If this is NOT a metaphor: "INVALID: [specific reason - technical term/literal action/standard formula/etc.]"

Focus on identifying genuine cross-domain comparisons and divine anthropomorphism while filtering out technical religious terminology.

VALIDATION:"""

        return prompt

    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            'total_validations': self.validation_count
        }


def test_metaphor_validator():
    """Test the metaphor validator with known cases"""

    # API key (same as main system)
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    validator = MetaphorValidator(api_key)

    print("=== TESTING METAPHOR VALIDATOR ===")

    # Test cases - known false positives from errors.md
    false_positive_cases = [
        {
            "name": "Honest Weights (should be INVALID)",
            "hebrew": "אֶ֣בֶן שְׁלֵמָ֤ה וָצֶ֙דֶק֙",
            "english": "completely honest weights",
            "figurative_text": "completely honest weights",
            "explanation": "Weights are used metaphorically to represent honesty and integrity",
            "confidence": 0.8
        },
        {
            "name": "Historical Statement (should be INVALID)",
            "hebrew": "עֲבָדִ֛ים הָיִ֥ינוּ לְפַרְעֹ֖ה בְּמִצְרָ֑יִם",
            "english": "We were slaves to Pharaoh in Egypt",
            "figurative_text": "We were slaves to Pharaoh",
            "explanation": "Slavery represents oppression metaphorically",
            "confidence": 0.75
        },
        {
            "name": "Legal Ritual (should be INVALID)",
            "hebrew": "וְחָלְצָ֤ה נַעֲלוֹ֙ מֵעַ֣ל רַגְל֔וֹ",
            "english": "pull the sandal off his foot",
            "figurative_text": "pull the sandal off his foot",
            "explanation": "Removing sandal represents legal relinquishment",
            "confidence": 0.8
        }
    ]

    # Test case - known true positive
    true_positive_cases = [
        {
            "name": "Fire and Wrath (should be VALID)",
            "hebrew": "אֵשׁ קָדְחָה בְאַפִּי",
            "english": "a fire has flared in My wrath",
            "figurative_text": "a fire has flared in My wrath",
            "explanation": "God's anger is equated with consuming fire",
            "confidence": 0.95
        }
    ]

    all_cases = false_positive_cases + true_positive_cases

    for case in all_cases:
        print(f"\n--- {case['name']} ---")
        print(f"Text: {case['figurative_text']}")

        is_valid, reason, error = validator.validate_metaphor(
            case['hebrew'],
            case['english'],
            case['figurative_text'],
            case['explanation'],
            case['confidence']
        )

        print(f"Validation Result: {'VALID' if is_valid else 'INVALID'}")
        print(f"Reason: {reason}")
        if error:
            print(f"Error: {error}")

    stats = validator.get_validation_stats()
    print(f"\nValidation Stats: {stats}")


if __name__ == "__main__":
    test_metaphor_validator()