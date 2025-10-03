#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test the two edge case forms"""

import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'private/src')

from hebrew_figurative_db.text_extraction.hebrew_divine_names_modifier import HebrewDivineNamesModifier

modifier = HebrewDivineNamesModifier()

# Test the two edge cases
edge_cases = [
    'אֱלֹ֔הַּ',      # Eloah with cantillation between holam and heh
    'אֱלוֹהֵ֥י',     # Elohei (construct - "God of")
]

print("Testing edge cases:\n")

for form in edge_cases:
    modified = modifier.modify_divine_names(form)
    status = "✓" if modified != form else "✗"
    print(f"{status} {form:20} → {modified:20}")
    if modified == form:
        print(f"  WARNING: Not modified!")
        # Show character breakdown
        print(f"  Characters: {' '.join([f'{c}({ord(c):04x})' for c in form])}")
    print()
