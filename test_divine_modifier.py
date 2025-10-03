#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, 'private/src')

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s', force=True)

modifier = HebrewDivineNamesModifier()

test_cases = [
    'אֶֽל־הַנָּחָשׁ֮',  # to the serpent - should NOT change
    'אֱלֹהִים',  # Elohim - should change to אֱלֹקִים
    'הָאֱלֹהִים',  # The Elohim - should change to הָאֱלֹקִים
    'יהוה',  # YHWH - should change to ה׳
    'אֶל־הָ֣אִשָּׁ֔ה',  # to the woman - should NOT change (Gen 3:1)
    'וַיֹּ֨אמֶר יְהֹוָ֧ה אֱלֹהִ֛ים אֶל־הַנָּחָשׁ֮',  # Full verse Gen 3:14 - only divine names should change
]

with open('test_results.txt', 'w', encoding='utf-8') as f:
    f.write("Testing Divine Names Modifier\n")
    f.write("=" * 50 + "\n")

    for i, test in enumerate(test_cases):
        result = modifier.modify_divine_names(test)
        status = "CHANGED" if test != result else "unchanged"
        f.write(f"\nTest {i+1}:\n")
        f.write(f"Input:  {test}\n")
        f.write(f"Output: {result}\n")
        f.write(f"Status: {status}\n")
        if test != result and (i == 0 or i == 4 or i == 5):
            # Check if non-divine text was changed
            if 'הַנָּחָשׁ' in test and 'קַנָּחָשׁ' in result:
                f.write(f"ERROR: 'the serpent' was incorrectly modified!\n")
            elif 'הָ֣אִשָּׁ֔ה' in test and 'קָ֣אִשָּׁ֔ק' in result:
                f.write(f"ERROR: 'the woman' was incorrectly modified!\n")

print("Results written to test_results.txt")
