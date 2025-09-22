#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two-stage metaphor validation system to reduce false positives
"""
import google.generativeai as genai
import os
import json
import time
from typing import List, Dict, Optional, Tuple


class MetaphorValidator:
    """Stage 2 validator for metaphor detection to eliminate false positives"""

    def __init__(self, api_key: str, db_manager=None, logger=None):
        """
        Initialize the validator with Gemini API

        Args:
            api_key: Gemini API key
            db_manager: DatabaseManager instance for logging deliberations
            logger: Logger instance
        """
        self.api_key = api_key
        self.db_manager = db_manager
        self.logger = logger
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
        self.type_validation_count = 0

    def validate_figurative_language(self,
                                   fig_type: str,
                                   hebrew_text: str,
                                   english_text: str,
                                   figurative_text: str,
                                   explanation: str,
                                   confidence: float,
                                   figurative_language_id: Optional[int] = None) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Validate whether detected figurative language is truly figurative

        Args:
            fig_type: Type of figurative language (metaphor, simile, etc.)
            hebrew_text: Original Hebrew text
            english_text: English translation
            figurative_text: The detected figurative expression
            explanation: Original explanation from stage 1
            confidence: Original confidence score
            figurative_language_id: ID of the figurative_language record for logging

        Returns:
            Tuple of (is_valid_figurative: bool, reason: str, error: Optional[str], corrected_type: Optional[str])
        """

        prompt = self._create_validation_prompt(
            fig_type, hebrew_text, english_text, figurative_text, explanation, confidence
        )

        # Initialize validation data for logging
        validation_data = {
            'validation_response': None,
            'validation_decision': None,
            'validation_reason': None,
            'validation_error': None
        }

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
                        validation_data['validation_decision'] = 'INVALID'
                        validation_data['validation_reason'] = "Content restricted by safety filters"
                        validation_data['validation_error'] = f"Safety restriction: {finish_reason.name}"
                        self._log_validation_data(figurative_language_id, validation_data)
                        return False, "Content restricted by safety filters", f"Safety restriction: {finish_reason.name}", None
                    elif str(finish_reason) in ['SAFETY', 'RECITATION', 'OTHER']:
                        validation_data['validation_decision'] = 'INVALID'
                        validation_data['validation_reason'] = "Content restricted by safety filters"
                        validation_data['validation_error'] = f"Safety restriction: {finish_reason}"
                        self._log_validation_data(figurative_language_id, validation_data)
                        return False, "Content restricted by safety filters", f"Safety restriction: {finish_reason}", None

            if response.text:
                # Parse the validation response
                response_text = response.text.strip()
                validation_data['validation_response'] = response_text

                # Expected format: "VALID: reason" or "INVALID: reason" or "RECLASSIFY: type - reason"
                if response_text.startswith("VALID:"):
                    reason = response_text[6:].strip()
                    validation_data['validation_decision'] = 'VALID'
                    validation_data['validation_reason'] = reason
                    self._log_validation_data(figurative_language_id, validation_data)
                    return True, reason, None, None
                elif response_text.startswith("INVALID:"):
                    reason = response_text[8:].strip()
                    validation_data['validation_decision'] = 'INVALID'
                    validation_data['validation_reason'] = reason
                    self._log_validation_data(figurative_language_id, validation_data)
                    return False, reason, None, None
                elif response_text.startswith("RECLASSIFY:"):
                    # Handles "RECLASSIFY: type - reason" or "RECLASSIFY: type"
                    content = response_text[11:].strip()
                    validation_data['validation_decision'] = 'RECLASSIFY'
                    
                    parts = content.split(" - ", 1)
                    potential_type = parts[0].strip().lower().rstrip('.:')
                    allowed_types = {'metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other'}

                    if potential_type in allowed_types:
                        corrected_type = potential_type
                        reason = parts[1].strip() if len(parts) > 1 else f"Reclassified to {corrected_type}"
                    else:
                        corrected_type = "other"
                        reason = content

                    validation_data['validation_reason'] = reason
                    self._log_validation_data(figurative_language_id, validation_data)
                    return True, reason, None, corrected_type
                else:
                    # Fallback parsing
                    if "RECLASSIFY" in response_text.upper():
                        validation_data['validation_decision'] = 'RECLASSIFY'
                        validation_data['validation_reason'] = response_text
                        self._log_validation_data(figurative_language_id, validation_data)
                        return True, response_text, None, "personification"
                    elif "VALID" in response_text.upper():
                        validation_data['validation_decision'] = 'VALID'
                        validation_data['validation_reason'] = response_text
                        self._log_validation_data(figurative_language_id, validation_data)
                        return True, response_text, None, None
                    else:
                        validation_data['validation_decision'] = 'INVALID'
                        validation_data['validation_reason'] = response_text
                        self._log_validation_data(figurative_language_id, validation_data)
                        return False, response_text, None, None
            else:
                validation_data['validation_decision'] = 'INVALID'
                validation_data['validation_reason'] = "No response generated"
                validation_data['validation_error'] = "Empty response"
                self._log_validation_data(figurative_language_id, validation_data)
                return False, "No response generated", "Empty response", None

        except Exception as e:
            error_msg = f"Validation API error: {str(e)}"
            if self.logger:
                self.logger.error(f"Validation API error for figurative_language_id {figurative_language_id}: {e}", exc_info=True)
            validation_data['validation_decision'] = 'INVALID'
            validation_data['validation_reason'] = "API error during validation"
            validation_data['validation_error'] = error_msg
            self._log_validation_data(figurative_language_id, validation_data)
            return False, "API error during validation", error_msg, None

    def validate_figurative_type(self,
                                fig_type: str,
                                hebrew_text: str,
                                english_text: str,
                                figurative_text: str,
                                explanation: str,
                                confidence: float) -> Tuple[bool, str, Optional[str], Optional[str]]:
        """
        Validate whether a specific figurative language type is correct

        Args:
            fig_type: Type of figurative language (metaphor, simile, etc.)
            hebrew_text: Original Hebrew text
            english_text: English translation
            figurative_text: The detected figurative expression
            explanation: Original explanation from stage 1
            confidence: Original confidence score

        Returns:
            Tuple of (is_valid_type: bool, reason: str, error: Optional[str], reclassified_type: Optional[str])
        """

        prompt = self._create_type_validation_prompt(
            fig_type, hebrew_text, english_text, figurative_text, explanation, confidence
        )

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            self.type_validation_count += 1

            # Check for safety restrictions
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    finish_reason = candidate.finish_reason
                    if hasattr(finish_reason, 'name') and finish_reason.name in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Safety restriction: {finish_reason.name}"
                        if self.logger:
                            self.logger.warning(f"Content restricted in type validation for '{figurative_text}'. Reason: {finish_reason.name}")
                        return False, "Content restricted by safety filters", error_msg, None
                    elif str(finish_reason) in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Safety restriction: {finish_reason}"
                        if self.logger:
                            self.logger.warning(f"Content restricted in type validation for '{figurative_text}'. Reason: {finish_reason}")
                        return False, "Content restricted by safety filters", error_msg, None

            if response.text:
                # Parse the validation response
                response_text = response.text.strip()

                # Expected format: "VALID: reason" or "INVALID: reason" or "RECLASSIFY: new_type - reason"
                if response_text.startswith("VALID:"):
                    reason = response_text[6:].strip()
                    return True, reason, None, None
                elif response_text.startswith("INVALID:"):
                    reason = response_text[8:].strip()
                    return False, reason, None, None
                elif response_text.startswith("RECLASSIFY:"):
                    # Parse "RECLASSIFY: new_type - reason" or "RECLASSIFY: new_type"
                    content = response_text[11:].strip()
                    parts = content.split(" - ", 1)
                    potential_type = parts[0].strip().lower().rstrip('.:')
                    allowed_types = {'simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other'}

                    if potential_type in allowed_types:
                        reclassified_type = potential_type
                        reason = parts[1].strip() if len(parts) > 1 else f"Reclassified from {fig_type} to {reclassified_type}"
                    else:
                        reclassified_type = "other"
                        reason = content

                    return False, reason, None, reclassified_type
                else:
                    # Fallback parsing
                    if "RECLASSIFY" in response_text.upper():
                        return False, response_text, None, "other"
                    elif "VALID" in response_text.upper():
                        return True, response_text, None, None
                    else:
                        return False, response_text, None, None
            else:
                return False, "No response generated", "Empty response", None

        except Exception as e:
            error_msg = f"Type validation API error: {str(e)}"
            if self.logger:
                self.logger.error(f"Type validation API error for '{figurative_text}': {e}", exc_info=True)
            return False, "API error during type validation", error_msg, None

    def _create_type_validation_prompt(self,
                                      fig_type: str,
                                      hebrew_text: str,
                                      english_text: str,
                                      figurative_text: str,
                                      explanation: str,
                                      confidence: float) -> str:
        """Create a validation prompt for a specific figurative language type"""

        prompt = f"""You are a biblical Hebrew scholar conducting validation of a specific figurative language type. Your task is to determine if this text is genuinely a "{fig_type.upper()}".

CONTEXT:
Hebrew: {hebrew_text}
English: {english_text}

DETECTED "{fig_type.upper()}":
Text: "{figurative_text}"
Explanation: {explanation}
Original Confidence: {confidence}

VALIDATION TASK: Is this text genuinely a {fig_type}?

TYPE-SPECIFIC VALIDATION RULES:

{self._get_type_specific_rules(fig_type)}

RESPONSE FORMAT:
If this is a valid {fig_type}: "VALID: [brief reason why it's genuinely a {fig_type}]"
If this is NOT a {fig_type} but IS another type: "RECLASSIFY: [correct_type] - [reason why it should be reclassified]"
If this is NOT figurative at all: "INVALID: [specific reason why it's not figurative]"

VALIDATION:"""

        return prompt

    def _get_type_specific_rules(self, fig_type: str) -> str:
        """Get type-specific validation rules"""

        if fig_type == 'metaphor':
            return """
METAPHOR VALIDATION:
- ACCEPT: Cross-domain comparisons where A is described as B (Egypt = iron furnace)
- ACCEPT: Divine body parts (God's hand, arm, face) - God is incorporeal
- ACCEPT: Abstract concepts described as concrete (anger = fire)
- REJECT: Literal comparisons or standard biblical terminology
- REJECT: Historical precedents or procedural language
"""

        elif fig_type == 'simile':
            return """
SIMILE VALIDATION:
- ACCEPT: Cross-domain comparisons using "like/as" for unlike things (like a lion)
- ACCEPT: Figurative quantity comparisons (as the stars of heaven)
- REJECT: Literal behavioral comparisons (as you do, like your brother did)
- REJECT: Role/function comparisons (a prophet like myself)
- REJECT: Historical precedent references (as the Edomites did)
"""

        elif fig_type == 'personification':
            return """
PERSONIFICATION VALIDATION:
- ACCEPT: Abstract concepts acting as agents (dread and fear...put upon)
- ACCEPT: Natural phenomena acting human-like (mountains skipped, sea fled)
- ACCEPT: Objects given human characteristics
- REJECT: Divine actions (God is a person in ANE context)
- REJECT: Standard anthropomorphic descriptions
"""

        elif fig_type == 'idiom':
            return """
IDIOM VALIDATION:
- ACCEPT: Set biblical phrases with non-literal meaning
- ACCEPT: Cultural expressions with meaning beyond literal words
- REJECT: Standard terminology or literal expressions
- REJECT: Technical religious terms
"""

        elif fig_type == 'hyperbole':
            return """
HYPERBOLE VALIDATION:
- ACCEPT: Deliberate exaggeration for effect
- ACCEPT: Impossible or extreme claims for emphasis
- REJECT: Standard biblical descriptions
- REJECT: Literal divine actions or judgments
"""

        elif fig_type == 'metonymy':
            return """
METONYMY VALIDATION:
- ACCEPT: Substitution of associated terms (crown for kingship)
- ACCEPT: Part for whole or whole for part relationships
- ACCEPT: Synechdoce as metonymy
- REJECT: Literal references to actual objects
- REJECT: Standard terminology
"""

        else:  # 'other'
            return """
OTHER FIGURATIVE LANGUAGE VALIDATION:
- ACCEPT: Genuine figurative language not fitting other categories
- ACCEPT: Complex figurative expressions
- REJECT: Literal language or standard terminology
"""

    def _create_validation_prompt(self,
                                 fig_type: str,
                                 hebrew_text: str,
                                 english_text: str,
                                 figurative_text: str,
                                 explanation: str,
                                 confidence: float) -> str:
        """Create the validation prompt"""

        prompt = f"""You are a biblical Hebrew scholar conducting a FINAL VALIDATION of figurative language detection. Your task is to determine if this detected "{fig_type}" is genuinely figurative or if it's actually literal language, and whether the type classification is correct.

CONTEXT:
Hebrew: {hebrew_text}
English: {english_text}

DETECTED "{fig_type.upper()}":
Text: "{figurative_text}"
Explanation: {explanation}
Original Confidence: {confidence}

[ANALYSIS] CRITICAL ANALYSIS NEEDED:
1. Distinguish between literal language and genuine figurative language
2. For SIMILES: Determine if using "as/like" for literal comparison vs. figurative comparison
3. For METAPHORS vs PERSONIFICATION: Determine correct classification
4. For OTHER TYPES: Is this genuinely figurative or standard biblical terminology? We consider DIVINE ANTHROPOMORPHISM to be LITERAL in the ANE context. If it's not figurative, consider it invalid.

[ACCEPT] ACCEPT AS VALID FIGURATIVE LANGUAGE:

[DIVINE] DIVINE ANTHROPOMORPHISM (Always metaphorical - God is incorporeal):
- In most respects treat God as any other human-like figure - God's actions (going, speaking, blessing, smiting, cursing, etc.) are LITERAL in the ANE context. An exception are God's body parts: "mighty hand", "outstretched arm", "God's shoulders", "hide My face". Since God does not have a body, these are metaphors.

[CROSS-DOMAIN] CROSS-DOMAIN COMPARISONS:
- Places as other things: "Egypt = iron blast furnace" (nation as industrial equipment)
- People as animals: "Dan = lion's whelp", "stiff-necked people"
- People as objects: "descendants = stars", "Israel = vine"
- Abstract as concrete: "anger = fire", "protection = shield"

[TRANSFERS] METAPHORICAL LANGUAGE TRANSFERS:
- Agricultural → Human: "first fruit of vigor" (child as harvest)
- Spatial → Moral: "turn right/left" (physical direction for spiritual deviation)
- Military → Divine: divine weapons, battles (God's warfare is metaphorical)
- Commercial → Spiritual: when economic terms describe non-economic relationships

[SIMILE] SIMILE-SPECIFIC VALIDATION:
- remember that a simile is a figurative comparison of two unlike things using "like" or "as" to create a new, imaginative meaning.
- ACCEPT: "like a lion" (animal comparison), "as the stars of heaven" (quantity comparison)
- REJECT: "as the Edomites did for me" (literal historical precedent, not figurative comparison)
- REJECT: "do X as you do Y" (instructional comparison, not figurative)
- REJECT: "die as your brother Aaron died" (manner description, not figurative)
- REJECT: "like all his fellow Levites" (comparison to a peer group, not figurative)
- REJECT: "a prophet like myself" (comparison of role/function, not figurative)
- REJECT: "according to the blessing" (a proportional/conditional statement, not a figurative comparison)
- REJECT: "pour it out like water" (literal, descriptive comparison of a physical action's outcome - both things are liquids being poured)
- REJECT: "eat it...just like the gazelle and the deer" (comparison of a permitted action/behavior, not figurative)

[REJECT] REJECT AS LITERAL:

[HISTORICAL] LITERAL HISTORICAL REFERENCES:
- "as the descendants of Esau did for me" = literal historical precedent (NOT figurative)
- "as the Moabites did" = actual past events being referenced literally
- Any reference to what specific peoples actually did historically

[RELIGIOUS and DIVINE] STANDARD BIBLICAL DIVINE ACTIONS & ATTRIBUTES (NOT figurative):
- God's actions are LITERAL in the ANE context, but since God is incorporeal, body parts are metaphorical.
- God taking actions like speaking, going, blessing, smiting, cursing, battling, watching, remembering, making covenants, etc. are all LITERAL in the ANE context.
- Note that if God's actions are described METAPHORICALLY by likening God to something God is NOT (e.g. "God is a man of battle", "God is a rock"), these are metaphors.
- God's attributes like "compassionate", "great", "holy" are standard descriptors (NOT figurative).
- "great nation" = standard political descriptor (NOT metaphorical)
- "signs and proofs" = standard covenant language

[MILITARY] LITERAL MILITARY ACTIONS & TERMS (NOT figurative):
- Human soldiers' actions: "defeat them", "march against", "wiping out", "conquered"
- Military terminology: "shock-troops" (חֲלוּצִים), "warriors" (בְּנֵי־חָֽיִל), "vanguard", "armed men"
- Literal human weapons and tactics
- Historical conquest descriptions: "the Caphtorim wiped them out"
- Actual tribal displacements and military campaigns

[COMMERCIAL] LITERAL COMMERCIAL/LEGAL ACTIONS:
- "honest weights" = actual trade regulation
- "pull off sandal" = actual legal ritual
- "pay wages" = literal economic transaction

[PROCEDURAL] LITERAL PROCEDURAL/TECHNICAL TERMS (NOT figurative):
- בְּמַסֹּת (trials/tests) = literal plagues and trials in Egypt (NOT metaphorical)
- Technical ritual terms and procedural language
- Legal formulations and covenant procedures

[DIVINE JUDGMENT] LITERAL DIVINE JUDGMENT ACTIONS (NOT figurative):
- "scatter you among the peoples" = literal exile/diaspora (standard ANE practice)
- "drive you out" = literal forced deportation (NOT metaphorical)
- "wipe out/destroy" = literal divine judgment (NOT metaphorical)
- All covenant curses and judgments = literal consequences, not metaphorical

[QUANTITATIVE] LITERAL NUMERICAL/QUANTITATIVE DESCRIPTIONS (NOT figurative):
- "scant few" = literal numerical description (NOT metaphorical)
- "many/few" = quantitative, not metaphorical
- "great/small" when describing size/quantity = literal measurement

[THEOPHANIC] LITERAL DIVINE MANIFESTATION (NOT figurative):
- "mountain ablaze with fire" = literal theophanic manifestation (NOT personification)
- Divine fire, clouds, thunder = literal divine presence in ANE context
- "sculptured image" = literal idolatry prohibition (NOT metaphorical)

[GEOGRAPHIC] LITERAL GEOGRAPHIC/HISTORICAL REFERENCES:
- Actual place names and historical events
- Literal population descriptions without comparison
- "this great wilderness" = geographic location (NOT metaphorical)

EXAMPLES OF VALID METAPHORS TO ACCEPT:
[VALID] "sword devours flesh" = a sword does not literally devour flesh
[VALID] "Egypt = iron blast furnace" = Egypt was not a literal furnace
[VALID] "first fruit of vigor" = a child is not literally fruit
[VALID] "turn right or left" = moral deviation using spatial metaphor
[VALID] "arrows drunk with blood" = arrows don't litrally get drunk

EXAMPLES OF RECLASSIFICATION:
[RECLASSIFY] "dread and fear...put upon peoples" = PERSONIFICATION (abstract concepts acting as agents)

RESPONSE FORMAT:
If this is valid figurative language as classified: "VALID: [brief reason why it's genuinely figurative]"
If this is NOT figurative: "INVALID: [specific reason - technical term/literal action/standard formula/historical reference/etc.]"
If this is figurative but incorrectly classified: "RECLASSIFY: [correct_type] - [reason why it should be reclassified]"

RECLASSIFICATION GUIDELINES:

[METAPHOR] vs [PERSONIFICATION] - KEY DISTINCTIONS:

METAPHOR (cross-domain comparison or divine body parts):
- God's body parts: "mighty hand", "outstretched arm", "hide My face" = METAPHOR (God has no literal body)
- Cross-domain transfers: "Egypt = iron furnace", "Israel = vine" = METAPHOR
- A is B statements: "The Lord is my shepherd" = METAPHOR

PERSONIFICATION (human traits given to non-human entities):
- Abstract concepts as agents: "dread and fear...put upon peoples" = PERSONIFICATION
- Natural phenomena acting like humans: "mountains skipped", "sea fled" = PERSONIFICATION

RECLASSIFY when:
- Abstract concepts acting as agents are labeled "metaphor" but should be "personification" (dread and fear acting)
- Divine body parts are labeled "personification" but should be "metaphor" (hand, arm, face)
- Natural phenomena acting human-like are labeled "metaphor" but should be "personification"

DO NOT RECLASSIFY SYNECHDOCHE or MERISM as 'OTHER'. SYNECHDOCE and MERISM should be considered types of METONYMY.

[ANE CONTEXT] ANCIENT NEAR EASTERN LITERARY CONTEXT:
Consider what would be understood as literal vs figurative by an Ancient Near Eastern reader:
- "Hear you mentioned" = literal reputation spread (standard ANE concept)
- Divine blessing, watching, presence = standard divine activities (NOT figurative)
- Geographic descriptions = typically literal unless explicitly comparative
- Literal "like" in ANE Texts: The particle 'כְּ' (like/as) is frequently used for literal, descriptive purposes such as "like yourself", "like myself","like all his fellow Levites".


Focus on identifying genuine cross-domain comparisons and divine anthropomorphism while filtering out technical religious terminology.

VALIDATION:"""

        return prompt

    def _log_validation_data(self, figurative_language_id: Optional[int], validation_data: Dict):
        """Log validation data to database if database manager is available"""
        if self.db_manager and figurative_language_id:
            try:
                self.db_manager.update_validation_data(figurative_language_id, validation_data)
            except Exception as e:
                # Don't let database logging errors break the validation process
                if self.logger:
                    self.logger.warning(f"Failed to log validation data: {e}")
                else:
                    print(f"Warning: Failed to log validation data: {e}")

    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            'total_validations': self.validation_count,
            'total_type_validations': self.type_validation_count
        }


def test_metaphor_validator():
    """Test the metaphor validator with known cases"""

    # API key (same as main system)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running.")

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

        is_valid, reason, error, corrected_type = validator.validate_figurative_language(
            'metaphor',
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
        if corrected_type:
            print(f"Corrected Type: {corrected_type}")

    stats = validator.get_validation_stats()
    print(f"\nValidation Stats: {stats}")


if __name__ == "__main__":
    test_metaphor_validator()
