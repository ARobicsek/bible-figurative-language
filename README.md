# Hebrew Figurative Language Database
A comprehensive system for detecting and analyzing figurative language in biblical Hebrew texts, featuring **two complementary processing systems**: a proven multi-model pipeline and a revolutionary flexible hierarchical tagging system for advanced scholarly research.

## 🎉 Project Status: Dual-System Architecture Complete
**LATEST ACHIEVEMENT**: Successfully implemented **Flexible Hierarchical Tagging System** alongside the original multi-model pipeline, providing scholars with both proven conservative detection and innovative hierarchical categorization capabilities.

**✅ PHASE 1 COMPLETED (Sept 22, 2025)**: Data preprocessing and cleanup successfully completed with comprehensive category normalization and multi-type instance handling.

**🎯 PHASE 2 READY**: LLM-based conceptual grouping to create semantic clusters for intuitive visualization.

### Latest Achievements

**🆕 Flexible Hierarchical Tagging System (Sept 25, 2025)**
- **Revolutionary Tagging**: Hierarchical arrays for Target/Vehicle/Ground/Posture (e.g., ["specific target", "target category", "general domain"])
- **Split Deliberations**: Separate LLM reasoning for detection vs. tagging analysis for token efficiency
- **Enhanced JSON Parsing**: Robust extraction from conversational AI responses with bracket matching
- **Increased Token Limits**: 15,000 tokens to prevent truncation of complex hierarchical analysis
- **Database Integration**: Complete schema v3 with JSON storage and validation pipeline compatibility
- **Proven Results**: 21 instances detected from Deuteronomy 30 with full hierarchical metadata

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

## 🧠 Current AI Models
- **Primary Model**: Gemini 2.5 Flash (latest, most capable)
- **Fallback Model**: Gemini 1.5 Flash (automatic fallback for restrictions)
- **Validation Model**: Gemini 1.5 Flash (conservative validation)

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
✅ **Deliberation Capture**: LLM explains what it considered and why for each verse
✅ **Validation Transparency**: Clear distinction between detection, reclassification, and rejection
✅ **Advanced Server Error Recovery**: Exponential backoff for 500 errors with 30-second timeout fallback
✅ **Intelligent Model Switching**: Automatic fallback to Gemini 1.5 Flash after persistent server errors
✅ **Comprehensive Error Tracking**: Separate statistics for content restrictions vs server error fallbacks
✅ **Interactive Processing**: Analyze any book, chapter, or verse range on demand
✅ **Context-Aware Prompting**: Different strategies for creation, legal, poetic, and narrative texts
✅ **Robust Error Handling**: Graceful handling of API restrictions, rate limits, and server errors
✅ **JSON Repair System**: Automatic recovery from truncated LLM responses to preserve partial results
✅ **Data Loss Tracking**: Database fields to track detected vs recovered instances for research integrity
✅ **Research-Grade Data**: Complete metadata for reproducible scholarly analysis
🎯 **Publication Quality**: Advanced validation makes results suitable for peer-reviewed research
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
# NEW: Flexible Hierarchical Tagging System (Revolutionary hierarchical tags)
python interactive_flexible_tagging_processor.py

# ORIGINAL: Proven Multi-Model System (Conservative detection)
python interactive_multi_model_processor.py

Both scripts will guide you through selecting the text you wish to process.

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
    vehicle_specific TEXT,
    target_level_1 TEXT,
    target_specific TEXT,
    ground_level_1 TEXT,
    ground_specific TEXT,
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
- **950 validated figurative language instances** from Deuteronomy
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