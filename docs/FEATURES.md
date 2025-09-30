# Interface Features Guide

**Complete guide to using the Hebrew Figurative Language Explorer**

This document explains all features and functionality of the interactive web interface.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Text Selection](#text-selection)
3. [Filtering by Figurative Type](#filtering-by-figurative-type)
4. [Text Version Options](#text-version-options)
5. [Search Functionality](#search-functionality)
6. [Metadata Search](#metadata-search)
7. [Viewing Results](#viewing-results)
8. [Verse Details Panel](#verse-details-panel)
9. [Navigation and Pagination](#navigation-and-pagination)
10. [Tips and Best Practices](#tips-and-best-practices)
11. [Keyboard Shortcuts](#keyboard-shortcuts)

---

## Getting Started

### Interface Layout

The interface is divided into three main areas:

1. **Left Sidebar**: Filters and search controls
2. **Main Content**: Verse results displayed with dual-language text
3. **Bottom Panel** (collapsible): Detailed AI analysis for selected verses

### Initial Load

When you first open the interface:
1. The database loads automatically
2. Statistics appear at the bottom showing total verses available
3. All figurative types are selected by default
4. Sacred text versions are displayed by default

**Ready to explore!** Use the "Load Verses" button or filters to begin.

---

## Text Selection

### Select by Book

**Location:** Sidebar → "Text Selection" → "Books"

**How to use:**
- Click to select a single book
- Hold `Ctrl` (Windows/Linux) or `Cmd` (Mac) to select multiple books
- Click while holding `Shift` to select a range

**Available books:**
- Genesis (Bereishit)
- Exodus (Shemot)
- Leviticus (Vayikra)
- Numbers (Bamidbar)
- Deuteronomy (Devarim)

**Example:** Select Genesis + Exodus to explore only the first two books.

### Filter by Chapter

**Location:** Sidebar → "Text Selection" → "Chapters"

**Syntax:**
- Single chapter: `1`
- Multiple chapters: `1,3,5`
- Range: `1-5`
- Combined: `1,3,5-7,10`
- All chapters: `all` (or leave blank)

**Examples:**
- `1-5` → Chapters 1 through 5
- `1,10,20` → Only chapters 1, 10, and 20
- `1-3,40-50` → Chapters 1-3 and 40-50

### Filter by Verse

**Location:** Sidebar → "Text Selection" → "Verses"

**Syntax:** Same as chapters

**Examples:**
- `1-10` → Verses 1 through 10 in selected chapters
- `15,20,25` → Only verses 15, 20, and 25
- `all` → All verses (default)

**Note:** Verse filtering applies within each selected chapter.

### Load Verses Button

**After setting your selections**, click the **"Load Verses"** button to fetch results.

The interface will:
1. Apply all active filters
2. Execute the search
3. Display the first 50 matching results
4. Update statistics at the bottom

---

## Filtering by Figurative Type

**Location:** Sidebar → "Figurative Language Types"

### Available Types

Each type is color-coded for easy identification:

| Type | Color | Description |
|------|-------|-------------|
| **Metaphor** | 🔴 Red | Direct comparison without "like/as" |
| **Simile** | 🔵 Blue | Comparison with "like/as" |
| **Personification** | 🟣 Purple | Human qualities to non-human entities |
| **Idiom** | 🟠 Orange | Fixed non-literal expressions |
| **Hyperbole** | 🟤 Brown-Orange | Deliberate exaggeration |
| **Metonymy** | 🟢 Teal | Substitution of associated concept |
| **Other** | ⚫ Gray | Other figurative types |
| **Not Figurative** | ⚪ Light Gray | Verses without figurative language |

### How to Filter

**Individual selection:**
- Check/uncheck boxes to include/exclude types

**Bulk actions:**
- **Select All** button: Check all types at once
- **Clear All** button: Uncheck all types

**Multi-type verses:**
- Verses with multiple figurative types will appear if **any** selected type matches
- Example: If only "Metaphor" is checked, verses with both metaphor AND idiom will still appear

### "Not Figurative" Option

When checked, this shows verses where the AI found **no figurative language**.

**Use cases:**
- Compare figurative vs. literal language
- Study specific passages regardless of figurative content
- Verify AI detection accuracy

---

## Text Version Options

**Location:** Sidebar → "Text Version"

The interface provides traditional Jewish text options that modify how divine names appear.

### Hebrew Text Options

**Sacred Names** (default)
- Displays Hebrew text with full divine names as they appear in the original
- Example: `יהוה` (the Tetragrammaton)

**Traditional Jewish**
- Follows traditional Jewish practice for study/printing
- Divine names abbreviated with apostrophes
- Example: `ה'` or `אלקים` instead of full forms
- See [NON_SACRED_HEBREW.md](NON_SACRED_HEBREW.md) for complete details

### English Text Options

**Sacred Names** (default)
- Standard English translation from Sefaria
- Example: "the LORD" or "God"

**Traditional Jewish**
- Modified English following traditional conventions
- Example: "Hashem" or "the L-rd"

### When to Use Non-Sacred Text

**Recommended for:**
- Traditional Jewish study environments
- Printing for educational use in Orthodox contexts
- Respecting cultural sensitivities

**Important:** Non-sacred text is AI-modified and should be reviewed by qualified authorities for ritual use.

---

## Search Functionality

**Location:** Sidebar → "Search Biblical Text"

### Search Types

Toggle between two search modes:

**English Search**
- Searches English translation text
- Case-insensitive
- Matches partial words

**Hebrew Search (עברית)**
- Searches Hebrew text without vowel points
- Supports both sacred and non-sacred versions
- Includes virtual Hebrew keyboard

### English Text Search

1. Click the **"English"** toggle button
2. Type your search term in the input field
3. Results update automatically as you type
4. Matching text is highlighted in **pink**

**Examples:**
- Search: `shepherd` → Finds "The LORD is my shepherd"
- Search: `heart` → Finds all verses with "heart" or "hearts"

### Hebrew Text Search

1. Click the **"עברית"** toggle button (active by default)
2. Enter Hebrew text using:
   - **Your keyboard** (if you have Hebrew input enabled)
   - **Virtual keyboard** (click ⌨ button to toggle)

**Virtual Hebrew Keyboard:**
- Click letters to insert them
- **Space** button: Add space
- **⌫** button: Delete last character
- **Clear** button: Clear entire search

**Hebrew keyboard layout:**
```
Row 1: א ב ג ד ה ו ז ח ט
Row 2: י כ ל מ נ ס ע פ צ
Row 3: ק ר ש ת ך ם ן ף ץ
Row 4: [Clear] [Space] [⌫]
```

**Tips:**
- Hebrew search uses text **without vowel points** (nikud)
- Search is right-to-left automatically
- Partial matches are supported

**Examples:**
- Search: `אלהים` → Finds all verses with "God" (Elohim)
- Search: `משה` → Finds all verses mentioning Moses

### Clear Search

**Two ways to clear:**
1. Click the **↻** button next to the search input
2. Click **"Clear"** on the Hebrew keyboard

After clearing, all filters are re-applied without text search.

---

## Metadata Search

**Location:** Sidebar → "Search Biblical Text" → "Search for Tag"

Search the hierarchical metadata (Target/Vehicle/Ground/Posture) assigned to each figurative instance.

### How Metadata Works

Each figurative language instance has four metadata dimensions stored as hierarchical arrays:

- **TARGET**: What/who the figure is about
- **VEHICLE**: What it's compared to
- **GROUND**: What quality is described
- **POSTURE**: Speaker's attitude/stance

See [METHODOLOGY.md](METHODOLOGY.md#classification-framework) for detailed explanations.

### Single Term Search

Enter a single search term in any field:

**Examples:**
- Target: `God` → Finds all figures about God
- Vehicle: `shepherd` → Finds figures using shepherd imagery
- Ground: `strength` → Finds figures describing strength
- Posture: `warning` → Finds figures with warning tone

### Multi-Term Search (Semicolon-Separated)

Enter multiple search terms separated by semicolons (`;`) to find instances matching **any** term:

**Syntax:** `term1;term2;term3`

**Examples:**
- Target: `Moses;Aaron` → Finds figures about Moses OR Aaron
- Vehicle: `lion;eagle;serpent` → Finds animal imagery
- Ground: `power;strength;might` → Finds strength-related qualities
- Posture: `praise;celebration` → Finds celebratory language

### Combining Multiple Fields

You can search **multiple metadata fields simultaneously** for **AND** logic:

**Example:**
- Target: `God`
- Vehicle: `shepherd;father`
- Ground: `care;protection`

This finds instances where:
- Target includes "God" **AND**
- Vehicle includes "shepherd" OR "father" **AND**
- Ground includes "care" OR "protection"

### How Matching Works

**Hierarchical matching:**
- Searches match at any level of the hierarchy
- Example: Target `["Moses", "prophet", "person"]` matches searches for:
  - `Moses` (specific)
  - `prophet` (category)
  - `person` (broad)

**Case-insensitive:**
- `God` matches `god`, `God`, `GOD`

**Partial matching:**
- `shep` matches `shepherd`

### Clear Metadata Search

Click the **↻** button next to "Search for Tag" heading to clear all metadata fields at once.

---

## Viewing Results

### Verse Display

Each verse is displayed in a card with:

1. **Verse Header** (clickable)
   - Reference (e.g., "Genesis 1:3")
   - Click to expand/collapse details panel

2. **Two-Column Layout:**
   - **Left**: English translation
   - **Right**: Hebrew text (right-to-left)

3. **Highlighting:**
   - **Yellow background**: Figurative language text
   - **Pink background**: Search term matches
   - **Pink with yellow border**: Search match inside figurative text

### Figurative Language Highlighting

**Yellow highlighting** indicates text identified as figurative.

**Hover over highlighted text** to see:
- A tooltip showing which figurative type(s) apply
- Color-coded indicators for each type

**Example tooltip:**
```
🔴 Metaphor 🟠 Idiom
```

This indicates the phrase is both a metaphor and an idiom.

### No Results

If no verses match your filters, you'll see:
```
No verses match the current filters.
Try adjusting your selections.
```

**Troubleshooting:**
- Check if any figurative types are selected
- Verify book/chapter/verse ranges
- Clear search terms to broaden results
- Check if "Not Figurative" is the only selected option

---

## Verse Details Panel

**Location:** Bottom of screen (slides up when activated)

### Opening the Panel

**Two ways to open:**
1. Click the **verse header** (reference at top of verse card)
2. Click any **highlighted figurative text**

### Panel Contents

**1. Figurative Detection Deliberation**

Shows the AI's complete reasoning for detecting figurative language in this verse, including:
- Which types were identified
- Why the AI classified it as figurative
- Contextual analysis

**Model badge** shows which AI model analyzed this verse:
- `gemini-2.5-flash` (most common)
- `gemini-2.5-pro` (complex cases)
- `claude-sonnet-4` (extremely complex cases)

**2. Annotation Details** (when clicking highlighted text)

If you clicked a specific figurative instance, additional details appear:

- **Figurative Text**: The exact phrase in English and Hebrew
- **Explanation**: Detailed explanation of the figure
- **Types**: Which figurative types apply (with color indicators)
- **Confidence**: AI confidence score (0.0-1.0)
- **Speaker**: Who is speaking in this verse
- **Metadata**:
  - Target: What the figure is about
  - Vehicle: What it's compared to
  - Ground: What quality is described
  - Posture: Speaker's attitude
- **Validation Reasoning**: Why the AI validated each type classification

### Closing the Panel

**Three ways to close:**
1. Click the **× button** in panel header
2. Click outside the panel
3. Press **Escape** key

---

## Navigation and Pagination

**Location:** Bottom of screen (fixed stats bar)

### Statistics Display

The bottom bar shows real-time statistics:

**Format:**
```
Showing verses [start]-[end] of [total] | [X] figurative instances | Load More / Previous
```

**Example:**
```
Showing verses 1-50 of 2,307 | 1,523 figurative instances | Load More
```

**What the numbers mean:**
- **Verses shown**: Current page range (e.g., 1-50)
- **Total verses**: Total matching your filters
- **Figurative instances**: Total figurative language instances in displayed verses

### Loading More Results

Click **"Load More"** to fetch the next 50 verses.

**Behavior:**
- New verses are **appended** to existing results
- Scroll position is maintained
- Statistics update to reflect new range

### Going Back

Click **"Previous"** to return to previous page of results.

**Behavior:**
- Removes the most recently loaded batch
- Returns to previous offset
- Useful for reviewing earlier results

### Pagination Details

- **Page size**: 50 verses per page
- **Total count**: Exact count of matching verses
- **Background loading**: Count is calculated in the background for performance

---

## Tips and Best Practices

### General Tips

1. **Start broad, then narrow**
   - Begin with all types selected and all books
   - Apply filters gradually to refine results

2. **Use metadata search for themes**
   - Find all God-as-shepherd metaphors: Target=`God`, Vehicle=`shepherd`
   - Explore anger language: Ground=`anger;wrath;fury`

3. **Combine search types**
   - Text search + metadata search work together
   - Example: Hebrew search for `ארץ` + Ground=`abundance` finds land abundance figures

4. **Toggle sacred/non-sacred**
   - Switch between versions to see different renderings
   - Useful for understanding traditional modifications

### Search Tips

**For best Hebrew search results:**
- Use unvocalized Hebrew (no nikud)
- Search short roots rather than full words
- Try multiple forms (e.g., `משה` and `משה׳`)

**For best English search results:**
- Use base words (e.g., `shepherd` not `shepherds`)
- Try synonyms for broader results
- Use partial words for flexibility

**For metadata search:**
- Start specific, then broaden if needed
- Use semicolons for OR logic across synonyms
- Combine fields for precise thematic searches

### Performance Tips

1. **Limit chapter/verse ranges when possible**
   - Narrower ranges load faster
   - Combine with type filters for best performance

2. **Use pagination intentionally**
   - Don't load all results at once if you have 1000+ matches
   - Browse incrementally with "Load More"

3. **Clear filters between major search changes**
   - Click "Clear All" types, then re-select
   - Clear search fields when starting new queries

### Research Workflows

**Finding patterns across books:**
1. Select all books
2. Choose one figurative type
3. Search specific metadata (e.g., Vehicle=`water`)
4. Browse results to identify patterns

**Analyzing a specific passage:**
1. Select single book and chapter
2. Include "Not Figurative" to see all verses
3. Read in context with figurative instances highlighted

**Thematic study (e.g., Divine Kingship):**
1. Target search: `God;Lord;deity`
2. Vehicle search: `king;ruler;throne`
3. Review all results for theological patterns

**Comparing translations:**
1. Search Hebrew text for a root
2. Read English translation alongside
3. Toggle sacred/non-sacred to see variations

---

## Keyboard Shortcuts

Currently, keyboard shortcuts are limited to:

### Active Shortcuts

- **Escape**: Close the verse details panel
- **Enter** (in search fields): Trigger search
- **Tab**: Navigate between form fields

### Mouse Interactions

- **Click verse header**: Open/close details panel
- **Click highlighted text**: View specific annotation details
- **Hover over highlights**: See type tooltip
- **Right-click**: Standard browser context menu

### Future Enhancements

Planned keyboard shortcuts (not yet implemented):

- `Ctrl/Cmd + F`: Focus search input
- `↑/↓`: Navigate between verses
- `Ctrl/Cmd + K`: Toggle Hebrew keyboard
- `N/P`: Next/Previous page

---

## Troubleshooting

### Common Issues

**"No verses match the current filters"**
- ✅ Ensure at least one figurative type is selected
- ✅ Check book/chapter/verse ranges are valid
- ✅ Clear search terms to broaden results

**Hebrew text not displaying correctly**
- ✅ Ensure browser supports Hebrew fonts
- ✅ Check browser zoom level (100% recommended)
- ✅ Try a different browser (Chrome/Firefox recommended)

**Hebrew keyboard not appearing**
- ✅ Click the ⌨ button next to search input
- ✅ Make sure Hebrew search mode is active (עברית button highlighted)
- ✅ Refresh the page if keyboard is stuck

**Search highlighting not working**
- ✅ Ensure search term is entered in active search box
- ✅ Check that verses contain the search term
- ✅ Try clearing and re-entering search term

**Slow performance**
- ✅ Narrow book/chapter/verse ranges
- ✅ Reduce number of selected figurative types
- ✅ Use pagination instead of loading all results
- ✅ Clear browser cache and reload

### Browser Compatibility

**Recommended browsers:**
- ✅ Google Chrome (latest)
- ✅ Mozilla Firefox (latest)
- ✅ Microsoft Edge (latest)
- ✅ Safari (latest)

**Minimum requirements:**
- HTML5 support
- CSS Grid support
- JavaScript ES6+ support
- Hebrew/RTL text rendering

---

## Advanced Features

### View AI Model Distribution

Check which AI models processed your results:
1. Open verse details panel for multiple verses
2. Note the model badge at the bottom of deliberation
3. Compare reasoning styles between models

**Insight:** Gemini Flash handles most cases; Pro/Claude appear for complex theological passages.

### Multi-Type Analysis

Study verses with multiple figurative types:
1. Select all types
2. Load results
3. Hover over highlights to see type tooltips
4. Look for common multi-type combinations

**Common combinations:**
- Metaphor + Idiom (e.g., "hardened heart")
- Personification + Metaphor (e.g., "the land vomited them")
- Hyperbole + Metaphor (e.g., "multiplied like the stars")

### Confidence Scoring Insights

While browsing annotation details, note confidence scores:
- **High (0.8-1.0)**: Clear figurative language
- **Medium (0.6-0.8)**: Interpretive judgment calls
- **Low (0.0-0.6)**: Borderline or uncertain cases

**Use this to assess reliability** for critical research.

---

## Accessibility

### Screen Reader Support

The interface includes:
- Semantic HTML structure
- ARIA labels on interactive elements
- Keyboard navigation support

**Note:** Some dynamic content may require manual navigation. Feedback welcome on accessibility improvements.

### Visual Accessibility

- High contrast text and backgrounds
- Color-coded types also have text labels
- Font sizes adjustable via browser zoom
- No critical information conveyed by color alone

### Language Support

- Hebrew text displays right-to-left (RTL) automatically
- English text displays left-to-right (LTR)
- Dual-language support for bilingual users

---

## Related Documentation

- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Database structure and SQL queries
- [METHODOLOGY.md](METHODOLOGY.md) - How the data was analyzed
- [FAQ.md](FAQ.md) - Frequently asked questions
- [NON_SACRED_HEBREW.md](NON_SACRED_HEBREW.md) - Hebrew divine name modifications
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Report issues or suggest features

---

## Feedback and Feature Requests

Found a bug or have a feature suggestion?

**Report it:** [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues)

**Suggest features:** [GitHub Discussions](https://github.com/[username]/bible-figurative-language-concordance/discussions)

We welcome all feedback to improve the interface!
