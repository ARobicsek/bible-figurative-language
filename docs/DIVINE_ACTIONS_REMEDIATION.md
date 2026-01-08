# Divine Actions Figurative Language Remediation

## Issue Summary

The batched processing prompt in `interactive_parallel_processor.py` was missing explicit guidance that **divine actions, emotions, and prophetic formulae are LITERAL in Ancient Near Eastern (ANE) context**, not figurative language. This caused the LLM to incorrectly tag standard biblical expressions as personification, metaphor, or metonymy.

## Root Cause

The guidance about divine actions being literal existed in two components of the pipeline:
- `metaphor_validator.py` (validation phase)
- `flexible_tagging_gemini_client.py` (per-verse detection)

However, this guidance was **missing from the batched chapter processing prompt** in `interactive_parallel_processor.py`, which is used for processing entire chapters at once. Books processed using the batched mode did not receive proper instructions about excluding divine actions from figurative detection.

## Fix Applied

**Commit**: `3495d0a` (2025-01-08)

Added explicit guidance to the batched prompt clarifying that the following are NOT figurative language:

### Divine Actions (LITERAL)
- Divine speech: "the word of GOD came to", "GOD said", "GOD spoke"
- Divine emotions: "GOD was angry", "GOD was pleased", "GOD loved"
- Divine actions: "GOD blessed", "GOD cursed", "GOD watched", "GOD remembered", "GOD fought"
- Prophetic call formulae: "the word of the LORD came to [prophet name]"

### Exception - Divine Body Parts (ARE Metaphorical)
Since God is incorporeal, references to God's body parts ARE correctly tagged as metaphorical:
- "God's hand", "mighty hand", "outstretched arm" = metaphor for divine power
- "God's face", "hide My face" = metaphor for divine presence/favor
- "God's eyes", "God's ears" = metaphor for divine awareness

### Standard Biblical Terminology (NOT figurative)
- Covenant language: "cut a covenant", "signs and wonders"
- Prophetic formulae: "thus says the LORD", "declares the LORD"
- Historical references: "as your fathers did", "in the days of"

## Examples of Incorrect Annotations

### Zechariah 1:1
| Field | Value |
|-------|-------|
| Reference | Zechariah 1:1 |
| Hebrew | הָיָה דְבַר־יְהֹוָה אֶל־זְכַרְיָה |
| English | "this word of GOD came to the prophet Zechariah" |
| **Incorrect Tags** | personification: yes, metonymy: yes |
| Explanation Given | "'Word' stands metonymically for God's message and is personified as something that can 'come' to the prophet" |
| **Should Be** | No figurative language - standard prophetic call formula |

### Zechariah 1:2
| Field | Value |
|-------|-------|
| Reference | Zechariah 1:2 |
| Hebrew | קָצַף יְהֹוָה עַל־אֲבוֹתֵיכֶם קָצֶף |
| English | "GOD was very angry with your ancestors" |
| **Incorrect Tags** | metaphor: yes, personification: yes |
| Explanation Given | "God's judicial opposition to sin is described with the human emotion of 'anger,' an anthropopathic metaphor" |
| **Should Be** | No figurative language - divine emotions are literal in ANE context |

## Affected Books

The following books were processed using the batched mode and may contain incorrect divine action annotations:

### Prophetic Books (High Priority)
These books heavily feature prophetic formulae and divine speech:
- **Major Prophets**: Isaiah, Jeremiah, Ezekiel
- **Minor Prophets (The Twelve)**: Hosea, Joel, Amos, Obadiah, Jonah, Micah, Nahum, Habakkuk, Zephaniah, Haggai, Zechariah, Malachi

### Former Prophets
- Joshua, Judges, 1 Samuel, 2 Samuel, 1 Kings, 2 Kings

### Ketuvim (Writings)
- Psalms (contains many divine action references)
- Other books may have scattered instances

### Torah
- Genesis through Deuteronomy (processed earlier, may have been done with per-verse mode with correct guidance - needs verification)

## Remediation Strategy Options

### Option 1: Targeted Query-Based Fix
Query the database for specific patterns that indicate incorrect tagging:
```sql
-- Find instances tagged as personification/metonymy with divine action patterns
SELECT fl.*, v.reference, v.english_text
FROM figurative_language fl
JOIN verses v ON fl.verse_id = v.id
WHERE (
    fl.personification = 'yes' OR fl.metonymy = 'yes'
) AND (
    fl.figurative_text LIKE '%word of%came to%' OR
    fl.figurative_text LIKE '%GOD was angry%' OR
    fl.figurative_text LIKE '%GOD said%' OR
    fl.figurative_text LIKE '%GOD spoke%' OR
    fl.figurative_text LIKE '%thus says the LORD%'
    -- Add more patterns
);
```

### Option 2: Re-run Validation Phase
Use the existing `metaphor_validator.py` (which has correct guidance) to re-validate all instances from affected books. The validator should reject divine actions.

### Option 3: Re-process Affected Books
Re-run the entire processing pipeline on affected books with the corrected prompt. This is the most thorough but most expensive option.

### Option 4: Hybrid Approach
1. Query for likely false positives using pattern matching
2. Use LLM to re-evaluate flagged instances with correct guidance
3. Bulk update the database based on re-evaluation

## Database Fields to Update

When remediating, the following fields may need to be updated:

```
figurative_language fl:
- figurative_language: 'yes' -> 'no' (if no other figurative language in instance)
- personification: 'yes' -> 'no'
- metonymy: 'yes' -> 'no'
- metaphor: 'yes' -> 'no' (for divine emotions incorrectly tagged)
- final_personification: 'yes' -> 'no'
- final_metonymy: 'yes' -> 'no'
- final_metaphor: 'yes' -> 'no'
- final_figurative_language: 'yes' -> 'no'
```

If an instance has NO remaining figurative language after removing the divine action tags, the entire `figurative_language` row should potentially be deleted.

## Verification Queries

After remediation, run these queries to verify the fix:

```sql
-- Count remaining divine action false positives
SELECT COUNT(*) FROM figurative_language fl
JOIN verses v ON fl.verse_id = v.id
WHERE fl.personification = 'yes'
AND fl.figurative_text LIKE '%word of%LORD%came%';

-- Verify prophetic books have reasonable detection rates
SELECT v.book, COUNT(DISTINCT v.id) as verses, COUNT(fl.id) as instances,
       ROUND(COUNT(fl.id) * 1.0 / COUNT(DISTINCT v.id), 2) as rate
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE v.book IN ('Zechariah', 'Jeremiah', 'Isaiah', 'Ezekiel')
GROUP BY v.book;
```

## Files Modified

| File | Change |
|------|--------|
| `private/interactive_parallel_processor.py` | Added "CRITICAL: WHAT IS NOT FIGURATIVE LANGUAGE" section to batched prompt |

## Related Files with Correct Guidance

These files already had the correct guidance and can be referenced:
- `private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py` (lines 483-484, 859-865)
- `private/flexible_tagging_gemini_client.py` (lines 159, 185, 194, 208)

## Next Steps

1. Determine scope of affected data (which books, how many instances)
2. Choose remediation strategy based on scope and budget
3. Create backup of database before remediation
4. Execute remediation
5. Verify results with test queries
6. Document any edge cases discovered during remediation
