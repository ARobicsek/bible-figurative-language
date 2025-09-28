#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hebrew Divine Names Modifier (Improved Version)

Modifies Hebrew text to render divine names in non-sacred format for traditional Jews,
with support for both voweled and unvoweled text.
"""

import re
import logging
from typing import Optional

class HebrewDivineNamesModifier:
    """Modifies Hebrew divine names to non-sacred format"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def modify_divine_names(self, hebrew_text: str) -> str:
        """Apply all divine name modifications to Hebrew text"""
        if not hebrew_text or not isinstance(hebrew_text, str):
            return hebrew_text

        modified_text = hebrew_text

        # Apply modifications in order of specificity (most specific first)
        # 1. Tetragrammaton: יהוה → ה׳
        modified_text = self._modify_tetragrammaton(modified_text)

        # 2. El Shaddai: שַׁדַּי → שַׁקַּי (before general patterns)
        modified_text = self._modify_el_shaddai(modified_text)

        # 3. Elohim family: replace ה with ק in divine names
        modified_text = self._modify_elohim_family(modified_text)

        # 4. El with tzere: אֵל → קֵל (NOT preposition אֶל)
        modified_text = self._modify_el_tzere(modified_text)

        # 5. Tzevaot: צְבָאוֹת → צְבָקוֹת
        modified_text = self._modify_tzevaot(modified_text)

        # Log if text changed
        if modified_text != hebrew_text:
            self.logger.debug(f"Divine names modified: '{hebrew_text}' → '{modified_text}'")

        return modified_text

    def _modify_tetragrammaton(self, text: str) -> str:
        """Replace יהוה with ה׳"""
        # Match both voweled and unvoweled forms
        patterns = [
            (r'יהוה', 'ה׳'),  # Unvoweled
            (r'יְ?[\u0591-\u05C7]*הֹ?[\u0591-\u05C7]*וָ?[\u0591-\u05C7]*ה', 'ה׳'),  # Voweled with cantillation marks
        ]

        modified = text
        for pattern, replacement in patterns:
            new_modified = re.sub(pattern, replacement, modified)
            if new_modified != modified:
                self.logger.debug(f"Tetragrammaton modified: {pattern} → {replacement}")
                modified = new_modified

        return modified

    def _modify_elohim_family(self, text: str) -> str:
        """Replace ה with ק in Elohim family words"""

        # Simple replacement approach - replace ה with ק in Elohim words
        modified = text

        # Pattern 1: Basic unvoweled אלהים
        if 'אלהים' in text:
            modified = modified.replace('אלהים', 'אלקים')
            self.logger.debug("Elohim (unvoweled) modified: אלהים → אלקים")

        # Pattern 2: Voweled Elohim patterns with cantillation marks
        # Look for א followed by vowels/cantillation, then לה with vowels/cantillation, then ים or י + suffix
        elohim_pattern = r'א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*([ִֵֶָ][\u0591-\u05C7]*[^\s]*)'
        def elohim_replacer(match):
            return match.group().replace('ה', 'ק')

        new_modified = re.sub(elohim_pattern, elohim_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Elohim (voweled) modified")
            modified = new_modified

        # Pattern 3: With definite article הָאֱלֹהִים (with cantillation marks)
        ha_elohim_pattern = r'ה[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*([ִֵֶָ][\u0591-\u05C7]*[^\s]*)'
        new_modified = re.sub(ha_elohim_pattern, elohim_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Ha-Elohim modified")
            modified = new_modified

        return modified

    def _modify_el_tzere(self, text: str) -> str:
        """Replace אֵל (with tzere) with קֵל, but NOT אֶל (with segol)"""
        # Pattern: א with tzere (ֵ) followed by ל, with optional cantillation marks
        # Use Hebrew word boundaries - not followed by Hebrew letters (but allow vowels/cantillation)
        pattern = r'אֵ[\u0591-\u05C7]*ל(?![\u05D0-\u05EA])'  # Hebrew letters range
        replacement = r'קֵ\1ל'  # Preserve any cantillation marks between א and ל

        # Alternative simpler approach - just match אֵל with any following marks
        pattern = r'אֵ([^\u05D0-\u05EA]*)ל'  # Match אֵ, capture non-Hebrew-letter marks, then ל
        replacement = r'קֵ\1ל'

        modified = re.sub(pattern, replacement, text)
        if modified != text:
            self.logger.debug(f"El (tzere) modified: אֵל → קֵל")

        return modified

    def _modify_tzevaot(self, text: str) -> str:
        """Replace א with ק in צְבָאוֹת"""
        # Unvoweled form
        if 'צבאות' in text:
            modified = text.replace('צבאות', 'צבקות')
            if modified != text:
                self.logger.debug("Tzevaot (unvoweled) modified: צבאות → צבקות")
        else:
            modified = text

        # Voweled form with cantillation marks - use replacer function
        tzevaot_pattern = r'צ[\u0591-\u05C7]*[ְ]?[\u0591-\u05C7]*ב[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[וֹ]?[\u0591-\u05C7]*ת'
        def tzevaot_replacer(match):
            return match.group().replace('א', 'ק')

        new_modified = re.sub(tzevaot_pattern, tzevaot_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Tzevaot (voweled) modified")
            modified = new_modified

        return modified

    def _modify_el_shaddai(self, text: str) -> str:
        """Replace ד with ק in שַׁדַּי"""
        # Unvoweled form
        if 'שדי' in text:
            modified = text.replace('שדי', 'שקי')
            if modified != text:
                self.logger.debug("El Shaddai (unvoweled) modified: שדי → שקי")
        else:
            modified = text

        # Voweled form with cantillation marks
        shaddai_pattern = r'ש[\u0591-\u05C7]*[ַׁ]?[\u0591-\u05C7]*ד[\u0591-\u05C7]*[ַּ]?[\u0591-\u05C7]*י'
        def shaddai_replacer(match):
            return match.group().replace('ד', 'ק')

        new_modified = re.sub(shaddai_pattern, shaddai_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"El Shaddai (voweled) modified")
            modified = new_modified

        return modified

    def has_divine_names(self, hebrew_text: str) -> bool:
        """Check if text contains any divine names that would be modified"""
        if not hebrew_text:
            return False

        patterns = [
            r'יהוה',  # Tetragrammaton (unvoweled)
            r'יְ?[\u0591-\u05C7]*הֹ?[\u0591-\u05C7]*וָ?[\u0591-\u05C7]*ה',  # Tetragrammaton (voweled with cantillation)
            r'אלהים',  # Elohim (unvoweled)
            r'א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶָ]',  # Elohim (voweled with cantillation)
            r'ה[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶָ]',  # Ha-Elohim with cantillation
            r'אֵ([^\u05D0-\u05EA]*)ל',  # El with tzere (matches our modifier pattern)
            r'צבאות',  # Tzevaot (unvoweled)
            r'צ[\u0591-\u05C7]*[ְ]?[\u0591-\u05C7]*ב[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[וֹ]?[\u0591-\u05C7]*ת',  # Tzevaot (voweled with cantillation)
            r'שדי',  # Shaddai (unvoweled)
            r'ש[\u0591-\u05C7]*[ַׁ]?[\u0591-\u05C7]*ד[\u0591-\u05C7]*[ַּ]?[\u0591-\u05C7]*י'   # Shaddai (voweled with cantillation)
        ]

        for pattern in patterns:
            if re.search(pattern, hebrew_text):
                return True

        return False

    def get_modification_summary(self, original: str, modified: str) -> dict:
        """Get summary of what modifications were made"""
        if original == modified:
            return {'has_modifications': False, 'modifications': []}

        modifications = []

        # Check each type of modification
        if ('יהוה' in original or 'יְהֹוָה' in original) and 'ה׳' in modified:
            modifications.append('tetragrammaton')

        if ('אלהי' in original or 'אלק' in modified) and original != modified:
            modifications.append('elohim_family')

        if 'אֵל' in original and 'קֵל' in modified:
            modifications.append('el_tzere')

        if ('צבאות' in original or 'צְבָאוֹת' in original) and ('צבקות' in modified or 'צְבָקוֹת' in modified):
            modifications.append('tzevaot')

        if ('שדי' in original or 'שַׁדַּי' in original) and ('שקי' in modified or 'שַׁקַּי' in modified):
            modifications.append('el_shaddai')

        return {
            'has_modifications': len(modifications) > 0,
            'modifications': modifications,
            'original_length': len(original),
            'modified_length': len(modified)
        }