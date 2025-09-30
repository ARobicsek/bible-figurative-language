# Frequently Asked Questions (FAQ)

**Common questions about the Hebrew Figurative Language Explorer**

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Data and Methodology](#data-and-methodology)
3. [Using the Interface](#using-the-interface)
4. [Technical Questions](#technical-questions)
5. [Academic and Research Use](#academic-and-research-use)
6. [Contributing and Feedback](#contributing-and-feedback)

---

## General Questions

### What is the Hebrew Figurative Language Explorer?

An interactive web-based tool providing access to 5,846 Torah verses analyzed for figurative language using advanced AI models. The database contains 3,020 validated instances of metaphors, similes, personifications, idioms, hyperboles, and metonymies.

### Is this tool free to use?

Yes! Both the interface and database are freely available under open licenses:
- **Code**: MIT License (free for any use)
- **Data**: CC BY 4.0 (free with attribution)

### Who created this?

The Hebrew Figurative Language Explorer was created by Ari Robicsek as a research tool for exploring biblical figurative language using modern AI capabilities.

### What does "The Pardes Project" mean?

"Pardes" (פרד״ס) is a Hebrew acronym representing four levels of biblical interpretation in Jewish tradition: Peshat (literal), Remez (hinted), Derash (interpretive), and Sod (mystical). The project name reflects this multi-layered approach to understanding biblical text.

### Can I use this for my research or teaching?

Absolutely! The tool is designed for scholarly research, teaching, and educational use. Just remember to:
- Cite the database appropriately (see README.md)
- Note that classifications are AI-generated
- Validate critical findings with traditional sources
- Acknowledge limitations in your methodology

---

## Data and Methodology

### Which books are included in the database?

The current version (1.0) covers the complete **Torah** (Pentateuch):
- Genesis (Bereishit)
- Exodus (Shemot)
- Leviticus (Vayikra)
- Numbers (Bamidbar)
- Deuteronomy (Devarim)

**Total:** 5,846 verses analyzed

**Future expansion** to Prophets and Writings is planned.

### Which AI models were used?

The analysis uses a three-tier fallback strategy:

1. **Gemini 2.5 Flash** (primary) - ~95% of verses
2. **Gemini 2.5 Pro** (fallback) - Complex passages
3. **Claude Sonnet 4** (final fallback) - Extremely complex cases

Every verse in the database includes a `model_used` field so you can see which AI analyzed it.

### How accurate are the AI classifications?

AI classifications should be viewed as **high-quality interpretations, not definitive truth**.

**Strengths:**
- Systematic and consistent methodology
- Complete transparency (full AI reasoning preserved)
- Two-stage validation process
- Confidence scoring for each instance

**Limitations:**
- AI may miss subtle cultural/historical context
- Multiple valid interpretations may exist
- Some classifications may differ from traditional commentaries

**Recommendation:** Use as a research tool to complement traditional scholarship, not replace it.

### What does "confidence score" mean?

Each figurative instance has a confidence score (0.0-1.0) representing the AI's self-assessed certainty:

- **0.8-1.0**: High confidence - clear figurative language
- **0.6-0.8**: Medium confidence - interpretive judgment
- **0.0-0.6**: Low confidence - borderline or uncertain

**Note:** Even low-confidence instances are included for completeness. You can filter by confidence if needed.

### Can a phrase be multiple figurative types at once?

Yes! The database supports **multi-type classification** because figurative language is complex.

**Example:** "God hardened Pharaoh's heart"
- ✅ **Metaphor** (heart = will/mind)
- ✅ **Idiom** (fixed non-literal expression)

**Why?** Different scholarly traditions and theoretical frameworks categorize figurative language differently. The database preserves this complexity.

### What are Target/Vehicle/Ground/Posture?

These are the four **metadata dimensions** used to classify each figurative instance:

- **TARGET**: What/who the figure is about (e.g., "Moses")
- **VEHICLE**: What it's compared to (e.g., "shepherd")
- **GROUND**: What quality is described (e.g., "leadership")
- **POSTURE**: Speaker's attitude (e.g., "reverence")

Each dimension is stored as a **hierarchical array** from specific to general, enabling both precise and broad searches.

See [METHODOLOGY.md](METHODOLOGY.md#classification-framework) for detailed explanations.

### Where does the Hebrew and English text come from?

All source texts are from **Sefaria.org**, an open-source repository of Jewish texts:
- Hebrew text with vowel points (nikud)
- English translations
- Consistent versification

**Sefaria is community-vetted** and widely used in digital biblical scholarship.

### What does "Two-Stage Analysis" mean?

Each verse goes through two independent AI analysis stages:

**Stage 1: Detection**
- AI reads the verse and identifies figurative language
- Classifies types and assigns metadata
- Records complete reasoning

**Stage 2: Validation**
- **Same AI model** re-analyzes its own detection
- Confirms, reclassifies, or rejects initial findings
- Documents validation reasoning

This two-stage process minimizes false positives and improves accuracy.

See [METHODOLOGY.md](METHODOLOGY.md#two-stage-analysis-process) for details.

---

## Using the Interface

### How do I search for a specific verse?

1. Select the book from the sidebar
2. Enter the chapter number (e.g., `3`)
3. Enter the verse number (e.g., `15`)
4. Click "Load Verses"

**Or** use text search to find verses containing specific words.

### How do I search Hebrew text if I don't have a Hebrew keyboard?

Use the **virtual Hebrew keyboard** built into the interface:

1. Click the ⌨ button next to the search input
2. Click Hebrew letters to type them
3. Use the keyboard's Space and Backspace buttons
4. Click ⌨ again to hide the keyboard

The keyboard includes all 22 Hebrew letters plus 5 final forms.

### What does the yellow highlighting mean?

**Yellow highlighting** indicates text identified as figurative language.

**Hover over yellow highlights** to see which figurative types apply (metaphor, simile, etc.) in a tooltip.

### What does the pink highlighting mean?

**Pink highlighting** indicates your **search term match** in the text.

If pink appears **inside** yellow highlighting, it means your search term is part of figurative language.

### Can I search for multiple words at once?

**In text search:** No, search treats your input as a single phrase.

**In metadata search:** Yes! Use semicolons (`;`) to separate multiple terms for OR logic:
- Example: `God;Lord;deity` finds any of these three

### How do I see the AI's reasoning?

Click on any **verse header** to open the bottom details panel, which shows:
- Complete detection deliberation
- Validation reasoning for each type
- Which AI model was used

### What does "Sacred Names" vs. "Traditional Jewish" mean?

**Sacred Names** (default):
- Shows full divine names as in original Hebrew
- Standard English translation

**Traditional Jewish**:
- Modifies Hebrew divine names with traditional abbreviations (e.g., `ה'`)
- Modifies English to follow Orthodox conventions (e.g., "Hashem", "G-d")

This option is provided for traditional Jewish study environments. See [NON_SACRED_HEBREW.md](NON_SACRED_HEBREW.md) for details.

### Why do some verses show "Not Figurative"?

If you select the **"Not Figurative"** filter, you'll see verses where the AI found **no figurative language**.

**Use cases:**
- Study literal vs. figurative language distribution
- Read specific passages in full context
- Verify AI detection patterns

### How many verses load at once?

The interface loads **50 verses per page** by default.

Click **"Load More"** at the bottom to fetch the next 50 verses. The new verses are appended to your current results.

### Can I export the data?

**Current version (1.0):** No built-in export feature yet.

**Workaround:** You can query the database directly (see [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)) and export via SQL.

**Planned (v1.1+):** CSV and JSON export features are on the roadmap.

---

## Technical Questions

### What technology is the interface built with?

**Frontend:**
- Pure HTML/CSS/JavaScript
- No framework dependencies
- Responsive design

**Backend:**
- Python Flask API server
- SQLite database (local version)
- Supabase PostgreSQL (hosted version)

**Why no frameworks?** To keep the tool lightweight, fast, and easy to deploy.

### Can I run this locally?

Yes! See [SETUP.md](../SETUP.md) for installation instructions.

**Requirements:**
- Python 3.8+
- Modern web browser

**Installation:**
```bash
pip install -r web/requirements.txt
python web/api_server.py
```

Then open http://localhost:5000

### Does this work on mobile devices?

Yes, the interface is **responsive** and works on tablets and smartphones.

**Note:** The Hebrew keyboard is optimized for desktop but functional on mobile.

### Which browsers are supported?

**Recommended:**
- Google Chrome (latest)
- Mozilla Firefox (latest)
- Microsoft Edge (latest)
- Safari (latest)

**Requirements:**
- HTML5, CSS Grid, JavaScript ES6+
- Hebrew/RTL text rendering support

### Can I host my own version?

Absolutely! The code is MIT-licensed, so you can:
- Run locally for personal use
- Deploy to your own server
- Modify the interface
- Integrate with other tools

See [SETUP.md](../SETUP.md) for deployment options.

### How do I migrate the SQLite database to PostgreSQL?

See [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md#migration-to-postgresql) for migration instructions.

**Key changes needed:**
- `INTEGER PRIMARY KEY AUTOINCREMENT` → `SERIAL PRIMARY KEY`
- `TIMESTAMP DEFAULT CURRENT_TIMESTAMP` → `TIMESTAMP DEFAULT NOW()`
- Consider using `JSONB` for metadata fields

### What's the database file size?

**Database file:** ~35 MB

**Contents:**
- 5,846 verses
- 3,020 figurative instances
- Complete Hebrew/English text
- All AI deliberations and metadata

---

## Academic and Research Use

### Can I cite this in a scholarly publication?

Yes! Please use the BibTeX citation in [README.md](../README.md#citation).

**Also remember to:**
- Note that classifications are AI-generated
- Acknowledge limitations in your methodology
- Validate critical findings with traditional sources

### Is this peer-reviewed?

No, the database represents **AI analysis**, not peer-reviewed scholarly consensus.

**This is a research tool**, not a substitute for:
- Traditional biblical commentaries
- Peer-reviewed linguistic studies
- Expert rabbinic interpretation

**Use it to:**
- Generate hypotheses
- Identify patterns
- Supplement traditional research
- Demonstrate concepts in teaching

### How should I describe this in my methodology section?

**Suggested language:**

> "Figurative language instances were identified using the Hebrew Figurative Language Explorer (Robicsek, 2025), an AI-analyzed database of Torah figurative language. The database uses Google Gemini and Anthropic Claude models with two-stage validation. All AI classifications cited in this study were manually verified against traditional commentaries."

### Can I use this for my dissertation/thesis?

Yes, with appropriate caveats:

**Recommended:**
- Use as **supplementary evidence** alongside traditional sources
- Manually verify all critical claims
- Discuss AI methodology and limitations
- Compare AI findings with scholarly consensus

**Not recommended:**
- Sole source for claims without verification
- Definitive theological arguments based only on AI analysis
- Quantitative analysis without acknowledging AI uncertainty

### Are there any comparable tools or databases?

**Similar projects:**
- Various biblical concordances (mostly literal, not figurative)
- Manual figurative language studies (limited scope)
- Some AI biblical analysis tools (different focus)

**What makes this unique:**
- Comprehensive Torah coverage (5,846 verses)
- Systematic AI analysis with validation
- Rich hierarchical metadata
- Complete transparency (full AI reasoning)
- Free and open-source

### Can I build on this for my own research?

Absolutely! The dual license structure supports this:

**Code (MIT License):**
- Modify the interface
- Create derivative tools
- Integrate with your own projects

**Data (CC BY 4.0):**
- Use in research with attribution
- Create derived datasets
- Publish analyses and visualizations

**Examples:**
- Statistical analysis of figurative patterns
- Comparative studies with other texts
- Visualization projects
- Machine learning training data (with attribution)

---

## Contributing and Feedback

### I found an incorrect classification. How do I report it?

**Use the Classification Feedback template:**

1. Go to [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues)
2. Click "New Issue"
3. Select "Classification Feedback" template
4. Provide:
   - Verse reference
   - What the AI classified
   - Why you think it's incorrect
   - Supporting evidence (optional)

**Community feedback helps improve the database!**

### Can I suggest new features?

Yes! We welcome feature suggestions.

**Submit via:**
- [GitHub Discussions](https://github.com/[username]/bible-figurative-language-concordance/discussions) (preferred)
- [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues) with "Feature Request" label

**Examples of features we're considering:**
- CSV/JSON export
- Bookmark and annotation system
- Advanced analytics and statistics
- Sankey diagrams for Target→Vehicle flows

### How can I contribute to the project?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

**Ways to contribute:**
- Report incorrect classifications
- Suggest interface improvements
- Fix bugs or add features (pull requests)
- Improve documentation
- Test on different browsers/devices
- Share the tool with colleagues

### Will this expand to other biblical books?

**Planned:** Yes! Future versions may include:
- Prophets (Nevi'im)
- Writings (Ketuvim)
- Possibly New Testament (if there's interest)

**Timeline:** To be determined based on resources and community interest.

**Want to help?** Reach out via GitHub Discussions!

### Can I help with translations (interface in other languages)?

We would love multilingual interface support!

**Currently supported:**
- English interface
- Hebrew and English biblical text

**Potential future languages:**
- Spanish
- French
- German
- Modern Hebrew interface

**Interested in helping?** Open a discussion on GitHub!

### Is there a mailing list or newsletter?

Not currently, but **watch the GitHub repository** for updates:
- Click "Watch" on the [GitHub repo](https://github.com/[username]/bible-figurative-language-concordance)
- Select "Custom" → "Releases"
- Get notified of new versions and features

---

## Privacy and Data

### Does the tool track my usage?

**Hosted version:** May use basic analytics (page views, anonymous usage stats)

**Local version:** No tracking whatsoever - runs entirely on your machine

**No personal data is collected** in either version.

### Can I use this offline?

**Local installation:** Yes! Once installed, the tool runs entirely offline.

**Hosted version:** Requires internet connection.

See [SETUP.md](../SETUP.md) for local installation instructions.

### Is my search history saved?

No. All searches are performed in real-time and **not logged or saved**.

Your search queries exist only in your browser session and are not transmitted to any server (except the API request for results).

---

## Troubleshooting

### The interface isn't loading. What do I do?

**Check:**
1. Is the API server running? (local version)
2. Is your internet connection working? (hosted version)
3. Try refreshing the page (Ctrl+F5 / Cmd+Shift+R)
4. Check browser console for errors (F12 → Console tab)
5. Try a different browser

If problems persist, open a [GitHub Issue](https://github.com/[username]/bible-figurative-language-concordance/issues).

### Hebrew text shows as boxes or question marks

**Solutions:**
1. Ensure your browser supports Hebrew fonts
2. Install Noto Sans Hebrew font on your system
3. Update your browser to the latest version
4. Try a different browser (Chrome/Firefox recommended)

### Search isn't working

**Troubleshooting steps:**
1. Clear the search field and try again
2. Check if Hebrew/English toggle matches your search language
3. Verify at least one figurative type is selected
4. Try a simpler search term
5. Refresh the page

### Performance is slow

**Optimization tips:**
1. Narrow book/chapter/verse ranges
2. Reduce number of selected figurative types
3. Use pagination (don't load 1000+ verses at once)
4. Clear browser cache
5. Close other browser tabs
6. Try local installation for better performance

---

## Still Have Questions?

**Didn't find your answer?**

- **Search existing issues:** [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues)
- **Ask a question:** Open a new issue with the "question" label
- **Join discussions:** [GitHub Discussions](https://github.com/[username]/bible-figurative-language-concordance/discussions)

**We're here to help!**
