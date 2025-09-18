#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Figurative language detection using rule-based patterns with confidence scoring
"""
import re
from typing import Tuple, Optional


class FigurativeLanguageDetector:
    """Enhanced figurative language detection with confidence scoring"""

    def __init__(self):
        self.human_actions = ['said', 'saw', 'called', 'made', 'separated', 'blessed']

    def detect_figurative_language(self, text: str, hebrew_text: str = "") -> Tuple[Optional[str], float, Optional[str]]:
        """
        Detect figurative language in text with confidence scoring

        Args:
            text: English text to analyze
            hebrew_text: Hebrew text for additional context

        Returns:
            Tuple of (type, confidence, pattern) or (None, 0.0, None) if not found
        """
        text_lower = text.lower()

        # Simile detection
        simile_result = self._detect_simile(text_lower, hebrew_text)
        if simile_result[0]:
            return simile_result

        # Metaphor detection
        metaphor_result = self._detect_metaphor(text_lower)
        if metaphor_result[0]:
            return metaphor_result

        # Personification detection
        personification_result = self._detect_personification(text_lower)
        if personification_result[0]:
            return personification_result

        return None, 0.0, None

    def _detect_simile(self, text_lower: str, hebrew_text: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Detect similes with 'like/as' markers"""
        if re.search(r'\b(like|as)\s+\w+', text_lower):
            pattern = 'like_as_marker'
            confidence = self._confidence_scoring(text_lower, 'simile', pattern)
            return 'simile', confidence, pattern

        if 'כְּ' in hebrew_text:  # Hebrew simile marker
            pattern = 'hebrew_simile_marker'
            confidence = self._confidence_scoring(text_lower, 'simile', pattern)
            return 'simile', confidence, pattern

        return None, 0.0, None

    def _detect_metaphor(self, text_lower: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Detect metaphors with 'is' constructions and image/likeness"""
        if re.search(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text_lower):
            pattern = 'is_metaphor'
            confidence = self._confidence_scoring(text_lower, 'metaphor', pattern)
            return 'metaphor', confidence, pattern

        if 'image' in text_lower or 'likeness' in text_lower:
            pattern = 'image_likeness'
            confidence = self._confidence_scoring(text_lower, 'metaphor', pattern)
            return 'metaphor', confidence, pattern

        return None, 0.0, None

    def _detect_personification(self, text_lower: str) -> Tuple[Optional[str], float, Optional[str]]:
        """Detect personification, especially God performing human actions"""
        if any(action in text_lower for action in self.human_actions) and 'god' in text_lower:
            pattern = 'god_human_action'
            confidence = self._confidence_scoring(text_lower, 'personification', pattern)
            return 'personification', confidence, pattern

        return None, 0.0, None

    def _confidence_scoring(self, text: str, detected_type: str, pattern_matched: str = None) -> float:
        """Calculate confidence score for detected figurative language"""
        confidence = 0.5  # Base confidence

        if detected_type == 'simile':
            if re.search(r'\b(like|as)\s+\w+', text):
                confidence = 0.9  # Very high for clear simile markers
            elif pattern_matched == 'hebrew_simile_marker':
                confidence = 0.95

        elif detected_type == 'metaphor':
            if re.search(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text):
                confidence = 0.85
            elif 'image' in text or 'likeness' in text:
                confidence = 0.8
            else:
                confidence = 0.7

        elif detected_type == 'personification':
            if any(action in text for action in self.human_actions) and 'god' in text:
                confidence = 0.9  # High for God+human action
            else:
                confidence = 0.6

        # Boost for pattern matching
        if pattern_matched:
            confidence += 0.0  # Already factored in above

        return min(max(confidence, 0.0), 1.0)

    def extract_text_snippet(self, verse_text: str, detected_type: str) -> str:
        """Extract relevant text snippet for the detected figurative language"""
        if detected_type == 'personification' and 'god' in verse_text.lower():
            # Extract the action phrase
            words = verse_text.split()
            god_index = next((i for i, word in enumerate(words) if 'god' in word.lower()), 0)
            return ' '.join(words[god_index:god_index+4])  # God + action + object

        # For other types, return first 50 characters
        return verse_text[:50] if len(verse_text) > 50 else verse_text