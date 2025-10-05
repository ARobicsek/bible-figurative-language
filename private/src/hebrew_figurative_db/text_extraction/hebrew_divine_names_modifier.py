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

        # 6. Eloah: אֱלוֹהַּ → אֱלוֹקַּ
        modified_text = self._modify_eloah(modified_text)

        # Log if text changed
        if modified_text != hebrew_text:
            self.logger.debug(f"Divine names modified: '{hebrew_text}' → '{modified_text}'")

        return modified_text

    def modify_english_with_hebrew_terms(self, english_text: str) -> str:
        """Apply divine name modifications to English text that contains Hebrew terms"""
        if not english_text or not isinstance(english_text, str):
            return english_text

        # This method applies the same Hebrew divine name modifications
        # but to English text that may contain Hebrew terms
        modified_text = english_text

        # Apply the same modifications as Hebrew text
        # The patterns should work the same way since we're looking for Hebrew characters

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

        # 6. Eloah: אֱלוֹהַּ → אֱלוֹקַּ
        modified_text = self._modify_eloah(modified_text)

        # Log if text changed
        if modified_text != english_text:
            self.logger.debug(f"English text with Hebrew divine names modified")

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
        # Must have: א + hataf segol + ל + holam + ה + any vowel + suffix
        # Covers: אֱלֹהִים (Elohim), אֱלֹהֶיךָ (Elohekha), אֱלֹהֵיכֶם (Eloheikhem),
        #         אֱלֹהַי (Elohai - my God), אֱלֹהָיו (Elohav - his God), etc.
        # Vowels include: hiriq (ִ), tzere (ֵ), segol (ֶ), patah (ַ), qamatz (ָ)
        elohim_pattern = r'א[\u0591-\u05C7]*[ֱ][\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ][\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶַָ][\u0591-\u05C7]*[םיּךֶָו]'
        def elohim_replacer(match):
            return match.group().replace('ה', 'ק')

        new_modified = re.sub(elohim_pattern, elohim_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Elohim (voweled) modified")
            modified = new_modified

        # Pattern 3: With definite article הָאֱלֹהִים (with cantillation marks)
        # Must have: ה + vowel + א + hataf segol + ל + holam + ה + any vowel + suffix
        # Covers forms with definite article
        ha_elohim_pattern = r'ה[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[ֱ][\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ][\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶַָ][\u0591-\u05C7]*[םיּךֶָו]'
        new_modified = re.sub(ha_elohim_pattern, elohim_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Ha-Elohim modified")
            modified = new_modified

        # Pattern 4: Construct form with vav-holam: אֱלוֹהֵי (Elohei - "God of")
        # This is a variant spelling where the 'o' is spelled with vav-holam instead of just holam
        # Example: אֱלוֹהֵ֥י יִשְׁעִֽי (Elohei yish'i - "God of my salvation", Psalms 18:47)
        # Pattern: א + hataf segol + ל + vav + holam + ה + vowel
        elohei_construct_pattern = r'א[\u0591-\u05C7]*[ֱ][\u0591-\u05C7]*ל[\u0591-\u05C7]*ו[\u0591-\u05C7]*[ֹ][\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶַָ]'
        new_modified = re.sub(elohei_construct_pattern, elohim_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Elohim construct (vav-holam) modified")
            modified = new_modified

        return modified

    def _modify_el_tzere(self, text: str) -> str:
        """Replace אֵל (with tzere) with קֵל, but NOT אֶל (with segol) or when part of other words"""
        # Use a simple approach: match אֵל that is preceded by space, hyphen, or start of string
        # and followed by space, hyphen, end of string, or only vowels/cantillation

        pattern = r'(^|[\s\-\u05BE])אֵ([\u0591-\u05C7]*)ל(?=[\s\-\u05BE]|$)'

        def replacer(match):
            prefix = match.group(1)
            cantillation = match.group(2)
            return f"{prefix}קֵ{cantillation}ל"

        modified = re.sub(pattern, replacer, text)
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
        """Replace ד with ק in שַׁדַּי (only when it's a standalone divine name, not part of another word)"""
        modified = text

        # Unvoweled form - only match when preceded/followed by word boundary
        # Word boundaries: start/end of string, space, hyphen (maqaf), or common punctuation
        # Allow optional cantillation marks after the yud before the word boundary
        unvoweled_pattern = r'(^|[\s\-\u05BE.,;:!?])שדי(?=[\u0591-\u05C7]*(?:[\s\-\u05BE.,;:!?]|$))'
        def unvoweled_replacer(match):
            prefix = match.group(1)
            return f"{prefix}שקי"

        new_modified = re.sub(unvoweled_pattern, unvoweled_replacer, modified)
        if new_modified != modified:
            self.logger.debug("El Shaddai (unvoweled) modified: שדי → שקי")
            modified = new_modified

        # Voweled form with cantillation marks - only match standalone word
        # Pattern: shin + (vowels/marks) + dalet + (vowels/marks) + yud + (optional cantillation after)
        # Must be preceded by word boundary, and followed by cantillation+word boundary
        # The yud can have cantillation marks after it, so we allow [\u0591-\u05C7]* after the final י
        shaddai_pattern = r'(^|[\s\-\u05BE.,;:!?])ש[\u0591-\u05C7]*[ַׁ]?[\u0591-\u05C7]*ד[\u0591-\u05C7]*[ַּ]?[\u0591-\u05C7]*י(?=[\u0591-\u05C7]*(?:[\s\-\u05BE.,;:!?]|$))'
        def shaddai_replacer(match):
            prefix = match.group(1)
            modified_word = match.group()[len(prefix):].replace('ד', 'ק')
            return f"{prefix}{modified_word}"

        new_modified = re.sub(shaddai_pattern, shaddai_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"El Shaddai (voweled) modified")
            modified = new_modified

        return modified

    def _modify_eloah(self, text: str) -> str:
        """Replace ה with ק in אֱלוֹהַּ (Eloah - singular form of Elohim)"""
        # Unvoweled form
        if 'אלוה' in text:
            modified = text.replace('אלוה', 'אלוק')
            if modified != text:
                self.logger.debug("Eloah (unvoweled) modified: אלוה → אלוק")
        else:
            modified = text

        # Voweled form with cantillation marks
        # Must have: א + hataf segol + ל + vav + holam + ה + patah/qamatz + dagesh
        # Example: אֱל֣וֹהַּ (from Psalms 114:7)
        # Pattern breakdown:
        # - א followed by optional cantillation/vowels
        # - ֱ (hataf segol) - required for Eloah
        # - ל followed by optional cantillation
        # - ו (vav) followed by optional cantillation
        # - ֹ (holam) - required for Eloah
        # - ה followed by optional cantillation
        # - ַ (patah) - required for Eloah
        # - Optional dagesh and other marks
        eloah_pattern = r'א[\u0591-\u05C7]*ֱ[\u0591-\u05C7]*ל[\u0591-\u05C7]*ו[\u0591-\u05C7]*ֹ[\u0591-\u05C7]*ה[\u0591-\u05C7]*ַ[\u0591-\u05C7]*'
        def eloah_replacer(match):
            return match.group().replace('ה', 'ק')

        new_modified = re.sub(eloah_pattern, eloah_replacer, modified)
        if new_modified != modified:
            self.logger.debug(f"Eloah (voweled) modified")
            modified = new_modified

        return modified

    def has_divine_names(self, text: str) -> bool:
        """Check if text (Hebrew or English with Hebrew terms) contains any divine names that would be modified"""
        if not text:
            return False

        patterns = [
            r'יהוה',  # Tetragrammaton (unvoweled)
            r'יְ?[\u0591-\u05C7]*הֹ?[\u0591-\u05C7]*וָ?[\u0591-\u05C7]*ה',  # Tetragrammaton (voweled with cantillation)
            r'אלהים',  # Elohim (unvoweled)
            r'א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶָ]',  # Elohim (voweled with cantillation)
            r'ה[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[ֱ]?[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ]?[\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶָ]',  # Ha-Elohim with cantillation
            r'(^|[\s\-\u05BE])אֵ[\u0591-\u05C7]*ל(?=[\s\-\u05BE]|$)',  # El with tzere (standalone word only)
            r'צבאות',  # Tzevaot (unvoweled)
            r'צ[\u0591-\u05C7]*[ְ]?[\u0591-\u05C7]*ב[\u0591-\u05C7]*[ָ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*[וֹ]?[\u0591-\u05C7]*ת',  # Tzevaot (voweled with cantillation)
            r'(^|[\s\-\u05BE.,;:!?])שדי(?=[\u0591-\u05C7]*(?:[\s\-\u05BE.,;:!?]|$))',  # Shaddai (unvoweled) - standalone only
            r'(^|[\s\-\u05BE.,;:!?])ש[\u0591-\u05C7]*[ַׁ]?[\u0591-\u05C7]*ד[\u0591-\u05C7]*[ַּ]?[\u0591-\u05C7]*י(?=[\u0591-\u05C7]*(?:[\s\-\u05BE.,;:!?]|$))',  # Shaddai (voweled) - standalone only
            r'אלוה',  # Eloah (unvoweled)
            r'א[\u0591-\u05C7]*ֱ[\u0591-\u05C7]*ל[\u0591-\u05C7]*ו[\u0591-\u05C7]*ֹ[\u0591-\u05C7]*ה[\u0591-\u05C7]*ַ[\u0591-\u05C7]*'  # Eloah (voweled with cantillation)
        ]

        for pattern in patterns:
            if re.search(pattern, text):
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