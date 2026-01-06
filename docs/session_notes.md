# Session Notes: Parallel Processing Fixes

**Date:** 2024-12-24 evening
**Session Focus:** Fixing SQLite threading and performance issues in chapter-level parallelization
**Commit:** `2664160`

---

## Problem Statement

When running Ezekiel chapters 1-10 with v2.2.0's chapter-level parallelization (`max_workers=3`), all chapters failed with database-related errors.

### Initial Error
```
SQLite objects created in a thread can only be used in that same thread.
The object was created in thread id 85284 and this is thread id 44952.
```

---

## Investigation Timeline

| Phase | Chapters | Result | Root Cause |
|-------|----------|--------|------------|
| 1 | Ezekiel 1-10 | 0/10 success | SQLite threading violation |
| 2 | Ezekiel 1-9 (after threading fix) | 6/9 success | Database lock timeout |
| 3 | Ezekiel 1,4,8,9 (after WAL mode) | 2/4 success | Database lock timeout |
| 4 | Ezekiel 1,4 (after transaction lock) | 1/2 success | Streaming corruption (intermittent) |
| 5 | Ezekiel 11-20 | 10/10 success | Performance issue (61 min, serialized) |
| 6 | Ezekiel 1 (retry) | 1/1 success | Confirmed streaming corruption is intermittent |

---

## Issues Identified and Fixed

### Issue 1: SQLite Threading Violation ✅

**Symptom:** All chapters failed with "SQLite objects created in a thread can only be used in that same thread"

**Root Cause:**
- `DatabaseManager` was created in main thread
- Worker threads tried to use the same connection
- SQLite prohibits sharing connections across threads

**Fix:** Thread-local `DatabaseManager` instances
```python
# In process_single_chapter_task() - each worker creates its own connection
db_manager = DatabaseManager(db_path)
db_manager.connect()
db_manager.setup_database(drop_existing=False)
try:
    # ... processing ...
finally:
    db_manager.close()
```

**File:** `private/interactive_parallel_processor.py:1086-1166`

---

### Issue 2: SQLite Timeout Too Short ✅

**Symptom:** "database is locked" errors even after threading fix

**Root Cause:**
- SQLite default timeout is 5 seconds
- Multiple threads writing simultaneously caused timeouts

**Fix:** Increased timeout to 30 seconds
```python
def connect(self, timeout: float = 30.0):
    self.conn = sqlite3.connect(self.db_path, timeout=timeout)
```

**File:** `private/src/hebrew_figurative_db/database/db_manager.py:32-38`

---

### Issue 3: WAL Mode Needed ✅

**Symptom:** Continued "database is locked" errors

**Root Cause:**
- Default rollback journal mode blocks aggressively
- Multiple writers couldn't access database concurrently

**Fix:** Enabled WAL (Write-Ahead Logging) mode
```python
self.conn.execute('PRAGMA journal_mode=WAL')
```

**File:** `private/src/hebrew_figurative_db/database/db_manager.py:40`

**What is WAL mode:**
- Creates `.db-wal` and `.db-shm` files
- Allows better concurrent access (multiple readers + one writer)
- Files are cleaned up automatically by SQLite

---

### Issue 4: Performance - Lock Too Broad ✅

**Symptom:** Chapters 11-20 took 61 minutes (should be ~20-25)

**Root Cause:**
- `_db_lock` wrapped entire operation (API call + inserts + commit)
- Workers were effectively serialized - only one processed at a time

**Evidence from log:**
```
Worker 2: Completed Ch 12 at 21:14:36 (536.6s)
Worker 1: Completed Ch 11 at 21:20:20 (880.5s) - waited for Worker 2
Worker 3: Completed Ch 13 at 21:26:05 (1225.2s) - waited for Workers 1 & 2
```

**Fix:** Narrowed lock to ONLY protect commits
```python
# BEFORE: Lock wrapped everything
with _db_lock:
    v, i, ... = process_chapter_batched(...)  # API call + inserts
    db_manager.commit()

# AFTER: Lock only protects commit
v, i, ... = process_chapter_batched(...)  # Runs in parallel
with _db_lock:
    db_manager.commit()  # Only this is serialized
```

**File:** `private/interactive_parallel_processor.py:1119-1130`

**Expected Improvement:** ~3x speedup with 3 workers

---

### Issue 5: Streaming Corruption (Intermittent) ⚠️

**Symptom:** JSON parsing failures with "Unterminated string" or "Expecting ',' delimiter"

**Example:**
```
JSON parsing failed: Expecting ',' delimiter: line 732 column 16
JSON repair failed: Unterminated string starting at: line 3 column 5
```

**Root Cause:** LLM streaming response occasionally gets corrupted during transmission

**Workaround:** Retry the chapter - usually succeeds on retry

**Status:** Not fixed - considered acceptable as intermittent issue

---

## Files Modified

| File | Changes |
|------|---------|
| `private/interactive_parallel_processor.py` | Thread-local DatabaseManager, narrow lock scope |
| `private/src/hebrew_figurative_db/database/db_manager.py` | 30s timeout, WAL mode |
| `docs/PARALLEL_PROCESSING_ISSUES.md` | Detailed technical documentation (created) |

---

## Performance Comparison

| Configuration | 10 Chapters Time | Notes |
|---------------|------------------|-------|
| Before any fixes | Failed | Threading errors |
| After threading fix (broad lock) | ~61 min | Workers serialized |
| After all fixes (narrow lock) | ~20-25 min (expected) | True parallelization |

---

## Architecture Summary

### Chapter-Level Parallelization (v2.2.0)
```
┌─────────────────────────────────────────────────────────┐
│                  ThreadPoolExecutor                      │
│                     max_workers=3                        │
└─────────────────────────────────────────────────────────┘
                           │
            ┌──────────────┼──────────────┐
            ▼              ▼              ▼
         Worker 1       Worker 2       Worker 3
            │              │              │
            │              │              │
    ┌───────▼───────┐ ┌──▼────────┐ ┌──▼────────┐
    │ API Call      │ │ API Call   │ │ API Call   │
    │ (4-6 min)     │ │ (4-6 min)  │ │ (4-6 min)  │
    │ [PARALLEL]    │ │ [PARALLEL] │ │ [PARALLEL] │
    └───────┬───────┘ └──┬────────┘ └──┬────────┘
            │              │              │
            ▼              ▼              ▼
    ┌───────▼───────┐ ┌──▼────────┐ ┌──▼────────┐
    │ DB Inserts    │ │ DB Inserts │ │ DB Inserts │
    │ (with lock)   │ │ (with lock)│ │ (with lock)│
    └───────┬───────┘ └──┬────────┘ └──┬────────┘
            │              │              │
            ▼              ▼              ▼
         ┌──▼──────────────────────────────▼──┐
         │      Commit (serialized lock)      │
         │  ┌─────┐  ┌─────┐  ┌─────┐        │
         │  │ W1  │→│ W2  │→│ W3  │        │
         │  └─────┘  └─────┘  └─────┘        │
         └────────────────────────────────────┘
```

**Key Points:**
- Each worker has its own `DatabaseManager` instance (separate SQLite connection)
- API calls happen in parallel (3x speedup)
- Database writes are serialized (safe)
- WAL mode enables better concurrent access

---

## Testing Checklist

- [x] Chapters 1-10: Initial run failed (threading)
- [x] Chapters 1-9: 6/9 success after threading fix
- [x] Chapters 1,4,8,9: 2/4 success after WAL mode
- [x] Chapters 1,4: 1/2 success after transaction lock
- [x] Chapter 1: Success on retry (streaming corruption is intermittent)
- [x] Chapters 11-20: 10/10 success but slow (61 min, broad lock)
- [ ] Chapters 21-30: Test with narrow lock (expected ~20-25 min)

---

## WAL Files (.db-wal, .db-shm)

**What they are:**
- `.db-wal`: Write-Ahead Log - contains changes not yet checkpointed
- `.db-shm`: Shared memory index for WAL file access

**Why they exist:**
- Created when WAL mode is enabled
- Persist until checkpoint occurs
- Normal and expected - don't delete manually

**Cleanup options:**
- Let SQLite handle automatically (default)
- Manual checkpoint: `PRAGMA wal_checkpoint(TRUNCATE)`

---

## Commands for Future Reference

```bash
# Run chapters in parallel
python private/interactive_parallel_processor.py Ezekiel 1-10

# Run specific chapters
python private/interactive_parallel_processor.py Ezekiel 5

# Check for failures
cat private/*failures.json | jq '.failed_items[]'

# Check database contents
sqlite3 database/your_file.db "SELECT book, chapter, COUNT(*) as instances FROM figurative_language GROUP BY book, chapter;"
```

---

## Next Steps

1. Verify performance improvement with chapters 21-30
2. Consider adding automatic retry logic for streaming corruption
3. Monitor WAL file size and add periodic checkpoint if needed
4. Consider adding metrics/logging to track parallel efficiency

---

## Session 2: 2024-12-25

**Focus:** Investigating Ezekiel 21-30 failures, improving error classification

### Problem

Ran Ezekiel 21-30 with 3 parallel workers. 7/10 chapters succeeded, 3 failed:
- Ezekiel 23: Failed
- Ezekiel 24: Failed
- Ezekiel 28: Failed

Failure manifest incorrectly labeled all as `json_parsing_failure`.

### Investigation

Examined debug response files - all contained **valid JSON** with complete verse data. The LLM responses were correct.

Actual error from logs:
```
ERROR - Error during batched processing of Ezekiel 23: database is locked
ERROR - Error during batched processing of Ezekiel 24: database is locked
ERROR - Error during batched processing of Ezekiel 28: database is locked
```

**Root cause:** Database lock timeout (30s) exceeded during concurrent inserts, NOT JSON parsing failure.

### Fixes Applied

#### 1. Increased SQLite timeout: 30s → 60s ✅
```python
def connect(self, timeout: float = 60.0):
```
**File:** `private/src/hebrew_figurative_db/database/db_manager.py:32`

#### 2. Improved error classification ✅
Now correctly distinguishes:
- `database_lock_timeout` - for "database is locked" errors
- `database_error` - for other SQLite errors
- `json_parsing_failure` - for actual JSON parsing failures

**File:** `private/interactive_parallel_processor.py:1138-1163`

#### 3. Return error message from process_chapter_batched() ✅
Function now returns 6-tuple including error message for proper classification.

**File:** `private/interactive_parallel_processor.py:2237-2244`

### Considered but Rejected

**Per-verse commits** - Would reduce lock contention but introduces risk of partial data (verses 1-14 committed, verse 15+ lost). Partial data is harder to detect than complete chapter failure. Rejected in favor of atomic chapter commits.

### Next Steps

1. Re-run Ezekiel 23, 24, 28 to verify 60s timeout is sufficient
2. If still failing, consider reducing `max_workers` from 3 to 2
3. Complete Ezekiel 31-48

---

## Session 3: 2024-12-25

**Focus:** Centralize pipeline output to dedicated output directory

### Goal

Move all pipeline output files from `private/` to a dedicated `output/` directory at project root, and gitignore the outputs.

### Changes Made

#### 1. Added OUTPUT_DIR constant ✅
```python
# Located at project root level: Bible/output/
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
```
**File:** `private/interactive_parallel_processor.py:94-96`

#### 2. Updated file paths to use OUTPUT_DIR ✅

All output files now saved to `output/`:
- Database files (`.db`)
- Log files (`_log.txt`)
- Results JSON (`_results.json`)
- Failure manifests (`_failures.json`)
- Processing manifests (`_manifest.json`)
- Debug files (`output/debug/debug_response_*.json`)

**Files modified:**
- `private/interactive_parallel_processor.py:2634-2644` - Command-line mode paths
- `private/interactive_parallel_processor.py:2700-2713` - Interactive mode paths
- `private/interactive_parallel_processor.py:791-798` - Debug file paths
- `private/interactive_parallel_processor.py:2768` - RunContext output_dir

#### 3. Updated .gitignore ✅
```
# Output directory (pipeline outputs)
output/
```
**File:** `.gitignore:58-59`

### Directory Structure

```
Bible/
├── output/                    # NEW - All pipeline outputs go here
│   ├── *.db                   # Database files
│   ├── *_log.txt              # Processing logs
│   ├── *_results.json         # Summary statistics
│   ├── *_failures.json        # Failure manifests
│   ├── *_manifest.json        # Processing manifests
│   └── debug/                 # Debug response files
│       └── debug_response_*.json
├── private/                   # Pipeline source code (no outputs)
├── database/                  # Production databases (tracked)
└── docs/                      # Documentation
```

### Benefits

1. **Clean separation** - Source code in `private/`, outputs in `output/`
2. **Git-friendly** - All outputs ignored, no accidental commits of large files
3. **Easy cleanup** - Delete `output/` to clear all pipeline outputs
4. **Consistent paths** - All outputs in one predictable location

---

## Session 4: 2024-12-25 (Later)

**Focus:** Eliminate database lock contention with WriteQueue architecture

### Problem

Running Hosea 1-14 with 3 parallel workers: 10/14 chapters (71%) failed with `database_lock_timeout`.

Pattern analysis showed that in each "wave" of 3 workers finishing API calls around the same time, ~2 failed and ~1 succeeded due to lock contention.

Root cause: With the current architecture, each worker acquires `_db_lock` for every single insert operation:
- Each `insert_verse()` call acquires lock
- Each `insert_figurative_language()` call acquires lock
- Final `commit()` acquires lock

For a chapter with 15 verses and 20 instances = 35+ lock acquisitions. With 3 workers finishing simultaneously, 100+ lock contentions in a short window.

### Solution: WriteQueue Architecture ✅

**Pipeline Version:** 2.2.1

Replaced direct database writes with a queue-based system:
- Workers put chapter results in a thread-safe queue
- A dedicated writer thread handles ALL database operations
- Zero lock contention (only one thread ever writes)

#### Architecture Diagram
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

#### Key Benefits
1. **Parallel API calls preserved** - Workers make LLM calls concurrently (3x speedup)
2. **Zero database contention** - Only writer thread touches database
3. **Atomic chapter commits** - Writer inserts all verses+instances, then commits
4. **No single-verse risk** - Entire chapter succeeds or fails as unit

### Files Modified

| File | Changes |
|------|---------|
| `private/interactive_parallel_processor.py` | Added ChapterWriteQueue class, modified process_chapter_batched(), process_single_chapter_task(), process_chapters_parallel() |

### New Classes

#### ChapterWriteQueue
```python
class ChapterWriteQueue:
    """Thread-safe queue for chapter write operations with dedicated writer thread."""

    def __init__(self, db_path, logger, validator=None, divine_names_modifier=None)
    def start_writer(self)
    def stop_writer(self, timeout=300.0)
    def submit_chapter(self, book, chapter, verses_data, instances_data, metadata) -> chapter_key
    def wait_for_result(self, chapter_key, timeout=300.0) -> result_dict
```

### Usage

WriteQueue is enabled by default. To use legacy mode (backward compatibility):
```python
results = process_chapters_parallel(..., use_write_queue=False)
```

### Bug Fix: `total_cost` Variable Reference Error

Initial test (Joel 1-3) failed with:
```
cannot access local variable 'total_cost' where it is not associated with a value
```

**Root Cause:** In the `return_data_only` code path, the function returned before `total_cost` was calculated (it's computed later from `token_metadata` + validation cost).

**Fix:** Use `detection_cost = token_metadata.get('cost', 0)` in the early return path.

```python
# Before (broken)
return collected_verses_data, collected_instances_data, processing_time, len(verses_data), total_cost, None

# After (fixed)
detection_cost = token_metadata.get('cost', 0)
return collected_verses_data, collected_instances_data, processing_time, len(verses_data), detection_cost, None
```

**File:** `private/interactive_parallel_processor.py:2511-2514`

### Expected Results

With WriteQueue:
- 0 `database_lock_timeout` failures (from 71% failure rate)
- Same total processing time (API calls still parallel)
- Same data integrity (atomic chapter commits maintained)

### Commit

```
55f3182 feat: Add WriteQueue architecture to eliminate database lock contention (v2.2.1)
```

---

## Related Documentation

- [PARALLEL_PROCESSING_ISSUES.md](PARALLEL_PROCESSING_ISSUES.md) - Detailed technical analysis
- [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) - Overall pipeline documentation

---

## Session 5: 2026-01-05

**Focus:** UI/UX Polish for Web Interface

### Goal
Address visual issues in the Tzafun web interface (`web/biblical_figurative_interface.html`), specifically a border layout issue, and improve overall polish.

### Changes Made

#### 1. Header Underline Fix ✅
**Problem:** The underline for sidebar headers (like "Text Selection") extended across the full width, looking "uncut".
**Fix:** Applied `width: fit-content` to `.sidebar h3` so the border matches the text width.

#### 2. Sidebar Control Polish ✅
**Problem:** "All | None" links and Reset (↻) buttons were cramped and used inline styles.
**Fix:**
- Created `.control-header`, `.control-group`, `.control-link`, and `.refresh-btn` CSS classes.
- Refactored inline styles to use these classes.
- Added proper spacing and alignment.

#### 3. Header Visibility ✅
**Problem:** "about" and "print" links were small and hard to see.
**Fix:** Increased font weight (600) and size for `.header-attribution a`.

#### 4. Book Reordering ✅
**Problem:** Books were listed in English bible order (or arbitrary).
**Fix:** Reordered `#book-select` options to follow the Tanakh order: Torah, Nevi'im (Prophets), Ketuvim (Writings).

#### 5. Animation Consistency ✅
**Problem:** "Search for Tag" reset button lacked the hover animation present on other buttons.
**Fix:** Standardized all reset buttons to use the `.refresh-btn` class, ensuring consistent `transform: rotate(30deg)` on hover.

### Files Modified
- `web/biblical_figurative_interface.html` - CSS and HTML refactoring.

---

## Session 6: 2026-01-05 (Deployment Optimization)

**Focus:** Mitigating Render Free Tier Cold Starts

### Problem
The deployed application on Render free tier (https://tzafun.onrender.com/) suffers from slow initial load times (30-60+ seconds) due to "spin down" after 15 minutes of inactivity.

### Solution: Uptime Monitor Workaround ✅
Instead of migrating to a new platform, implemented a "keep-alive" strategy using a free uptime monitor.

**Strategy:**
- **Tool:** UptimeRobot (free tier)
- **Configuration:** Ping `https://tzafun.onrender.com/` every 5 minutes
- **Effect:** Prevents the service from spinning down by simulating activity

### Benefits
- **Zero Cost:** Remains on Render free tier
- **Immediate Performance:** Eliminates cold start latency (load time 30s -> ~2s)
- **No Code Changes:** No refactoring required (e.g. for serverless)

---

## Session 7: 2026-01-06

**Focus:** Debugging Text Highlighting and Search Rendering

### Problem
Users reported issues with the new `TextHighlighter` class:
1.  **Missing English Highlights:** Specific verses (Isaiah 40:14, 41:11) containing figurative language were not highlighting the English text, despite correct data.
2.  **Inconsistent Search Highlights:** Search terms were sometimes highlighted in pink (background) instead of just underlined, or mixed with figurative highlights.
3.  **Visual Clashes:** Search highlights (pink underline) and figurative highlights (yellow background) needed to coexist without overriding each other.

### Changes Made

#### 1. TextHighlighter Refactor ✅
**Goal:** robust, language-aware normalization for matching text against annotations.
- **Strict Normalization:** Updated English normalization to strip a wider range of punctuation, brackets, and quotes (`[God]` -> `god`, `"word"` -> `word`).
- **Whitespace Handling:** Updated logic to collapse multiple spaces and handle newlines/tags correctly.
- **Mapping Fix:** Updated `buildMap` to insert spaces when skipping block-level HTML tags (`<br>`, `<div>`, `<p>`) to prevent words from merging (e.g., "end</div><div>start" -> "end start" instead of "endstart").
- **Annotation Cleaning:** Removed aggressive "bracket cleaning" that was stripping vital text (e.g., `[God]`) from annotations, causing mismatches.

#### 2. Visual CSS Separation ✅
**Goal:** Clear distinction between "Found Search Term" and "Figurative Language".
- **Search Highlight:** Forced `background-color: transparent !important` and used `border-bottom: 3px solid #ffb3d9` (pink underline).
- **Figurative Highlight:** Retained yellow background.
- **Combined:** Now a word can have a yellow background (figurative) AND a pink underline (search match) simultaneously.

### Ongoing Challenges ⚠️

Despite these fixes, highlights in Isaiah 40:14 ("Whom did [God] consult") and Isaiah 41:11 ("become as naught") are **still failing** in the latest test.

**Potential Causes:**
1.  **Normalization Mismatch:** There may still be a discrepancy between how the HTML text is normalized vs. how the database annotation is normalized (e.g., smart quotes vs. straight quotes, or specific hidden characters).
2.  **HTML Structure:** The `buildMap` function might still be losing sync with the DOM if the browser renders whitespace differently than our logic assumes (especially around complex verse references or line breaks).
3.  **Data Integrity:** The actual text strings in the JSON data might differ slightly from the JPS text displayed (e.g., "God" vs "[God]"), requiring fuzzier matching.

### Next Steps (UI Refactor)

To continue the work, look at `task.md` under **Visual Overhaul**. The immediate next tasks are:
1.  **Glassmorphism & Theming:**
    -  Refactor CSS variables for better theme management.
    -  Implement the glassmorphism design for the sidebar and header.
2.  **Layout Improvements:**
    -  Switch Verse Container to a CSS Grid layout for better alignment of Hebrew/English.
    -  Add the "Details Drawer" (slide-out panel) to replace the current modal for viewing annotation details.
3.  **Continued Debugging:**
    -  Add verbose logging to `TextHighlighter.findRanges` to dump the exact `normalizedText` and `targetPhrase` to the console. This is the only way to definitively see *why* the match is failing (e.g., Is "God" matching "god"? Is "naught" becoming "naught " with a space?).


## Session 8: Visual Overhaul of Tzafun Interface

**Date:** 2026-01-06

### Summary
This session focused on a comprehensive visual overhaul of the web interface to modernize the design and resolve layout issues. The application was updated with a new CSS variable system, a premium "Glassmorphism" aesthetic, and a robust CSS Grid layout for verses.

### Completed Tasks
1.  **CSS Refactoring:** Established a semantic system of CSS variables for colors, typography, and spacing in :root, ensuring consistent theming across the app.
2.  **GlassmorphismUI:** Implemented a modern frosted-glass effect for the Sidebar and Header, complete with a subtle gradient body background to enhance the depth.
3.  **Grid Layout Implementation:**
    -   Converted .verse-content to display: grid with lign-items: start.
    -   This successfully resolved the whitespace alignment issues noted in verses like Isaiah 40:14.
4.  **Detail Panel Modernization:** Updated the bottom detail panel to match the glass style (though user feedback suggests relocating this).

### Code Changes
-   **web/biblical_figurative_interface.html**: Extensive CSS updates and minor HTML structural changes to support the new grid layout.

### Outstanding Issues / User Feedback
1.  **Metadata Search Visibility:** The 'posture' search field is reportedly missing or hidden. This is likely a CSS flex/overflow issue in the sidebar.
2.  **Detail Panel UI:** The user requested moving the Detail Panel from a bottom sheet to a **Right-Side Drawer** for better UX.

### Next Steps
1.  **Refine UI:**
    -   Fix the metadata search visibility.
    -   Implement the Right-Side Drawer for verse details.
2.  **Highlighting Debugging:**
    -   Investigate and fix the persistent issue where highlights are missing in Isaiah 40:14 and 41:11 (as noted in Session 7).


## Session 9: UI Refinements & Highlighting Robustness

**Date:** 2026-01-06

### Summary
This session addressed critical UI feedbacks and continued the debugging of English text highlighting. The UI was successfully refined by fixing the sidebar layout and transforming the detail panel into a modern right-side drawer. Highlighting robustness was improved by treating bracketed/parenthesized text as wildcards, though some English highlighting issues persist.

### Completed Tasks
1.  **UI Refinements:**
    -   **Metadata Search Visibility:** Fixed the hidden 'Posture' field by converting the container to a 2-column Grid layout.
    -   **Detail Drawer:** Transformed the detail panel from a bottom sheet to a **Right-Side Drawer** (`transform: translateX`) for better use of screen real estate.
    -   **Sidebar Layout:** preventing the bottom search fields from being cut off by adding padding to the sidebar bottom.
2.  **Highlighting Logic (Phase 1):**
    -   **Wildcard Support:** Updated `TextHighlighter.findRanges` to treat text inside brackets `[...]` AND parentheses `(...)` as wildcards. This fixes issues where annotations like "Whom did (God) consult" failed to match "With whom did He consult".
    -   **Smarter Cleaning:** Refined `cleanFigurativeText` to only strip specific glosses (e.g., `lit.`, `Heb.`) rather than removing all parenthetical content blindly.
3.  **Deployment:** committed and pushed syntax fixes and UI changes to `main`.

### Code Changes
-   **web/biblical_figurative_interface.html**: 
    -   CSS updates for `.detail-panel`, `.metadata-search`, and `.sidebar`.
    -   JavaScript updates to `TextHighlighter` class for regex-based wildcard matching.

### Outstanding Issues
1.  **English Highlighting:** While the *logic* for wildcards works (verified via reproduction script), the user reports that English highlighting is **still failing often** in the main app.
    -   *Hypothesis:* The `TextHighlighter` might be failing on other edge cases like punctuation handling, complex sentence structures, or data normalization mismatches not yet covered by the wildcard logic.
    -   *Action:* Next session needs a deep dive into the `TextHighlighter` to make it fundamentally more robust (fuzzy matching?) or debug why the verified logic fails in the full app context.

### Next Steps Prompt
Use the prompt provided in the task notification to start the next session.
