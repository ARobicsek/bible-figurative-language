# Database Schema Documentation

Complete technical reference for the Hebrew Figurative Language Explorer database structure.

---

## Overview

The database uses SQLite 3 with a two-table design:

1. **`verses`** - All analyzed verses (8,373 verses from Torah and Psalms)
2. **`figurative_language`** - Figurative language instances found in verses (5,865 instances)

**Relationship:** One-to-Many (one verse can have multiple figurative language instances)

---

## Table of Contents

1. [Verses Table](#verses-table)
2. [Figurative Language Table](#figurative-language-table)
3. [Indexes](#indexes)
4. [Common Queries](#common-queries)
5. [Data Types and Constraints](#data-types-and-constraints)
6. [JSON Fields](#json-fields)

---

## Verses Table

Stores all processed verses with AI detection deliberation.

### Schema

```sql
CREATE TABLE verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    hebrew_text_stripped TEXT,
    hebrew_text_non_sacred TEXT,
    english_text TEXT NOT NULL,
    english_text_non_sacred TEXT,
    figurative_detection_deliberation TEXT,
    model_used TEXT DEFAULT 'gemini-2.5-flash',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key | `1` |
| `reference` | TEXT | Full verse reference | `"Genesis 1:2"` |
| `book` | TEXT | Book name | `"Genesis"` |
| `chapter` | INTEGER | Chapter number | `1` |
| `verse` | INTEGER | Verse number | `2` |
| `hebrew_text` | TEXT | Hebrew text with vowel points | `"וְהָאָ֗רֶץ הָיְתָ֥ה תֹ֙הוּ֙ וָבֹ֔הוּ"` |
| `hebrew_text_stripped` | TEXT | Hebrew without vowel points | `"והארץ היתה תהו ובהו"` |
| `hebrew_text_non_sacred` | TEXT | Hebrew with traditional abbreviations for divine names | `"וה' אלקים ברא"` |
| `english_text` | TEXT | English translation | `"And the earth was without form"` |
| `english_text_non_sacred` | TEXT | English with traditional divine name renderings | Uses "the Lord" variations |
| `figurative_detection_deliberation` | TEXT | AI reasoning about figurative language in this verse | Full AI explanation |
| `model_used` | TEXT | AI model that processed this verse | `"gemini-2.5-flash"`, `"gemini-2.5-pro"`, `"claude-sonnet-4"` |
| `processed_at` | TIMESTAMP | Processing timestamp | `"2025-09-29 10:30:00"` |

### Books Included

- Genesis (Bereishit)
- Exodus (Shemot)
- Leviticus (Vayikra)
- Numbers (Bamidbar)
- Deuteronomy (Devarim)
- Psalms (Tehillim) - all 150 chapters

### Example Row

```json
{
  "id": 42,
  "reference": "Genesis 3:15",
  "book": "Genesis",
  "chapter": 3,
  "verse": 15,
  "hebrew_text": "וְאֵיבָ֣ה ׀ אָשִׁ֗ית בֵּֽינְךָ֙ וּבֵ֣ין הָֽאִשָּׁ֔ה",
  "hebrew_text_stripped": "ואיבה אשית בינך ובין האשה",
  "english_text": "And I will put enmity between you and the woman",
  "figurative_detection_deliberation": "This verse contains personification...",
  "model_used": "gemini-2.5-flash",
  "processed_at": "2025-09-26 14:23:11"
}
```

---

## Figurative Language Table

Stores validated figurative language instances.

### Schema

```sql
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,

    -- Final validated classifications
    final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')),
    final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')),
    final_simile TEXT CHECK(final_simile IN ('yes', 'no')),
    final_personification TEXT CHECK(final_personification IN ('yes', 'no')),
    final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')),
    final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')),
    final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')),
    final_other TEXT CHECK(final_other IN ('yes', 'no')),

    -- Hierarchical metadata (JSON arrays)
    target TEXT,
    vehicle TEXT,
    ground TEXT,
    posture TEXT,

    -- Core instance data
    confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    figurative_text_in_hebrew_non_sacred TEXT,
    explanation TEXT,
    speaker TEXT,

    -- Validation audit trail
    validation_reason_metaphor TEXT,
    validation_reason_simile TEXT,
    validation_reason_personification TEXT,
    validation_reason_idiom TEXT,
    validation_reason_hyperbole TEXT,
    validation_reason_metonymy TEXT,
    validation_reason_other TEXT,

    model_used TEXT DEFAULT 'gemini-2.5-flash',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (verse_id) REFERENCES verses (id)
);
```

### Column Descriptions

| Column | Type | Description | Example |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key | `1` |
| `verse_id` | INTEGER | References verses.id | `42` |
| **Figurative Types** | | | |
| `final_metaphor` | TEXT | Validated as metaphor | `"yes"` or `"no"` |
| `final_simile` | TEXT | Validated as simile | `"yes"` or `"no"` |
| `final_personification` | TEXT | Validated as personification | `"yes"` or `"no"` |
| `final_idiom` | TEXT | Validated as idiom | `"yes"` or `"no"` |
| `final_hyperbole` | TEXT | Validated as hyperbole | `"yes"` or `"no"` |
| `final_metonymy` | TEXT | Validated as metonymy | `"yes"` or `"no"` |
| `final_other` | TEXT | Other figurative type | `"yes"` or `"no"` |
| **Metadata** | | | |
| `target` | TEXT | JSON array: what the figure is about | `["God","deity","divine being"]` |
| `vehicle` | TEXT | JSON array: what it's compared to | `["shepherd","occupation","person"]` |
| `ground` | TEXT | JSON array: shared quality | `["care","emotional quality"]` |
| `posture` | TEXT | JSON array: speaker's stance | `["reassurance","comfort"]` |
| **Instance Details** | | | |
| `confidence` | REAL | AI confidence (0.0-1.0) | `0.85` |
| `figurative_text` | TEXT | The figurative phrase (English) | `"The Lord is my shepherd"` |
| `figurative_text_in_hebrew` | TEXT | Hebrew with vowel points | `"יְהוָ֥ה רֹעִ֑י"` |
| `figurative_text_in_hebrew_non_sacred` | TEXT | Hebrew with traditional forms | `"ה' רֹעִ֑י"` |
| `explanation` | TEXT | AI explanation of the figure | Full explanation text |
| `speaker` | TEXT | Who is speaking | `"David"`, `"Narrator"`, `"God"` |
| **Validation** | | | |
| `validation_reason_metaphor` | TEXT | Why validated as metaphor | AI reasoning |
| `validation_reason_simile` | TEXT | Why validated as simile | AI reasoning |
| *(similar for other types)* | | | |
| **Tracking** | | | |
| `model_used` | TEXT | AI model used | `"gemini-2.5-flash"` |
| `processed_at` | TIMESTAMP | Processing time | `"2025-09-26 14:23:11"` |

### Example Row

```json
{
  "id": 523,
  "verse_id": 42,
  "final_metaphor": "yes",
  "final_simile": "no",
  "final_personification": "yes",
  "final_idiom": "no",
  "final_hyperbole": "no",
  "final_metonymy": "no",
  "final_other": "no",
  "target": ["serpent", "animal", "living creature"],
  "vehicle": ["enemy", "adversary", "hostile entity"],
  "ground": ["hostility", "conflict", "opposition"],
  "posture": ["warning", "consequence", "divine decree"],
  "confidence": 0.88,
  "figurative_text": "he shall bruise your head",
  "figurative_text_in_hebrew": "הוּא֙ יְשֽׁוּפְךָ֣ רֹ֔אשׁ",
  "explanation": "The serpent is personified as having enmity...",
  "speaker": "God",
  "validation_reason_metaphor": "Confirmed as metaphor because...",
  "model_used": "gemini-2.5-flash",
  "processed_at": "2025-09-26 14:23:11"
}
```

---

## Indexes

Performance indexes for common queries:

### Verses Table Indexes

```sql
CREATE INDEX idx_verses_reference ON verses (reference);
CREATE INDEX idx_verses_book_chapter ON verses (book, chapter);
```

### Figurative Language Table Indexes

```sql
-- Type indexes (for filtering)
CREATE INDEX idx_final_metaphor ON figurative_language (final_metaphor);
CREATE INDEX idx_final_simile ON figurative_language (final_simile);
CREATE INDEX idx_final_personification ON figurative_language (final_personification);
CREATE INDEX idx_final_idiom ON figurative_language (final_idiom);
CREATE INDEX idx_final_hyperbole ON figurative_language (final_hyperbole);
CREATE INDEX idx_final_metonymy ON figurative_language (final_metonymy);
CREATE INDEX idx_final_other ON figurative_language (final_other);

-- Metadata indexes
CREATE INDEX idx_figurative_confidence ON figurative_language (confidence);
CREATE INDEX idx_figurative_speaker ON figurative_language (speaker);
```

---

## Common Queries

### Get All Verses with Figurative Language

```sql
SELECT
    v.reference,
    v.english_text,
    v.hebrew_text,
    COUNT(fl.id) as figurative_count
FROM verses v
INNER JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.final_figurative_language = 'yes'
GROUP BY v.id
ORDER BY v.book, v.chapter, v.verse;
```

### Find All Metaphors in Genesis

```sql
SELECT
    v.reference,
    fl.figurative_text,
    fl.explanation,
    fl.confidence
FROM verses v
INNER JOIN figurative_language fl ON v.id = fl.verse_id
WHERE v.book = 'Genesis'
  AND fl.final_metaphor = 'yes'
ORDER BY v.chapter, v.verse;
```

### Search Hebrew Text

```sql
SELECT
    reference,
    hebrew_text,
    english_text
FROM verses
WHERE hebrew_text_stripped LIKE '%אלהים%'
ORDER BY book, chapter, verse;
```

### Get Statistics by Book

```sql
SELECT
    v.book,
    COUNT(DISTINCT v.id) as total_verses,
    COUNT(DISTINCT CASE WHEN fl.id IS NOT NULL THEN v.id END) as verses_with_figurative,
    COUNT(fl.id) as total_instances,
    ROUND(AVG(fl.confidence), 3) as avg_confidence
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
  AND fl.final_figurative_language = 'yes'
GROUP BY v.book
ORDER BY
    CASE v.book
        WHEN 'Genesis' THEN 1
        WHEN 'Exodus' THEN 2
        WHEN 'Leviticus' THEN 3
        WHEN 'Numbers' THEN 4
        WHEN 'Deuteronomy' THEN 5
    END;
```

### Find Instances by Target

```sql
SELECT
    v.reference,
    fl.figurative_text,
    fl.target,
    fl.vehicle,
    fl.ground
FROM verses v
INNER JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.target LIKE '%God%'
  AND fl.final_figurative_language = 'yes'
ORDER BY v.book, v.chapter, v.verse;
```

### Get Multiple Figurative Types

```sql
SELECT
    v.reference,
    fl.figurative_text,
    fl.final_metaphor,
    fl.final_simile,
    fl.final_personification,
    fl.final_idiom
FROM verses v
INNER JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.final_metaphor = 'yes'
  AND fl.final_idiom = 'yes'  -- Both metaphor AND idiom
ORDER BY v.book, v.chapter, v.verse;
```

### Get Verses Without Figurative Language

```sql
SELECT
    v.reference,
    v.english_text,
    v.hebrew_text
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
WHERE fl.id IS NULL
   OR fl.final_figurative_language = 'no'
ORDER BY v.book, v.chapter, v.verse;
```

### Complex Search: Target AND Vehicle

```sql
SELECT
    v.reference,
    fl.figurative_text,
    fl.target,
    fl.vehicle,
    fl.explanation
FROM verses v
INNER JOIN figurative_language fl ON v.id = fl.verse_id
WHERE (fl.target LIKE '%God%' OR fl.target LIKE '%Israel%')
  AND (fl.vehicle LIKE '%shepherd%' OR fl.vehicle LIKE '%father%')
  AND fl.final_figurative_language = 'yes'
ORDER BY v.book, v.chapter, v.verse;
```

---

## Data Types and Constraints

### Text Constraints

All figurative type fields use CHECK constraints:

```sql
CHECK(final_metaphor IN ('yes', 'no'))
```

Valid values: `'yes'`, `'no'`, or `NULL`

### Confidence Range

```sql
CHECK(confidence >= 0.0 AND confidence <= 1.0)
```

Valid range: 0.0 to 1.0 (representing 0% to 100% confidence)

### Model Names

Standard values:
- `"gemini-2.5-flash"` - Primary model (most instances)
- `"gemini-2.5-pro"` - Fallback for complex cases
- `"claude-sonnet-4"` - Final fallback for extremely complex cases

---

## JSON Fields

Four metadata fields store hierarchical data as JSON arrays:

### Target

**What** the figurative language is about (the subject being described).

**Format:** JSON array ordered from specific to general

**Example:**
```json
["David", "king", "person", "human"]
```

### Vehicle

**What** the target is being compared to or likened to.

**Format:** JSON array ordered from specific to general

**Example:**
```json ["lion", "predatory animal", "living creature"]
```

### Ground

**What quality** is being described (the shared characteristic).

**Format:** JSON array ordered from specific to general

**Example:**
```json
["courage", "moral quality", "character trait"]
```

### Posture

**Speaker's attitude** or stance toward the subject.

**Format:** JSON array ordered from specific to general

**Example:**
```json
["celebration", "praise", "positive sentiment"]
```

### Querying JSON Fields

SQLite's JSON functions can be used:

```sql
-- Extract first element of target array
SELECT
    reference,
    json_extract(target, '$[0]') as target_specific
FROM figurative_language
WHERE target IS NOT NULL;

-- Search within JSON arrays
SELECT *
FROM figurative_language
WHERE target LIKE '%shepherd%';
```

---

## Database Size and Performance

**Database File:** `Pentateuch_Psalms_fig_language.db`
**Size:** ~50 MB
**Total Verses:** 8,373
**Figurative Instances:** 5,865

**Performance Notes:**
- All indexes created for common query patterns
- Hebrew text searches use `hebrew_text_stripped` (no vowel points)
- Pagination recommended for large result sets (50-100 verses per page)

---

## Schema Versioning

**Current Version:** 4.0
**Last Updated:** September 25, 2025

**Major Changes from Previous Versions:**
- Added hierarchical JSON metadata fields (target, vehicle, ground, posture)
- Added non-sacred text fields for Hebrew and English
- Added validation reasoning fields for each figurative type
- Added model tracking fields

---

## Data Export

### Export to CSV

```bash
sqlite3 database/torah_figurative_language.db

.mode csv
.headers on
.output verses.csv
SELECT * FROM verses;
.output figurative_language.csv
SELECT * FROM figurative_language;
.quit
```

### Export to JSON

```bash
sqlite3 database/torah_figurative_language.db

.mode json
.output verses.json
SELECT * FROM verses;
.output figurative_language.json
SELECT * FROM figurative_language;
.quit
```

---

## Migration to PostgreSQL

For Supabase or other PostgreSQL deployments:

### Key Changes Needed

1. **Primary Keys:**
   ```sql
   -- SQLite
   id INTEGER PRIMARY KEY AUTOINCREMENT

   -- PostgreSQL
   id SERIAL PRIMARY KEY
   ```

2. **CHECK Constraints:**
   - SQLite inline CHECK constraints work in PostgreSQL
   - No changes needed

3. **Timestamps:**
   ```sql
   -- SQLite
   TIMESTAMP DEFAULT CURRENT_TIMESTAMP

   -- PostgreSQL
   TIMESTAMP DEFAULT NOW()
   ```

4. **JSON Fields:**
   - SQLite stores as TEXT
   - PostgreSQL can use native JSON or JSONB type
   - Consider using `JSONB` for better indexing

---

## Related Documentation

- [METHODOLOGY.md](METHODOLOGY.md) - How the data was generated
- [FEATURES.md](FEATURES.md) - How to query the database via the interface
- [SETUP.md](../SETUP.md) - How to deploy your own instance

---

## Questions?

Open an issue with the "question" label on [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues).
