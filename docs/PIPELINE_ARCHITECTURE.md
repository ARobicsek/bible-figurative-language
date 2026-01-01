# Hebrew Figurative Language Detection Pipeline Architecture

**Part 1 Documentation: Data Generation Pipeline**

*Last Updated: December 2025 (v2.2.1)*

---

## Overview

This document describes the architecture of the **data generation pipeline** - the system that analyzes biblical Hebrew text to detect and classify figurative language instances. This is **Part 1** of the larger project, which also includes a website to render the data searchable (Part 2, not covered here).

The pipeline uses a multi-stage LLM-based approach to:
1. Fetch Hebrew and English text from the Sefaria API
2. Detect figurative language using AI analysis with hierarchical tagging
3. Validate detections using a second AI pass
4. Store results in a SQLite database with full audit trails

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Core Components](#core-components)
4. [Processing Modes](#processing-modes)
5. [Data Flow](#data-flow)
6. [Module Reference](#module-reference)
7. [Database Schema](#database-schema)
8. [Known Issues and Risks](#known-issues-and-risks)
9. [Configuration](#configuration)

---

## Quick Start

### Prerequisites

```bash
# Required environment variables (.env file in project root)
OPENAI_API_KEY=your_key      # Required for GPT-5.1 (primary model)
ANTHROPIC_API_KEY=your_key   # Optional for Claude fallback
GEMINI_API_KEY=your_key      # Optional for Gemini fallback
```

### Running the Pipeline

```bash
# Interactive mode (prompts for book/chapter selection)
cd private
python interactive_parallel_processor.py

# Command-line mode (specific book and chapter)
python interactive_parallel_processor.py Proverbs 15
```

### Supported Books

**v2.2.0: All books now use batched chapter-level processing with parallel chapter support.**

| Book | Chapters | Processing Mode |
|------|----------|-----------------|
| Genesis | 50 | **Batched (GPT-5.1)** |
| Exodus | 40 | **Batched (GPT-5.1)** |
| Leviticus | 27 | **Batched (GPT-5.1)** |
| Numbers | 36 | **Batched (GPT-5.1)** |
| Deuteronomy | 34 | **Batched (GPT-5.1)** |
| Psalms | 150 | **Batched (GPT-5.1)** |
| Proverbs | 31 | **Batched (GPT-5.1)** |
| Isaiah | 66 | **Batched (GPT-5.1)** |
| Jeremiah | 52 | **Batched (GPT-5.1)** |

**Chapter-Level Parallelization:** Multiple chapters can be processed simultaneously (default: 3 parallel chapters).

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    interactive_parallel_processor.py                     │
│                         (Main Orchestrator)                              │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
┌──────────────────┐    ┌──────────────────────┐    ┌──────────────────┐
│  SefariaClient   │    │ FlexibleTagging      │    │  DatabaseManager │
│  (Text Source)   │    │ GeminiClient         │    │  (Storage)       │
└──────────────────┘    │ (Detection)          │    └──────────────────┘
                        └──────────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │ UnifiedLLMClient     │
                        │ (Multi-Model Engine) │
                        └──────────────────────┘
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
          ▼                         ▼                         ▼
   ┌─────────────┐         ┌─────────────────┐       ┌─────────────────┐
   │  GPT-5.1    │         │  Claude Opus    │       │  Gemini 3.0     │
   │  (Primary)  │         │  4.5 (Fallback) │       │  Pro (Fallback) │
   └─────────────┘         └─────────────────┘       └─────────────────┘
                                    │
                                    ▼
                        ┌──────────────────────┐
                        │ MetaphorValidator    │
                        │ (Validation Stage)   │
                        └──────────────────────┘
```

---

## Core Components

### 1. interactive_parallel_processor.py (Main Entry Point)

**Location:** `private/interactive_parallel_processor.py`

The main orchestrator that:
- Provides interactive CLI for book/chapter/verse selection
- Manages two distinct processing modes (per-verse parallel vs. batched)
- Coordinates all sub-components
- Handles error recovery and validation verification
- Generates output files (database, logs, JSON summaries)

**Key Functions:**

| Function | Lines | Description |
|----------|-------|-------------|
| `main()` | ~1900-2320 | Entry point, initializes all components, orchestrates processing |
| `get_user_selection()` | 118-320 | Interactive CLI for flexible selection of books/chapters/verses |
| `process_validation_result()` | 385-450 | **[NEW]** Shared function for processing validation results |
| `recover_missing_validations()` | 453-556 | **[NEW]** Automatic recovery of missing validation data |
| `process_chapter_batched()` | 559-1480 | Batched processing for Proverbs/Isaiah (single API call per chapter) |
| `process_single_verse()` | ~1482-1630 | Per-verse processing with fallback chain |
| `process_verses_parallel()` | ~1632-1825 | Parallel processing of multiple verses with ThreadPoolExecutor |
| `parse_selection()` | 79-116 | Parses user input for flexible selection (e.g., "1,3,5-7", "all") |
| `has_corrupted_hebrew()` | 33-64 | Detects UTF-8 corruption in Hebrew text during streaming |
| `extract_individual_verses()` | 335-383 | Fallback JSON extraction from malformed responses |

---

### 2. FlexibleTaggingGeminiClient

**Location:** `private/flexible_tagging_gemini_client.py`

Enhanced LLM client that adds:
- Hierarchical tagging framework (TARGET/VEHICLE/GROUND/POSTURE)
- Context-aware prompting based on biblical text type
- 10-strategy JSON extraction system for robustness
- Claude Sonnet 4 tertiary fallback

**Key Methods:**

| Method | Description |
|--------|-------------|
| `analyze_figurative_language_flexible()` | Main analysis entry point with flexible tagging |
| `_create_flexible_tagging_prompt()` | Builds context-aware prompts with hierarchical tag instructions |
| `_parse_flexible_response()` | Extracts structured data from LLM responses |
| `analyze_with_claude_fallback()` | Claude Sonnet 4 fallback for complex verses |

**Context Types:**

| Context | Applied To | Detection Sensitivity |
|---------|------------|----------------------|
| `CREATION_NARRATIVE` | Genesis 1-3 | Ultra conservative |
| `POETIC_BLESSING` | Genesis 49, etc. | Balanced |
| `POETIC_WISDOM` | Proverbs, Psalms | Balanced (wisdom-aware) |
| `LEGAL_CEREMONIAL` | Leviticus, etc. | Moderate conservative |
| `NARRATIVE` | Default | Standard conservative |
| `PROPHETIC` | Isaiah | Enhanced sensitivity |

---

### 3. UnifiedLLMClient

**Location:** `private/src/hebrew_figurative_db/ai_analysis/unified_llm_client.py`

Multi-model engine with three-tier fallback:

```
GPT-5.1 (Primary) → Claude Opus 4.5 → Gemini 3.0 Pro
```

**Features:**
- Automatic fallback on model failures
- Token and cost tracking across all models
- Model-specific parameter translation
- Usage statistics and reporting

**Key Methods:**

| Method | Description |
|--------|-------------|
| `analyze_with_custom_prompt()` | Executes custom prompt through fallback chain |
| `_call_gpt51_with_prompt()` | GPT-5.1 API call with reasoning_effort parameter |
| `_call_claude_opus45_with_prompt()` | Claude API call with extended thinking |
| `_call_gemini3_pro_with_prompt()` | Gemini API call with thinking mode |

---

### 4. MetaphorValidator

**Location:** `private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py`

Second-stage validation system using GPT-5.1:

**Purpose:**
- Validates initial figurative language detections
- Can reclassify (e.g., metaphor → simile)
- Can reject false positives
- Provides validation reasoning for audit trail

**Key Methods:**

| Method | Description |
|--------|-------------|
| `validate_chapter_instances()` | Bulk validation for entire chapter (batched mode) |
| `validate_verse_instances()` | Validation for single verse's instances |
| `validate_chapter_instances_with_retry()` | Enhanced validation with 4-tier retry strategy |
| `_extract_json_with_fallbacks()` | Robust JSON extraction from validation responses |

**Validation Decisions:**
- `VALID`: Detection confirmed
- `INVALID`: False positive rejected
- `RECLASSIFIED`: Correct figurative language, different type

---

### 5. DatabaseManager

**Location:** `private/src/hebrew_figurative_db/database/db_manager.py`

SQLite database manager for:
- Verse storage with Hebrew/English text
- Figurative language instances with validation
- Hierarchical tags as JSON arrays
- Divine names modifications for traditional users

**Key Methods:**

| Method | Description |
|--------|-------------|
| `setup_database()` | Creates tables and indexes |
| `insert_verse()` | Inserts verse record, returns verse_id |
| `insert_figurative_language()` | Inserts detection with sanitization |
| `update_validation_data()` | Updates with validation results |
| `verify_validation_data_for_chapter()` | Checks validation coverage |
| `get_statistics()` | Returns processing statistics |

---

### 6. Supporting Modules

#### SefariaClient
**Location:** `private/src/hebrew_figurative_db/text_extraction/sefaria_client.py`

- Fetches Hebrew and English text from Sefaria API
- Handles HTML cleanup and text normalization
- Parses chapter/verse structure

#### HebrewTextProcessor
**Location:** `private/src/hebrew_figurative_db/text_extraction/hebrew_utils.py`

- Strips diacritics (cantillation marks, vowel points)
- Extracts root letters
- Identifies speakers from text patterns

#### HebrewDivineNamesModifier
**Location:** `private/src/hebrew_figurative_db/text_extraction/hebrew_divine_names_modifier.py`

- Modifies divine names for traditional Jewish users
- יהוה → ה׳ (Tetragrammaton)
- אלהים → אלקים (Elohim)
- Handles both voweled and unvoweled text

---

## Processing Modes

### Batched Chapter Processing with Parallel Chapters (v2.2.0+)

**Used for:** All supported books (Genesis through Jeremiah)

**Architecture (v2.2.1 - WriteQueue):**
- Each chapter is processed as a single batched API call
- Multiple chapters can be processed in parallel (default: 3 parallel chapters)
- **WriteQueue architecture** eliminates database lock contention (new in v2.2.1)

**Flow (v2.2.1):**
1. Build list of all chapter tasks from user selection
2. Start WriteQueue with dedicated writer thread
3. Submit chapters to ThreadPoolExecutor (default: 3 workers)
4. Each worker processes one chapter:
   a. Fetch all verses for chapter via Sefaria API (with caching)
   b. Build single prompt with ALL verses in chapter
   c. Single GPT-5.1 API call with streaming
   d. Parse JSON array with verse-by-verse results
   e. **Submit prepared data to WriteQueue** (no direct DB writes)
   f. Wait for write confirmation
5. Writer thread processes queue sequentially (zero lock contention)
6. Results aggregated across all parallel workers

**WriteQueue Architecture Diagram (v2.2.1):**
```
Workers (3 threads)              Write Queue            Writer Thread
    |                               |                       |
    |-- API call (parallel) --------|                       |
    |                               |                       |
    |-- put(chapter_data) --------->|                       |
    |                               |<-- get() -------------|
    |                               |                       |
    |                               |       insert all ---->|
    |                               |       commit -------->|
    |                               |                       |
    |-- API call (parallel) --------|                       |
```

**Advantages:**
- 95% token savings vs. per-verse processing
- Chapter-level parallelization for speed
- Better context for all biblical literature
- Chapter-wide thematic understanding
- Configurable parallelism (1-6 parallel chapters)

**Risks:**
- More complex JSON parsing required
- Single-point-of-failure for entire chapter (mitigated by parallel retry capability)
- Truncation handling more complex

### Legacy: Per-Verse Parallel Processing

**Status:** Deprecated in v2.2.0 - all books now use batched mode for cost efficiency.

The per-verse parallel processing mode is still available in the codebase but is no longer used by default.

---

## Data Flow

### Detection Phase

```
1. SefariaClient.extract_hebrew_text(reference)
   └── Returns: [{reference, hebrew, english, verse_num}, ...]

2. FlexibleTaggingGeminiClient.analyze_figurative_language_flexible()
   ├── _determine_text_context() → context type
   ├── _create_flexible_tagging_prompt() → prompt with hierarchical tags
   └── UnifiedLLMClient.analyze_with_custom_prompt()
       ├── Try GPT-5.1 → success? return
       ├── Try Claude Opus 4.5 → success? return
       └── Try Gemini 3.0 Pro → return (or error)

3. Parse response
   └── Extract: instances[], deliberation, confidence scores
```

### Validation Phase

```
4. MetaphorValidator.validate_chapter_instances(instances)
   ├── Build validation prompt with all instances
   ├── Call GPT-5.1 with reasoning_effort="medium"
   └── Parse validation results
       ├── VALID → final_{type} = 'yes'
       ├── INVALID → final_{type} = 'no'
       └── RECLASSIFIED → final_{new_type} = 'yes'
```

### Storage Phase

```
5. DatabaseManager.insert_verse(verse_data)
   └── Returns: verse_id

6. DatabaseManager.insert_figurative_language(verse_id, instance_data)
   └── Returns: figurative_language_id

7. DatabaseManager.update_validation_data(figurative_language_id, validation_data)
   └── Updates: final_* fields, validation_decision_*, validation_reason_*
```

---

## Module Reference

### File Structure

```
private/
├── interactive_parallel_processor.py    # Main entry point
├── flexible_tagging_gemini_client.py    # Hierarchical tagging client
├── tag_taxonomy_rules.json              # Flexible tagging rules
├── claude_sonnet_client.py              # Claude Sonnet 4 fallback
└── src/hebrew_figurative_db/
    ├── ai_analysis/
    │   ├── unified_llm_client.py        # Multi-model engine
    │   ├── gemini_api_multi_model.py    # Legacy wrapper
    │   └── metaphor_validator.py        # Validation system
    ├── text_extraction/
    │   ├── sefaria_client.py            # Sefaria API client
    │   ├── hebrew_utils.py              # Hebrew text processing
    │   └── hebrew_divine_names_modifier.py  # Divine names handling
    └── database/
        └── db_manager.py                # SQLite database manager
```

### Import Graph

```
interactive_parallel_processor.py
├── SefariaClient
├── DatabaseManager
├── HebrewTextProcessor
├── HebrewDivineNamesModifier
├── MetaphorValidator
├── FlexibleTaggingGeminiClient
│   ├── MultiModelGeminiClient (wrapper)
│   │   └── UnifiedLLMClient
│   │       ├── OpenAI (GPT-5.1)
│   │       ├── Anthropic (Claude Opus 4.5)
│   │       └── google.generativeai (Gemini 3.0)
│   └── ClaudeSonnetClient (optional tertiary fallback)
└── OpenAI (for batched processing)
```

---

## Database Schema

### Tables

```sql
-- Verses table
verses (
    id, reference, book, chapter, verse,
    hebrew_text, hebrew_text_stripped, hebrew_text_non_sacred,
    english_text, english_text_non_sacred,
    word_count, llm_restriction_error,
    figurative_detection_deliberation, figurative_detection_deliberation_non_sacred,
    instances_detected, instances_recovered, instances_lost_to_truncation,
    truncation_occurred, both_models_truncated,
    model_used, processed_at
)

-- Figurative language instances
figurative_language (
    id, verse_id,
    -- Initial detections
    figurative_language, simile, metaphor, personification,
    idiom, hyperbole, metonymy, other,
    -- Final validated
    final_figurative_language, final_simile, final_metaphor, final_personification,
    final_idiom, final_hyperbole, final_metonymy, final_other,
    -- Hierarchical tags (JSON arrays)
    target, vehicle, ground, posture,
    -- Instance details
    confidence, figurative_text, figurative_text_in_hebrew,
    figurative_text_in_hebrew_stripped, figurative_text_in_hebrew_non_sacred,
    explanation, speaker, purpose, tagging_analysis_deliberation,
    -- Validation audit trail
    validation_decision_*, validation_reason_*,
    validation_response, validation_error,
    model_used, processed_at
)
```

For complete schema details, see `docs/DATABASE_SCHEMA.md`.

---

## Known Issues and Risks

### Critical Issues

#### 1. Validation Data Loss Risk - RESOLVED
**Location:** `interactive_parallel_processor.py`

**Previous Problem:** The batched validation could fail silently, leaving instances without validation data.

**Resolution (December 2024):**
- Added `process_validation_result()` - shared function for consistent validation processing
- Added `recover_missing_validations()` - automatic recovery of missing validation data
- Automatic post-batch recovery runs at end of processing session
- Post-recovery verification confirms all issues are resolved

**Current Status:** Validation recovery is now **automatic**. No manual intervention required.

---

#### 2. JSON Parsing Fragility (HIGH)
**Location:** `interactive_parallel_processor.py:~930-1050`

**Problem:** The JSON repair logic is complex and may produce incorrect results:
- Truncated responses may lose later verses entirely
- Bracket counting can fail on nested structures
- Error recovery adds closing braces which may break semantics

**Symptoms:**
- "Successfully repaired JSON" messages with fewer verses than expected
- Chapter processing returns 0 verses despite API success

---

#### 3. Streaming Corruption Handling (MEDIUM)
**Location:** `interactive_parallel_processor.py:~760-830`

**Problem:** Hebrew text corruption during streaming is detected but verses are skipped:
- Corrupted chunks are silently dropped
- `skipped_verses` set may not accurately track affected verses
- No automatic retry for corrupted verses

---

### Code Quality Issues - RESOLVED

#### 4. Duplicate Code in Validation Processing - RESOLVED
**Location:** `interactive_parallel_processor.py`

**Previous Problem:** Validation result processing was duplicated in two places.

**Resolution (December 2024):**
- Extracted to shared `process_validation_result()` function (lines 385-450)
- Both initial validation and recovery now use the same function
- Removed ~130 lines of duplicate code

---

#### 5. Error Handling Inconsistency
**Location:** Various

**Problem:** Different error handling strategies used:
- Some errors return empty lists
- Some errors return structured error dicts
- Some errors raise exceptions

---

#### 6. Hardcoded Model Names
**Location:** Multiple files

**Problem:** Model names like "gpt-5.1", "claude-opus-4-5" are hardcoded in multiple places:
- `interactive_parallel_processor.py:596-597`
- `metaphor_validator.py:57`
- `unified_llm_client.py:various`

**Recommendation:** Centralize model configuration.

---

### Performance Issues

#### 7. Memory Usage in Large Chapters
**Location:** `process_chapter_batched()`

**Problem:** Entire chapter response is held in memory during streaming:
- `response_text` can grow very large
- No streaming to database
- Full chapter context in prompt

---

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | GPT-5.1 API key (primary model) |
| `ANTHROPIC_API_KEY` | No | Claude Opus 4.5 key (fallback) |
| `GEMINI_API_KEY` | No | Gemini 3.0 Pro key (fallback) |

### Configurable Parameters

| Parameter | Default | Location | Description |
|-----------|---------|----------|-------------|
| `max_workers` | 3 | CLI input | Parallel chapters (1-6) - v2.2.0 changed from per-verse to per-chapter parallelization |
| `enable_debug` | False | CLI input | Verbose logging |
| `reasoning_effort` | "medium" | metaphor_validator.py:58 | GPT-5.1 reasoning level |
| `max_completion_tokens` | 65536 | interactive_parallel_processor.py | Batched mode token limit (100000 for prophetic books) |

### Output Files

| File | Description |
|------|-------------|
| `{book}_c{chapter}_*.db` | SQLite database |
| `{book}_c{chapter}_*_log.txt` | Processing log |
| `{book}_c{chapter}_*_results.json` | Summary statistics |
| `debug/debug_response_*.json` | Raw API responses |

---

## Recovery Scripts

### Automatic Validation Recovery (Built-in)

As of December 2024, validation recovery is **automatic**. The pipeline:
1. Detects validation issues after processing each batch
2. Automatically runs `recover_missing_validations()` for affected chapters
3. Re-verifies coverage after recovery
4. Reports any remaining issues

No manual scripts required for normal operation.

### Manual Recovery (Legacy)

If needed, manual recovery scripts are still available:

```bash
# Manual validation recovery
python scripts/recover_missing_validation.py --database path/to/database.db

# Validation health check
python scripts/validation_health_check.py --database path/to/database.db
```

---

## Appendix: API Pricing (December 2024)

| Model | Input (per 1M tokens) | Output (per 1M tokens) |
|-------|----------------------|------------------------|
| GPT-5.1 | $1.25 | $10.00 |
| Claude Opus 4.5 | $15.00 | $75.00 |
| Gemini 3.0 Pro | $2.00 | $8.00 |

**Note:** Batched processing achieves ~95% cost savings vs. per-verse for Proverbs/Isaiah/Jeremiah.

---

## Version 2.1.0 Features (December 2024)

### New Capabilities

#### 1. Jeremiah Support
- Added Jeremiah (52 chapters, ~1,364 verses) to supported books
- Uses batched GPT-5.1 processing like Isaiah

#### 2. Enhanced Failure Tracking
- **Run Context**: Each processing run gets a unique ID (e.g., `20241223_143052_a1b2c3d4`)
- **Failure Manifest**: `*_failures.json` with structured error taxonomy
- **Processing Manifest**: `*_manifest.json` with full run metadata
- **Verse-level tracking**: Failed verses tracked individually, not just chapters

#### 3. Improved Robustness
- **Pydantic schema validation**: LLM responses validated against typed schemas
- **Increased token limits**: Prophetic books use 100,000 tokens (vs 65,536 default)
- **Sefaria caching**: `.sefaria_cache/` directory caches API responses for faster reruns

#### 4. Smart Batching
```python
# Get recommended batches for a book
from interactive_parallel_processor import get_recommended_batches, print_batch_recommendations

# For Jeremiah (52 chapters):
batches = get_recommended_batches("Jeremiah")
# Returns: [(1,10), (11,20), (21,30), (31,40), (41,52)]

print_batch_recommendations("Jeremiah")
# Prints detailed batching strategy with cost/time estimates
```

#### 5. Database Tracking
New `processing_runs` table tracks all runs:
```sql
SELECT run_id, book, verses_processed, instances_detected,
       estimated_cost, pipeline_version
FROM processing_runs
ORDER BY started_at DESC;
```

### Output Files (v2.1.0)

| File | Description |
|------|-------------|
| `{book}_c{chapter}_*.db` | SQLite database |
| `{book}_c{chapter}_*_log.txt` | Processing log with run ID |
| `{book}_c{chapter}_*_results.json` | Summary statistics |
| `{book}_c{chapter}_*_failures.json` | **NEW**: Structured failure manifest |
| `{book}_c{chapter}_*_manifest.json` | **NEW**: Processing metadata |
| `.sefaria_cache/*.json` | **NEW**: Cached Sefaria responses |

### Configuration Constants

```python
PIPELINE_VERSION = "2.1.0"
SUPPORTED_BOOKS = {"Genesis": 50, ..., "Jeremiah": 52}
BATCHED_PROCESSING_BOOKS = ["Proverbs", "Isaiah", "Jeremiah"]
MAX_COMPLETION_TOKENS_DEFAULT = 65536
MAX_COMPLETION_TOKENS_PROPHETIC = 100000
```

---

## Version 2.2.0 Features (December 2024)

### Major Changes

#### 1. All Books Use Batched Processing
- **Breaking Change**: All supported books now use chapter-level batched processing
- Previously only Proverbs, Isaiah, and Jeremiah used batched mode
- This provides ~95% cost savings for ALL books

#### 2. Chapter-Level Parallelization
- Multiple chapters can now be processed simultaneously
- Default: 3 parallel chapters (configurable 1-6)
- Each chapter still uses a single GPT-5.1 API call (preserving cost advantages)
- Thread-safe database operations via locking

#### 3. New Functions

```python
# Process multiple chapters in parallel
process_chapters_parallel(chapter_tasks, sefaria_cache, sefaria_client,
                          validator, divine_names_modifier, db_manager, logger,
                          max_workers, run_context)

# Process a single chapter (used by parallel executor)
process_single_chapter_task(task_data, sefaria_cache, validator,
                            divine_names_modifier, db_manager, logger, run_context)
```

### Configuration Constants (v2.2.0)

```python
PIPELINE_VERSION = "2.2.0"
SUPPORTED_BOOKS = {"Genesis": 50, ..., "Jeremiah": 52}
BATCHED_PROCESSING_BOOKS = list(SUPPORTED_BOOKS.keys())  # ALL books
MAX_COMPLETION_TOKENS_DEFAULT = 65536
MAX_COMPLETION_TOKENS_PROPHETIC = 100000  # For Isaiah, Jeremiah
```

---

## Version 2.2.1 Features (December 2025)

### Major Changes

#### 1. WriteQueue Architecture - Eliminates Database Lock Contention

**Problem Solved:** Running parallel workers caused 70%+ chapter failures due to `database_lock_timeout`. Multiple workers finishing API calls simultaneously all competed for database locks.

**Solution:** WriteQueue architecture with dedicated writer thread.

```python
class ChapterWriteQueue:
    """Thread-safe queue for chapter write operations with dedicated writer thread."""

    def __init__(self, db_path, logger, validator=None, divine_names_modifier=None)
    def start_writer(self)
    def stop_writer(self, timeout=300.0)
    def submit_chapter(self, book, chapter, verses_data, instances_data, metadata) -> chapter_key
    def wait_for_result(self, chapter_key, timeout=300.0) -> result_dict
```

**Key Benefits:**
- **Zero database lock contention** - Only writer thread touches database
- **Parallel API calls preserved** - Workers make LLM calls concurrently (3x speedup)
- **Atomic chapter commits** - Writer inserts all verses+instances, then commits
- **No single-verse failure risk** - Entire chapter succeeds or fails as unit

#### 2. Modified Functions

```python
# process_chapter_batched() now supports return_data_only mode
def process_chapter_batched(..., return_data_only: bool = False):
    # When True: returns prepared data instead of writing to DB
    # Used by WriteQueue architecture

# process_single_chapter_task() now accepts write_queue parameter
def process_single_chapter_task(..., write_queue: ChapterWriteQueue = None):
    # When write_queue provided: submits to queue instead of direct writes

# process_chapters_parallel() uses WriteQueue by default
def process_chapters_parallel(..., use_write_queue: bool = True):
    # Set use_write_queue=False for legacy behavior
```

#### 3. Backward Compatibility

Legacy mode (direct database writes with locking) is still available:

```python
results = process_chapters_parallel(..., use_write_queue=False)
```

### Configuration Constants (v2.2.1)

```python
PIPELINE_VERSION = "2.2.1"
# WriteQueue enabled by default in process_chapters_parallel()
```

### Performance Comparison

| Configuration | Failure Rate | Notes |
|---------------|--------------|-------|
| v2.2.0 (lock-based) | ~70% with 3 workers | Database lock timeout |
| v2.2.1 (WriteQueue) | ~0% with 3 workers | Zero lock contention |

---

## Recent Updates (December 2025)

### Website Deployment & Database Expansion

**Production Website:** https://tzafun.onrender.com

#### Database Growth
- **Previous:** 6 books (Torah + Psalms) - 8,373 verses
- **Current:** 13 books - 13,548 verses (+62% growth)
- **New Books Added:**
  - Proverbs (Wisdom Literature)
  - Isaiah, Jeremiah, Ezekiel (Major Prophets)
  - Hosea, Joel, Amos (Minor Prophets/Twelve)

#### Hosting Architecture
- **Database Storage:** Google Drive (105MB)
  - Database file: `Biblical_fig_language.db` (consolidated from previous separate book DBs)
  - Previous database: `Pentateuch_Psalms_fig_language.db` (6 books) → replaced
  - Eliminates Git LFS costs
  - Auto-downloaded during Render.com deployment via `gdown` library
  - Cached in container (survives cold starts)
- **Web Hosting:** Render.com Free Tier
  - Oregon region
  - Gunicorn WSGI server (1 worker, 2 threads)
  - Python 3.11

#### Website Highlighting Improvements (December 31, 2025)
Recent fixes to figurative text highlighting system:

1. **Ellipsis Support** - Handles partial quotes with `...` or `…`
   - Example: `"The wolf ... with a child"` now highlights full span
   - Works for both English and Hebrew

2. **Hebrew Normalization** - Proper diacritic handling for ellipses
   - Removes vowel points and cantillation marks before matching
   - Handles maqaf (־) normalization

3. **Punctuation Flexibility** - Matches despite punctuation differences
   - Handles period/comma/semicolon variations
   - Example: `"them,"` matches `"them."`

4. **Smart Quote Normalization** - Unicode quote handling
   - Normalizes curly quotes (U+2018, U+2019, U+201C, U+201D)
   - Fixes verses with trailing smart quotes
   - Example: Genesis 49:27 with `spoil."` vs `spoil."`

These improvements ensure robust highlighting across all 13 biblical books with various text formatting edge cases.

---

*Document generated from codebase analysis. For schema details, see `DATABASE_SCHEMA.md`. For methodology, see `METHODOLOGY.md`. For session notes, see `session_notes.md`.*
