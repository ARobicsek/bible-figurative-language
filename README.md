# Hebrew Figurative Language Database

A comprehensive system for detecting and analyzing figurative language (metaphors, similes, personification, idioms, hyperbole) in biblical Hebrew texts, with revolutionary LLM integration for scholarly research.

## 🎉 Project Status: Production-Ready Validation System

**Phase 1-3 Complete:** Real Gemini API integration with comprehensive validation framework for biblical Hebrew figurative language analysis.

### Key Achievements
- ✅ **Hebrew-Native Analysis**: Working directly with original Hebrew text
- ✅ **7x Detection Improvement**: 21 instances vs 3 from simulation (Deuteronomy 30)
- ✅ **Scholarly Explanations**: PhD-level analysis and reasoning
- ✅ **Multi-Instance Detection**: Multiple figurative language types per verse
- ✅ **Enhanced Database Schema**: Support for detailed explanations and subcategorization
- ✅ **Validation Framework**: 200-verse random sampling system for quality assessment
- ✅ **Individual Verse Processing**: Precise targeting without chapter-level processing
- ✅ **Production Database Schema**: Optimized for Hebrew + English figurative text storage

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

### Example LLM Analysis Output (Genesis 2:23)
```json
{
  "type": "metaphor",
  "figurative_text": "bone of my bones and flesh of my flesh",
  "figurative_text_in_hebrew": "עֶצֶם מֵעֲצָמַי וּבָשָׂר מִבְּשָׂרִי",
  "explanation": "The man's statement uses 'bone of my bones and flesh of my flesh' metaphorically to express the profound intimacy and oneness he feels with the woman, emphasizing their shared essence and origin.",
  "subcategory": "body",
  "confidence": 0.98
}
```

### Detection Capabilities
- **Metaphor**: Direct comparisons without "like/as"
- **Simile**: Comparisons using "like/as" or Hebrew כְּ/כַּאֲשֶׁר
- **Personification**: Human characteristics attributed to non-human entities
- **Idiom**: Expressions with non-literal meanings
- **Hyperbole**: Deliberate exaggeration for emphasis
- **Metonymy**: Substitution with closely associated concepts

## 🗂️ Project Structure

```
src/hebrew_figurative_db/
├── pipeline.py                    # Main processing pipeline
├── text_extraction/
│   ├── sefaria_client.py          # Hebrew/English text API client
│   └── hebrew_utils.py            # Hebrew processing utilities
├── ai_analysis/
│   ├── gemini_api.py              # Real Gemini API integration with usage tracking
│   ├── hybrid_detector.py         # LLM-only detection (no rule fallback)
│   ├── figurative_detector.py     # Legacy rule-based detection
│   └── llm_detector.py            # LLM interface
└── database/
    └── db_manager.py              # Production SQLite operations

validation/
├── generate_random_validation_set.py   # 200-verse random sampler
├── process_individual_verses.py        # Individual verse processor
├── validation_set_200_verses.json      # Random verse references
└── query_non_figurative_verses.sql     # Analysis queries
```

## 📈 Performance Metrics

### Phase 1 Foundation Results
- **80 verses processed** (Genesis 1-3)
- **42 figurative instances detected**
- **0% error rate** (perfect execution)
- **61.7 verses/second** processing speed
- **<0.1ms** database query performance

### Phase 2.5 LLM Breakthrough
- **Real Gemini API integration** with Hebrew-native analysis
- **21 figurative instances** detected in Deuteronomy 30 vs 3 from simulation
- **Scholarly-quality explanations** suitable for academic research
- **Multiple instance detection** per verse when applicable

## 🛠️ Database Schema

Enhanced schema with comprehensive figurative language support:

```sql
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'other')),
    confidence REAL NOT NULL,
    english_text TEXT NOT NULL,
    hebrew_text TEXT,
    hebrew_text_stripped TEXT,        -- Hebrew without diacritics
    figurative_text TEXT,            -- Specific figurative words
    explanation TEXT,                -- WHY it's figurative language
    subcategory TEXT,               -- Domain classification
    speaker TEXT,                   -- Who is speaking
    pattern TEXT,
    detection_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🔍 Available Databases

### Research-Quality Databases
- **`gemini_deuteronomy_30.db`** ⭐ **RECOMMENDED** - Real LLM analysis (21 instances)
- **`performance_test.db`** - Original Genesis 1-3 analysis (42 instances)

### Tools and Scripts
- **`test_llm_pipeline.py`** - Compare LLM vs rule-based detection
- **`query_database.py`** - Interactive database queries
- **`view_results_genesis_1_3.py`** - Complete results viewer

## 📚 Research Applications

### Proximity Analysis
Find figurative language within N verses of a reference:
```sql
SELECT * FROM figurative_language
WHERE book = 'Genesis'
AND ABS((chapter - 1) * 100 + verse - 115) <= 5
ORDER BY chapter, verse;
```

### Domain Classification Analysis
```sql
SELECT subcategory, COUNT(*) as count
FROM figurative_language
GROUP BY subcategory
ORDER BY count DESC;
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
**Status**: Production-ready with revolutionary LLM integration
**Research Quality**: Suitable for biblical scholarship and linguistic analysis