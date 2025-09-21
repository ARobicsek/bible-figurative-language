Hebrew Figurative Language Database
A comprehensive system for detecting and analyzing figurative language in biblical Hebrew texts, featuring a robust, context-aware multi-model LLM pipeline with two-stage validation for scholarly research.

🎉 Project Status: Production-Ready Validation Pipeline
LATEST BREAKTHROUGH: Deployed a comprehensive two-stage validation system that captures ALL detection deliberations and validation decisions. The system now provides complete audit trails for both accepted AND rejected figurative language instances, enabling deep analysis of detection accuracy and systematic improvement.

## 🧠 Current AI Models
- **Primary Model**: Gemini 2.5 Flash (latest, most capable)
- **Fallback Model**: Gemini 1.5 Flash (automatic fallback for restrictions)
- **Validation Model**: Gemini 1.5 Flash (conservative validation)

## 🎯 Current Status
✅ **Two-Stage Validation**: Primary detection + secondary validation to eliminate false positives
✅ **Complete Audit Trail**: Every detection and validation decision logged with reasoning
✅ **Deliberation Capture**: LLM explains what it considered and why for each verse
✅ **Rejected Instance Storage**: Failed validations stored with complete reasoning
✅ **Automatic Retry Logic**: Retries on server errors (500s) with exponential backoff
✅ **Interactive Processing**: Analyze any book, chapter, or verse range on demand
✅ **Context-Aware Prompting**: Different strategies for creation, legal, poetic, and narrative texts
✅ **Robust Error Handling**: Graceful handling of API restrictions, rate limits, and server errors
✅ **Research-Grade Data**: Complete metadata for reproducible scholarly analysis
🎯 **Publication Quality**: Comprehensive validation makes results suitable for peer-reviewed research
Multi-Model API Achievements
✅ Context-Aware Analysis: Uses different prompting strategies for creation_narrative, poetic_blessing, and legal_ceremonial texts to improve accuracy.
✅ Automated Fallback: Automatically switches from the primary model (e.g., Gemini 2.0 Flash) to a fallback model (e.g., Gemini 1.5 Flash) on content restriction errors.
✅ Intelligent Retries: Overcomes API rate limits by automatically waiting the recommended duration.
✅ JSON Extraction: Reliably extracts JSON data from "chatty" or conversational LLM responses.
✅ Type Sanitization: Prevents database crashes by automatically converting non-standard figurative language types (e.g., "irony") to 'other'.
✅ Scholar Confidence: The robust and transparent pipeline builds confidence in the results for academic use.
Technical Achievements
✅ Context-Aware Prompt Engineering: Tailors prompts based on the biblical text's genre.
✅ Complete Pipeline: End-to-end processing from Hebrew text extraction to sanitized database storage.
✅ 100% LLM-Based Detection: Pure AI-driven analysis with robust error handling and data validation.
✅ Enhanced Vehicle/Tenor Classification: Improved precision with specific categorization guidelines.
✅ Scholarly Explanations: PhD-level analysis with communicative intent detection.
✅ Multi-Instance Detection: Captures multiple figurative language types per verse.
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
🛠️ Enhanced Database Schema
The schema supports comprehensive analysis with complete audit trails.

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

-- Comprehensive figurative language table with validation tracking
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other')),
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
    -- Validation audit trail
    original_detection_type TEXT,    -- Original type before validation
    validation_decision TEXT CHECK(validation_decision IN ('VALID', 'INVALID', 'RECLASSIFY', NULL)),
    validation_reason TEXT,          -- Why validator made this decision
    validation_response TEXT,        -- Full validator response
    validation_error TEXT,           -- Any validation errors
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
```

## 📊 Data Completeness
- **Accepted Instances**: Full detection + validation data
- **Rejected Instances**: Complete audit trail of why they were rejected
- **Deliberations**: LLM reasoning about all potential figurative elements per verse
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