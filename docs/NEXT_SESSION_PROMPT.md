# Next Session Prompt

**Last Updated**: 2025-11-29
**Session**: 5
**Priority**: CRITICAL - Architecture Fix Required

## CRITICAL Issue to Fix

**Problem**: FlexibleTaggingGeminiClient's custom prompt is not being used

### Root Cause
The `_build_prompt()` override in FlexibleTaggingGeminiClient is never called because:
1. `FlexibleTaggingGeminiClient.analyze_figurative_language_flexible()`
2. → delegates to `self.unified_client.analyze_figurative_language()`
3. → which calls `UnifiedLLMClient._build_prompt()` (standard prompt)
4. → The override in FlexibleTaggingGeminiClient is in the wrong class layer and never executes

### Evidence
- Proverbs 1 test: 0% detection (0/33 verses)
- Proverbs 3:18 debug test revealed standard prompt being sent (not flexible tagging)
- Debug logging confirmed GPT-5.1 received UnifiedLLMClient prompt with emojis still in it

### Impact
- System runs without crashes
- GPT-5.1 is working correctly
- **But**: Flexible tagging format not being used (TARGET/VEHICLE/GROUND taxonomy missing)

## Solution Options

### Option A: Pass Custom Prompt to UnifiedLLMClient (RECOMMENDED)
Build the flexible tagging prompt in FlexibleTaggingGeminiClient, then pass it directly:

```python
# In FlexibleTaggingGeminiClient.analyze_figurative_language_flexible()
text_context = self._determine_text_context(book, chapter)
custom_prompt = self._create_flexible_tagging_prompt(
    hebrew_text, english_text, text_context, chapter_context
)

# Pass the pre-built prompt to UnifiedLLMClient
result, error, metadata = self.unified_client.analyze_with_custom_prompt(
    custom_prompt, hebrew_text, english_text
)
```

Add new method to UnifiedLLMClient:
```python
def analyze_with_custom_prompt(self, custom_prompt: str, hebrew_text: str,
                               english_text: str) -> Tuple[str, Optional[str], Dict]:
    """Analyze using a custom pre-built prompt instead of _build_prompt()"""
    # Try GPT-5.1, Claude, Gemini with the custom_prompt
```

### Option B: Prompt Builder Callback
Pass the prompt builder function as a parameter to UnifiedLLMClient constructor.

### Option C: Add custom_prompt Parameter
Add optional `custom_prompt` parameter to `analyze_figurative_language()`.

## Task List for Next Session

### 1. Fix Architecture (30-45 minutes)
- [ ] Implement Option A (analyze_with_custom_prompt)
- [ ] Update FlexibleTaggingGeminiClient to use it
- [ ] Test with Proverbs 3:18 to verify flexible tagging prompt is used

### 2. Verify Fix (15 minutes)
- [ ] Run Proverbs 3:18 test again
- [ ] Check debug logs confirm flexible tagging prompt sent
- [ ] Verify TARGET/VEHICLE/GROUND fields in output

### 3. Re-run Proverbs Test (optional - only if time permits)
- [ ] Run Proverbs 1 again (33 verses, ~$2.40, 8-10 minutes)
- [ ] Expect >60% detection rate for wisdom literature
- [ ] Verify results look correct

## Important Reminders

### UTF-8 Encoding for Test Scripts
**ALWAYS add this at the top of test scripts to avoid Unicode errors on Windows:**

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script description"""

import sys

# Fix Windows console encoding - MUST BE BEFORE ANY PRINT STATEMENTS
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
```

### API Configuration Notes
- GPT-5.1: NO temperature parameter (only supports default of 1)
- GPT-5.1: reasoning_effort="high" is critical
- Claude Opus 4.5: timeout=540.0 to avoid streaming requirement
- Gemini 3.0 Pro: Works as final fallback

### Performance Metrics (from Proverbs 3:18 test)
- GPT-5.1 processing time: ~96 seconds per verse
- Cost: ~$0.072 per verse
- For 915 verses (full Proverbs): ~$64, ~2.5 hours with 6 workers

## Files to Modify

1. **`private/src/hebrew_figurative_db/ai_analysis/unified_llm_client.py`**
   - Add `analyze_with_custom_prompt()` method

2. **`private/flexible_tagging_gemini_client.py`**
   - Update `analyze_figurative_language_flexible()` to use custom prompt method

## Testing Strategy

**Step 1**: Quick test with Proverbs 3:18
```bash
cd "C:\Users\ariro\OneDrive\Documents\Bible"
python test_proverbs_3_18.py
```

**Step 2**: If successful, consider Proverbs 1 re-test
- Only run if architecture fix is confirmed working
- Costs ~$2.40 for 33 verses

**Step 3**: Full Proverbs processing
- **DON'T RUN** until user approves cost (~$64)
- Requires ~2.5 hours processing time

## Blockers

None - clear path forward with Option A

## Reference Files

- Test script: [test_proverbs_3_18.py](file:///c:/Users/ariro/OneDrive/Documents/Bible/test_proverbs_3_18.py)
- Implementation log: [docs/IMPLEMENTATION_LOG.md](file:///c:/Users/ariro/OneDrive/Documents/Bible/docs/IMPLEMENTATION_LOG.md)
- Project status: [docs/PROJECT_STATUS.md](file:///c:/Users/ariro/OneDrive/Documents/Bible/docs/PROJECT_STATUS.md)
