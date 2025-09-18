#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced figurative language detection with rule-based patterns, AI analysis, and subcategorization
"""
import re
from typing import Tuple, Optional, Dict, List


class FigurativeLanguageDetector:
    """Enhanced figurative language detection with confidence scoring and subcategorization"""

    def __init__(self):
        self.human_actions = ['said', 'saw', 'called', 'made', 'separated', 'blessed', 'formed', 'breathed', 'planted', 'walked', 'delight', 'rejoiced', 'loved', 'hated', 'angry', 'pleased', 'grieved', 'remembered', 'forgot', 'thought', 'felt', 'wanted', 'desired']

        # Subcategory patterns for metaphors and similes
        self.subcategory_patterns = {
            'body': ['heart', 'hand', 'eye', 'face', 'arm', 'mouth', 'breath', 'blood', 'bone', 'flesh'],
            'agricultural': ['seed', 'plant', 'tree', 'fruit', 'harvest', 'vineyard', 'field', 'grain', 'olive'],
            'hunting': ['trap', 'snare', 'hunt', 'prey', 'catch', 'bow', 'arrow', 'spear'],
            'construction': ['foundation', 'cornerstone', 'build', 'house', 'tower', 'wall', 'gate', 'pillar'],
            'zoological': ['lion', 'lamb', 'eagle', 'dove', 'serpent', 'wolf', 'bear', 'sheep', 'goat', 'ox'],
            'familial': ['father', 'mother', 'son', 'daughter', 'brother', 'sister', 'husband', 'wife', 'child'],
            'natural': ['mountain', 'valley', 'river', 'sea', 'wind', 'fire', 'water', 'stone', 'rock', 'earth'],
            'divine': ['god', 'lord', 'holy', 'spirit', 'angel', 'heaven', 'throne', 'glory', 'worship']
        }

        # Idiom patterns
        self.idiom_patterns = [
            r'\bsleep with (his|their) fathers\b',  # death euphemism
            r'\bknow good and (bad|evil)\b',  # moral knowledge
            r'\bharden (his|their) heart\b',  # stubbornness
            r'\bstiff(-| )necked\b',  # stubborn people
            r'\bgo down to (the grave|sheol)\b',  # death
            r'\bwhite as snow\b',  # purity/cleanliness
            r'\bstrong as death\b',  # intensity
        ]

        # Hyperbole patterns
        self.hyperbole_patterns = [
            r'\ball the earth\b',
            r'\bevery living thing\b',
            r'\bfrom (the|one) end.*to (the|another) end\b',
            r'\bas numerous as.*stars\b',
            r'\bas sand.*sea\b',
            r'\ba thousand generations\b',
            r'\bforever and ever\b',
        ]

    def detect_figurative_language(self, text: str, hebrew_text: str = "") -> List[Dict]:
        """
        Detect ALL figurative language instances in text

        Args:
            text: English text to analyze
            hebrew_text: Hebrew text for additional context

        Returns:
            List of Dict with detection results for each figurative language instance found
        """
        text_lower = text.lower()
        all_findings = []

        # Try each detection method and collect ALL results
        detection_methods = [
            ('idiom', self._detect_idiom),
            ('hyperbole', self._detect_hyperbole),
            ('personification', self._detect_personification),
            ('simile', self._detect_simile),
            ('metaphor', self._detect_metaphor)
        ]

        for method_name, method in detection_methods:
            results = method(text_lower, hebrew_text, find_all=True)
            for result in results:
                if result['type']:
                    # Add subcategorization
                    result['subcategory'] = self._categorize_figurative_language(text_lower, result['type'])
                    all_findings.append(result)

        return all_findings

    def detect_figurative_language_single(self, text: str, hebrew_text: str = "") -> Dict:
        """
        Detect first figurative language instance (backward compatibility)
        """
        results = self.detect_figurative_language(text, hebrew_text)
        if results:
            return results[0]

        return {
            'type': None,
            'confidence': 0.0,
            'pattern': None,
            'subcategory': None,
            'figurative_text': None,
            'explanation': None
        }

    def _detect_idiom(self, text_lower: str, hebrew_text: str, find_all: bool = False) -> List[Dict]:
        """Detect biblical idioms"""
        findings = []

        for pattern in self.idiom_patterns:
            if find_all:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'type': 'idiom',
                        'confidence': 0.85,
                        'pattern': pattern,
                        'figurative_text': match.group(0),
                        'explanation': f"Biblical idiom with established meaning different from literal interpretation"
                    })
            else:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    return [{
                        'type': 'idiom',
                        'confidence': 0.85,
                        'pattern': pattern,
                        'figurative_text': match.group(0),
                        'explanation': f"Biblical idiom with established meaning different from literal interpretation"
                    }]

        return findings if find_all else [{'type': None, 'confidence': 0.0, 'pattern': None, 'figurative_text': None, 'explanation': None}]

    def _detect_hyperbole(self, text_lower: str, hebrew_text: str, find_all: bool = False) -> List[Dict]:
        """Detect hyperbolic expressions"""
        findings = []

        for pattern in self.hyperbole_patterns:
            if find_all:
                matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        'type': 'hyperbole',
                        'confidence': 0.8,
                        'pattern': pattern,
                        'figurative_text': match.group(0),
                        'explanation': f"Exaggerated expression used for emphasis, not meant literally"
                    })
            else:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    return [{
                        'type': 'hyperbole',
                        'confidence': 0.8,
                        'pattern': pattern,
                        'figurative_text': match.group(0),
                        'explanation': f"Exaggerated expression used for emphasis, not meant literally"
                    }]

        return findings if find_all else [{'type': None, 'confidence': 0.0, 'pattern': None, 'figurative_text': None, 'explanation': None}]

    def _detect_simile(self, text_lower: str, hebrew_text: str, find_all: bool = False) -> List[Dict]:
        """Detect similes with 'like/as' markers"""
        findings = []

        if find_all:
            # Find all like/as patterns
            matches = re.finditer(r'\b(like|as)\s+[^,\.]+', text_lower)
            for match in matches:
                findings.append({
                    'type': 'simile',
                    'confidence': 0.9,
                    'pattern': 'like_as_marker',
                    'figurative_text': match.group(0).strip(),
                    'explanation': "Direct comparison using 'like' or 'as' to show similarity between two different things"
                })

            # Check for Hebrew simile markers
            if 'כְּ' in hebrew_text:
                findings.append({
                    'type': 'simile',
                    'confidence': 0.95,
                    'pattern': 'hebrew_simile_marker',
                    'figurative_text': 'Hebrew כְּ comparison',
                    'explanation': "Hebrew simile using כְּ (ke-) prefix indicating comparison"
                })
        else:
            match = re.search(r'\b(like|as)\s+[^,\.]+', text_lower)
            if match:
                return [{
                    'type': 'simile',
                    'confidence': 0.9,
                    'pattern': 'like_as_marker',
                    'figurative_text': match.group(0).strip(),
                    'explanation': "Direct comparison using 'like' or 'as' to show similarity between two different things"
                }]

            if 'כְּ' in hebrew_text:
                return [{
                    'type': 'simile',
                    'confidence': 0.95,
                    'pattern': 'hebrew_simile_marker',
                    'figurative_text': 'Hebrew כְּ comparison',
                    'explanation': "Hebrew simile using כְּ (ke-) prefix indicating comparison"
                }]

        return findings if find_all else [{'type': None, 'confidence': 0.0, 'pattern': None, 'figurative_text': None, 'explanation': None}]

    def _detect_metaphor(self, text_lower: str, hebrew_text: str, find_all: bool = False) -> List[Dict]:
        """Detect metaphors with 'is' constructions and image/likeness"""
        findings = []

        if find_all:
            # Find all 'is' metaphors
            is_matches = re.finditer(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text_lower)
            for match in is_matches:
                findings.append({
                    'type': 'metaphor',
                    'confidence': 0.85,
                    'pattern': 'is_metaphor',
                    'figurative_text': match.group(0),
                    'explanation': "Direct metaphorical identification - one thing described as being another thing"
                })

            # Find image/likeness metaphors
            words = text_lower.split()
            for key_word in ['image', 'likeness']:
                if key_word in text_lower:
                    figurative_phrase = self._extract_figurative_phrase(words, key_word)
                    findings.append({
                        'type': 'metaphor',
                        'confidence': 0.8,
                        'pattern': 'image_likeness',
                        'figurative_text': figurative_phrase,
                        'explanation': "Metaphorical concept of divine image/likeness - humans reflecting God's nature"
                    })
        else:
            is_match = re.search(r'\b\w+\s+is\s+(my|a|an)\s+\w+', text_lower)
            if is_match:
                return [{
                    'type': 'metaphor',
                    'confidence': 0.85,
                    'pattern': 'is_metaphor',
                    'figurative_text': is_match.group(0),
                    'explanation': "Direct metaphorical identification - one thing described as being another thing"
                }]

            if 'image' in text_lower or 'likeness' in text_lower:
                words = text_lower.split()
                key_word = 'image' if 'image' in text_lower else 'likeness'
                figurative_phrase = self._extract_figurative_phrase(words, key_word)
                return [{
                    'type': 'metaphor',
                    'confidence': 0.8,
                    'pattern': 'image_likeness',
                    'figurative_text': figurative_phrase,
                    'explanation': "Metaphorical concept of divine image/likeness - humans reflecting God's nature"
                }]

        return findings if find_all else [{'type': None, 'confidence': 0.0, 'pattern': None, 'figurative_text': None, 'explanation': None}]

    def _detect_personification(self, text_lower: str, hebrew_text: str, find_all: bool = False) -> List[Dict]:
        """Detect personification, especially God performing human actions"""
        god_terms = ['god', 'lord', 'yhwh', 'יהוה']
        findings = []

        if any(god_term in text_lower for god_term in god_terms):
            for action in self.human_actions:
                if action in text_lower:
                    # Extract the specific figurative phrase
                    words = text_lower.split()
                    figurative_phrase = self._extract_figurative_phrase(words, action, god_terms)

                    finding = {
                        'type': 'personification',
                        'confidence': 0.9,
                        'pattern': 'god_human_action',
                        'figurative_text': figurative_phrase,
                        'explanation': f"Attributes human emotion/action '{action}' to God, giving divine being human characteristics"
                    }

                    if find_all:
                        findings.append(finding)
                    else:
                        return [finding]

        return findings if find_all else [{'type': None, 'confidence': 0.0, 'pattern': None, 'figurative_text': None, 'explanation': None}]

    def _extract_figurative_phrase(self, words: List[str], key_word: str, context_words: List[str] = None) -> str:
        """Extract the specific figurative phrase from text"""
        try:
            key_index = words.index(key_word)
            start = max(0, key_index - 2)
            end = min(len(words), key_index + 3)
            return ' '.join(words[start:end])
        except ValueError:
            return key_word

    def _categorize_figurative_language(self, text_lower: str, fig_type: str) -> Optional[str]:
        """Categorize metaphors and similes by domain"""
        if fig_type not in ['metaphor', 'simile']:
            return None

        for category, keywords in self.subcategory_patterns.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return 'other'

    def extract_text_snippet(self, verse_text: str, detected_type: str) -> str:
        """Extract relevant text snippet for the detected figurative language"""
        if detected_type == 'personification' and 'god' in verse_text.lower():
            # Extract the action phrase
            words = verse_text.split()
            god_index = next((i for i, word in enumerate(words) if 'god' in word.lower()), 0)
            return ' '.join(words[god_index:god_index+4])  # God + action + object

        # For metaphors and similes, try to extract the comparison
        if detected_type in ['metaphor', 'simile']:
            if 'like' in verse_text.lower() or 'as' in verse_text.lower():
                # Find the comparison phrase
                words = verse_text.split()
                for i, word in enumerate(words):
                    if word.lower() in ['like', 'as']:
                        start = max(0, i-2)
                        end = min(len(words), i+4)
                        return ' '.join(words[start:end])

        # For other types, return first 60 characters
        return verse_text[:60] if len(verse_text) > 60 else verse_text