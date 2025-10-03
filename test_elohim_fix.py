#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the fixed Elohim modifier patterns"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'private/src')

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

modifier = HebrewDivineNamesModifier()

# Test cases from the problem verses
test_cases = [
    ('אֱלֹהֶ֑֔יךָ', 'אֱלֹקֶ֑֔יךָ', 'Elohekha (Exodus 20:2)'),
    ('אֱלֹהֵיכֶ֑ם', 'אֱלֹקֵיכֶ֑ם', 'Eloheikhem (Deuteronomy 14:1)'),
    ('אֱלֹהִ֑ים', 'אֱלֹקִ֑ים', 'Elohim (standard)'),
    ('אֱלוֹהַּ', 'אֱלוֹקַּ', 'Eloah (singular)'),
]

print("=== TESTING FIXED MODIFIER ===\n")

all_passed = True
for original, expected, description in test_cases:
    result = modifier.modify_divine_names(original)
    status = "✓ PASS" if result == expected else "✗ FAIL"
    if result != expected:
        all_passed = False
    print(f"{status} - {description}")
    print(f"  Original:  {original}")
    print(f"  Expected:  {expected}")
    print(f"  Got:       {result}")
    print()

if all_passed:
    print("✓ All tests passed! Ready to regenerate database.")
else:
    print("✗ Some tests failed. Fix needed before regenerating.")
