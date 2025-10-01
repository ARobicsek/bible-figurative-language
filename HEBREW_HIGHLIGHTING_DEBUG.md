# Hebrew Highlighting Bug - Debug Notes

## Current Status: NOT FIXED
**Date**: October 1, 2025

## Problem Description
Hebrew text with figurative language is **not being highlighted** in yellow, even though:
1. The verse has figurative language in the database
2. The verse is visible (appears when "Not Figurative" is unchecked)
3. The annotations exist and are returned by the API

## Affected Verses (Examples)
- **Psalms 6:8** - ORIGINAL ISSUE
- **Genesis 3:16**
- **Genesis 3:17**
- **Genesis 3:19**

## What We Know

### Console Logs Show
```
[Unknown] Language: hebrew, Found 0 relevant annotations for text: "עָשְׁשָׁה מִכַּעַס עֵינִי..."
```

This means annotations are being **filtered out** before highlighting attempts.

### API Response (Psalms 6:8)
The API correctly returns the annotation:
```json
{
  "figurative_text_in_hebrew": "עָשְׁשָׁ֣ה מִכַּ֣עַס עֵינִ֑י עָ֝תְקָ֗ה בְּכׇל־צוֹרְרָֽי",
  "hebrew_text": "עָשְׁשָׁ֣ה מִכַּ֣עַס עֵינִ֑י עָ֝תְקָ֗ה בְּכׇל־צוֹרְרָֽי"
}
```

The texts look identical but have **subtle diacritics differences** that prevent matching.

### Code Location
File: `web/biblical_figurative_interface.html`

**Filter function**: Lines ~1625-1700
- Function: `annotations.filter(annotation => {...})`
- This filters which annotations to highlight
- Currently returning 0 annotations for Hebrew verses

**Highlighting function**: Lines ~1794+
- Function: `highlightAnnotations(text, annotations, language)`
- Only runs if filter passes annotations through

## Attempted Fixes (All Failed)

### Attempt 1: Skip exact match for Hebrew
- Changed Hebrew to always use normalized matching
- **Result**: Still didn't work

### Attempt 2: Always include Hebrew annotations
- Made filter return `true` for all Hebrew with visible types
- **Result**: Broke highlighting for ALL verses (too permissive)

### Attempt 3: Normalized matching in filter
- Strip diacritics from both verse text and figurative text
- Compare normalized strings
- **Result**: Still not working (current state)

## The Real Issue

The problem is likely in the **normalization logic** itself. The diacritics stripping might not be complete, or there's another difference between the texts that we're not accounting for.

### Possible Causes:
1. **Different Unicode normalization** - texts might use different combining characters
2. **Whitespace differences** - invisible characters or different space types
3. **Paragraph markers** - `{ס}` or `{פ}` markers in text
4. **cleanHebrewText() function** - might be altering the text in unexpected ways
5. **HTML entities** - verse text might have entities that figurative text doesn't

## Next Steps for Debugging

### 1. Add Detailed Logging
Add console logs to see exactly what's being compared:
```javascript
console.log('Verse text raw:', highlightedText);
console.log('Fig text raw:', figurativeText);
console.log('Verse normalized:', normalizedVerseText);
console.log('Fig normalized:', normalizedFigText);
console.log('Match?', normalizedVerseText.includes(normalizedFigText));
```

### 2. Check Unicode Normalization
Hebrew texts might need Unicode normalization (NFC vs NFD):
```javascript
const normalizedVerseText = highlightedText.normalize('NFD')...
const normalizedFigText = figurativeText.normalize('NFD')...
```

### 3. Test with Specific Verse
Add a test specifically for Psalms 6:8:
```javascript
if (highlightedText.includes('עשש')) {
    console.log('=== PSALMS 6:8 DEBUG ===');
    console.log('Full verse:', highlightedText);
    console.log('Fig text:', figurativeText);
    // ... more debugging
}
```

### 4. Check cleanHebrewText() Function
The `cleanHebrewText()` function (line ~1370) is called on the figurative text.
It might be stripping something important. Try comparing:
- Raw figurative text from annotation
- After cleanHebrewText()
- Verse text

### 5. Character-by-Character Comparison
For Psalms 6:8, do a character-by-character comparison:
```javascript
for (let i = 0; i < Math.min(verseText.length, figText.length); i++) {
    if (verseText[i] !== figText[i]) {
        console.log(`Diff at ${i}: verse="${verseText[i]}" (${verseText.charCodeAt(i)}) vs fig="${figText[i]}" (${figText.charCodeAt(i)})`);
    }
}
```

## Files to Review

1. **web/biblical_figurative_interface.html**
   - Line ~1370: `cleanHebrewText()` function
   - Line ~1625: Filter function (`relevantAnnotations`)
   - Line ~1794: Highlighting logic

2. **web/api_server.py**
   - Check what the API is actually returning
   - Verify `hebrew_text_stripped` vs `figurative_text_in_hebrew`

## Test Data

### Psalms 6:8 Query
```bash
curl "http://localhost:5000/api/verses?books=Psalms&chapters=6&verses=8"
```

### Genesis 3:16-19 Query
```bash
curl "http://localhost:5000/api/verses?books=Genesis&chapters=3&verses=16-19"
```

## Performance Context

**Note**: We just completed major performance optimizations:
- Added database indexes (100-1300x speedup)
- Added Flask-Caching (5-minute TTL)
- System is stable and fast
- This is purely a highlighting display bug, not a performance issue

## Related Commits

- `10ecae5` - Performance optimization (indexes + caching) ✅ WORKING
- `15a9454` - UI improvements (25 verses/page, fix negative count) ✅ WORKING
- `a05824b` - Hebrew highlighting fix attempt #1 ❌ FAILED
- `17980d2` - Hebrew highlighting fix attempt #2 ❌ FAILED (current)

---

**CRITICAL**: The highlighting logic is complex and fragile. Any fix must:
1. Preserve highlighting for verses that currently work
2. Fix highlighting for verses with diacritics variations
3. Not break English highlighting
4. Be thoroughly tested locally before pushing
