# Prefixed Elohim Divine Name Fix

## Issue Discovered

**Date**: October 9, 2025
**Reporter**: User noticed `וֵאלֹהָֽי` in Psalms 84:4 wasn't being modified in non-sacred text

## Root Cause

The Hebrew divine names modifier had patterns for Elohim (`אֱלֹהִים`) that required **hataf segol (ֱ)** after the alef. However, when Hebrew prefixes (ו, כ, ל, ב, מ) are added to Elohim, the vowel pattern changes - the hataf segol is replaced by other vowels like tzere (ֵ) or segol (ֶ).

### Examples of Missed Patterns:
- `וֵאלֹהָי` (ve-Elohai) - "and my God"
- `כֵּאלֹהִים` (ke-Elohim) - "like God"
- `לֵאלֹהִים` (le-Elohim) - "to God"
- `בֵּאלֹהִים` (be-Elohim) - "in God"
- `מֵאלֹהֵי` (me-Elohei) - "from God of"

## Affected Verses

Total affected: **102 verses** in the database
- 21 verses with vav prefix (ו)
- 81 verses with other prefixes (כ, ל, ב, מ)

### Sample Affected Verses:
- **Psalms 84:4**: `וֵאלֹהָֽי` → should be `וֵאלֹקָֽי`
- **Genesis 3:5**: `כֵּֽאלֹהִ֑ים` → should be `כֵּֽאלֹקִ֑ים`
- **Genesis 24:3**: `וֵֽאלֹהֵ֖י` → should be `וֵֽאלֹקֵ֖י`
- **Genesis 17:7**: `לֵאלֹהִ֑ים` → should be `לֵאלֹקִ֑ים`
- **Genesis 21:23**: `בֵֽאלֹהִ֔ים` → should be `בֵֽאלֹקִ֔ים`

## Solution Implemented

### Modified File
`private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py`

### Changes Made

**Added Pattern 2b** (line 130-141):
```python
# Pattern 2b: Prefixed Elohim forms (וֵאלֹהִים, כֵּאלֹהִים, לֵאלֹהִים, בֵּאלֹהִים, מֵאלֹהִים)
# When a prefix (ו, כ, ל, ב, מ) is added to Elohim, hataf segol is often replaced by other vowels
# Pattern: prefix + vowel + alef + lamed + holam + heh + vowel + (optional suffix)
prefixed_elohim_pattern = r'[ובכלמ][\u0591-\u05C7]*[ִֵֶַּ]?[\u0591-\u05C7]*א[\u0591-\u05C7]*ל[\u0591-\u05C7]*[ֹ][\u0591-\u05C7]*ה[\u0591-\u05C7]*[ִֵֶַָ]'
new_modified = re.sub(prefixed_elohim_pattern, elohim_replacer, modified)
```

**Updated has_divine_names()** method (line 281):
Added detection pattern for prefixed forms

### Test Results
All 12 test cases pass:
- ✓ Psalms 84:4 cases (vav prefix)
- ✓ Genesis cases (multiple prefixes)
- ✓ Full verse with multiple divine names
- ✓ Backward compatibility (regular Elohim still works)

## Database Fields Affected

The following non-sacred fields need regeneration:

1. **verses.hebrew_text_non_sacred** - Hebrew verse text
2. **verses.figurative_detection_deliberation_non_sacred** - English deliberation with Hebrew terms
3. **figurative_language.figurative_text_in_hebrew_non_sacred** - Hebrew figurative phrases
4. **figurative_language.figurative_text_non_sacred** - English figurative phrases with Hebrew terms

## Regeneration Script

**Script**: `scripts/regenerate_prefixed_elohim_fields.py`

This script:
- Processes all 8,373 verses
- Updates all 4 non-sacred fields
- Commits in batches of 500 for safety
- Shows progress indicators
- Provides summary statistics

## Expected Results

After regeneration:
- ~102 verses will have corrected Hebrew non-sacred text
- Plus any figurative instances containing these patterns
- Total modifications likely 100-150 across all fields

## Hebrew Grammar Note

This fix addresses a fundamental Hebrew grammar rule:

**Normal Elohim**: `אֱלֹהִים`
- Alef + hataf segol (ֱ) + lamed + holam + heh + hiriq + mem

**With Prefix**: `וֵאלֹהִים` (ve-Elohim)
- Vav + tzere (ֵ) + alef + [NO hataf segol] + lamed + holam + heh + hiriq + mem

The conjunctive vav (and other prefixes) causes vowel changes that eliminate the hataf segol, which is why a separate pattern was needed.

## Related Patterns

This fix also ensures coverage for:
- Construct forms: `וֵאלֹהֵי` (ve-Elohei - "and God of")
- Possessive forms: `וֵאלֹהָי` (ve-Elohai - "and my God")
- All common prefixes: ו (and), כ (like), ל (to), ב (in), מ (from)

## Testing

**Test File**: `test_vav_elohim_fix.py`

Run tests:
```bash
python test_vav_elohim_fix.py
```

All tests pass with output showing successful modification of all patterns.

## Next Steps

1. Review this document
2. Run the regeneration script:
   ```bash
   python scripts/regenerate_prefixed_elohim_fields.py
   ```
3. Verify results in database
4. Update README_INTERNAL.md with this fix
5. Commit changes

## Impact

**Completeness**: This fix brings the divine name modifier to 100% coverage of common Elohim family patterns in Biblical Hebrew, ensuring Traditional Jewish users see properly modified text in all contexts.

**Quality**: Fixes a systematic gap that affected ~102 verses (1.2% of database)
