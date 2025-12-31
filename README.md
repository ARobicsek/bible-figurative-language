# Tzafun

**A concordance of Biblical figurative language**

*"Tzafun" (צָפֻן) means "hidden" or "concealed" and also implies treasure, as in Psalms 31:20: "How abundant is the good that You have in store (צָפַ֢נְתָּ) for those who fear You" and Psalm 119:11: "I have treasured (צָפַ֣נְתִּי) Your word in my heart."*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE-CODE.md)
[![Data License: CC BY 4.0](https://img.shields.io/badge/Data%20License-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA.md)

---

## 🌟 Overview

Tzafun is a comprehensive research tool that provides access to over 13,500 verses from 13 biblical books, analyzed for figurative language using advanced AI models (GPT-5.1, Claude Opus 4.5, Gemini 3.0). It originated with the question - couldn't we use powerful AI tools to compile a 'concordance' of biblical figurative speech? The database now contains over 11,000 validated instances of figurative language, including metaphors, similes, personifications, idioms, hyperboles, and metonymies from across the Torah (Pentateuch), Psalms, Proverbs, and major prophets.

**Key Features:**
- 🔍 Interactive search across Hebrew and English text
- 📊 Advanced filtering by figurative type, book, chapter, and metadata
- 🕊️ Sacred/non-sacred text toggle for traditional Jewish scholarship
- 📖 Dual-language display with proper Hebrew (RTL) support
- 🎯 Rich metadata including Target/Vehicle/Ground/Posture classifications
- 🤖 Complete AI transparency with full deliberation records

---

## 🚀 Live Demo

**[Try it now at https://tzafun.onrender.com](https://tzafun.onrender.com)**

*Note: The free tier deployment may take 30-60 seconds to wake up after periods of inactivity.*

---

## 📈 Database Statistics

The database provides comprehensive coverage across 13 biblical books with validated AI analysis:

| Metric | Count |
|--------|-------|
| **Total verses analyzed** | 13,548 |
| **Total figurative instances** | 11,119 |
| **Books covered** | 13 |

### Coverage by Book Category

| Category | Books | Verses |
|----------|-------|--------|
| **Torah (Pentateuch)** | Genesis, Exodus, Leviticus, Numbers, Deuteronomy | 5,846 |
| **Wisdom Literature** | Psalms, Proverbs | 3,380 |
| **Major Prophets** | Isaiah, Jeremiah, Ezekiel | 3,927 |
| **Minor Prophets** | Hosea, Joel, Amos | 395 |

### By Figurative Type

| Type | Count | Percentage |
|------|-------|------------|
| **Metaphors** | 5,368 | 48.3% |
| **Idioms** | 3,919 | 35.2% |
| **Metonymies** | 3,213 | 28.9% |
| **Personifications** | 1,223 | 11.0% |
| **Similes** | 849 | 7.6% |
| **Hyperboles** | 784 | 7.1% |
| **Other** | 185 | 1.7% |

*Note: Percentages sum to more than 100% because phrases can be classified as multiple types simultaneously*

---

## ✨ Key Features

### Interactive Exploration
- **Dual-language search**: Search Hebrew or English text with intelligent highlighting
- **Multi-criteria filtering**: Filter by book, chapter, figurative type, or metadata
- **Metadata search**: Find instances by Target/Vehicle/Ground/Posture classifications
- **Smart navigation**: Paginated browsing with exact verse counts

### Scholarly Transparency
- **AI deliberations**: View complete reasoning for each classification
- **Validation records**: See validation decisions and reclassifications
- **Model tracking**: Know which AI model analyzed each instance
- **Confidence scores**: Assess reliability of classifications

### Cultural Sensitivity
- **Non-sacred text option**: Traditional Jewish text modifications for study and printing
- **Hebrew divine names**: Automatic modification following traditional requirements
- **Dual-language support**: Both Hebrew and English text include non-sacred versions

### Research-Grade Quality
- **Three-tier AI validation**: Primary detection → secondary validation → quality assurance
- **Multi-type classification**: Phrases can be multiple figurative types simultaneously
- **Complete audit trail**: Full reasoning recorded for reproducibility
- **Hierarchical metadata**: Rich Target/Vehicle/Ground/Posture classifications

---

## 📚 Use Cases

### For Biblical Scholars
- Track figurative language patterns across Torah books
- Compare usage in narrative vs. legal vs. poetic texts
- Analyze divine representations and theological metaphors
- Generate publication-ready analyses with full citation

### For Linguists
- Study ancient Hebrew figurative language systems
- Analyze semantic domains and conceptual mappings
- Compare Hebrew source with English translations
- Identify patterns in Target→Vehicle relationships

### For Educators
- Prepare lesson materials on biblical Hebrew rhetoric
- Demonstrate figurative language concepts with real examples
- Create assignments with verifiable source material
- Engage students with interactive exploration

### For Students
- Research specific passages for papers and projects
- Learn to identify figurative language in context
- Understand Hebrew-English translation challenges
- Access scholarly-grade primary source material

---

## 🛠️ Getting Started

### Option 1: Use the Hosted Version (Recommended)

Simply visit [https://tzafun.onrender.com](https://tzafun.onrender.com) to start exploring immediately. No installation required!

### Option 2: Run Locally

**Requirements:**
- Python 3.8+
- Modern web browser

**Installation:**

```bash
# Clone the repository
git clone https://github.com/ARobicsek/bible-figurative-language.git
cd bible-figurative-language

# Install dependencies
pip install -r web/requirements.txt

# Start the server
cd web
python api_server.py
```

Then open http://localhost:5000 in your browser.

---

## 📖 Documentation

For detailed documentation on the project's methodology, database schema, and technical architecture, see:
- [PROJECT_OVERVIEW_AND_DECISIONS.md](PROJECT_OVERVIEW_AND_DECISIONS.md) - Complete project overview and strategic decisions
- [README_INTERNAL.md](README_INTERNAL.md) - Development history and technical achievements
- **About Page** - Visit the live application and click "About" for end-user documentation

---

## 🔬 Methodology

This database was created using a robust AI analysis pipeline with intelligent fallback handling:

**AI Model Strategy:**
- **Primary Model** (Gemini 2.5 Flash): Handles both initial detection and validation for most verses
- **Fallback Model** (Gemini 2.5 Pro): Used when Flash encounters complexity or token limits
- **Final Fallback** (Claude Sonnet 4): Reserved for extremely complex passages that exceed both Gemini models' capabilities

**Two-Stage Process:**
1. **Detection Stage**: AI analyzes each verse to identify figurative language and classify types
2. **Validation Stage**: The same AI model validates its own detections, with capability to reclassify or reject false positives

Each verse includes:
- Initial AI detection reasoning
- Validation decision and reasoning
- Reclassification notes (if applicable)
- Confidence scores
- Model attribution (which AI was used)

**Classification Framework:**

The analysis uses a structured metadata system to characterize each figurative instance:

- **TARGET** = WHO/WHAT the figurative speech is ABOUT (the subject being described)
  - *Example: "Judah is a lion" → Target: Judah*

- **VEHICLE** = WHAT the target is being LIKENED TO (the comparison/image used)
  - *Example: "Judah is a lion" → Vehicle: lion*

- **GROUND** = WHAT QUALITY of the target is being described (the shared characteristic)
  - *Example: "Judah is a lion" → Ground: strength*

- **POSTURE** = SPEAKER ATTITUDE/STANCE toward the subject (emotional orientation)
  - *Example: Celebratory, critical, warning, etc.*

**For complete methodology details, see [docs/METHODOLOGY.md](docs/METHODOLOGY.md)**

---

## 🎓 Citation

If you use this tool or database in your research, please cite:

```bibtex
@software{robicsek_tzafun_2025,
  author = {Robicsek, Ari},
  title = {Tzafun: A Concordance of Figurative Language in the Torah and Psalms},
  year = {2025},
  url = {https://github.com/ARobicsek/bible-figurative-language},
  note = {Version 1.0}
}
```

**APA Format:**
```
Robicsek, A. (2025). Tzafun: A Concordance of Figurative Language in the Torah and Psalms (Version 1.0) [Computer software]. https://github.com/ARobicsek/bible-figurative-language
```

**MLA Format:**
```
Robicsek, Ari. Tzafun: A Concordance of Figurative Language in the Torah and Psalms. Version 1.0, 2025, https://github.com/ARobicsek/bible-figurative-language.
```

---

## 📊 Technical Architecture

**Frontend:**
- Pure HTML/CSS/JavaScript
- Responsive design for all devices
- Hebrew (RTL) and English display
- Flask backend with REST API

**Backend:**
- Flask (Python) server
- SQLite database (49MB)
- Optimized queries with intelligent indexing
- Deployed on Render.com free tier

**Data Source:**
- Hebrew text: Miqra According to the Masorah (MAM) via Sefaria.org
- English translation: Jewish Publication Society, 2006 via Sefaria.org
- AI Analysis: Gemini 2.5 Flash/Pro + Claude Sonnet 4

---

## 🤝 Contributing

We welcome contributions! Areas where you can help:

- **Validation**: Report incorrect classifications
- **Features**: Suggest or implement new interface features
- **Documentation**: Improve guides and examples
- **Bug Reports**: Report issues or unexpected behavior
- **Translations**: Help translate the interface to other languages

Please open an issue on GitHub to discuss your contribution before starting work.

---

## 📜 License

This project uses a dual-license structure:

- **Code** (interface, scripts): [MIT License](LICENSE-CODE.md)
- **Data** (database, analysis): [CC BY 4.0](LICENSE-DATA.md)

You are free to:
- ✅ Use the data in research and publications (with attribution)
- ✅ Modify and build upon the code
- ✅ Use commercially (with attribution)
- ✅ Share and redistribute

**Attribution is required for all uses.**

---

## 🙏 Acknowledgments

- **Sefaria.org**: Hebrew and English text source
- **Google Gemini**: Primary AI analysis models
- **Anthropic Claude**: Fallback analysis for complex passages

---

## ⚠️ Limitations & Disclaimers

**This tool is designed for research and educational purposes.** Please note:

- AI classifications may contain errors and should be verified for critical research
- The database represents AI interpretation, not definitive scholarly consensus
- Cultural and religious sensitivities should be respected when using this tool
- Non-sacred text feature (i.e. names of God rendered in Hebrew using traditional abbreviations) is provided for traditional Jewish users but should be reviewed by qualified authorities for ritual use

**Validation and human review are recommended for scholarly publications.**

---

## 📞 Contact & Support

- **Issues & Bug Reports**: [GitHub Issues](https://github.com/ARobicsek/bible-figurative-language/issues)
- **Feature Requests**: [GitHub Discussions](https://github.com/ARobicsek/bible-figurative-language/discussions)
- **General Questions**: Open an issue with the "question" label

---

## 🌟 Project Status

**Version:** 1.0.0 (Public Release)
**Status:** ✅ Production Ready
**Last Updated:** October 1, 2025

---

## 🗺️ Roadmap

### Current (v1.0)
- ✅ Complete Torah database (8,373 verses)
- ✅ All 150 chapters of Psalms
- ✅ Interactive web interface
- ✅ Advanced filtering and search
- ✅ Sacred/non-sacred text toggle
- ✅ Complete AI transparency

### Planned (v1.1+)
- 🔜 Data export (CSV/JSON)
- 🔜 Bookmark and annotation features
- 🔜 Sankey visualization of Target→Vehicle flows
- 🔜 Advanced analytics and statistics
- 🔜 API access for programmatic queries

### Future Considerations
- Expansion to Prophets and other Writings
- Multi-language interface support
- Community validation system
- Integration with Bible study software

---

**Built with ❤️ for biblical scholarship and digital humanities**
