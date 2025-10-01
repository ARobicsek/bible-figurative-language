# Next Session: Fix Hebrew Text Highlighting Bug

## Context
We're working on **Tzafun** (https://tzafun.onrender.com), a biblical figurative language concordance with 8,373 analyzed verses.

**Recent Success**: Just completed major performance optimizations achieving **100-1300x speedup** through database indexes and query caching. System is stable and fast! 🎉

## Current Critical Issue: Hebrew Highlighting Not Working

### The Problem
Hebrew text with figurative language is **not being highlighted in yellow**, even though:
- ✅ The verse has figurative language in the database
- ✅ The verse is visible when filtering
- ✅ The API returns the annotation correctly
- ❌ The highlighting doesn't appear on screen

### Affected Verses (Test Cases)
1. **Psalms 6:8** - Original reported issue
2. **Genesis 3:16, 3:17, 3:19** - Also broken

### What We Know
Console logs show:
```
[Unknown] Language: hebrew, Found 0 relevant annotations for text: "עָשְׁשָׁה מִכַּעַס עֵינִי..."
```

This means the **filter is rejecting annotations** before highlighting even tries.

## Root Cause
The verse text and figurative text have **subtle diacritics differences**:
- Verse: `עָ֝תְקָ֗ה` (with certain cantillation marks)
- Figurative: `עָתְקָ֗ה` (with slightly different marks)

The filter's normalization logic is **not working** - it's still failing to match these texts.

## What We've Tried (All Failed)
1. ❌ Always use normalized matching for Hebrew (skipped exact match)
2. ❌ Always include Hebrew annotations (too permissive, broke everything)
3. ❌ Current: Normalize by stripping `[\u0591-\u05C7\u05F0-\u05F4]` - STILL NOT WORKING

## Your Task

**Fix the Hebrew text highlighting** so verses like Psalms 6:8 and Genesis 3:16-19 show yellow highlights.

### Step 1: Debug the Current State
Add detailed logging to see what's actually being compared:

In `web/biblical_figurative_interface.html` around line 1644-1666 (the filter), add:
```javascript
if (language === 'hebrew' && highlightedText.includes('עשש')) {
    console.log('=== DEBUG PSALMS 6:8 ===');
    console.log('Raw verse text:', highlightedText);
    console.log('Raw fig text:', figurativeText);
    console.log('Normalized verse:', normalizedVerseText);
    console.log('Normalized fig:', normalizedFigText);
    console.log('Includes?', normalizedVerseText.includes(normalizedFigText));
}
```

Test locally with Psalms 6:8 and see what the logs show.

### Step 2: Possible Solutions

**Option A: Unicode Normalization**
Hebrew might need Unicode NFC/NFD normalization:
```javascript
const normalizedVerseText = highlightedText.normalize('NFD')
    .replace(/[\u0591-\u05C7\u05F0-\u05F4]/g, '')...
```

**Option B: More Aggressive Stripping**
Current regex might not catch all diacritics. Try:
```javascript
.replace(/[\u0591-\u05FF]/g, '') // Strip ALL Hebrew marks
.replace(/[^\u05D0-\u05EA]/g, '') // Keep ONLY Hebrew letters (א-ת)
```

**Option C: Character-by-Character Comparison**
Compare byte-by-byte to find exactly what's different:
```javascript
for (let i = 0; i < Math.min(verseText.length, figText.length); i++) {
    if (verseText[i] !== figText[i]) {
        console.log(`Diff at ${i}: "${verseText[i]}" (U+${verseText.charCodeAt(i).toString(16).toUpperCase()})`);
    }
}
```

**Option D: Check cleanHebrewText() Function**
The `cleanHebrewText()` function (line ~1370) might be the issue. It's called on figurative text but not verse text.

### Step 3: Test Thoroughly
Before pushing, verify ALL these work:
- ✅ Psalms 6:8 highlights
- ✅ Genesis 3:16, 3:17, 3:19 highlight
- ✅ English highlighting still works (test Genesis 3:16 English side)
- ✅ Other Hebrew verses that were working still work

### Step 4: Deploy
Once working locally:
```bash
git add web/biblical_figurative_interface.html
git commit -m "fix: Resolve Hebrew highlighting with proper diacritics normalization"
git push origin main
```

## Important Files

### Main File to Edit
- `web/biblical_figurative_interface.html`
  - Line ~1370: `cleanHebrewText()` function
  - Line ~1625-1700: Filter function (where the bug is)
  - Line ~1794+: Highlighting logic

### Debug Reference
- See `HEBREW_HIGHLIGHTING_DEBUG.md` for detailed debug notes

### Testing
Local server:
```bash
cd web
python api_server.py
# Visit http://localhost:5000
```

Test queries:
```bash
curl "http://localhost:5000/api/verses?books=Psalms&chapters=6&verses=8"
curl "http://localhost:5000/api/verses?books=Genesis&chapters=3&verses=16-19"
```

## Success Criteria
When you see **yellow highlighting** on:
1. Psalms 6:8 Hebrew text
2. Genesis 3:16, 3:17, 3:19 Hebrew text
3. All other verses that previously had highlighting

**You're done!** 🎉

## Additional Context

### Recent Wins (Working Great!)
- ✅ Database indexes added (100-1300x faster queries)
- ✅ Flask-Caching (5-min TTL for repeated queries)
- ✅ UI improvements (25 verses/page, precise "Load verses 26-32" button)
- ✅ Reset icons for Chapters/Verses
- ✅ Clean semicolon instructions

### System Status
- Production: https://tzafun.onrender.com
- Auto-deploys from main branch (~2-3 minutes)
- Free tier: 512MB RAM, fast with optimizations
- Database: 51MB SQLite with 8,373 verses, 5,933 instances

---

**Start here**: Read `HEBREW_HIGHLIGHTING_DEBUG.md`, then add debug logging to see what the filter is comparing. The answer is in the details of what's different between the two Hebrew strings! 🔍
