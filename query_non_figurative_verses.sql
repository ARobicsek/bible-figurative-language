-- SQL Query to retrieve all verses that the LLM does NOT detect figurative language in
-- This query finds verses that exist in the verses table but have no corresponding
-- entries in the figurative_language table

-- Query 1: Basic query - verses without any figurative language detection
SELECT
    v.reference,
    v.book,
    v.chapter,
    v.verse,
    v.hebrew_text,
    v.english_text,
    v.speaker,
    v.word_count,
    v.processed_at
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
ORDER BY v.book, v.chapter, v.verse;

-- Query 2: With book filtering - only show specific books
SELECT
    v.reference,
    v.hebrew_text,
    v.english_text,
    v.speaker,
    v.word_count
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
  AND v.book IN ('Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy')
ORDER BY v.book, v.chapter, v.verse;

-- Query 3: Count of non-figurative verses by book
SELECT
    v.book,
    COUNT(*) as non_figurative_count,
    COUNT(DISTINCT v.chapter) as chapters_with_non_figurative
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
GROUP BY v.book
ORDER BY non_figurative_count DESC;

-- Query 4: Percentage of verses without figurative language by book
SELECT
    v.book,
    COUNT(*) as total_verses,
    COUNT(CASE WHEN fl.verse_id IS NULL THEN 1 END) as non_figurative_verses,
    ROUND(
        COUNT(CASE WHEN fl.verse_id IS NULL THEN 1 END) * 100.0 / COUNT(*),
        2
    ) as percentage_non_figurative
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
GROUP BY v.book
ORDER BY percentage_non_figurative DESC;

-- Query 5: Non-figurative verses with context (show surrounding verses)
SELECT
    v.reference,
    v.hebrew_text,
    v.english_text,
    v.speaker,
    LAG(v.reference, 1) OVER (PARTITION BY v.book ORDER BY v.chapter, v.verse) as previous_verse,
    LEAD(v.reference, 1) OVER (PARTITION BY v.book ORDER BY v.chapter, v.verse) as next_verse
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
ORDER BY v.book, v.chapter, v.verse;

-- Query 6: Random sample of non-figurative verses for manual review
SELECT
    v.reference,
    v.hebrew_text,
    v.english_text,
    v.speaker
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
ORDER BY RANDOM()
LIMIT 50;

-- Query 7: Non-figurative verses by speaker (to see patterns)
SELECT
    v.speaker,
    COUNT(*) as count,
    GROUP_CONCAT(v.reference, '; ') as sample_references
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
  AND v.speaker IS NOT NULL
GROUP BY v.speaker
ORDER BY count DESC;

-- Query 8: Long non-figurative verses (might be more likely to contain missed figurative language)
SELECT
    v.reference,
    v.hebrew_text,
    v.english_text,
    v.word_count,
    v.speaker
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.verse_id IS NULL
  AND v.word_count > 10  -- Adjust threshold as needed
ORDER BY v.word_count DESC
LIMIT 100;