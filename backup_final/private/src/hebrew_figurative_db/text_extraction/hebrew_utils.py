#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hebrew text processing utilities
"""
import re
from typing import List, Optional


class HebrewTextProcessor:
    """Utilities for processing Hebrew text"""

    # Unicode ranges for Hebrew cantillation marks and vowel points
    CANTILLATION_MARKS = (
        '\u0591-\u05AF'  # Hebrew cantillation marks
        '\u05BD'         # Hebrew point meteg
        '\u05BF'         # Hebrew point rafe
        '\u05C0'         # Hebrew punctuation paseq
        '\u05C3'         # Hebrew punctuation sof pasuq
        '\u05C6'         # Hebrew punctuation nun hafukha
    )

    VOWEL_POINTS = (
        '\u05B0-\u05BC'  # Hebrew points (vowel points)
        '\u05C1-\u05C2'  # Hebrew points (shin/sin dots)
        '\u05C4-\u05C5'  # Hebrew punctuation marks
        '\u05C7'         # Hebrew point qamats qatan
    )

    # Combined pattern for all diacritics
    DIACRITICS_PATTERN = f'[{CANTILLATION_MARKS}{VOWEL_POINTS}]'

    @classmethod
    def strip_diacritics(cls, hebrew_text: str) -> str:
        """
        Remove cantillation marks and vowel points from Hebrew text

        Args:
            hebrew_text: Hebrew text with diacritics

        Returns:
            Hebrew text with only consonants and maqqef
        """
        if not hebrew_text:
            return hebrew_text

        # Remove all diacritical marks
        stripped = re.sub(cls.DIACRITICS_PATTERN, '', hebrew_text)

        # Clean up any extra whitespace
        stripped = ' '.join(stripped.split())

        return stripped

    @classmethod
    def extract_root_letters(cls, hebrew_text: str) -> str:
        """
        Extract only Hebrew letters (consonants), removing everything else

        Args:
            hebrew_text: Hebrew text

        Returns:
            Only Hebrew consonant letters
        """
        if not hebrew_text:
            return hebrew_text

        # Keep only Hebrew letters (consonants)
        # Unicode range for Hebrew letters: U+05D0-U+05EA
        hebrew_letters_only = re.sub(r'[^\u05D0-\u05EA\u05F0-\u05F4]', '', hebrew_text)

        return hebrew_letters_only

    @classmethod
    def identify_speaker_patterns(cls, english_text: str, hebrew_text: str) -> Optional[str]:
        """
        Identify the speaker based on text patterns

        Args:
            english_text: English translation
            hebrew_text: Hebrew text

        Returns:
            Speaker identification or None
        """
        if not english_text:
            return None

        text_lower = english_text.lower()

        # Direct speech patterns
        if any(phrase in text_lower for phrase in [
            'god said', 'yhwh said', 'the lord said', 'and god said'
        ]):
            return 'God'

        if any(phrase in text_lower for phrase in [
            'moses said', 'moses spoke', 'moses commanded'
        ]):
            return 'Moses'

        # Quoted speech
        if '"' in english_text or "'" in english_text:
            # Look for who is speaking before the quote
            if any(phrase in text_lower for phrase in [
                'god', 'lord', 'yhwh'
            ]) and 'said' in text_lower:
                return 'God'
            elif 'moses' in text_lower and 'said' in text_lower:
                return 'Moses'
            else:
                return 'Speaker'

        # Narrative text (no direct speech)
        return 'Narrator'


def test_hebrew_processor():
    """Test the Hebrew text processor"""
    test_cases = [
        {
            'input': 'בְּרֵאשִׁית בָּרָא אֱלֹהִים',
            'expected_stripped': 'בראשית ברא אלהים',
            'expected_letters': 'בראשיתברא אלהים'
        },
        {
            'input': 'וַיֹּאמֶר אֱלֹהִים',
            'expected_stripped': 'ויאמר אלהים',
            'expected_letters': 'ויאמראלהים'
        }
    ]

    processor = HebrewTextProcessor()

    for i, case in enumerate(test_cases):
        stripped = processor.strip_diacritics(case['input'])
        letters = processor.extract_root_letters(case['input'])

        print(f"Test {i+1}:")
        print(f"  Input: {case['input']}")
        print(f"  Stripped: {stripped}")
        print(f"  Letters only: {letters}")
        print()


if __name__ == "__main__":
    test_hebrew_processor()