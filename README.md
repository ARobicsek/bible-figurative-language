# Hebrew Figurative Language Database
A comprehensive production-ready system for detecting and analyzing figurative language in biblical Hebrew texts, featuring an **advanced three-tier AI architecture** with intelligent fallback processing and complete validation pipeline for scholarly research.

## 🎉 Project Status: Production-Ready Advanced AI Architecture
**LATEST ACHIEVEMENT**: Successfully completed **parallel processing integration** with hardcoded fallback fixes - the system now features high-performance parallel analysis with 100% verse coverage and comprehensive validation.

**✅ MAJOR BREAKTHROUGHS (Sept 27-29, 2025)**:
- **🔍 TEXT SEARCH FIX (Sept 29)**: Resolved critical bug where text search didn't work with "Not Figurative" filter - now properly filters non-figurative verses by search terms
- **⚡ PERFORMANCE OPTIMIZATION (Sept 29)**: Major database query optimizations - 3-5x faster page loads with bulk annotation fetching and improved query structure
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

**🔧 Hebrew Text Display Contamination Resolution (Sept 29, 2025)**
- **Critical Issue**: Hebrew text display was contaminated with English deliberation text (4,268+ characters) and validation reasons
- **Root Cause**: Massive annotation objects with large text fields were being serialized into HTML `data-annotation` attributes, causing display corruption
- **Solution**: Implemented minimal annotation storage system - only essential fields (target, vehicle, ground, types, etc.) stored in HTML attributes
- **Data Recovery**: Full annotation details retrieved from `appState.verses` when needed for click functionality
- **Performance Impact**: Reduced HTML attribute size from 4,000+ to ~200 characters per annotation, eliminating display contamination
- **Functionality Preserved**: All features working - Hebrew text clean, validation reasons display correctly, explanations intact
- **Result**: **Production-ready Hebrew text display** with zero contamination and full interactive functionality

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
- **🔍 Advanced Metadata Filtering**: Multi-field search with Target/Vehicle/Ground/Posture metadata using AND/OR logic
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **⚡ Real-Time Data**: Live connection to your SQLite database with intelligent pagination
- **🔗 Enhanced Interactive Details**:
  - Click verses for AI deliberations and model information
  - Click highlighted text for comprehensive analysis including validation reasons
  - Hover over highlights for instant type information with colored indicators
  - Dynamic panel sizing for optimal content viewing
- **🎯 Smart Navigation**: Clear "Load Next X Verses" button with exact counts and completion status
- **📊 Detailed Statistics**: Complete figurative language instance counts and database transparency

**🆕 Latest Interface Enhancements (Sept 29, 2025):**
- **🎭 "Not Figurative" Filtering**: Revolutionary new option to view verses WITHOUT figurative language
  - Added "Not Figurative" checkbox to figurative language type selector
  - Fixed "Clear All" behavior to show NO verses instead of ALL verses (user-requested improvement)
  - Enhanced user control: show only figurative, only non-figurative, or all verses
  - Yellow highlighting now always appears regardless of filter selections for better UX
- **🔧 Backend API Enhancement**: Updated server to handle `show_not_figurative` parameter with intelligent filtering logic

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
7. **Advanced Filter**: Use metadata search fields for Target/Vehicle/Ground/Posture filtering

**🎉 Current Status:** **FULLY OPERATIONAL** - Professional-grade interface with comprehensive filtering options

**✅ TEXT SEARCH & PERFORMANCE FIXES (Sept 29, 2025 - LATEST)**:
- **🔍 Search Functionality Fixed**: Text search now works correctly with "Not Figurative" filter - users can search within non-figurative verses
- **⚡ Major Performance Boost**: 3-5x faster page loads through database query optimizations:
  - Bulk annotation fetching (single query vs N+1 queries)
  - Optimized JOIN operations and GROUP BY usage
  - Improved count query performance
- **✅ Complete Testing**: Verified with multiple search terms - all filter combinations working perfectly

**✅ Enhanced Filtering System (Sept 29, 2025):** Added "Not Figurative" option for complete control over verse display - users can now view only figurative verses, only non-figurative verses, or all verses combined

**✅ Multi-Line Issue Resolved (Sept 28, 2025):** Successfully replaced complex annotation system with reliable yellow highlighting approach - works perfectly for all scenarios

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