# Jeremiah Processing Guide

## Overview

This document provides guidance for processing the Book of Jeremiah through the Hebrew Figurative Language Pipeline. Jeremiah is a prophetic book with 52 chapters and approximately 1,364 verses.

## Pipeline Version

- **Pipeline Version**: 2.1.0
- **Last Updated**: December 2024

## Book Characteristics

Jeremiah presents unique processing challenges:

| Characteristic | Value | Impact |
|----------------|-------|--------|
| Chapters | 52 | Requires batched processing |
| Verses | ~1,364 | Moderate-large book |
| Genre | Prophetic | High metaphor density |
| Average verses/chapter | ~26 | Similar to Isaiah |

### Expected Figurative Language Types

Based on Isaiah processing, expect high rates of:
- **Metaphor**: Divine attributes, agricultural imagery, covenant language
- **Personification**: Jerusalem/Zion as person, nature responding
- **Simile**: "like a lion", "as the potter"
- **Idiom**: Prophetic formulae ("Thus says the LORD")
- **Hyperbole**: Judgment pronouncements

## Processing Strategy

### Recommended Batch Sizes

```
Batch 1: Chapters 1-10  (Call narrative, temple sermon, early oracles)
Batch 2: Chapters 11-20 (Confessions, symbolic actions)
Batch 3: Chapters 21-30 (Judgment oracles, Book of Consolation begins)
Batch 4: Chapters 31-40 (New covenant, fall of Jerusalem)
Batch 5: Chapters 41-52 (Egypt oracles, historical appendix)
```

### Execution Commands

```bash
cd C:\Users\ariro\OneDrive\Documents\Bible\private

# Batch 1
python interactive_parallel_processor.py Jeremiah 1
python interactive_parallel_processor.py Jeremiah 2
# ... through Jeremiah 10

# Or use interactive mode for batch selection
python interactive_parallel_processor.py
```

## Configuration

The pipeline uses these settings for Jeremiah:

| Setting | Value | Rationale |
|---------|-------|-----------|
| `max_completion_tokens` | 100,000 | Higher limit for long chapters |
| `reasoning_effort` | "medium" | Balance quality and cost |
| `processing_mode` | Batched | Efficient API usage |
| `validation_retries` | 4 | With degrading effort levels |

## Output Files

Each run produces:

```
{book}_c{chapter}_all_v_batched_{YYYYMMDD}_{HHMM}.db      # Database
{book}_c{chapter}_all_v_batched_{YYYYMMDD}_{HHMM}_log.txt # Detailed log
{book}_c{chapter}_all_v_batched_{YYYYMMDD}_{HHMM}_results.json  # Summary
{book}_c{chapter}_all_v_batched_{YYYYMMDD}_{HHMM}_failures.json # Failure manifest
{book}_c{chapter}_all_v_batched_{YYYYMMDD}_{HHMM}_manifest.json # Processing manifest
```

## Cost Estimates

Based on Isaiah processing experience:

| Item | Estimate |
|------|----------|
| Cost per chapter | $0.08-0.15 |
| Total book cost | $4-8 |
| Processing time | 2-4 hours |
| Expected success rate | 95%+ |

## Failure Recovery

If chapters fail:

1. Check the `_failures.json` file for detailed error information
2. Use the retry commands listed in the manifest
3. Common failures:
   - JSON parsing: Usually recovers on retry
   - Streaming corruption: Fixed with non-streaming fallback
   - Sefaria API: Retry after delay

### Retry Failed Chapters

```bash
# The failures.json will contain retry commands like:
python interactive_parallel_processor.py Jeremiah 25
```

## Validation

After processing, verify:

1. **Database integrity**: Check `processing_runs` table
2. **Validation coverage**: Should be >95%
3. **Instance count**: Compare to Isaiah baseline (~800-1000 instances expected)

```sql
-- Check processing run
SELECT * FROM processing_runs WHERE book='Jeremiah';

-- Check verse coverage
SELECT COUNT(DISTINCT verse_id) FROM verses WHERE book='Jeremiah';

-- Check figurative language instances
SELECT COUNT(*) FROM figurative_language
JOIN verses ON figurative_language.verse_id = verses.id
WHERE verses.book='Jeremiah';
```

## Known Issues

### Potential Challenges

1. **Chapters 46-51** (Oracles against nations): Dense metaphorical language
2. **Chapter 52**: Historical appendix with less figurative content
3. **Confessions (11-20)**: Complex poetic structure

### Workarounds

- If a chapter fails repeatedly, try reducing batch size
- For very long chapters, monitor streaming for corruption
- Cache is preserved for reruns via `.sefaria_cache/`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.1.0 | Dec 2024 | Added Jeremiah support, enhanced failure tracking |
| 2.0.0 | Nov 2024 | Initial batched processing for prophetic books |

## See Also

- [PIPELINE_ARCHITECTURE.md](PIPELINE_ARCHITECTURE.md) - Full pipeline documentation
- [PROVERBS_LESSONS_LEARNED.md](PROVERBS_LESSONS_LEARNED.md) - Processing insights
