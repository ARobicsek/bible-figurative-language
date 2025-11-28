# Next Session Prompt

**Last Updated**: 2025-11-28

## Where We Are

**Current Phase**: Phase 1 - Multi-Model LLM Client ✅ COMPLETE
**Next Phase**: Phase 2 - Add Book of Proverbs

## What to Do Next

Start Phase 2 by adding Proverbs to the database:

1. **Update book definitions** in `private/interactive_parallel_processor.py`:
   - Add "Proverbs": 31 to books dictionary (~line 84-86)
   - Add "Proverbs": 915 to verse_estimates (~line 639-642)
   - Update other book references as needed

2. **Configure POETIC_WISDOM context** for Proverbs:
   - Already added to UnifiedLLMClient in Phase 1
   - Context provides balanced figurative detection for wisdom literature
   - Includes animal metaphors, nature imagery, personification rules

3. **Test with Proverbs 1** (31 verses):
   - Run: `python private/interactive_parallel_processor.py`
   - Select: Book = Proverbs, Chapter = 1
   - Verify: High figurative detection rate (>60%)
   - Check: Database integration works correctly

4. **Process full Proverbs** (if test succeeds):
   - Process all 31 chapters (~915 verses)
   - Monitor model usage and costs
   - Verify quality with spot-checks

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
