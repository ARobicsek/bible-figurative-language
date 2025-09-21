Hebrew Figurative Language Database
A comprehensive system for detecting and analyzing figurative language in biblical Hebrew texts, featuring a robust, context-aware multi-model LLM pipeline with multi-type classification and intelligent reclassification for scholarly research.

🎉 Project Status: Advanced Multi-Type Classification System
LATEST BREAKTHROUGH: Deployed an advanced multi-type classification system that allows phrases to be classified as multiple figurative language types simultaneously (e.g., both metaphor AND idiom). The system includes intelligent reclassification capabilities where the validator can correct misclassifications and provides complete audit trails for both initial detection and final validation results.

## 🧠 Current AI Models
- **Primary Model**: Gemini 2.5 Flash (latest, most capable)
- **Fallback Model**: Gemini 1.5 Flash (automatic fallback for restrictions)
- **Validation Model**: Gemini 1.5 Flash (conservative validation)

## 🎯 Current Status
✅ **Multi-Type Classification**: Each phrase can be classified as multiple figurative language types
✅ **Intelligent Reclassification**: Validator can correct misclassifications (e.g., metaphor → simile)
✅ **Dual-Field Architecture**: Separate tracking of initial detection vs. final validated results
✅ **Complete Audit Trail**: Every detection and validation decision logged with reasoning
✅ **Deliberation Capture**: LLM explains what it considered and why for each verse
✅ **Validation Transparency**: Clear distinction between detection, reclassification, and rejection
✅ **Automatic Retry Logic**: Retries on server errors (500s) with exponential backoff
✅ **Interactive Processing**: Analyze any book, chapter, or verse range on demand
✅ **Context-Aware Prompting**: Different strategies for creation, legal, poetic, and narrative texts
✅ **Robust Error Handling**: Graceful handling of API restrictions, rate limits, and server errors
✅ **Research-Grade Data**: Complete metadata for reproducible scholarly analysis
🎯 **Publication Quality**: Advanced validation makes results suitable for peer-reviewed research
Multi-Model API Achievements
✅ Context-Aware Analysis: Uses different prompting strategies for creation_narrative, poetic_blessing, and legal_ceremonial texts to improve accuracy.
✅ Automated Fallback: Automatically switches from the primary model (e.g., Gemini 2.0 Flash) to a fallback model (e.g., Gemini 1.5 Flash) on content restriction errors.
✅ Intelligent Retries: Overcomes API rate limits by automatically waiting the recommended duration.
✅ JSON Extraction: Reliably extracts JSON data from "chatty" or conversational LLM responses.
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
Prerequisites
Python 3.9+
Virtual environment recommended
Installation
bash
git clone https://github.com/ARobicsek/bible-figurative-language
cd bible-figurative-language
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
Note: Ensure python-dotenv is included in your requirements.txt file.

Configuration (Required)
In the root directory of the project, create a file named .env.
Add your Gemini API key to this file:
plaintext
GEMINI_API_KEY=AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk
Crucially, add .env to your .gitignore file to keep your API key secure.
Usage
IMPORTANT: Unicode Support Required On Windows, always run this command first in your terminal to enable proper display of Hebrew text and emojis:

bash
chcp 65001
Interactive Processing (Recommended for Targeted Analysis)
This script allows you to analyze any book, chapter, or specific range of verses.

bash
# Run the interactive processor
python interactive_multi_model_processor.py
The script will guide you through selecting the text you wish to process.

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
🛠️ Advanced Multi-Type Database Schema
The schema supports multi-type classification with comprehensive audit trails.

```sql
-- Verses table with deliberation capture
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    english_text TEXT NOT NULL,
    word_count INTEGER,
    llm_restriction_error TEXT,      -- API errors for this verse
    llm_deliberation TEXT,           -- LLM's reasoning about ALL potential figurative elements
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Advanced multi-type figurative language table with reclassification support
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
    -- Core Analysis Fields
    vehicle_level_1 TEXT,
    vehicle_level_2 TEXT,
    tenor_level_1 TEXT,
    tenor_level_2 TEXT,
    confidence REAL NOT NULL,
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    explanation TEXT,
    speaker TEXT,
    purpose TEXT,
    original_detection_types TEXT,   -- Comma-separated list of originally detected types
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
    validation_response TEXT,        -- Full validator response
    validation_error TEXT,           -- Any validation errors
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
```

## 📊 Advanced Data Architecture
- **Multi-Type Detection**: Each phrase can be simultaneously classified as multiple types
- **Initial vs. Final Fields**: Clear separation between what was detected vs. what was validated
- **Reclassification Tracking**: Complete audit trail when validator corrects type assignments
- **Deliberations**: LLM reasoning about all potential figurative elements per verse
- **Per-Type Validation**: Independent validation decisions and reasoning for each figurative type
- **Error Tracking**: Complete logging of API errors and restrictions
🎯 Use Cases
Biblical Scholarship
Targeted Analysis: Use the interactive script to quickly analyze specific passages, verses, or ranges for research papers or class preparation.
Character-Specific Patterns: Reliably track how specific characters (e.g., Jacob, Moses) use figurative language across different contexts.
Cross-Book Comparative Studies: Confidently compare figurative language use across different books, thanks to the consistent and robust pipeline.
Linguistic Research
Hebrew Figurative Language Patterns: Study patterns with research-grade accuracy, backed by a resilient data collection method.
Translation Analysis: Compare the original Hebrew with English translations, using the LLM's analysis as a guide.
🤝 Contributing
This project is designed for biblical scholarship and linguistic research. Contributions are welcome for:

Enhancing context-aware prompting rules.
Adding new analysis scripts or features.
Creating scholarly validation datasets to further refine accuracy.
📜 License
This project is open source and available for academic and research use.