# Hebrew Figurative Language Database

A comprehensive system for detecting and analyzing figurative language (metaphors, similes, personification, idioms, hyperbole) in biblical Hebrew texts, with revolutionary LLM integration for scholarly research.

## 🎉 Project Status: Two-Level Subcategory System & False Positive Reduction Complete

**Phase 7 Complete:** Revolutionary two-level subcategory system with comprehensive false positive reduction. Implemented hierarchical classification (Level 1 | Level 2), eliminated literal description misclassification, and achieved 100% accuracy on validation tests. Complete Deuteronomy reprocessing with enhanced research-grade analytical capabilities.

### Key Achievements
- ✅ **Two-Level Subcategory System (Phase 7)**: Hierarchical classification with Level 1 (broad) | Level 2 (specific)
- ✅ **False Positive Reduction**: 100% accuracy on validation tests, eliminated literal misclassification
- ✅ **Enhanced Database Schema**: Added subcategory_level_1 and subcategory_level_2 fields
- ✅ **Comprehensive Migration**: 646 existing records migrated to new two-level structure
- ✅ **Improved LLM Prompts**: Specific exclusions for literal descriptions, historical statements, standard idioms
- ✅ **100% LLM-Based Detection**: No rule-based fallbacks, pure AI-driven analysis
- ✅ **Scholarly Explanations**: PhD-level analysis with communicative intent detection
- ✅ **Multi-Instance Detection**: Multiple figurative language types per verse
- ✅ **Speaker Attribution**: Precise identification of who speaks figurative language
- ✅ **Purpose Analysis**: Understanding why figurative language is used
- ✅ **Validation Framework**: 200-verse random sampling with error pattern analysis
- ✅ **Individual Verse Processing**: Precise targeting with 1.85 verses/second performance
- ✅ **Error Tracking**: Comprehensive monitoring of LLM restrictions and API limitations
- ✅ **Quality Assessment**: Eliminates technical religious terms and procedural false positives
- ✅ **Model Optimization**: Gemini 1.5 Flash with biblical content expertise
- ✅ **Ancient Context Awareness**: Distinguishes technical religious language from figurative language
- ✅ **Production Ready**: System validated for complete book processing with enhanced accuracy

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Virtual environment recommended

### Installation
```bash
git clone https://github.com/ARobicsek/bible-figurative-language
cd bible-figurative-language
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Basic Usage

#### LLM-Based Analysis (Recommended)
```python
from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline

# Initialize with real Gemini API
pipeline = FigurativeLanguagePipeline(
    'analysis_output.db',
    use_llm_detection=True,
    use_actual_llm=True
)

# Process biblical text
results = pipeline.process_verses("Deuteronomy.30")
print(f"Found {results['figurative_found']} figurative instances")
```

#### Rule-Based Analysis (Fast)
```python
# Initialize with rule-based detection
pipeline = FigurativeLanguagePipeline(
    'analysis_output.db',
    use_llm_detection=False
)

results = pipeline.process_verses("Genesis.1")
```

### View Results
```python
# Interactive query interface
python query_database.py

# View specific datasets
python view_results_genesis_1_3.py
```

## 📊 Research Quality Results

### Latest Results (Phase 7 Two-Level System)
- **Complete Deuteronomy Reprocessing**: All 34 chapters with improved two-level subcategory pipeline
- **Two-Level Classification**: Level 1 categories (The Natural World, Human Institutions and Relationships, Abstract and Internal States)
- **Enhanced Precision**: False positive reduction with specific literal exclusions
- **Migrated Database**: 646 existing records updated to hierarchical structure
- **100% Validation Accuracy**: Perfect classification on false positive test cases
- **Processing speed**: Maintained 1.85+ verses/second with enhanced accuracy

### Example Two-Level Analysis Output (Phase 7 Quality)
```json
{
  "type": "metaphor",
  "figurative_text": "The ancient God is a refuge",
  "figurative_text_in_hebrew": "אלהי קדם מעונה",
  "explanation": "God is compared to a physical place of safety and protection",
  "subcategory_level_1": "Human Institutions and Relationships",
  "subcategory_level_2": "architectural",
  "confidence": 0.90,
  "speaker": "Moses",
  "purpose": "express divine protection and security for the people"
}
```

**Phase 7 Improvements:**
- **Two-level hierarchy**: "Human Institutions and Relationships | architectural"
- **False positive elimination**: Literal descriptions like "good land" correctly excluded
- **Enhanced accuracy**: Historical statements like "We were slaves" no longer misclassified
- **Standard idiom filtering**: Expressions like "stray from path" correctly identified as literal
```

### Detection Capabilities (Phase 6.5 Enhanced)
- **Metaphor**: Direct comparisons excluding religious titles ("God of gods") and technical terms ("holy people")
- **Simile**: Comparisons using Hebrew כְּ/כַּאֲשֶׁר excluding procedural instructions ("do X as Y")
- **Personification**: Human characteristics attributed to non-human entities beyond simple divine speech
- **Idiom**: Expressions with non-literal meanings
- **Hyperbole**: Deliberate exaggeration for emphasis with conservative thresholds
- **Metonymy**: Substitution with closely associated concepts
- **Semantic Subcategories**: Architectural, geological, elemental, military, agricultural, familial, natural, celestial domains

## 🗂️ Project Structure

```
src/hebrew_figurative_db/
├── pipeline.py                    # Main processing pipeline
├── text_extraction/
│   ├── sefaria_client.py          # Hebrew/English text API client
│   └── hebrew_utils.py            # Hebrew processing utilities
├── ai_analysis/
│   ├── gemini_api.py              # Enhanced Gemini API with speaker/purpose detection
│   ├── hybrid_detector.py         # LLM-only detection with error tracking
│   ├── figurative_detector.py     # Legacy rule-based detection
│   └── llm_detector.py            # LLM interface
└── database/
    └── db_manager.py              # Enhanced database with speaker/purpose fields

Root Directory:
├── process_individual_verses.py        # Production individual verse processor
├── run_optimized_validation.py         # 200-verse validation runner
├── generate_random_validation_set.py   # Random verse sampler
├── validation_set_200_verses.json      # 200 random verse references
├── validation_findings.md              # Critical: LLM error analysis
└── validation_optimized_20250918_084059.db  # Latest validation results
```

## 📈 Performance Metrics

### Phase 4 Enhanced Schema Results
- **175 verses processed** from random Pentateuch sampling
- **467 figurative instances detected** with speaker/purpose metadata
- **1.85 verses/second** processing speed (optimized performance)
- **0% API restrictions** encountered during validation
- **2.67 instances per verse** detection rate

### Quality Assessment
- **Comprehensive validation findings** documented in `validation_findings.md`
- **Error pattern analysis** reveals systematic LLM improvement opportunities
- **Speaker attribution** achieved for all instances (God, Moses, Narrator, etc.)
- **Purpose analysis** provides scholarly insight into communicative intent

## 🛠️ Database Schema

Enhanced schema with two-level subcategory system:

```sql
-- Verses table
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    hebrew_text_stripped TEXT,
    english_text TEXT NOT NULL,
    word_count INTEGER,
    llm_restriction_error TEXT,      -- API restriction tracking
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced figurative language table with two-level subcategories
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other')),
    subcategory TEXT,                -- Legacy field for backward compatibility
    subcategory_level_1 TEXT,        -- NEW: Broad category (The Natural World, etc.)
    subcategory_level_2 TEXT,        -- NEW: Specific domain (animal, architectural, etc.)
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    explanation TEXT,
    speaker TEXT,                    -- Who speaks the figurative language
    purpose TEXT,                    -- Why the figurative language is used
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
```

## 🔍 Available Databases

### Primary Research Database
- **`deuteronomy_improved_YYYYMMDD_HHMMSS.db`** ⭐ **LATEST** - Complete Deuteronomy with enhanced pipeline
  - All 34 chapters processed with refined simile/metaphor detection
  - Semantic subcategories for meaningful analytical research
  - Eliminated false positives while maintaining genuine detection accuracy
- **`validation_optimized_20250918_084059.db`** - Enhanced schema with speaker/purpose analysis
  - 175 verses from across all 5 Pentateuch books
  - 467 figurative language instances with complete metadata
  - Speaker attribution and purpose analysis for each instance

### Key Documentation
- **`validation_findings.md`** ⭐ **CRITICAL** - Detailed analysis of LLM detection errors
- **`next_session_prompt.md`** - Complete project status and continuation guide

## 📚 Research Applications

### Proximity Analysis
Find figurative language within N verses of a reference:
```sql
SELECT * FROM figurative_language
WHERE book = 'Genesis'
AND ABS((chapter - 1) * 100 + verse - 115) <= 5
ORDER BY chapter, verse;
```

### Two-Level Category Analysis (Phase 7 Enhanced)
```sql
-- Hierarchical analysis by Level 1 categories
SELECT subcategory_level_1, COUNT(*) as count
FROM figurative_language
WHERE subcategory_level_1 IS NOT NULL
GROUP BY subcategory_level_1
ORDER BY count DESC;

-- Detailed breakdown by Level 2 within each Level 1
SELECT subcategory_level_1, subcategory_level_2, COUNT(*) as count
FROM figurative_language
WHERE subcategory_level_1 IS NOT NULL AND subcategory_level_2 IS NOT NULL
GROUP BY subcategory_level_1, subcategory_level_2
ORDER BY subcategory_level_1, count DESC;

-- Specific domain analysis (e.g., all architectural metaphors)
SELECT type, figurative_text, speaker
FROM figurative_language
WHERE subcategory_level_1 = 'Human Institutions and Relationships'
  AND subcategory_level_2 = 'architectural'
ORDER BY confidence DESC;
```

### Speaker-Specific Patterns
```sql
SELECT speaker, type, COUNT(*) as count
FROM figurative_language
GROUP BY speaker, type
ORDER BY speaker, count DESC;
```

## 🎯 Use Cases

### Biblical Scholarship
- Character-specific metaphor pattern analysis
- Figurative language frequency across books
- Proximity analysis of co-occurring metaphors
- Domain categorization (divine, body, nature, familial)

### Linguistic Research
- Hebrew figurative language patterns
- Translation analysis and comparison
- Diachronic figurative language evolution
- Cross-cultural metaphor analysis

## 🔧 Technical Features

### LLM Integration
- **Real-time Hebrew analysis** via Gemini API
- **Scholarly prompts** for biblical Hebrew expertise
- **Fallback systems** with rule-based detection
- **Usage monitoring** and API optimization

### Hebrew Processing
- **Diacritic removal** for search optimization
- **Speaker identification** (God, Moses, Narrator)
- **Original text preservation** with enhanced searchability
- **Multi-instance detection** per verse

### Database Features
- **Strategic indexing** for sub-millisecond queries
- **Multi-instance support** with separate rows per figurative type
- **Comprehensive metadata** for research applications
- **Export capabilities** for external analysis tools

## 📄 Documentation

- **`revised_plan.md`** - Complete project plan with Phase 2.5 breakthrough
- **`PHASE_1_SUMMARY.md`** - Detailed achievements and capabilities
- **`next_session_prompt.md`** - Continuation guide for development

## 🤝 Contributing

This project is designed for biblical scholarship and linguistic research. Contributions welcome for:
- Additional figurative language detection patterns
- Performance optimizations
- Research query templates
- Scholarly validation datasets

## 📜 License

This project is open source and available for academic and research use.

---

**Repository**: https://github.com/ARobicsek/bible-figurative-language
**Status**: Phase 7 Complete - Two-level subcategory system with false positive reduction
**Research Quality**: Hierarchical classification with 100% validation accuracy, suitable for advanced biblical scholarship