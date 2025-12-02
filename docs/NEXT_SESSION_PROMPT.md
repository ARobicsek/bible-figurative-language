# Next Session Prompt

**Last Updated**: 2025-12-02 (End of Session 18)
**Session**: 19
**Priority**: Fix Verse-Specific Deliberation Extraction

---

## SESSION 18 ACCOMPLISHED: FIXED VALIDATION BATCHING ✅

### Issue 1: HIGH API COSTS - RESOLVED!

**Root Cause**: Validation was making separate API calls for each verse instead of batching all instances together.

**Solution Implemented**:
1. Created new `validate_chapter_instances()` method in `metaphor_validator.py`
2. Modified `interactive_parallel_processor.py` to collect all instances from all verses and make a single validation API call

**Results**:
- **Before**: 1 detection call + 8 validation calls = ~$0.40 for 8 verses
- **After**: 1 detection call + 1 validation call = ~$0.11 for 8 verses
- **Savings**: 73% reduction in API costs!
- Test completed successfully with Proverbs 3:11-18

### Issue 2: VERSE-SPECIFIC DELIBERATION - STILL NEEDS FIXING

**Problem**: The `figurative_detection_deliberation` field still contains chapter-level deliberation for ALL verses, but each verse record should only contain deliberation for that ONE verse.

**Evidence from code**:
- File: `interactive_parallel_processor.py` line 782
- Code: `'figurative_detection_deliberation': chapter_deliberation`
- The same `chapter_deliberation` (5,301 characters) is copied to EVERY verse record

**What happens now**:
- Verse 11 gets deliberation for verses 11-18
- Verse 12 gets deliberation for verses 11-18
- Verse 13 gets deliberation for verses 11-18
- (etc.)

**What should happen**:
- Verse 11 should get ONLY the deliberation about verse 11
- Verse 12 should get ONLY the deliberation about verse 12
- (etc.)

---

## SESSION 19 TASKS - STEP BY STEP

### TASK: FIX VERSE-SPECIFIC DELIBERATION (HIGH PRIORITY)

**Goal**: Each verse should get ONLY the deliberation text specific to that verse.

**Current problematic code** (`interactive_parallel_processor.py` line 782):
```python
'figurative_detection_deliberation': chapter_deliberation,  # Same for ALL verses
```

**Solution approach**:

1. **Add a function to parse verse-specific deliberation**:
   ```python
   def extract_verse_deliberation(chapter_deliberation: str, verse_num: int) -> str:
       """
       Extract only the deliberation text for a specific verse.

       The chapter deliberation contains sections like:
       "Verse 11: [deliberation text]"
       "Verse 12: [deliberation text]"

       This function extracts just the section for the given verse number.
       """
       # Use regex to find "Verse X:" sections
       # Return only the section for the given verse_num
       pass
   ```

2. **Call this function when building verse_data** (around line 782):
   ```python
   verse_specific_deliberation = extract_verse_deliberation(chapter_deliberation, verse_num)

   verse_data = {
       ...
       'figurative_detection_deliberation': verse_specific_deliberation,  # Verse-specific now!
       ...
   }
   ```

**Example of what the chapter deliberation looks like**:
```
Verse 11: Considered "discipline" (מוּסַר) as potential metaphor. The term...
Verse 12: Examined the simile "as a father" (כְּאָב). This is clearly...
Verse 13: Analyzed "finds wisdom" (מָצָא חָכְמָה). This could be...
```

**Expected result**:
- Verse 11 record gets: "Considered discipline (מוּסַר) as potential metaphor..."
- Verse 12 record gets: "Examined the simile as a father (כְּאָב)..."
- Each verse has its OWN deliberation, not the full chapter.

---

### VERIFY AND TEST

**Testing script**: `test_proverbs_3_11-18_batched_validated.py`

**Verification checklist**:
- [ ] Run test with Proverbs 3:11-18 (8 verses)
- [ ] Check API cost is ~$0.10 (should stay the same)
- [ ] Check database `figurative_detection_deliberation` field for each verse
- [ ] Verify verse 11 has ONLY deliberation about verse 11
- [ ] Verify verse 12 has ONLY deliberation about verse 12
- [ ] (etc. for all 8 verses)

**How to check the database**:
```python
import sqlite3
conn = sqlite3.connect('output/proverbs_3_11-18_batched_validated_20251202_110103.db')
cursor = conn.execute('SELECT reference, figurative_detection_deliberation FROM verses')
for row in cursor:
    print(f"\n{row[0]}:")
    print(row[1][:200])  # First 200 chars
```

---

## CODE LOCATIONS REFERENCE

### Detection (BATCHED - Working correctly)
- **File**: `private/interactive_parallel_processor.py`
- **Function**: `process_chapter_batched()` lines 289-927
- **API call**: lines 434-442 (streaming GPT-5.1 call)

### Validation (NOT BATCHED - Needs fixing)
- **File**: `private/interactive_parallel_processor.py`
- **Loop**: lines 851-916 (loops through each verse)
- **Validator file**: `private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py`
- **Validation method**: `validate_verse_instances()` lines 67-115

### Deliberation Assignment (Needs verse-specific extraction)
- **File**: `private/interactive_parallel_processor.py`
- **Location**: line 782
- **Current**: `'figurative_detection_deliberation': chapter_deliberation`

---

## EXPECTED COSTS AFTER FIXES

| Scenario | Detection | Validation | Total (8 verses) | Per Verse |
|----------|-----------|------------|------------------|-----------|
| Before (broken) | $0.05 | $0.32 (8 calls) | $0.37 | $0.046 |
| After (fixed) | $0.05 | $0.05 (1 call) | $0.10 | $0.0125 |

**Full Proverbs projection (915 verses)**:
- Before: ~$42 (validation costs too high)
- After: ~$11.40 (properly batched)

---

## PREVIOUS SESSION ACCOMPLISHMENTS (Sessions 14-16)

### Session 14: JSON Truncation RESOLVED
- Fixed streaming to capture complete responses (22,342+ chars)
- Detection is now working properly

### Session 15-16: False Positive Truncation Detection FIXED
- Fixed markdown code block handling
- Deliberation extraction working (5,301+ chars captured)
- Detection pipeline fully operational

### Session 17: Root Cause Analysis Complete
- Identified why costs are high (validation not batched)
- Identified deliberation issue (chapter-level copied to all verses)
- No code changes made - just analysis and documentation

---

## FILES TO REVIEW

1. **Main processor**: `private/interactive_parallel_processor.py`
   - `process_chapter_batched()` function (lines 289-927)

2. **Validator**: `private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py`
   - `validate_verse_instances()` method (lines 67-115)

3. **Test script**: `test_proverbs_3_11-18_batched_validated.py`
   - Use this to test your changes

---

## DO NOT TOUCH

- Detection API call (lines 434-442) - This is working correctly
- Deliberation extraction regex patterns (lines 466-480) - These are working
- Truncation detection logic (lines 510-564) - This is working after Session 16 fixes
- JSON extraction logic (lines 581-640) - This is working

---

## QUESTIONS TO ASK IF STUCK

1. "How do I batch multiple verse validations into one API call?"
2. "How do I parse the chapter deliberation to find verse-specific sections?"
3. "How do I map validation results back to their original instances?"
