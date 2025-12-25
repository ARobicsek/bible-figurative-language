# Session Notes: Parallel Processing Fixes

**Date:** 2024-12-24
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

## Related Documentation

- [PARALLEL_PROCESSING_ISSUES.md](PARALLEL_PROCESSING_ISSUES.md) - Detailed technical analysis
- [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) - Overall pipeline documentation
