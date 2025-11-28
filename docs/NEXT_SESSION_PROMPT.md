# Next Session Prompt

**Last Updated**: 2025-11-28

## Where We Are

**Current Phase**: Phase 2 - Add Proverbs ✅ IMPLEMENTATION COMPLETE
**Next Phase**: Phase 2 Testing or Phase 3 - Progress Tracking

## What to Do Next

### Option A: Test Phase 2 Implementation (RECOMMENDED)

Test the Proverbs implementation with chapter context:

1. **Test with Proverbs 1** (33 verses):
   ```bash
   cd "C:\Users\ariro\OneDrive\Documents\Bible"
   python private/interactive_parallel_processor.py
   ```
   - Select: Book = Proverbs (or 7)
   - Select: Chapters = 1
   - Select: Verses = all
   - Workers: 6 (recommended)

2. **Verify Chapter Context Working**:
   - Check logs for: "Generated chapter context for Proverbs 1 (X chars)"
   - Check logs for: "Using chapter context for Proverbs 1 (wisdom literature mode)"
   - Confirm chapter text included in prompts

3. **Check Results Quality**:
   - Figurative detection rate should be >60%
   - Spot-check instances:
     - Animal metaphors (lion, etc.) detected?
     - Path/way metaphors identified?
     - Personification of Wisdom recognized?
   - Review database entries for completeness

4. **If Test Succeeds**: Process Proverbs 2-31
   - Run full book: Select "Proverbs", Chapters = "all"
   - Monitor processing time and costs
   - Track model usage (GPT-5.1 vs Claude vs Gemini)
   - Verify database integration for all 915 verses

### Option B: Proceed to Phase 3 (Optional)

Only needed if Proverbs processing runs are very long:
- Create session_tracker.py for checkpointing
- Add cost summaries
- Add error recovery messages

## Implementation Complete

**Phase 2 Changes**:
- ✅ Added Proverbs to book definitions (31 chapters, ~915 verses)
- ✅ Implemented chapter context parameter throughout pipeline
- ✅ Added POETIC_WISDOM context rules to flexible tagging client
- ✅ Chapter context generation for Proverbs (Hebrew + English full chapter)
- ✅ Updated all analysis methods to accept and pass chapter_context
- ✅ Backward compatible (other books unaffected)

**Files Modified**:
- `private/interactive_parallel_processor.py` (7 locations updated)
- `private/flexible_tagging_gemini_client.py` (chapter context support + POETIC_WISDOM rules)

## Blockers

None currently.

## Phase 1 Accomplishments

✅ Created unified_llm_client.py with three-model fallback chain
✅ Updated all dependent files (gemini_api_multi_model.py, metaphor_validator.py, flexible_tagging_gemini_client.py)
✅ Tested and verified API connections for GPT-5.1, Claude Opus 4.5, Gemini 3.0 Pro
✅ Maintained backward compatibility with existing code
✅ All API keys configured in .env

## Critical Configuration Reminders

⚠️ **GPT-5.1**: `reasoning_effort` DEFAULTS TO "none" - must explicitly set to "high"!
✅ **Claude Opus 4.5**: `effort="high"`, model ID: `"claude-opus-4-5-20251101"`
✅ **Gemini 3.0 Pro**: `thinking_level="high"` (defaults to "high", good!)

## Reference Materials

- **Implementation Plan**: `C:\Users\ariro\.claude\plans\dazzling-squishing-brooks.md`
- **Psalms Project Reference**: `C:\Users\ariro\OneDrive\Documents\Psalms\docs\IMPLEMENTATION_LOG.md`
  - Session 143: GPT-5.1 implementation
  - Session 145: Claude Opus 4.5 integration

## API Keys Required

Ensure `.env` contains:
```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=...  # Existing
```
