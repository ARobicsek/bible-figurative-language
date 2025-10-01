# Hebrew Highlighting Bug - RESOLVED ✅

## Status: FIXED (Oct 1, 2025)

**Problem:** Hebrew text with maqaf (־) hyphens wasn't being highlighted in yellow.

**Root Cause:** Unicode normalization order issue where maqaf (U+05BE) was being removed instead of replaced with space, breaking word boundary matching.

**Solution:** Fixed in commit `c3851e8` - Modified normalization order and regex pattern matching.

---

## Original Problem Description

Hebrew text with figurative language was **not being highlighted** in yellow, even though:
1. The verse had figurative language in the database
2. The verse was visible (appeared when "Not Figurative" was unchecked)
3. The annotations existed and were returned by the API

## Affected Verses (Examples)
- **Psalms 6:8** - ORIGINAL ISSUE ✅ FIXED
- **Genesis 3:1** - "וַיֹּאמֶר אֶל־הָאִשָּׁה" ✅ FIXED
- **Genesis 3:16** ✅ FIXED
- **Genesis 3:17** ✅ FIXED
- **Genesis 3:19** ✅ FIXED

## Root Cause Analysis

### The Unicode Issue

The maqaf character (־, U+05BE) is used in Hebrew to join words, similar to a hyphen. The problem occurred because:

1. **Original normalization code:**
   ```javascript
   .replace(/[\u0591-\u05C7\u05F0-\u05F4]/g, '') // Remove Hebrew diacritics
   .replace(/־/g, ' ')  // Replace hyphens with spaces
   ```

2. **The issue:** U+05BE (maqaf) falls within the range `\u0591-\u05C7`:
   - U+0591 = 1425 (decimal)
   - U+05BE = 1470 (decimal) ← **MAQAF IS HERE**
   - U+05C7 = 1479 (decimal)

3. **Result:** The maqaf was **removed** by line 1, before line 2 could replace it with a space!

4. **Example:**
   - Original: `אֶל־הָאִשָּׁה` (el-ha'ishah, "to the woman")
   - After removing diacritics: `אל־האשה`
   - After removing maqaf (U+05BE): `אלהאשה` ❌ (no space!)
   - Expected: `אל האשה` ✅ (with space)

5. **Matching failure:**
   - Verse normalized text: `ויאמר אלהאשה` (no space between words)
   - Figurative normalized text: `ויאמר אל האשה` (with space)
   - Result: `includes()` returns `false` ❌

## The Fix

### Three Changes Made

#### 1. Filter Normalization (lines 1652-1660)
```javascript
// BEFORE (broken):
.replace(/[\u0591-\u05C7\u05F0-\u05F4]/g, '') // Removes U+05BE!
.replace(/־/g, ' ')  // Too late, already removed

// AFTER (fixed):
.replace(/־/g, ' ')  // Replace maqaf FIRST
.replace(/[\u0591-\u05BD\u05BF-\u05C7\u05F0-\u05F4]/g, '') // Exclude U+05BE
```

**Key:** Changed range to `\u0591-\u05BD\u05BF-\u05C7` which **excludes U+05BE** (maqaf).

#### 2. Highlighting Normalization (lines 1853-1862)
Same fix as above for consistency between filter and highlighting logic.

#### 3. Regex Pattern Matching (lines 1871-1891)
```javascript
// Build pattern character by character
for (let i = 0; i < figTextToUse.length; i++) {
    const char = figTextToUse[i];
    if (char === ' ') {
        // Space should match: space OR hyphen OR diacritics
        flexiblePattern += '(?:<br\\s*\\/??>|<[^>]*>|&[a-zA-Z0-9#]+;|\\{[^}]*\\}|־|[\\u0591-\\u05BD\\u05BF-\\u05C7\\u05F0-\\u05F4]|\\s)+';
    } else {
        // Allow diacritics after each character
        const escapedChar = char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        flexiblePattern += escapedChar + '(?:<br\\s*\\/??>|<[^>]*>|&[a-zA-Z0-9#]+;|\\{[^}]*\\}|[\\u0591-\\u05BD\\u05BF-\\u05C7\\u05F0-\\u05F4])*';
    }
}
```

**Key:** Spaces in normalized text now match **either space OR maqaf (־)** in the original text.

## Debug Process

### Debugging Steps Taken

1. Added console logging to see normalized text comparison
2. Discovered normalized text had no space: `אלהאשה` vs `אל האשה`
3. Identified Unicode range issue with maqaf (U+05BE)
4. Fixed normalization order
5. Updated regex pattern to handle space/hyphen interchangeably
6. Tested with Genesis 3:1, Psalms 6:8, Genesis 3:16-19
7. Verified English highlighting still worked
8. Removed debug logging

### Key Insight

The user's observation was critical: **"All fig speech with hyphens was NOT highlighted; all fig speech without hyphens WAS correctly highlighted."** This led directly to identifying the maqaf issue.

## Testing Performed

**Test Cases:**
- ✅ Genesis 3:1 - `וַיֹּאמֶר אֶל־הָאִשָּׁה` highlights correctly
- ✅ Psalms 6:8 - All Hebrew text highlights
- ✅ Genesis 3:16-19 - All verses with hyphens work
- ✅ Genesis 1:1 - `הַשָּׁמַיִם וְאֵת הָאָרֶץ` highlights correctly
- ✅ English highlighting - Still works on all verses
- ✅ All other Hebrew verses - Continue to work

## Files Modified

1. **web/biblical_figurative_interface.html**
   - Lines 1652-1660: Filter normalization
   - Lines 1853-1862: Highlighting normalization
   - Lines 1871-1891: Regex pattern building

2. **README_INTERNAL.md**
   - Updated to reflect fix status

## Related Commits

- `c3851e8` - fix: Resolve Hebrew highlighting for verses with maqaf (hyphen)
- `17980d2` - fix: CRITICAL - Restore Hebrew highlighting with proper normalized matching (attempted fix, didn't work)
- `a05824b` - fix: Fix Hebrew highlighting and improve UI with multiple enhancements (attempted fix, didn't work)

## Lessons Learned

1. **Unicode ranges are tricky** - Always check if your target character falls within removal ranges
2. **Order matters** - Replace before remove, not the other way around
3. **Test with real data** - The specific verses with maqaf were essential test cases
4. **User observations are gold** - "All verses with hyphens fail" was the key insight
5. **Character-level debugging** - Examining normalized output character-by-character revealed the issue

---

## For Future Reference

If you encounter similar highlighting issues:

1. **Check console logs** - Look for "Found 0 relevant annotations"
2. **Add debug logging** - Log normalized verse and figurative text
3. **Compare character-by-character** - Find the exact difference
4. **Check Unicode ranges** - Make sure you're not accidentally removing what you want to replace
5. **Test order of operations** - Replace before remove, escape before pattern matching

**This bug is now RESOLVED and all Hebrew highlighting works correctly.** ✅
