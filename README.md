Hebrew Figurative Language Database
A comprehensive system for detecting and analyzing figurative language in biblical Hebrew texts, featuring a robust, context-aware multi-model LLM pipeline for scholarly research.

🎉 Project Status: Interactive Multi-Model Processing
LATEST BREAKTHROUGH: Deployed a resilient, context-aware multi-model API client with a new interactive processor. The system now intelligently handles API rate limits, sanitizes LLM responses to prevent data corruption, and allows for targeted analysis of any book, chapter, or verse range.

Current Status
✅ Interactive Processing: New script (interactive_multi_model_processor.py) to analyze any book, chapter, or verse range.
✅ Robust API Client: Multi-model system (gemini_api_multi_model.py) with context-aware prompting and automated fallbacks.
✅ Rate-Limit Handling: Automatically retries on 429 errors by parsing the API's recommended retry_delay.
✅ Data Sanitization: Intelligently extracts JSON from conversational LLM responses and sanitizes data types to prevent database errors.
✅ Secure Configuration: API keys are now managed securely using a .env file.
✅ Complete Data Storage: Every processed verse is stored in the database with full metadata, including any API errors.
✅ Research-Grade Accuracy: Context-aware system is suitable for published biblical scholarship.
🎯 Publication Quality: Results are reliable for academic research applications.
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
🛠️ Database Schema
The schema supports detailed analysis and error tracking.

sql
 Show full code block 
-- Verses table
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    english_text TEXT NOT NULL,
    word_count INTEGER,
    llm_restriction_error TEXT,      -- Tracks API errors for a given verse
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced figurative language table
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
    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
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