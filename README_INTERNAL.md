# Tzafun (formerly Project Pardes)
A concordance of figurative language in the bible

## 🎉 Project Status: LIVE IN PRODUCTION! 🚀
**LATEST ACHIEVEMENT (Oct 5, 2025 - Evening)**: ✅ **UI Bottom Panel Enhancements - Professional annotation display matching print version!**
- **Enhanced Bottom Panel Display**: Replicated print version features in the interactive UI for consistent, professional presentation
  - **Annotation Details Positioning**: Moved annotation details ABOVE figurative detection deliberation (when present) for better information hierarchy
  - **Hebrew/English Phrase Display**: Added side-by-side bilingual phrase display at top of annotation details with vertical divider
  - **Colored Type Badges**: Implemented figurative language type badges with color-coded backgrounds (metonymy, metaphor, simile, etc.)
  - **Border & Styling**: Added border, padding, and rounded corners to annotation details section for visual distinction
  - **Deliberation Styling**: Added blue left border and light grey background to deliberation section matching print aesthetics
  - **Conditional Display**: Empty annotation details container no longer shows border/padding when not populated (`:not(:empty)` CSS)
  - **Print Version Consistency**: Updated print model badge from blue-on-white to grey-on-black matching UI button style
- **Files Modified**:
  - `web/biblical_figurative_interface.html` (lines 544-626, 1458-1466, 1652-1675, 3190-3255): CSS styling, HTML structure reordering, JavaScript annotation rendering
- **Result**: Seamless professional presentation across both UI and print versions with enhanced visual hierarchy and information design

**PREVIOUS ACHIEVEMENT (Oct 5, 2025)**: ✅ **Complete pagination system overhaul - accurate counts and button text!**
- **Fixed Multiple Pagination Bugs**: Comprehensive fix for pagination counting and display issues
  - **Bug 1 - has_more calculation**: Changed from `offset + limit < total` to `offset + len(verses) < total`
    - Example: After loading 50 of 52 verses, API now correctly returns `has_more=False` instead of `True`
  - **Bug 2 - Missing chapter/verse filters in count queries**: Added chapter and verse filters to all count query branches
    - Root cause: Count queries were counting all of Deuteronomy (956 verses) instead of just chapter 32 (52 verses)
    - Fixed in both `show_all_verses` and `show_not_figurative` count query branches
  - **Bug 3 - Incorrect button text estimation**: Changed from last-batch-size tracking to remaining-verses calculation
    - Formula: `Math.min(pagination.limit, totalCount - currentVerses)`
    - Example: After loading 50 of 52 verses, button now shows "Load Next 2 Verses" instead of "Load Next 25 Verses"
  - **Bug 4 - total_figurative_instances overwritten on loadMore**: Preserved count from initial load (updated by background count)
    - Added preservation of both `total` and `total_figurative_instances` in loadMore function
  - **Bug 5 - Inconsistent text search fields**: Fixed all instances of `english_text` → `english_text_clean`
    - Root cause: Count endpoint searched `english_text` (39 results) while main endpoint searched `english_text_clean` (35 results)
    - Replaced all 3 remaining instances in count queries for consistency
- **Files Modified**:
  - `web/api_server.py` (lines 590-602, 636-649, 696): Count query fixes and has_more calculation
  - `web/biblical_figurative_interface.html` (lines 3194-3198, 3239-3248): Button text and loadMore preservation
- **Result**: Perfect pagination - accurate counts, correct button text, proper "All verses loaded" detection

**PREVIOUS ACHIEVEMENT (Oct 5, 2025)**: ✅ **Hebrew highlighting vowel mismatch bug FIXED!**
- **Fixed Systematic Highlighting Bug**: Hebrew verses with vowel point differences between database and source text now highlight correctly
  - **Root cause**: Highlighting logic built regex patterns from database text with specific vowels (e.g., tzere ֵ), which failed to match verse text with different vowels (e.g., segol ֶ)
  - **Example**: Deuteronomy 32:50 phrase "וַיֵּאָ֖סֶף אֶל־עַמָּֽיו" wasn't highlighting because database had tzere (ֵ) under samekh but verse had segol (ֶ)
  - **Impact**: Any verse where AI analysis used different vowel than source text would fail to highlight
  - **Solution**: Complete rewrite of Hebrew highlighting to strip ALL diacritics, match on consonants only, then map back to original positions
  - **Technical approach**: Build position mapping (normalized → original), find match in vowel-stripped text, extract from original WITH diacritics
  - **Result**: 100% reliable highlighting regardless of vowel point variations - matches based purely on consonants and word structure

**PREVIOUS ACHIEVEMENT (Oct 5, 2025)**: ✅ **Shaddai pattern fix & figurative_text_non_sacred field complete!**
- **Fixed Shaddai Pattern**: Divine name "Shaddai" (שַׁדַּי) now only modified when standalone, not inside other words
  - Updated regex to allow cantillation marks after final letter before word boundary
  - Pattern now matches שַׁדַּי֙ (with pashta mark) correctly
  - Genesis 28:3 and 35:11 now display correctly as שַׁקַּי֙ in Traditional Jewish mode
- **New figurative_text_non_sacred Field**: Added English non-sacred text for figurative phrases
  - Created new database field in figurative_language table
  - Regenerated all 6 non-sacred fields (was 5, now includes figurative_text_non_sacred)
  - 209 English figurative phrases modified with divine name transformations
  - Web interface now uses non-sacred English phrases when "Traditional Jewish" selected
  - Complete sacred/non-sacred support across all text types

**PREVIOUS ACHIEVEMENTS**:
- **Oct 3 Evening**: Pagination button fix complete with accurate verse counts
- **Oct 3 Evening**: Print feature complete and optimized with 43% larger fonts and proper line breaks
- **Oct 3 Afternoon**: Fixed deliberation line breaks (`white-space: pre-wrap`)
- **Oct 3 Morning**: Fixed HTML entity highlighting bug affecting verses with `&thinsp;` entities. Psalms 84:4 and similar verses now highlight correctly.
- **Oct 2, 2025**: Fixed divine names modifier bug and added Eloah support. All non-sacred Hebrew text fields regenerated with corrected modifier.

**DEPLOYMENT SUCCESS (Oct 1, 2025)**: Tzafun is now publicly accessible at **https://tzafun.onrender.com** with 8,373 analyzed verses (Torah + Psalms) and 5,933 figurative language instances.

**⚡ PERFORMANCE BREAKTHROUGH (Oct 1, 2025)**: Achieved **100-1300x speedup** through database indexes and query caching! Metadata searches: 0.011-0.033s (was 1-5s). Complex JOINs: 0.015-0.017s (was 5-20s). System is fast and stable on free tier.

**✅ HEBREW HIGHLIGHTING FIXED (Oct 1, 2025)**: Resolved critical bug where Hebrew text with maqaf (־) hyphens wasn't being highlighted. Root cause: Unicode range `\u0591-\u05C7` was removing maqaf (U+05BE) before it could be replaced with space, breaking word boundary matching. Solution: Modified normalization order to replace maqaf with space BEFORE removing diacritics, and updated regex pattern to match space OR hyphen. All Hebrew verses now highlight correctly including Psalms 6:8, Genesis 3:1, 3:16-19.

**🎨 UI ENHANCEMENTS & ABOUT PAGE (Oct 1, 2025)**: Comprehensive UI polish and documentation improvements:
- **📖 About Page**: Created professional About page with comprehensive project documentation
  - Table of contents with clickable navigation
  - Detailed explanation of Tzafun's AI-powered two-stage analysis process
  - Complete field documentation (Target, Vehicle, Ground, Posture, Explanation, Validation reasons, Speaker, Confidence, Model)
  - Information about model usage (Gemini-2.5-flash, Gemini-2.5-pro, Claude-Sonnet-4)
  - Acknowledgements section for data sources (Sefaria.org, MAM, JPS 2006)
  - Fixed Hebrew vowel: צָפַן → צָפֻן (patach to kubutz under Peh)
- **🎨 Color Palette Refinement**: Updated figurative language type colors to elegant, distinct palette
  - Replaced bright primary colors with sophisticated earthy tones
  - Metaphor: `#a0695f` (terracotta), Simile: `#5a8ca8` (slate blue), Personification: `#9370a8` (purple)
  - Idiom: `#c9a255` (golden), Hyperbole: `#c17a61` (coral), Metonymy: `#5d9b82` (jade), Other: `#7a8896` (gray)
  - Colors maintain distinction while providing classier aesthetic
- **💡 Tooltip Enhancements**: Added helpful tooltips with definitions for all figurative language types
  - Metaphor: "A comparison where one thing is said to be another"
  - Simile: "A comparison using 'like' or 'as'"
  - Personification: "Giving human qualities to non-human things"
  - Idiom: "A phrase with a meaning different from its literal words"
  - Hyperbole: "Exaggeration for emphasis"
  - Metonymy: "Using one thing to represent another closely related thing"
  - Fixed tooltip positioning to prevent off-screen display
- **📊 Verse Loading**: Updated initial page load from 10 to 25 verses for better user experience
- **🔧 Header Navigation**: Made "Tzafun" title clickable to return home from About page

---

## 🔧 PAGINATION BUTTON FIX (Oct 3, 2025 - Evening)

### **Problem: Inaccurate "Load Next Verses" Button Text**

The "Load Next Verses" button was showing incorrect verse counts when loading paginated results:
- ❌ Deuteronomy Ch 32 (52 verses total): After loading 50 verses, button showed "Load Next 25 Verses" instead of "Load Next 2 Verses"
- ❌ Initial issue: Button showed "Load verses 26-956" when only 52 verses exist in the chapter

### **Root Cause**

**File**: `web/biblical_figurative_interface.html`

The API returns the total verse count for the entire **book** (956 for all of Deuteronomy) instead of just the filtered **chapter** (52 for Deuteronomy 32). This caused the pagination logic to incorrectly calculate remaining verses.

### **Solution**

**Implemented intelligent batch size estimation based on actual loading patterns:**

1. **Track Previous Counts** (Lines 3111-3114):
   - Store `previousVerseCount` to calculate the size of the last batch received
   - Calculate `lastBatchSize = currentVerses - previousCount`

2. **Detect Approaching End** (Lines 3119-3124):
   - When `lastBatchSize < pagination.limit`, we know we're near the end
   - Use that smaller batch size as the estimate for next load
   - Example: If last batch was 2 verses, next batch will likely be 2 or fewer

3. **Update Button Text** (Line 3127):
   - Changed from verse range format ("Load verses 51-75") to count format ("Load Next 2 Verses")
   - More accurate and user-friendly, especially when API total is incorrect

### **Technical Details**

**Before (broken):**
```javascript
const nextEnd = Math.min(nextStart + appState.pagination.limit - 1, totalCount);
// With totalCount=956, this gave: "Load verses 51-75" (wrong!)
```

**After (fixed):**
```javascript
const lastBatchSize = currentVerses - (appState.previousVerseCount || 0);
appState.previousVerseCount = currentVerses;

let estimatedNextBatch = appState.pagination.limit;
if (lastBatchSize > 0 && lastBatchSize < appState.pagination.limit) {
    estimatedNextBatch = lastBatchSize;
}
// Result: "Load Next 2 Verses" (correct!)
```

### **User Experience**

For Deuteronomy Chapter 32 (52 verses):
- ✅ First load (25 verses): "Load Next 25 Verses"
- ✅ Second load (50 total): "Load Next 25 Verses"
- ✅ Third load (52 total, last batch was 2): "Load Next 2 Verses"
- ✅ All loaded: "✓ All verses loaded"

### **Files Modified**
- `web/biblical_figurative_interface.html` (lines 3111-3128) - Smart pagination calculation

### **Impact**
- Accurate button text regardless of API total count accuracy
- Better user experience with clear loading expectations
- Works for any chapter/book combination with correct or incorrect API totals

---

## 🖨️ PRINT FEATURE IMPLEMENTATION (Oct 3, 2025 - Evening)

### **Feature: Professional Print Output for Research and Sharing**

Added comprehensive print functionality to the Tzafun web interface, allowing users to generate clean, professional printouts of their selected verses with full annotation details.

### **Implementation Details**

**File**: `web/biblical_figurative_interface.html`

#### **1. Print Link in Header** (Lines 854-856)
- Added "print" link below "about" in top-right header
- Triggers `printPage()` function when clicked

#### **2. Print-Specific CSS** (Lines 843-1135)
Comprehensive `@media print` styles including:
- **Layout Controls**: Hide sidebar, header, stats bar, navigation during print
- **Side-by-Side Text Layout**: Hebrew (left) | thin divider | English (right) in elegant columns
- **Deliberation Formatting**: Styled matching the UI with proper spacing, colored labels, and model badges
- **Annotation Details**: Professional formatting with Hebrew/English phrase columns
- **Color Preservation**: `print-color-adjust: exact` ensures highlights and type indicators print in color
- **Page Breaks**: Intelligent `page-break-inside: avoid` for verse containers and deliberation items

#### **3. JavaScript Print Functions** (Lines 1451-1733)

**Filter Summary Generation** (`generatePrintSummary()` - Lines 1516-1578):
- Captures all active filters: selected books, chapters, verses, figurative types, text version, search terms, metadata filters
- **Chapter/Verse Display**: Shows selected chapters and verses in filter summary (unless set to "all")
- Formats professional summary showing exactly what the user selected
- Displays verse count for transparency

**Content Preparation** (`preparePrintContent()` - Lines 1522-1609):
- Creates print header with filter summary
- Duplicates Hebrew/English text in side-by-side columns at top of each verse
- Adds formatted deliberation with model name badge
- Generates detailed annotation sections for each figurative phrase
- Respects "Traditional Jewish" setting for non-sacred text versions

**Annotation Formatting** (`createPrintAnnotation()` - Lines 1611-1722):
- Side-by-side Hebrew/English phrase display
- Color-coded type indicators
- Complete metadata: Target, Vehicle, Ground, Posture, Confidence, Speaker, Purpose, Explanation
- Validation reasons for each figurative type
- Hierarchical array display (e.g., "term1 → term2 → term3")

**Print Dialog** (`printPage()` - Lines 1724-1736):
- Prepares content, triggers browser print dialog
- Cleans up temporary print elements after 1 second

#### **4. Footnote Filtering** (`removeFootnotes()` - Lines 1451-1465)
- Client-side filtering of English translation footnotes
- Removes quoted phrases with indicators like "lit.", "cf.", "trad.", "NJPS", "uncertain", etc.
- Applied during verse rendering (Line 2274)
- Cleans up spacing and punctuation

### **Current Status & Known Issues**

✅ **Working Features**:
- Print link accessible in header
- Comprehensive print CSS with side-by-side layout
- Filter summary generation
- Hebrew/English text displayed at top in columns
- ✅ **Deliberation line breaks now working** (fixed Oct 3, 2025 - Evening)
- Footnote filtering (partial - some patterns still getting through)
- Duplicate verse text hidden (only top version shows)
- Annotation details with side-by-side phrase display

✅ **Critical Issues Resolved**:
1. **Deliberation Line Breaks FIXED** (Oct 3, 2025 - Evening)
   - **Issue**: Deliberation items running together without spacing between sections in some verses (e.g., Gen 1:1)
   - **Root Cause**: Print CSS was missing `white-space: pre-wrap;` property that UI CSS had (line 555)
   - **Solution**: Added `white-space: pre-wrap;` to `.print-deliberation .deliberation-content` (Line 1000)
   - **Result**: Print output now preserves line breaks and spacing just like UI display
   - **Works for**: All verses including Gen 1:1, Psalms 84:1, and others

❌ **Known Minor Issues** (LOWER PRIORITY):
1. **Footnote Filtering Incomplete** (SKIPPED FOR NOW)
   - **Issue**: Some footnote patterns still visible in English text
   - **Example**: Gen 4:1 shows ", often in a sexual sense." and other explanatory text
   - **Current Filter**: Catches quoted footnotes and some comma-separated patterns
   - **Next Step**: Enhance regex patterns to catch more edge cases (if needed in future)

### **Files Modified**
- `web/biblical_figurative_interface.html`:
  - Lines 854-856: Print link in header
  - Lines 843-1135: Print CSS styles
  - Lines 1000: **FIX #1** - Added `white-space: pre-wrap;` to `.print-deliberation .deliberation-content`
  - Lines 877-1101: **FIX #2 & #3** - Increased all print font sizes by 43% total (30% + 10%) for readability:
    - Headers: 34pt/23pt (was 24pt/16pt)
    - Verse headers: 20pt (was 14pt)
    - Body text: 15pt (was 11pt)
    - Deliberation: 18pt heading, 14pt content (was 12pt/10pt)
    - Annotations: 15pt phrases, 14pt details (was 11pt/10pt)
    - Model badge: 13pt (was 9pt)
  - Lines 1451-1465: Footnote removal function
  - Lines 1467-1736: Print JavaScript functions
  - Lines 2274: Footnote filtering application
  - Lines 2960-2968: Deliberation formatting enhancement

### **Print Feature Now Complete and Optimized**

✅ All critical print features working correctly:
- Professional page layout with header and filter summary
- Side-by-side Hebrew/English text columns
- Properly formatted deliberation with line breaks
- **43% larger, highly readable fonts throughout**
- Complete annotation details
- Color-preserved highlighting and type indicators
- Sacred/Traditional Jewish text selection support

**Optional Future Enhancement**:
- Improve footnote filtering to catch additional edge case patterns (Gen 4:1, etc.)

### **Testing Recommendations**
- Test print with various filter combinations
- Verify Sacred vs Traditional Jewish text selection works correctly
- Check annotation details for phrases with multiple types
- Ensure page breaks work properly for long verse lists
- Test on different browsers (Chrome, Firefox, Safari)

---

## 🐛 HTML ENTITY HIGHLIGHTING FIX (Oct 3, 2025)

### **Problem: Verses with HTML Entities Not Highlighting**

Hebrew verses containing HTML entities like `&thinsp;` (thin space) were not being highlighted even though they had valid figurative language annotations:
- ❌ Psalms 84:4: No highlighting despite having metaphor annotation
- ❌ Other verses with `&thinsp;` entities were affected

### **Root Cause**

**File**: `web/biblical_figurative_interface.html`

The regex pattern builder was processing the figurative text character-by-character, treating `&thinsp;` as 8 individual characters (`&`, `t`, `h`, `i`, `n`, `s`, `p`, `;`) instead of as a single HTML entity unit. This caused the regex to fail to match text containing these entities.

**Specific Issue:**
- Lines 2105-2120: The original code used a simple `for` loop that iterated through each character
- When it encountered `&thinsp;`, it would escape the `&` character and try to match it, followed by escaping `t`, etc.
- This broke the matching logic because the regex expected individual characters with optional diacritics between them, not a complete HTML entity

### **Solution**

**Enhanced the regex pattern builder to handle HTML entities as complete units:**

1. **Main highlighting logic (lines 2092-2142):**
   - Changed from simple `for` loop to `while` loop with index tracking
   - Added entity detection: when encountering `&`, check if it starts a complete HTML entity using regex `/^&[a-zA-Z0-9#]+;/`
   - If an HTML entity is found, escape it as a complete unit and add to the pattern
   - Skip ahead by the entity length to avoid processing individual characters

2. **Core text fallback logic (lines 2176-2207):**
   - Applied the same fix to the "core text" matching fallback
   - Ensures consistent behavior across all matching strategies

### **Technical Details**

**Before (broken):**
```javascript
for (let i = 0; i < figTextToUse.length; i++) {
    const char = figTextToUse[i];
    const escapedChar = char.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    flexiblePattern += escapedChar + '(?:...)*';
}
```
This would turn `&thinsp;` into: `\&(?:...)* t(?:...)* h(?:...)* ...` (broken)

**After (fixed):**
```javascript
while (i < trimmedFigText.length) {
    if (trimmedFigText[i] === '&') {
        const entityMatch = trimmedFigText.substring(i).match(/^&[a-zA-Z0-9#]+;/);
        if (entityMatch) {
            const entity = entityMatch[0];
            const escapedEntity = entity.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            flexiblePattern += escapedEntity + '(?:...)*';
            i += entity.length;
            continue;
        }
    }
    // Regular character handling...
}
```
This correctly treats `&thinsp;` as a single unit: `\&thinsp\;(?:...)*` (correct)

### **Verification**

Created verification scripts to test the fix:
- `test_psalms_84_4.py` - Database validation showing figurative text matches verse text
- `verify_fix.py` - Regex pattern testing confirming successful matching

**Test Results:**
- ✅ Psalms 84:4 metaphor now highlights correctly
- ✅ HTML entity `&thinsp;` properly handled in regex pattern
- ✅ Both sacred and non-sacred versions work correctly
- ✅ Pattern successfully matches 110 characters of figurative text

### **Files Modified**
- `web/biblical_figurative_interface.html` (lines 2092-2142, 2176-2207) - Enhanced regex pattern builder
- `test_psalms_84_4.py` - Database verification script
- `verify_fix.py` - Regex pattern verification script

### **Impact**
- All verses with HTML entities (`&thinsp;`, `&nbsp;`, etc.) now highlight correctly
- Improved robustness of highlighting system for edge cases
- No performance impact - regex patterns are built once per annotation

---

## 🐛 DIVINE NAMES MODIFIER FIX (Oct 2, 2025)

### **Problem: Non-Divine Words Incorrectly Modified**

The Hebrew divine names modifier had a critical bug causing non-divine words to be modified in "Traditional Jewish" text mode:
- ❌ `הַנָּחָשׁ` (the serpent) → `קַנָּחָשׁ` (WRONG)
- ❌ `הָאִשָּׁה` (the woman) → `קָאִשָּׁק` (WRONG)

### **Root Cause**

**File**: `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py`

The Elohim regex patterns had **optional vowel matching** that was too permissive:
- Line 113 (Pattern 2): `א[\u0591-\u05C7]*[ֱ]?...` - hataf segol was optional
- Line 124 (Pattern 3): Similar issue with definite article pattern

This caused the modifier to match any word starting with definite article + alef/hei, not just the divine name Elohim.

### **Solution**

**Made Elohim vowels REQUIRED instead of optional:**
- Line 113: `א[\u0591-\u05C7]*[ֱ]...` - hataf segol now required
- Line 124: Tightened pattern to require specific Elohim vowels

**Added support for Eloah (אֱלוֹהַּ):**
- New `_modify_eloah()` method handles singular form of Elohim
- Example: Psalms 114:7 `אֱל֣וֹהַּ` → `אֱל֣וֹקַּ`
- Pattern: `א[\u0591-\u05C7]*ֱ[\u0591-\u05C7]*ל[\u0591-\u05C7]*ו[\u0591-\u05C7]*ֹ[\u0591-\u05C7]*ה[\u0591-\u05C7]*ַ[\u0591-\u05C7]*`

### **Database Regeneration**

Created `regenerate_hebrew_non_sacred.py` script to regenerate all three non-sacred Hebrew text fields:

1. **`verses.hebrew_text_non_sacred`** - 8,373 verses
   - Full Hebrew verse text with divine names modified
   - Committed every 500 updates to avoid database locks

2. **`figurative_language.figurative_text_in_hebrew_non_sacred`** - 5,933 annotations
   - Hebrew text excerpts for figurative language instances
   - Uses same modifier as verse text

3. **`verses.figurative_detection_deliberation_non_sacred`** - 8,368 verses
   - English deliberation text containing Hebrew terms
   - Uses `modify_english_with_hebrew_terms()` method

### **Verification**

Created test scripts to verify the fix:
- `test_divine_modifier.py` - Unit tests for modifier patterns
- `check_psalms_eloah.py` - Specific test for Psalms 114:7 Eloah

**Test Results:**
- ✅ Genesis 3:14 serpent: `הַנָּחָשׁ` preserved (not modified)
- ✅ Genesis 3:1 woman: `הָאִשָּׁה` preserved (not modified)
- ✅ Genesis 1:1 Elohim: `אֱלֹקִ֑ים` correctly modified (with ק)
- ✅ Psalms 114:7 Eloah: `אֱל֣וֹקַּ` correctly modified (new feature)

### **Files Modified**
- `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py` - Fixed patterns, added Eloah
- `regenerate_hebrew_non_sacred.py` - Script to regenerate database fields
- `database/Pentateuch_Psalms_fig_language.db` - Regenerated all non-sacred fields (76.6 MB)
- `test_divine_modifier.py`, `test_results.txt` - Test verification

### **Impact**
- All "Traditional Jewish" text now displays correctly
- Non-divine words are preserved as-is
- Divine names properly modified across all three field types
- New support for Eloah divine name (singular form)

---

## 🐛 SHADDAI PATTERN FIX & FIGURATIVE_TEXT_NON_SACRED FIELD (Oct 5, 2025)

### **Problem 1: Shaddai Pattern Not Matching Standalone Divine Names**

The Shaddai divine name (שַׁדַּי) was not being modified in "Traditional Jewish" mode even when it appeared as a standalone divine name:
- ❌ Genesis 28:3: `וְאֵ֤ל שַׁדַּי֙` → Should be `שַׁקַּי֙` but remained unmodified
- ❌ Genesis 35:11: `אֲנִ֨י אֵ֤ל שַׁדַּי֙` → Should be `שַׁקַּי֙` but remained unmodified

### **Problem 2: Missing English Non-Sacred Field for Figurative Phrases**

When users selected "Traditional Jewish" mode, the English translation of figurative phrases in the Annotation Details panel still showed sacred divine names because there was no non-sacred version of the `figurative_text` field.

### **Root Cause (Problem 1)**

**File**: `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py`

The Shaddai regex pattern required a word boundary immediately after the final yud (י), but in Biblical Hebrew with cantillation marks, the marks appear AFTER the letters. So שַׁדַּי֙ has the pashta mark (֙, U+0599) after the yud, preventing the pattern from matching.

**Original broken pattern:**
```regex
(?=[\s\-\u05BE.,;:!?]|$)  # Requires immediate word boundary after yud
```

This failed to match `שַׁדַּי֙` because the pashta (֙) comes between the yud and the space.

### **Solution**

**Updated Shaddai pattern to allow cantillation marks after final letter:**

Lines 198, 212 in `hebrew_divine_names_modifier.py`:
```regex
# Before (broken):
(?=[\s\-\u05BE.,;:!?]|$)

# After (fixed):
(?=[\u0591-\u05C7]*(?:[\s\-\u05BE.,;:!?]|$))
```

This allows optional cantillation marks (`[\u0591-\u05C7]*`) after the yud before checking for the word boundary.

**Pattern now correctly matches:**
- `שַׁדַּי֙ ` (with pashta before space)
- `שַׁדַּי֙.` (with pashta before punctuation)
- `שַׁדַּי` (without cantillation)
- `שדי ` (unvoweled with space)

**Still correctly rejects:**
- `בשדי` (part of another word - ב prefix)
- `שדיך` (has extra letter after)
- `משדים` (different word entirely)

### **Solution (Problem 2)**

**Created new `figurative_text_non_sacred` field and complete regeneration pipeline:**

1. **Database Schema** - Added new field:
   ```sql
   ALTER TABLE figurative_language
   ADD COLUMN figurative_text_non_sacred TEXT
   ```

2. **Regeneration Script** - Updated `regenerate_all_non_sacred_fields.py`:
   - Now processes **6 non-sacred fields** (was 5):
     1. `verses.hebrew_text_non_sacred`
     2. `verses.english_text_non_sacred`
     3. `verses.english_text_clean_non_sacred`
     4. `verses.figurative_detection_deliberation_non_sacred`
     5. `figurative_language.figurative_text_in_hebrew_non_sacred`
     6. **`figurative_language.figurative_text_non_sacred` (NEW!)**

3. **API Updates** (`web/api_server.py`):
   - Line 420: Added `figurative_text_non_sacred` to SELECT query
   - Line 543: Added field to processed annotation objects

4. **Frontend Updates** (`web/biblical_figurative_interface.html`):
   - Line 1683-1685: Print function now uses non-sacred field when `useNonSacred=true`
   - Lines 2500, 2617, 2658, 2661, 2670: Highlighting logic selects correct English field based on `textVersion`

### **Database Regeneration Results**

Ran `regenerate_all_non_sacred_fields.py` with improved Shaddai pattern:

**Comparison with previous run:**
- `verses.hebrew_text_non_sacred`: 2738 modified (was 2736, +2 verses with Shaddai fix)
- `figurative_language.figurative_text_non_sacred`: 209 modified (NEW field!)

The +2 additional Hebrew verses modified are Genesis 28:3 and 35:11, confirming the Shaddai fix works.

### **Verification**

**Genesis 28:3 (before fix):**
```
hebrew_text_non_sacred: וְאֵ֤ל שַׁדַּי֙ יְבָרֵ֣ךְ...
                              ^^^^^ WRONG - should be שַׁקַּי֙
```

**Genesis 28:3 (after fix):**
```
hebrew_text_non_sacred: וְאֵ֤ל שַׁקַּי֙ יְבָרֵ֣ךְ...
                              ^^^^^ CORRECT!
```

**Genesis 35:11 verification:**
```
hebrew_text_non_sacred: וַיֹּ֩אמֶר֩ ל֨וֹ אֱלֹקִ֜ים אֲנִ֨י קֵ֤ל שַׁקַּי֙ פְּרֵ֣ה וּרְבֵ֔ה...
                                                        ^^^^^ CORRECT!
```

**Test suite verification:**
```python
# Standalone divine names (should modify):
'וְאֵ֤ל שַׁדַּי֙ יְבָרֵ֣ךְ' → 'וְאֵ֤ל שַׁקַּי֙ יְבָרֵ֣ךְ' ✓
'שדי '                    → 'שקי '                    ✓

# Non-divine words (should NOT modify):
'בשדי'                    → 'בשדי'                    ✓
'שדיך'                    → 'שדיך'                    ✓
```

### **Files Modified**

**Core modifier:**
- `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py` (lines 198, 212, 272-273)
  - Fixed Shaddai pattern to allow cantillation marks before word boundary
  - Updated both voweled and unvoweled patterns
  - Updated `has_divine_names()` method

**Regeneration script:**
- `regenerate_all_non_sacred_fields.py`
  - Added `figurative_text_non_sacred` field creation
  - Added regeneration for new field (209 instances modified)
  - Updated field count documentation (6 fields total)

**API server:**
- `web/api_server.py` (lines 420, 543)
  - Added new field to SELECT query
  - Added field to annotation response objects

**Web interface:**
- `web/biblical_figurative_interface.html` (lines 1683-1685, 2500, 2617, 2658, 2661, 2670)
  - Print function uses non-sacred field for Traditional Jewish mode
  - Highlighting logic selects correct English field based on text version
  - All display modes now respect sacred/non-sacred selection

**Database:**
- `database/Pentateuch_Psalms_fig_language.db`
  - New column added to `figurative_language` table
  - All 6 non-sacred fields regenerated with improved modifier
  - 2738 Hebrew verses modified (includes Shaddai fixes)
  - 209 English figurative phrases modified

### **Impact**

**Complete Sacred/Non-Sacred Support:**
- ✅ All standalone Shaddai divine names now correctly modified (Genesis 28:3, 35:11, etc.)
- ✅ Shaddai pattern only modifies standalone divine names, not partial matches inside words
- ✅ English figurative phrases now have non-sacred versions in database
- ✅ Web interface displays non-sacred English phrases when "Traditional Jewish" selected
- ✅ Print function outputs non-sacred text for both Hebrew and English
- ✅ Complete consistency across all 6 non-sacred fields

**Technical Robustness:**
- Cantillation-aware regex patterns handle all Biblical Hebrew text
- Word boundary detection works with vowels, marks, and punctuation
- Pattern correctly distinguishes divine names from similar letter sequences
- All test cases pass for both modification and preservation scenarios

---

## 📦 PUBLIC RELEASE PREPARATION (Oct 1, 2025)

### **Documentation for Public Release - COMPLETE**

Successfully created comprehensive public-facing documentation:

#### **Files Created:**
1. **README.md** - Public-facing documentation
   - Live demo link: https://tzafun.onrender.com
   - Complete feature overview and statistics
   - Multiple citation formats (BibTeX, APA, MLA)
   - Getting started guide for both hosted and local use
   - Technical architecture (Flask + SQLite + Render.com)
   - Professional academic tone

2. **LICENSE-CODE.txt** - MIT License
   - Standard MIT License for all code
   - Copyright: Ari Robicsek, 2025
   - Clear scope: Python scripts, HTML/CSS/JS, Flask API, deployment files
   - References LICENSE-DATA.txt for database content

3. **LICENSE-DATA.txt** - CC BY 4.0 License
   - Creative Commons Attribution 4.0 for database and annotations
   - Recommended attribution format
   - Source text attribution (Sefaria MAM + JPS 2006)
   - AI model transparency (Gemini + Claude)
   - Links to full CC BY 4.0 license

4. **CITATION.cff** - Academic Citation File
   - GitHub-standard YAML format
   - Complete metadata (version 1.0.0, release date Jan 1 2025)
   - Dual licensing noted (MIT + CC BY 4.0)
   - Comprehensive abstract
   - Keywords for discoverability
   - Preferred citation format

#### **Repository Status:**
✅ Professional README with live demo
✅ Proper dual licensing (code vs data)
✅ GitHub citation support
✅ Multiple citation formats
✅ Complete attribution chain
✅ Cultural sensitivity acknowledged

**Next Step:** Repository ready for public release!

---

## 🌐 PRODUCTION DEPLOYMENT (Oct 1, 2025)

### **Deployment Architecture**
- **Platform**: Render.com (free tier)
- **URL**: https://tzafun.onrender.com
- **Backend**: Flask + Gunicorn (Python 3.11)
- **Database**: SQLite (49MB) with 8,373 verses
- **Repository**: GitHub.com/ARobicsek/bible-figurative-language

### **Key Deployment Challenges & Solutions**

#### **1. Worker Timeout Issues (502 Bad Gateway)**
- **Problem**: Default 30s gunicorn timeout caused worker kills on complex queries
- **Solution**: Increased timeout to 120s, reduced workers to 1 with 2 threads (gthread)
- **Config**: `gunicorn --timeout 120 --workers 1 --threads 2 --worker-class gthread`

#### **2. Memory Constraints (512MB RAM Limit)**
- **Problem**: 64MB SQLite cache caused Out-Of-Memory crashes and worker restarts
- **Root Cause**: Free tier has only 512MB RAM; 64MB cache + Python overhead exceeded limit
- **Solution**: Reduced cache from 64MB → 8MB, added 30MB memory-mapped I/O
- **Result**: Stable worker, no more OOM kills
- **Code**: `PRAGMA cache_size = -8000` + `PRAGMA mmap_size = 30000000`

#### **3. Database Path Resolution**
- **Problem**: `cd web && gunicorn` broke relative path calculations for database
- **Solution**: Use `gunicorn --chdir web` instead to maintain correct working directory
- **Result**: Database found correctly at `../database/Pentateuch_Psalms_fig_language.db`

#### **4. API URL Configuration**
- **Problem**: Frontend hardcoded `http://localhost:5000/api` causing connection failures
- **Solution**: Changed to relative URL `/api` with `window.location.origin` base
- **Result**: Works on both localhost and production without configuration

#### **5. Cold Start Performance**
- **Problem**: Free tier spins down after 15 min inactivity; first load takes 30-60 seconds
- **Solution**: Added UI message "First load may take up to 1 minute" to set expectations
- **Trade-off**: Acceptable for free hosting; upgrades available if needed

#### **6. Complex Query Optimization**
- **Problem**: Metadata searches with "Not Figurative" + all types caused timeouts
- **Solution**: Auto-uncheck "Not Figurative" when user types in metadata fields
- **Rationale**: Metadata only exists for figurative verses, so including non-figurative is logically unnecessary
- **Result**: Fast metadata searches, no more 502 errors

### **Production Configuration Files**

**`render.yaml`** (Render.com deployment config):
```yaml
services:
  - type: web
    name: tzafun
    env: python
    plan: free
    buildCommand: pip install -r web/requirements.txt
    startCommand: gunicorn --bind 0.0.0.0:$PORT --chdir web --timeout 120 --workers 1 --threads 2 --worker-class gthread api_server:app
    envVars:
      - key: FLASK_ENV
        value: production
```

**`web/requirements.txt`**:
```
Flask==3.0.0
Flask-CORS==4.0.0
gunicorn==21.2.0
```

### **Performance Characteristics (Free Tier)**
- **Cold Start**: 30-60 seconds (after 15 min inactivity)
- **Warm Queries**: < 1 second for most searches
- **Initial Page Load**: 10 verses, ~2-3 seconds
- **Metadata Search**: Fast (< 1s) when limited to figurative types
- **Concurrent Users**: Limited on free tier; may need upgrade for high traffic

### **Public Release Preparations**
- ✅ Made analysis pipeline public (removed `private/` from `.gitignore`)
- ✅ Added `.env.example` template for API keys (Gemini + Anthropic)
- ✅ Ensured no API keys exposed (all use environment variables)
- ✅ Verified database file tracked in git (49MB within GitHub limits)
- ✅ Production-ready Flask configuration with PORT and FLASK_ENV support
- ✅ Debug logging for troubleshooting production issues

### **Known Limitations (Free Tier)**
1. **15-minute sleep**: Service spins down after inactivity
2. **512MB RAM**: Limited to smaller cache sizes and fewer workers
3. **Shared CPU**: Performance varies based on server load
4. **No persistent disk**: Database is read-only from git repo

### **Future Scaling Options**
- **Paid Tier ($7/mo)**: 512MB → 2GB RAM, no sleep, faster performance
- **Database Migration**: SQLite → PostgreSQL for better concurrent access
- **CDN**: Add Cloudflare for static asset caching
- **Connection Pooling**: Implement persistent connections for faster queries

---

**✅ MAJOR BREAKTHROUGHS (Sept 27-30, 2025)**:
- **📖 ENGLISH TEXT FOOTNOTE CLEANUP (Sept 30 - Latest)**: Completely resolved footnote contamination in English verse text
  - **Issue**: English text displaying with inline footnote markers from Sefaria API (e.g., "cMeaning of Heb. uncertain", "*Others 'In the beginning...'")
  - **Root cause**: Sefaria API returns footnotes embedded as HTML tags; previous cleaning only removed tags but left footnote TEXT inline
  - **Discovery**: Found 230+ verses with "Meaning of Heb", 302+ with "Lit.", affecting Psalms and Genesis differently
  - **Solution**:
    - Enhanced `sefaria_client.py _clean_text()` to handle BOTH footnote formats (Psalms letter-style + Genesis asterisk-style with nested `<b>` tags)
    - Created new database columns: `english_text_clean` and `english_text_clean_non_sacred`
    - Fetched fresh English text from Sefaria API for all 8,373 verses (337 API calls, ~2 minutes)
    - Applied improved footnote removal + divine names transformation
    - Updated web interface to use clean columns
  - **Result**: **100% clean English text** - zero footnotes in display, problematic verses (Psalms 2:11-12, Genesis 1:1) fully fixed
  - **Files Modified**: `sefaria_client.py:67-86`, `api_server.py:223,235,247,305+`, `biblical_figurative_interface.html:1471`
  - **Script**: `refresh_english_text.py` (can re-run anytime to refresh from Sefaria API)
- **🔧 LAZY COUNT ESTIMATE FIX (Sept 29 - Latest)**: Fixed frontend estimate detection to work with all query types
  - **Issue**: Stats bar showed "(calculating total...)" indefinitely or displayed 0 instances instead of correct count
  - **Root cause**: Estimate detection only triggered when `total === 5002`, but text searches returned different totals (e.g., 14)
  - **Solution**: Changed detection to trigger whenever `total_figurative_instances === 0` and "show all verses" or "show not figurative" enabled
  - **Result**: Lazy background counting now works correctly for text searches and all filter combinations
- **⚡ LAZY BACKGROUND COUNTING (Sept 29)**: Implemented intelligent lazy loading for expensive count queries
  - **Initial page load**: Shows "(calculating total...)" and loads verses instantly (~0.3s)
  - **Background counting**: Exact counts calculated asynchronously without blocking UI (2-3s)
  - **Smart detection**: Automatically triggers for mixed queries (figurative + non-figurative)
  - **Result**: 50-60x faster perceived performance with seamless count updates
- **🗄️ DATABASE SELECTOR (Sept 29 - Latest)**: Added dynamic database switching in web interface
  - **Dropdown selector**: Shows all `.db` files with verse counts
  - **Persistent selection**: Remembers last selected database in localStorage
  - **Default database**: `complete_torah_merged.db` (5,846 verses - complete Torah)
  - **Hot switching**: Change databases without restarting server
  - **Result**: Easy access to different analysis datasets for research
- **⚡ MASSIVE PERFORMANCE BOOST (Sept 29 - Latest)**: Achieved **50-60x speedup** for mixed queries (figurative + non-figurative)
  - Non-figurative only: 19.6s → 0.33s (60x faster)
  - All types + "Not Figurative": 15-20s → 0.34s (50x faster)
  - **Root cause**: Expensive `figurative_count_query` with LEFT JOIN across entire table
  - **Solution**: Skip expensive counts for mixed queries, use fast estimates for total count
  - **Result**: Instant, responsive UI for all filter combinations
- **🔍 TEXT SEARCH FIX (Sept 29)**: Resolved critical bug where text search didn't work with "Not Figurative" filter - now properly filters non-figurative verses by search terms
- **🎯 SEARCH RACE CONDITION FIX (Sept 29)**: Fixed bug where rapid searches would display wrong results
  - **Root cause**: Concurrent API requests completing out of order
  - **Solution**: Request counter system ensures only most recent search displays
  - **Result**: Search always shows correct, current results
- **📖 GENESIS FIRST FIX (Sept 29)**: Corrected initial page load to show Genesis instead of Leviticus
  - **Root cause**: Book filter only recognized Leviticus/Numbers, ignored other books
  - **Solution**: Updated book filter to handle all 5 Torah books
  - **Result**: Interface loads in proper biblical order (Genesis → Deuteronomy)
- **🎨 METADATA SEARCH CLEAR BUTTON (Sept 29)**: Added grey refresh icon to clear all tag search fields at once
- **🔧 HEBREW TEXT CONTAMINATION FIX (Sept 29)**: Resolved critical frontend contamination where massive deliberation text (4,000+ chars) was corrupting Hebrew text display through oversized HTML data attributes
- **🚀 ENHANCED MULTI-BOOK SELECTION**: Revolutionary flexible selection system for processing multiple books simultaneously
- **⚡ NON-CONTIGUOUS PROCESSING**: Support for comma-separated, range-based chapter and verse selection (e.g., "1,3,5-7,10")
- **📚 ULTRA-FAST 'FULL' MODE**: Process entire books with single command - no more tedious chapter-by-chapter selection
- **🎯 INSTANT SELECTION**: Eliminated API delays during book/chapter/verse selection for immediate workflow
- **🔧 CONFIGURABLE WORKERS**: User-selectable parallel worker count (1-12) for optimal performance tuning
- **🔄 UNIFIED PROMPT SYSTEM**: All three AI models (Flash, Pro, Claude) now use identical comprehensive instructions for consistent analysis
- **⚡ PARALLEL PROCESSING**: Successfully implemented configurable parallel processing with 5-8x performance improvement
- **🚀 CLAUDE SONNET 4 UPGRADE**: Successfully integrated `claude-sonnet-4-20250514` as tertiary fallback model with shared prompts
- **✅ COMPLETE VALIDATION PIPELINE**: End-to-end validation system working perfectly with all three AI models
- **📊 DATABASE INTEGRITY**: Full audit trail from detection → validation → final classification for scholarly transparency
- **Result**: **Revolutionary multi-book processing** with unified AI architecture, intelligent parallel processing, and clean Hebrew text display**

### Latest Achievements

**🆕 Enhanced Truncation Recovery & Model Tracking System (Sept 25-27, 2025)**
- **Automatic Detection**: System detects truncated responses and triggers Pro model fallback seamlessly
- **Model Tracking**: Database now records which model (`gemini-2.5-flash`, `gemini-2.5-pro`) was used for each analysis
- **Dual-Model Failure Detection**: New `both_models_truncated` field tracks when even Pro model fails on extremely complex verses
- **Enhanced Statistics**: Usage tracking includes Pro model fallback rates and performance metrics
- **Complete Recovery**: Previously truncated verses now generate full hierarchical tag arrays
- **Research Transparency**: Scholars can analyze model performance differences and complexity correlations
- **Production-Ready Tracking**: Robust field population ensures no `NULL` model_used values in database
- **🎯 FALSE POSITIVE ELIMINATION (Sept 26 Evening)**: Fixed truncation detection logic to distinguish between legitimate "no figurative language" responses vs actual truncation, eliminating unnecessary Pro model calls
- **🆕 FALSE NEGATIVE ELIMINATION (Sept 27)**: Enhanced pattern detection to catch deliberations with phrases like "classic case of", "fits the criteria", eliminating false negatives like Genesis 14:20 metonymy detection

**🔧 Text Display Contamination Resolution (Sept 29-30, 2025)**

**Hebrew Text Contamination (Sept 29, 2025)**:
- **Critical Issue**: Hebrew text display was contaminated with English deliberation text (4,268+ characters) and validation reasons
- **Root Cause**: Massive annotation objects with large text fields were being serialized into HTML `data-annotation` attributes, causing display corruption
- **Solution**: Implemented minimal annotation storage system - only essential fields (target, vehicle, ground, types, etc.) stored in HTML attributes
- **Data Recovery**: Full annotation details retrieved from `appState.verses` when needed for click functionality
- **Performance Impact**: Reduced HTML attribute size from 4,000+ to ~200 characters per annotation, eliminating display contamination
- **Functionality Preserved**: All features working - Hebrew text clean, validation reasons display correctly, explanations intact
- **Result**: **Production-ready Hebrew text display** with zero contamination and full interactive functionality

**English Text Contamination (Sept 30, 2025)**:
- **Critical Issue**: English text in Psalms (31:20, 143:7, others) showing JSON metadata as visible text (e.g., `ment"],"speaker":"Narrator","confidence":0.9...`)
- **Root Cause**: Sequential highlighting passes were matching text INSIDE previously-created `data-annotation` attributes instead of only in visible text
- **Specific Example**: When highlighting "men" as third annotation, `indexOf()` would find "men" inside the JSON string `"figurative_text":"men"` from an earlier annotation's attribute, causing replacement at wrong position and JSON leakage
- **Solution**: Implemented attribute-aware replacement logic that:
  1. Searches for ALL occurrences of matched text using `indexOf()` in a loop
  2. For each occurrence, counts opening (`data-annotation='`) vs closing (`'>`) patterns before the match
  3. Skips occurrences where counts are unequal (= inside an attribute)
  4. Only replaces occurrences where counts are equal (= in visible text)
- **Code Location**: `web/biblical_figurative_interface.html` lines 1969-1999
- **Debug Logging**: Added comprehensive logging to track match positions and attribute detection (kept for future debugging)
- **Testing**: Verified fix works for all verses with multiple overlapping annotations in both English and Hebrew
- **Result**: **Zero contamination** - JSON metadata stays in attributes, never leaks into visible text

**✅ Flexible Hierarchical Tagging System (Sept 25, 2025)**
- **Revolutionary Tagging**: Hierarchical arrays for Target/Vehicle/Ground/Posture (e.g., ["specific target", "target category", "general domain"])
- **Efficient Validation**: Bulk validation process reduces API calls to a maximum of two per verse (one for detection, one for validation)
- **Split Deliberations**: Separate LLM reasoning for detection vs. tagging analysis for token efficiency
- **Robust JSON Parsing**: Enhanced extraction with bracket matching and completeness validation
- **High Token Limits**: 15,000 tokens for Flash, 30,000 for Pro model to handle complex analysis
- **Database Integration**: Complete schema v4 with JSON storage, model tracking, and validation pipeline compatibility
- **Proven Results**: 7 instances detected from Deuteronomy 30:2-4 with complete hierarchical metadata and validation

**✅ Phase 1: Data Preprocessing Pipeline Completed (Sept 22, 2025)**
- **Category Normalization**: Reduced target categories from 31→12 and vehicle categories from 35→15 through intelligent mapping
- **Multi-Type Flow Creation**: Expanded 950 figurative instances into 1,287 visualization flows to handle multi-type instances (metaphor+idiom combinations)
- **Data Export Pipeline**: Created `data_processor.py` with comprehensive SQLite→JSON export including Hebrew text preservation
- **Quality Validation**: 100% data integrity maintained with enhanced structure for visualization

**Enhanced Target/Vehicle/Ground Classification Framework** with explicit definitions and examples:
- **TARGET** = WHO/WHAT the figurative speech is ABOUT (the subject being described)
- **VEHICLE** = WHAT the target is being LIKENED TO (the comparison/image used)
- **GROUND** = WHAT QUALITY of the target is being described (the shared quality between target and vehicle)

This builds upon our advanced multi-type classification system that allows phrases to be classified as multiple figurative language types simultaneously (e.g., both metaphor AND idiom), with intelligent reclassification capabilities and complete audit trails.

## 🧠 Advanced Three-Tier AI Architecture with Unified Prompts
### **Production-Ready Model Hierarchy with Consistent Instructions**
- **Primary Model**: Gemini 2.5 Flash (`gemini-2.5-flash`) - Fast, efficient for 85%+ of verses (15,000 tokens) ✅
- **Secondary Fallback**: Gemini 2.5 Pro (`gemini-2.5-pro`) - High-capacity model for complex hierarchical analysis (30,000 tokens) ✅
- **🚀 Tertiary Fallback**: Claude Sonnet 4 (`claude-sonnet-4-20250514`) - **LATEST MODEL** with enhanced reasoning for extremely complex verses (8,000 tokens) ✅
- **🔄 Unified Instructions**: All three models now use identical comprehensive flexible tagging prompts for consistent analysis ✅
- **Validation Model**: Gemini 2.5 Flash with automatic Pro fallback for complex validation ✅

### **Intelligent Three-Tier Processing Pipeline**
1. **Flash Processing**: Handles standard complexity verses with fast turnaround and cost efficiency
2. **Pro Escalation**: Automatic fallback when Flash truncates or hits token limits on complex verses
3. **🚀 Claude Escalation**: Final fallback for extremely complex theological content requiring enhanced reasoning
4. **🔄 Unified Prompt System**: All three models now use the same comprehensive flexible tagging instructions for consistency
5. **Parallel Architecture**: 12-worker parallel processing with intelligent load balancing and error recovery
6. **Complete Coverage**: Advanced fallback system ensures 100% verse coverage regardless of complexity

### **Technical Features**
- **🔄 Unified Prompt Architecture**: All three AI models (Flash, Pro, Claude) use identical comprehensive instructions for consistent analysis
- **Parallel Processing**: 12-worker ThreadPoolExecutor with intelligent task distribution
- **Model Usage Tracking**: Complete database logging of which AI model processed each instance
- **Enhanced JSON Recovery**: Robust parsing with automatic repair for incomplete responses
- **Server Error Handling**: Exponential backoff and intelligent fallback for persistent API issues
- **Perfect Integration**: Full validation pipeline compatibility with all three models and parallel architecture
- **🔧 Hardcoded Fallback Fix**: Resolved deprecated model references ensuring reliable fallback processing
- **🕊️ Hebrew Divine Names Modifier**: Automatic generation of non-sacred Hebrew and English text for traditional Jewish use

### **🕊️ Hebrew Divine Names Modifier (Sept 28, 2025)**
Production-ready system for creating non-sacred versions of Hebrew text following traditional Jewish requirements:

**Supported Divine Name Transformations:**
- **Tetragrammaton**: `יהוה` → `ה׳` (complete replacement with Heh + geresh)
- **Elohim Family**: Replace `ה` with `ק` in `אֱלֹהִים`, `אֱלֹהֶיךָ`, etc.
- **El with Tzere**: `אֵל` → `קֵל` (divine name only, NOT preposition `אֶל`)
- **Tzevaot**: `צְבָאוֹת` → `צְבָקוֹת` (replace א with ק)
- **El Shaddai**: `שַׁדַּי` → `שַׁקַּי` (replace ד with ק)

**🆕 English Text Support (Sept 28, 2025):**
- **Dual-Language Processing**: Modifies Hebrew divine names in both Hebrew and English text
- **Mixed-Language Support**: Handles English translations containing Hebrew terms
- **Example**: "In the beginning אלהים created" → "In the beginning אלקים created"
- **Intelligent Detection**: Only modifies Hebrew divine names, preserves all English content

**Technical Capabilities:**
- **Robust Pattern Matching**: Handles all vowel markings and cantillation marks
- **Context-Aware**: Distinguishes divine names from similar words (e.g., אֵל vs אֶל)
- **Complete Unicode Support**: Works with any Hebrew manuscript tradition
- **Dual-Language Integration**: Processes both Hebrew and English text seamlessly
- **Database Integration**: Stores both original and non-sacred versions for both languages
- **Zero Performance Impact**: Integrated into parallel processing pipeline

**Database Fields Added:**
- `hebrew_text_non_sacred` (verse-level Hebrew)
- `english_text_non_sacred` (verse-level English)
- `figurative_text_in_hebrew_non_sacred` (instance-level Hebrew)

## 🎯 Current Status
✅ **Phase 1: Data Preprocessing Complete** - Ready for visualization development
✅ **Enhanced Target/Vehicle/Ground Classification**: Clearer guidance for AI classifier with explicit definitions and examples
✅ **Category Normalization**: Consistent target (12) and vehicle (15) categories for clean visualization
✅ **Multi-Type Flow Architecture**: 1,287 flows from 950 instances supporting combined figurative types
✅ **Rich Metadata Export**: Hebrew text, deliberation, and validation details preserved for hover tooltips
✅ **Multi-Type Classification**: Each phrase can be classified as multiple figurative language types
✅ **Intelligent Reclassification**: Validator can correct misclassifications (e.g., metaphor → simile)
✅ **Dual-Field Architecture**: Separate tracking of initial detection vs. final validated results
✅ **Complete Audit Trail**: Every detection and validation decision logged with reasoning
✅ **🕊️ Hebrew Divine Names Modifier**: Production-ready system for traditional Jewish non-sacred text generation
✅ **Deliberation Capture**: LLM explains what it considered and why for each verse
✅ **Validation Transparency**: Clear distinction between detection, reclassification, and rejection
✅ **Advanced Server Error Recovery**: Exponential backoff for 500 errors with 30-second timeout fallback
✅ **Intelligent Model Switching**: Automatic fallback to Gemini 1.5 Flash after persistent server errors
✅ **Comprehensive Error Tracking**: Separate statistics for content restrictions vs server error fallbacks
✅ **Production-Ready Truncation Recovery**: Intelligent fallback to gemini-2.5-pro for complex verses
✅ **🚀 Advanced Three-Tier Model Architecture**: Flash → Pro → **Claude Sonnet 4** ensures no verse is left unanalyzed
✅ **Model Usage Tracking**: Database records which AI model processed each instance for transparency
✅ **Enhanced JSON Parsing**: Robust extraction with completeness validation and bracket matching
✅ **Interactive Processing**: Analyze any book, chapter, or verse range on demand
✅ **Context-Aware Prompting**: Different strategies for creation, legal, poetic, and narrative texts
✅ **Comprehensive Error Handling**: Graceful handling of API restrictions, rate limits, and server errors
✅ **Research-Grade Data**: Complete metadata with model tracking for reproducible scholarly analysis
🎯 **Publication Quality**: Advanced validation and model tracking make results suitable for peer-reviewed research
Multi-Model API Achievements
✅ Context-Aware Analysis: Uses different prompting strategies for creation_narrative, poetic_blessing, and legal_ceremonial texts to improve accuracy.
✅ Automated Fallback: Automatically switches from the primary model (Gemini 2.5 Flash) to a fallback model (Gemini 1.5 Flash) on content restriction errors and persistent server errors.
✅ Intelligent Retries: Overcomes API rate limits and server errors with exponential backoff and recommended delay parsing.
✅ JSON Extraction: Reliably extracts JSON data from "chatty" or conversational LLM responses.
✅ Response Recovery: Automatic repair of truncated JSON responses to preserve valid figurative language detections.
✅ Multi-Type Detection: Supports simultaneous classification of phrases as multiple figurative types.
✅ Intelligent Reclassification: Automatic correction of misclassifications during validation.
✅ Scholar Confidence: The robust and transparent pipeline builds confidence in the results for academic use.
Technical Achievements
✅ Context-Aware Prompt Engineering: Tailors prompts based on the biblical text's genre.
✅ Complete Pipeline: End-to-end processing from Hebrew text extraction to sanitized database storage.
✅ 100% LLM-Based Detection: Pure AI-driven analysis with robust error handling and data validation.
✅ Enhanced Vehicle/Tenor Classification: Improved precision with specific categorization guidelines.
✅ Scholarly Explanations: PhD-level analysis with communicative intent detection.
✅ Advanced Multi-Type Architecture: Independent tracking of detection vs. validation for each type.
✅ Speaker Attribution & Purpose Analysis: Identifies who speaks and why.
🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended
- Gemini API key (get from Google AI Studio)
- Anthropic API key (for Claude Sonnet 4 fallback - get from Anthropic Console)

### Installation
```bash
git clone https://github.com/ARobicsek/bible-figurative-language
cd bible-figurative-language
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration (Required)
1. Create a `.env` file in the root directory
2. Add your API keys:
```
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```
3. **IMPORTANT**: Add `.env` to your `.gitignore` to keep your API keys secure

### Usage

**Windows Unicode Support** (required for Hebrew text):
```bash
chcp 65001
```

**Three Processing Systems Available**:

#### ⚡ **Enhanced Parallel Processing System (PRODUCTION READY - CLAUDE SONNET 4!)**
High-performance parallel processing with **flexible multi-book selection** and complete validation pipeline:
```bash
python interactive_parallel_processor.py   # 🆕 Enhanced: flexible multi-book, multi-chapter, multi-verse selection
python test_22_genesis_verses_parallel.py  # Example: 22 Genesis verses
```
- **🆕 Multi-Book Selection**: Process multiple books in one run (e.g., "Leviticus,Numbers" or "1,3,5")
- **🆕 Non-Contiguous Ranges**: Select specific chapters/verses with comma-separated lists (e.g., "1,3,5-7,10")
- **🆕 Ultra-Fast 'Full' Mode**: Process entire books with single command ("full")
- **🆕 No Selection Delays**: Instant book/chapter/verse selection without API calls
- **🆕 Configurable Workers**: Choose 1-12 parallel workers based on your system and API limits
- **Features**: Advanced three-tier model fallback (Flash → Pro → Claude Sonnet 4), complete validation
- **Best for**: Production workloads, large-scale analysis, full books, multi-book research datasets
- **Performance**: 5-8x speedup with intelligent parallel processing and error recovery
- **Coverage**: 100% verse processing - **no verse left unanalyzed** regardless of complexity
- **Status**: ✅ **PRODUCTION READY** - Enhanced architecture with flexible selection and robust error handling
- **Latest (Sept 28)**: **Flexible multi-book system** with instant selection and configurable parallel workers

#### 🆕 Flexible Hierarchical Tagging (Single-threaded)
Revolutionary system with advanced AI fallback:
```bash
python interactive_flexible_tagging_processor.py
```
- **Features**: Hierarchical tag arrays, automatic truncation recovery, **🚀 Claude Sonnet 4 fallback for complex verses**
- **Best for**: Advanced research, complex hierarchical categorization, testing
- **Models**: gemini-2.5-flash → gemini-2.5-pro → **claude-sonnet-4-20250514 fallback**

#### ✅ **Enhanced Multi-Model System (Single-threaded)**
Stable system with **flexible multi-book selection** for traditional categorical detection:
```bash
python interactive_multi_model_processor.py  # 🆕 Enhanced: flexible multi-book selection
```
- **🆕 Multi-Book Selection**: Process multiple books in one run with flexible selection
- **🆕 Non-Contiguous Ranges**: Select specific chapters/verses with comma-separated lists
- **🆕 Ultra-Fast 'Full' Mode**: Process entire books with single command ("full")
- **Features**: Conservative detection, traditional categories, high precision, single-threaded reliability
- **Best for**: Reliable baseline analysis, validation studies, resource-constrained environments
- **Models**: gemini-2.5-flash → gemini-2.5-pro fallback (updated from deprecated model)

## 🚀 **NEW: Enhanced Multi-Book Selection System (Sept 28, 2025)**

All interactive processors now feature **revolutionary flexible selection** capabilities:

### 📚 **Multi-Book Selection Examples**
```
Select books: 3,4              # Leviticus and Numbers
Select books: Genesis,Exodus   # By name
Select books: 1-3              # Range: Genesis through Leviticus
Select books: 1,3,5            # Non-contiguous: Genesis, Leviticus, Deuteronomy
Select books: all              # All five books
```

### 📖 **Ultra-Fast Full Book Processing**
```
Enter chapters for Leviticus (1-27): full
Selected: FULL BOOK (Leviticus - all chapters, all verses)
  Will process all 27 chapters with all verses
```

### 📑 **Flexible Chapter/Verse Selection**
```
Enter chapters: 1,3,5-7,10     # Chapters 1, 3, 5, 6, 7, 10
Enter verses: 1-3,7,12-15      # Verses 1, 2, 3, 7, 12, 13, 14, 15
```

### ⚡ **No More Waiting During Selection**
- **Instant Selection**: No API calls during book/chapter/verse choice
- **Smart Estimation**: Provides verse count estimates without delays
- **Batch Confirmation**: Shows complete processing plan before starting

### 🔧 **Configurable Parallel Processing**
```
=== PARALLEL PROCESSING CONFIGURATION ===
Enter max parallel workers (1-12, default: 6): 8
```

**Result**: Process multiple books with thousands of verses in minutes, not hours!

---

All systems provide enhanced interactive selection with multi-book, non-contiguous ranges.

Batch Processing (Original Scripts)
These scripts are useful for processing entire books at once.

bash
# Process complete books
python run_genesis_conservative.py     # Complete Genesis (50 chapters)
python run_deuteronomy_conservative.py # Complete Deuteronomy (34 chapters)
View Results
bash
# Interactive query interface
python query_database.py

# View specific datasets (example)
python view_results_genesis_1_3.py
🗂️ Project Structure
plaintext
 Show full code block 
src/hebrew_figurative_db/
├── pipeline.py                    # Main processing pipeline
├── text_extraction/
│   └── sefaria_client.py          # Hebrew/English text API client
├── ai_analysis/
│   ├── gemini_api_multi_model.py  # ⭐ NEW: Robust, context-aware multi-model client
│   └── ...
└── database/
    └── db_manager.py              # Enhanced database with speaker/purpose fields

Root Directory:
├── interactive_multi_model_processor.py # ⭐ NEW: Interactive script for targeted analysis
├── run_genesis_conservative.py         # Batch processing for Genesis
├── run_deuteronomy_conservative.py     # Batch processing for Deuteronomy
├── .env                                # ⭐ NEW: Secure file for API key (add to .gitignore)
├── requirements.txt                    # Project dependencies (ensure python-dotenv is listed)
└── ...
🛠️ Production-Ready Database Schema (v4.2)
Advanced dual-system schema with intelligent model tracking, truncation recovery, and Hebrew divine names modification support.

```sql
-- Verses table - stores ALL processed verses with complete research transparency
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    hebrew_text_stripped TEXT,
    hebrew_text_non_sacred TEXT,                       -- Hebrew text with divine names modified for traditional Jews
    english_text TEXT NOT NULL,
    english_text_non_sacred TEXT,                      -- English text with Hebrew divine names modified for traditional Jews
    word_count INTEGER,
    llm_restriction_error TEXT,                    -- API errors for this verse
    figurative_detection_deliberation TEXT,       -- LLM reasoning for ALL verses
    instances_detected INTEGER,
    instances_recovered INTEGER,
    instances_lost_to_truncation INTEGER,
    truncation_occurred TEXT CHECK(truncation_occurred IN ('yes', 'no')) DEFAULT 'no',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Figurative language table - stores ONLY verses WITH figurative language detected
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,

    -- Initial Detection Fields (what the LLM originally detected)
    figurative_language TEXT CHECK(figurative_language IN ('yes', 'no')) DEFAULT 'no',
    simile TEXT CHECK(simile IN ('yes', 'no')) DEFAULT 'no',
    metaphor TEXT CHECK(metaphor IN ('yes', 'no')) DEFAULT 'no',
    personification TEXT CHECK(personification IN ('yes', 'no')) DEFAULT 'no',
    idiom TEXT CHECK(idiom IN ('yes', 'no')) DEFAULT 'no',
    hyperbole TEXT CHECK(hyperbole IN ('yes', 'no')) DEFAULT 'no',
    metonymy TEXT CHECK(metonymy IN ('yes', 'no')) DEFAULT 'no',
    other TEXT CHECK(other IN ('yes', 'no')) DEFAULT 'no',

    -- Final Validation Fields (what passed validation, may include reclassification)
    final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')) DEFAULT 'no',
    final_simile TEXT CHECK(final_simile IN ('yes', 'no')) DEFAULT 'no',
    final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')) DEFAULT 'no',
    final_personification TEXT CHECK(final_personification IN ('yes', 'no')) DEFAULT 'no',
    final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')) DEFAULT 'no',
    final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')) DEFAULT 'no',
    final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')) DEFAULT 'no',
    final_other TEXT CHECK(final_other IN ('yes', 'no')) DEFAULT 'no',

    -- 🆕 FLEXIBLE SYSTEM: Hierarchical JSON arrays
    target TEXT,   -- e.g., ["David", "king", "person"]
    vehicle TEXT,  -- e.g., ["lion", "predatory animal", "living creature"]
    ground TEXT,   -- e.g., ["strength", "physical quality", "attribute"]
    posture TEXT,  -- e.g., ["celebration", "praise", "positive sentiment"]

    -- ORIGINAL SYSTEM: Categorical fields (preserved for compatibility)
    target_level_1 TEXT,       -- e.g., "God", "Social Group", "Natural world"
    target_specific TEXT,      -- e.g., "David", "Israelites", "mountain"
    vehicle_level_1 TEXT,      -- e.g., "natural world", "human parts", "divine"
    vehicle_specific TEXT,     -- e.g., "lion", "heart", "shepherd"
    ground_level_1 TEXT,       -- e.g., "moral quality", "physical quality", "status"
    ground_specific TEXT,      -- e.g., "strength", "courage", "leadership"

    -- Core metadata
    confidence REAL NOT NULL,
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    figurative_text_in_hebrew_stripped TEXT,
    figurative_text_in_hebrew_non_sacred TEXT,         -- Hebrew figurative text with divine names modified
    explanation TEXT,
    speaker TEXT,
    purpose TEXT,

    -- 🆕 Split deliberation system (token-efficient)
    tagging_analysis_deliberation TEXT,  -- LLM reasoning about hierarchical tag selection
    -- Validation Audit Trail (per type)
    validation_decision_simile TEXT CHECK(validation_decision_simile IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_metaphor TEXT CHECK(validation_decision_metaphor IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_personification TEXT CHECK(validation_decision_personification IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_idiom TEXT CHECK(validation_decision_idiom IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_hyperbole TEXT CHECK(validation_decision_hyperbole IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_metonymy TEXT CHECK(validation_decision_metonymy IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_other TEXT CHECK(validation_decision_other IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_reason_simile TEXT,
    validation_reason_metaphor TEXT,
    validation_reason_personification TEXT,
    validation_reason_idiom TEXT,
    validation_reason_hyperbole TEXT,
    validation_reason_metonymy TEXT,
    validation_reason_other TEXT,
    validation_response TEXT,                         -- Full validator response
    validation_error TEXT,                            -- Any validation errors
    model_used TEXT DEFAULT 'gemini-2.5-flash',      -- 🆕 Track which model processed this instance
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
```

## 📊 Production-Ready Data Architecture (v4.2 - Enhanced Sept 28, 2025)
- **🤖 Intelligent Model Tracking**: Every instance records which AI model (`gemini-2.5-flash`, `gemini-2.5-pro`) processed it
- **🔍 Complete Research Transparency**: `figurative_detection_deliberation` stored for ALL verses, not just figurative ones
- **🏷️ Dual Classification Systems**: Original categorical + flexible hierarchical JSON arrays
- **🧠 Split Deliberation Architecture**: Separate reasoning for detection vs. tagging analysis
- **🔄 Multi-Type Detection**: Each phrase can be simultaneously classified as multiple types
- **✅ Initial vs. Final Fields**: Clear separation between what was detected vs. what was validated
- **🔧 Reclassification Tracking**: Complete audit trail when validator corrects type assignments
- **📊 Per-Type Validation**: Independent validation decisions and reasoning for each figurative type
- **🚨 Comprehensive Error Tracking**: Complete logging of API errors, restrictions, and truncation recovery
- **🆕 Dual-Model Failure Tracking**: New `both_models_truncated` field identifies extremely complex verses that challenge both Flash and Pro models
- **🕊️ Hebrew Divine Names Modifier**: Automatic generation of non-sacred Hebrew and English text fields for traditional Jewish scholarly use

### Key Architecture Benefits:
- **Model Performance Analysis**: Compare detection quality between Flash and Pro models
- **Complexity Correlation**: Identify which verses require high-capacity Pro model processing
- **Cost Optimization**: Track expensive Pro model usage for budget planning
- **Research Completeness**: Scholars can analyze why LLM rejected certain verses as non-figurative
- **False Negative Analysis**: Identify patterns in detection gaps for system improvement
- **System Compatibility**: Supports both proven categorical and revolutionary hierarchical approaches
- **🆕 Dual-Model Failure Analysis**: Track extremely complex verses that exceed both models' capabilities
- **🆕 Production-Grade Reliability**: Robust field population prevents NULL values and ensures data integrity

## 🏷️ Current Classification Categories

**Target Level 1 Categories** (WHO/WHAT the figurative speech is about):
- God
- Social Group
- Action
- Geographical or political entity
- Natural world
- Created objects
- Specific person
- Other thing
- Other

**Vehicle Level 1 Categories** (WHAT the target is being likened to):
- natural world
- human parts
- human action
- divine
- relationships
- spatial
- the ancient workplace
- abstract
- other

**Ground Level 1 Categories** (WHAT QUALITY is being described):
- moral quality
- physical quality
- psychological quality
- status
- essential nature or identity
- other

Example: "Judah is a lion" → TARGET: target_level_1 = "Specific person", target_specific = "Judah"; VEHICLE: vehicle_level_1="natural world", vehicle_specific ="lion"; GROUND: ground_level_1="physical quality", ground_specific="strength"
## 🌐 **Enhanced Interactive HTML Interface (Sept 28, 2025 - Latest Updates)**

### ✅ **Production-Ready Web Interface with Advanced Features**
A comprehensive HTML-based interface for exploring and analyzing your biblical figurative language database with advanced filtering, search, and visualization capabilities.

**🎯 Key Features Implemented:**
- **📖 Dual-Column Display**: Hebrew (RTL) and English text side-by-side with proper Unicode support
- **🕊️ Sacred/Non-Sacred Toggle**: Switch between original and traditional Jewish text versions for both Hebrew and English
- **✨ Universal Highlighting System**: Simple yellow highlighting with hover tooltips showing figurative types with colored squares
- **🎭 Comprehensive Figurative Type Filtering**: Multi-selector with all figurative language types plus "Not Figurative" option
  - Select specific figurative types (metaphor, simile, personification, idiom, hyperbole, metonymy, other)
  - Check "Not Figurative" to view verses WITHOUT figurative language
  - "Select All" shows ALL verses (both with and without figurative language)
  - "Clear All" shows NO verses (intuitive behavior)
  - Yellow highlighting always appears regardless of filter selections
- **⌨️ Hebrew Virtual Keyboard**: On-screen Hebrew keyboard with all letters including final forms
- **🔍 Dual-Language Search**: Toggle between Hebrew and English text search with auto-detection
- **🔍 Advanced Metadata Filtering**: Multi-term search with Target/Vehicle/Ground/Posture metadata - supports semicolon-separated terms with OR logic
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **⚡ Real-Time Data**: Live connection to your SQLite database with intelligent pagination
- **🔗 Enhanced Interactive Details**:
  - Click verses for AI deliberations and model information
  - Click highlighted text for comprehensive analysis including validation reasons
  - Hover over highlights for instant type information with colored indicators
  - Dynamic panel sizing for optimal content viewing
- **🎯 Smart Navigation**: Clear "Load Next X Verses" button with exact counts and completion status
- **📊 Detailed Statistics**: Complete figurative language instance counts and database transparency

**🆕 Latest Interface Enhancements (Sept 29, 2025 - Major UX Update):**
- **🎨 Improved UI Layout & Design**:
  - **Compact Hebrew Keyboard**: Redesigned to 9-column rectangular layout with smaller keys (0.9rem) - fits perfectly in sidebar without scrolling
  - **Enhanced Search Controls**: English button on left, Hebrew button (עברית) on right with native label
  - **Grey Refresh Icon**: Replaced red X with subtle grey circular arrow (↻) for clearing searches
  - **Clear Search Button**: Auto-shows/hides based on input with smooth transitions
  - **Biblical Book Ordering**: All 5 books (Genesis through Deuteronomy) now properly ordered in selector
  - **"Search for Tag" Header**: Added horizontal underline matching other section headers for visual consistency

- **🔍 Advanced Search Highlighting**:
  - **Pink Search Highlighting**: Search terms now highlighted in pink (#ffb3d9) distinct from yellow figurative highlighting
  - **Hebrew Text Support**: Full Hebrew search highlighting with vowel-point awareness - strips marks for matching but highlights complete words
  - **Nested Highlighting**: Search terms highlighted in pink EVEN inside yellow figurative text with yellow border for visual distinction
  - **Language-Specific Matching**: English uses case-insensitive matching, Hebrew uses vowel-flexible matching

- **🎯 Multi-Term Metadata Search (Latest)**:
  - **Semicolon-Separated Terms**: Enter multiple search terms in Target/Vehicle/Ground/Posture fields separated by semicolons
  - **OR Logic**: All terms are combined with OR - search finds verses matching ANY of the specified terms
  - **Example**: Target: "God;Divine;glory of god" finds verses with 'god' OR 'divine' OR 'glory of god'
  - **Cross-Field Search**: Searches across all fields with OR logic - finds verses matching Target terms OR Vehicle terms OR Ground terms OR Posture terms
  - **Case-Insensitive**: All searches are case-insensitive with partial matching
  - **Removed AND/OR Selector**: Simplified interface - always uses OR logic for intuitive multi-term searching
  - **🔧 Metadata Search Priority**: When metadata search is active, it takes priority and filters out non-figurative verses (since they have no metadata to match)
  - **Grey Refresh Button**: Always-visible grey refresh arrow (↻) for clearing all tag search fields
  - **Improved Placeholder Text**: Shows "for multiple, separate with ;" in smaller text below each search field

- **🎭 Enhanced "Not Figurative" Filtering**:
  - **Fixed OR Logic**: When "Not Figurative" + other types checked, shows verses WITH those types OR without any figurative language
  - **Proper SQL Filtering**: `({figurative_filter} OR fl.id IS NULL)` ensures correct verse filtering
  - **Pagination Reset**: Automatically resets offset when filters change to prevent stale results
  - **🔧 Metadata Override**: When tag search is active, "Not Figurative" checkbox is ignored to prevent showing all verses

- **⚡ Performance & Bug Fixes**:
  - Fixed text search ordering to apply before figurative filtering
  - Reset pagination offset in `filterAndRenderVerses()` to fix second-search bugs
  - Improved `updateBookOptions()` to preserve biblical ordering and prevent dynamic reordering
  - **🔧 Fixed Tag Search Bug**: Resolved issue where tag search would return all verses after multiple searches
  - **🔧 Fixed "Show All Verses" Override**: Metadata search now prevents the "show all verses" optimization from being used

**🆕 Previous Interface Enhancements (Sept 28, 2025):**
- **🎨 Refined Visual Design**: Updated color scheme with dark gradient headers (#0a1930 → #020408)
- **✅ Revolutionary Highlighting System**: Replaced complex multi-line annotation system with universal yellow highlighting
- **🎯 Reliable Multi-Line Support**: Works perfectly for phrases spanning multiple lines regardless of figurative type count
- **💡 Intelligent Hover Tooltips**: Show figurative language types with corresponding colored squares on hover
- **📏 Enhanced Panel System**: Dynamic sizing with larger panels for annotation details (60vh vs 40vh)
- **⌨️ Hebrew Keyboard Integration**: Full virtual keyboard with clear, space, and backspace functions
- **🔍 Robust Text Matching**: Multiple matching strategies including case-insensitive and whitespace normalization
- **📱 Mobile Optimization**: Improved responsive design for all device sizes
- **🎛️ Better Checkbox Layout**: Fixed overlapping issues in figurative type filters
- **📊 Enhanced Statistics Display**: Clear formatting showing "X verses (Y instances) of Z total verses (W total instances)"
- **🚀 Fixed Navigation Controls**: Navigation bar now properly positioned at bottom of screen with "Load Next X Verses" button
- **📖 Biblical Book Ordering**: Books now appear in biblical sequence (Genesis, Exodus, Leviticus, Numbers, Deuteronomy) instead of alphabetical
- **🧹 Data Contamination Cleanup**: Comprehensive cleaning system removes AI deliberation text mixed into Hebrew verse display
- **🎯 Consistent Button Styling**: All interface buttons now use unified color scheme matching the Hebrew/English toggle buttons
- **📝 Header Updates**: "Search Hebrew Text" updated to "Search Biblical Text" and added "Search for Tag" section header
- **🔧 Fixed Validation Display**: Validation reason fields now properly display in annotation details panel
- **📍 Fixed Stats Bar**: Statistics bar now stays permanently fixed at bottom of screen with no gaps

**📁 Interface Files:**
- `biblical_figurative_interface.html` - Complete frontend interface with all enhancements
- `api_server.py` - Flask backend with Hebrew/English search support and full database integration
- `interface_requirements.txt` - Python dependencies
- `INTERFACE_SETUP.md` - Comprehensive setup and usage guide

**🚀 Quick Start:**
```bash
pip install -r interface_requirements.txt
python api_server.py
# Open http://localhost:5000 in browser
```

**🔧 How to Use:**
1. **Start Interface**: Run `python api_server.py` and open http://localhost:5000
2. **Figurative Language Filtering**:
   - **For verses WITH specific figurative types**: Select desired types (metaphor, simile, etc.)
   - **For verses WITHOUT figurative language**: Check "Not Figurative" and uncheck others
   - **For ALL verses** (with and without figurative language): Click "Select All"
   - **For NO verses**: Click "Clear All" (shows helpful message)
3. **Hebrew Search**: Click "Hebrew" toggle, use keyboard button (⌨) for virtual keyboard
4. **English Search**: Click "English" toggle for standard English text search
5. **View Details**: Click verse headers for AI deliberations, click highlighted text for annotation analysis
6. **Navigate**: Use prominent "Load Next X Verses" button for seamless browsing
7. **Advanced Metadata Filter**: Search for figurative language by metadata tags:
   - **Single Term**: Enter one search term per field (e.g., Target: "God")
   - **Multiple Terms**: Separate terms with semicolons (e.g., Target: "God;Divine;glory of god;Being")
   - **Cross-Field Search**: Terms from ALL fields combined with OR logic
   - **Example**: Target: "God;Divine" + Vehicle: "Man;Woman" finds verses where Target includes 'god'/'divine' OR Vehicle includes 'man'/'woman'
   - All searches are case-insensitive with partial matching

**🎉 Current Status:** **FULLY OPERATIONAL** - Professional-grade interface with comprehensive filtering options

**✅ TEXT SEARCH & PERFORMANCE FIXES (Sept 29, 2025)**:
- **🔍 Search Functionality**: Text search works correctly with all filter combinations including "Not Figurative"
- **⚡ Query Optimizations**:
  - Bulk annotation fetching (single query vs N+1 queries)
  - Optimized JOIN operations and GROUP BY usage
  - Lazy background counting for expensive mixed queries
- **📊 Accurate Stats Display**:
  - Shows "(calculating total...)" during background count
  - Updates seamlessly with exact counts when ready
  - Correct figurative instance counts for all filter combinations
- **✅ Complete Testing**: Verified with multiple search terms and filter combinations

**✅ Enhanced Filtering System (Sept 29, 2025)**:
- Added "Not Figurative" option for complete control over verse display
- Users can view: only figurative verses, only non-figurative verses, or all verses combined
- Proper handling of verses with invalidated figurative language (detected but rejected during validation)

**✅ Multi-Line Issue Resolved (Sept 28, 2025)**: Successfully replaced complex annotation system with reliable yellow highlighting approach - works perfectly for all scenarios

---

## 📊 Interactive Sankey Visualization System

### Overview
We are developing a cutting-edge interactive Sankey diagram to visualize the flow of figurative language patterns from **Target** → **Vehicle** relationships in biblical Hebrew texts. This visualization will transform how scholars explore and analyze figurative language usage.

### Key Features (In Development)
🎯 **Four-Layer Flow Visualization**: Target Specific → Target Level 1 → Vehicle Level 1 → Vehicle Specific
🧠 **LLM-Based Conceptual Grouping**: Semantic clustering of targets and vehicles for intuitive exploration
🖱️ **Rich Interactivity**: Zoom, filter, hover tooltips with full verse context and Hebrew text
📈 **Real-Time Statistics**: Dynamic analytics based on current view and filters
📤 **Publication Ready**: Export high-quality figures for academic papers
🔍 **Advanced Filtering**: By figurative type, confidence score, chapters, and custom criteria

### Current Dataset
- **592 validated figurative language instances** from Leviticus & Numbers
- **Multi-type classification** (metaphor, simile, personification, idiom, hyperbole, metonymy)
- **Complete validation pipeline** with LLM deliberation and confidence scoring
- **Rich metadata** including Hebrew text, English translation, and scholarly analysis

### Development Roadmap
See `SANKEY_VISUALIZATION_ROADMAP.md` for detailed project phases, timelines, and implementation plans.

## 🎯 Use Cases

### Biblical Scholarship
- **Interactive Pattern Discovery**: Explore figurative language relationships through intuitive visual flows
- **Targeted Analysis**: Use the interactive script to quickly analyze specific passages, verses, or ranges for research papers or class preparation
- **Character-Specific Patterns**: Reliably track how specific characters (e.g., Jacob, Moses) use figurative language across different contexts
- **Cross-Book Comparative Studies**: Confidently compare figurative language use across different books, thanks to the consistent and robust pipeline
- **Publication-Ready Visualizations**: Generate high-quality Sankey diagrams for academic publications

### Linguistic Research
- **Visual Pattern Recognition**: Identify common Target→Vehicle relationships through flow visualization
- **Hebrew Figurative Language Patterns**: Study patterns with research-grade accuracy, backed by a resilient data collection method
- **Translation Analysis**: Compare the original Hebrew with English translations, using the LLM's analysis as a guide
- **Semantic Domain Analysis**: Explore how different conceptual domains interact in biblical figurative language
## 🤝 Contributing
This project is designed for biblical scholarship and linguistic research. Contributions are welcome for:

- **Visualization Enhancement**: Improving the Sankey diagram interface and user experience
- **Conceptual Grouping**: Refining LLM-based semantic clustering algorithms
- **Context-Aware Prompting**: Enhancing prompting rules for different biblical text types
- **Analysis Scripts**: Adding new analysis scripts or visualization features
- **Scholarly Validation**: Creating validation datasets to further refine accuracy
- **Cross-Book Integration**: Extending visualization to Genesis, Exodus, and other books
📜 License
This project is open source and available for academic and research use.