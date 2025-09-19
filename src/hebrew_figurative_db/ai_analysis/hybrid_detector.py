#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hybrid figurative language detector: LLM-powered with rule-based fallback and two-stage metaphor validation
"""
import json
import time
from typing import List, Dict, Optional
from .llm_detector import LLMFigurativeDetector
from .figurative_detector import FigurativeLanguageDetector
from .metaphor_validator import MetaphorValidator


class HybridFigurativeDetector:
    """
    Hybrid detector that prioritizes LLM analysis with two-stage metaphor validation
    """

    def __init__(self, prefer_llm: bool = True, use_actual_llm: bool = False, allow_rule_fallback: bool = False,
                 enable_metaphor_validation: bool = True, gemini_api_key: str = None):
        self.prefer_llm = prefer_llm
        self.use_actual_llm = use_actual_llm
        self.allow_rule_fallback = allow_rule_fallback
        self.enable_metaphor_validation = enable_metaphor_validation
        self.llm_detector = LLMFigurativeDetector()

        if allow_rule_fallback:
            self.rule_detector = FigurativeLanguageDetector()
        else:
            self.rule_detector = None

        # Initialize metaphor validator for two-stage validation
        if enable_metaphor_validation and gemini_api_key and use_actual_llm:
            self.metaphor_validator = MetaphorValidator(gemini_api_key)
        else:
            self.metaphor_validator = None

        # Track validation statistics
        self.validation_stats = {
            'metaphors_detected': 0,
            'metaphors_validated': 0,
            'metaphors_rejected': 0,
            'validation_errors': 0
        }

    def detect_figurative_language(self, english_text: str, hebrew_text: str = "") -> tuple[List[Dict], Optional[str]]:
        """
        Detect figurative language using hybrid approach

        Args:
            english_text: English translation
            hebrew_text: Original Hebrew text

        Returns:
            Tuple of (detection results, error message if restricted)
        """
        results = []
        error_msg = None

        if self.prefer_llm:
            # Try LLM first
            try:
                print(f"    [LLM] Analyzing with Hebrew + English...")
                llm_results, error_msg = self._analyze_with_llm(hebrew_text, english_text)
                if llm_results:
                    # Apply two-stage validation for metaphors
                    validated_results = self._validate_metaphors(llm_results, hebrew_text, english_text)
                    results.extend(validated_results)
                    print(f"    [LLM] Found {len(llm_results)} instances, {len(validated_results)} after validation")
                else:
                    print(f"    [LLM] No instances found")
                    if self.allow_rule_fallback:
                        print(f"    [LLM] Trying rule-based fallback...")
                        rule_results = self._analyze_with_rules(english_text, hebrew_text)
                        if rule_results:
                            results.extend(rule_results)
                            print(f"    [RULE] Found {len(rule_results)} instances")

            except Exception as e:
                error_msg = f"LLM Error: {e}"
                print(f"    [LLM] Error: {e}")
                if self.allow_rule_fallback:
                    print(f"    [LLM] Falling back to rules...")
                    rule_results = self._analyze_with_rules(english_text, hebrew_text)
                    if rule_results:
                        results.extend(rule_results)

        else:
            # Use rule-based primarily
            rule_results = self._analyze_with_rules(english_text, hebrew_text)
            results.extend(rule_results)

        return results, error_msg

    def extract_text_snippet(self, verse_text: str, detected_type: str) -> str:
        """Extract relevant text snippet for the detected figurative language"""
        # Use the rule-based detector's snippet extraction
        return self.rule_detector.extract_text_snippet(verse_text, detected_type)

    def _analyze_with_llm(self, hebrew_text: str, english_text: str) -> tuple[List[Dict], Optional[str]]:
        """Analyze using LLM detector"""
        if not hebrew_text:
            return [], None

        # Create a more sophisticated prompt for actual use
        prompt = self._create_analysis_prompt(hebrew_text, english_text)

        if self.use_actual_llm:
            # Call real Gemini API
            response, error = self._call_gemini_api(hebrew_text, english_text)
        else:
            # Enhanced simulation based on Hebrew patterns
            response = self._enhanced_simulation(hebrew_text, english_text)
            error = None

        return self._parse_llm_response(response), error

    def _analyze_with_rules(self, english_text: str, hebrew_text: str) -> List[Dict]:
        """Analyze using rule-based detector"""
        if self.rule_detector is None:
            return []
        return self.rule_detector.detect_figurative_language(english_text, hebrew_text)

    def _create_analysis_prompt(self, hebrew_text: str, english_text: str) -> str:
        """Create analysis prompt for LLM"""
        return f"""Analyze this biblical Hebrew verse for ALL instances of figurative language.

Hebrew: {hebrew_text}
English: {english_text}

Identify: metaphors, similes, personification, idioms, hyperbole, metonymy

For each instance, provide:
1. Type of figurative language
2. The specific Hebrew words (with English)
3. Explanation of why it's figurative
4. Category (divine, body, nature, family, etc.)
5. Confidence (0.0-1.0)

Return as JSON array. Example:
[{{"type": "metaphor", "hebrew_text": "רֹעִי", "english_text": "my shepherd", "explanation": "God compared to a shepherd", "subcategory": "pastoral", "confidence": 0.9}}]

Analysis:"""

    def _enhanced_simulation(self, hebrew_text: str, english_text: str) -> str:
        """Enhanced simulation that analyzes both Hebrew and English"""
        results = []

        # Check for God/divine personification
        if any(term in hebrew_text for term in ["יהוה", "אלהים", "אל"]):
            divine_actions = ["said", "made", "saw", "called", "blessed", "formed", "breathed", "planted", "delight"]
            for action in divine_actions:
                if action in english_text.lower():
                    results.append({
                        "type": "personification",
                        "hebrew_text": "יהוה/אלהים",
                        "english_text": f"God {action}",
                        "explanation": f"God attributed human action/emotion: {action}",
                        "subcategory": "divine",
                        "confidence": 0.9
                    })

        # Check for Hebrew simile marker כְּ
        if "כְּ" in hebrew_text or "כִּ" in hebrew_text:
            results.append({
                "type": "simile",
                "hebrew_text": "כְּ/כִּ",
                "english_text": "like/as comparison",
                "explanation": "Hebrew simile marker indicating comparison",
                "subcategory": "comparative",
                "confidence": 0.95
            })

        # Check for English simile markers
        import re
        simile_match = re.search(r'\b(like|as)\s+([^,\.]+)', english_text.lower())
        if simile_match:
            results.append({
                "type": "simile",
                "hebrew_text": "comparison phrase",
                "english_text": simile_match.group(0),
                "explanation": "Direct comparison using 'like' or 'as'",
                "subcategory": "comparative",
                "confidence": 0.85
            })

        # Check for metaphorical concepts
        metaphor_terms = {
            "צלם": ("image", "Metaphorical concept of divine image"),
            "דמות": ("likeness", "Metaphorical concept of divine likeness"),
            "רועי": ("shepherd", "Metaphorical role comparison")
        }

        for hebrew_term, (english_term, explanation) in metaphor_terms.items():
            if hebrew_term in hebrew_text and english_term in english_text.lower():
                results.append({
                    "type": "metaphor",
                    "hebrew_text": hebrew_term,
                    "english_text": english_term,
                    "explanation": explanation,
                    "subcategory": "divine" if "divine" in explanation else "pastoral",
                    "confidence": 0.8
                })

        return json.dumps(results, ensure_ascii=False, indent=2)

    def _call_gemini_api(self, hebrew_text: str, english_text: str) -> tuple[str, Optional[str]]:
        """Call real Gemini API"""
        try:
            from .gemini_api import GeminiAPIClient

            # Initialize Gemini client
            api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
            client = GeminiAPIClient(api_key)

            # Make API call (now returns tuple)
            response, error = client.analyze_figurative_language(hebrew_text, english_text)

            # Handle markdown code block wrapper
            if response.startswith("```json"):
                # Extract JSON from markdown code block
                lines = response.split('\n')
                json_lines = []
                in_json = False
                for line in lines:
                    if line.strip() == "```json":
                        in_json = True
                        continue
                    elif line.strip() == "```":
                        break
                    elif in_json:
                        json_lines.append(line)

                return '\n'.join(json_lines), error

            return response, error

        except Exception as e:
            error_msg = f"Gemini API call failed: {e}"
            print(error_msg)
            return "[]", error_msg  # Return empty result on failure

    def _parse_llm_response(self, response: str) -> List[Dict]:
        """Parse LLM JSON response with confidence threshold filtering"""
        try:
            data = json.loads(response)
            results = []

            for item in data:
                if isinstance(item, dict) and item.get('type'):
                    confidence = float(item.get('confidence', 0.0))

                    # Apply confidence threshold filtering (0.7 minimum)
                    if confidence < 0.7:
                        continue

                    # Convert to pipeline format
                    result = {
                        'type': item.get('type', '').lower(),
                        'confidence': confidence,
                        'pattern': 'llm_detected',
                        'figurative_text': item.get('english_text', ''),
                        'explanation': item.get('explanation', ''),
                        'subcategory': item.get('subcategory', ''),  # Keep for backward compatibility
                        'subcategory_level_1': item.get('subcategory_level_1', ''),
                        'subcategory_level_2': item.get('subcategory_level_2', ''),
                        'hebrew_source': item.get('hebrew_text', ''),
                        'speaker': item.get('speaker', ''),
                        'purpose': item.get('purpose', '')
                    }
                    results.append(result)

            return results

        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing LLM response: {e}")
            return []

    def _validate_metaphors(self, results: List[Dict], hebrew_text: str, english_text: str) -> List[Dict]:
        """Apply two-stage validation to detected metaphors"""
        if not self.metaphor_validator:
            # No validation enabled, return all results
            return results

        validated_results = []

        for result in results:
            if result.get('type') == 'metaphor':
                self.validation_stats['metaphors_detected'] += 1

                # Extract validation parameters
                figurative_text = result.get('figurative_text', '')
                explanation = result.get('explanation', '')
                confidence = result.get('confidence', 0.0)

                try:
                    # Validate with stage 2
                    is_valid, reason, error = self.metaphor_validator.validate_metaphor(
                        hebrew_text, english_text, figurative_text, explanation, confidence
                    )

                    if error:
                        self.validation_stats['validation_errors'] += 1
                        print(f"    [VALIDATE] Error validating metaphor: {error}")
                        # On error, keep the metaphor (conservative approach)
                        validated_results.append(result)
                    elif is_valid:
                        self.validation_stats['metaphors_validated'] += 1
                        print(f"    [VALIDATE] VALID: Metaphor validated: {figurative_text}")
                        validated_results.append(result)
                    else:
                        self.validation_stats['metaphors_rejected'] += 1
                        print(f"    [VALIDATE] REJECTED: Metaphor rejected: {figurative_text} - {reason}")
                        # Don't add to validated_results (filter out)

                except Exception as e:
                    self.validation_stats['validation_errors'] += 1
                    print(f"    [VALIDATE] Exception during validation: {e}")
                    # On exception, keep the metaphor (conservative approach)
                    validated_results.append(result)
            else:
                # Non-metaphor types pass through without validation
                validated_results.append(result)

        return validated_results

    def get_validation_statistics(self) -> Dict:
        """Get validation statistics"""
        stats = self.validation_stats.copy()
        if self.metaphor_validator:
            validator_stats = self.metaphor_validator.get_validation_stats()
            stats.update(validator_stats)
        return stats

    def print_validation_summary(self):
        """Print a summary of validation results"""
        stats = self.get_validation_statistics()
        print(f"\n=== METAPHOR VALIDATION SUMMARY ===")
        print(f"Metaphors detected: {stats['metaphors_detected']}")
        print(f"Metaphors validated: {stats['metaphors_validated']}")
        print(f"Metaphors rejected: {stats['metaphors_rejected']}")
        print(f"Validation errors: {stats['validation_errors']}")

        if stats['metaphors_detected'] > 0:
            validation_rate = (stats['metaphors_validated'] / stats['metaphors_detected']) * 100
            rejection_rate = (stats['metaphors_rejected'] / stats['metaphors_detected']) * 100
            print(f"Validation rate: {validation_rate:.1f}%")
            print(f"Rejection rate: {rejection_rate:.1f}%")


def test_hybrid_detector():
    """Test the hybrid detector"""
    print("=== TESTING HYBRID DETECTOR ===\n")

    detector = HybridFigurativeDetector(prefer_llm=True, use_actual_llm=False)

    test_cases = [
        {
            "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
            "english": "The LORD is my shepherd; I shall not want",
            "name": "Psalm 23:1"
        },
        {
            "hebrew": "וַיֹּאמֶר אֱלֹהִים נַעֲשֶׂה אָדָם בְּצַלְמֵנוּ כִּדְמוּתֵנוּ",
            "english": "And God said, 'Let us make humankind in our image, after our likeness'",
            "name": "Genesis 1:26"
        },
        {
            "hebrew": "כִּי יְהוָה יָשִׂישׂ עָלַיִךְ כַּאֲשֶׁר שָׂשׂ עַל־אֲבֹתֶיךָ",
            "english": "For the LORD will delight in you as he delighted in your ancestors",
            "name": "Deuteronomy 30:9"
        }
    ]

    for case in test_cases:
        print(f"Testing {case['name']}:")
        print(f"English: {case['english']}")

        results, error = detector.detect_figurative_language(case['english'], case['hebrew'])

        if error:
            print(f"LLM Error: {error}")

        if results:
            print(f"Found {len(results)} instances:")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['type']} ({result['confidence']:.2f})")
                print(f"     Text: '{result['figurative_text']}'")
                print(f"     Hebrew: {result.get('hebrew_source', 'N/A')}")
                print(f"     Explanation: {result['explanation']}")
                print(f"     Category: {result['subcategory']}")
        else:
            print("No figurative language detected")

        print()


if __name__ == "__main__":
    test_hybrid_detector()