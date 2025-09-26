-- Hebrew Figurative Language Database Schema v4.0
-- CURRENT WORKING SYSTEM (Sept 25, 2025)
-- Dual-system architecture: Original multi-model + Flexible hierarchical tagging

-- =============================================================================
-- CORE TABLES - CURRENT WORKING ARCHITECTURE
-- =============================================================================

-- Verses table - stores ALL processed verses with figurative detection deliberation
CREATE TABLE IF NOT EXISTS verses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT NOT NULL,
    hebrew_text_stripped TEXT,
    english_text TEXT NOT NULL,
    word_count INTEGER,
    llm_restriction_error TEXT,
    llm_deliberation TEXT,
    figurative_detection_deliberation TEXT,  -- LLM reasoning about figurative language detection for this verse
    instances_detected INTEGER,
    instances_recovered INTEGER,
    instances_lost_to_truncation INTEGER,
    truncation_occurred TEXT CHECK(truncation_occurred IN ('yes', 'no')) DEFAULT 'no',
    both_models_truncated TEXT CHECK(both_models_truncated IN ('yes', 'no')) DEFAULT 'no',  -- Track when both Flash and Pro models fail
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Figurative language table - stores only verses WITH figurative language found
CREATE TABLE IF NOT EXISTS figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,

    -- Initial detection fields (what LLM originally detected)
    figurative_language TEXT CHECK(figurative_language IN ('yes', 'no')) DEFAULT 'no',
    simile TEXT CHECK(simile IN ('yes', 'no')) DEFAULT 'no',
    metaphor TEXT CHECK(metaphor IN ('yes', 'no')) DEFAULT 'no',
    personification TEXT CHECK(personification IN ('yes', 'no')) DEFAULT 'no',
    idiom TEXT CHECK(idiom IN ('yes', 'no')) DEFAULT 'no',
    hyperbole TEXT CHECK(hyperbole IN ('yes', 'no')) DEFAULT 'no',
    metonymy TEXT CHECK(metonymy IN ('yes', 'no')) DEFAULT 'no',
    other TEXT CHECK(other IN ('yes', 'no')) DEFAULT 'no',

    -- Final validated fields (post-validation results)
    final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')) DEFAULT 'no',
    final_simile TEXT CHECK(final_simile IN ('yes', 'no')) DEFAULT 'no',
    final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')) DEFAULT 'no',
    final_personification TEXT CHECK(final_personification IN ('yes', 'no')) DEFAULT 'no',
    final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')) DEFAULT 'no',
    final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')) DEFAULT 'no',
    final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')) DEFAULT 'no',
    final_other TEXT CHECK(final_other IN ('yes', 'no')) DEFAULT 'no',

    -- FLEXIBLE SYSTEM: Hierarchical JSON arrays
    target TEXT,   -- Hierarchical tag array as JSON e.g., ["David", "king", "person"]
    vehicle TEXT,  -- Hierarchical tag array as JSON e.g., ["lion", "predatory animal", "living creature"]
    ground TEXT,   -- Hierarchical tag array as JSON e.g., ["strength", "physical quality", "attribute"]
    posture TEXT,  -- Hierarchical tag array as JSON e.g., ["celebration", "praise", "positive sentiment"]

    -- ORIGINAL SYSTEM: Categorical fields (preserved for compatibility)
    target_level_1 TEXT,       -- e.g., "God", "Social Group", "Natural world"
    target_specific TEXT,      -- e.g., "David", "Israelites", "mountain"
    vehicle_level_1 TEXT,      -- e.g., "natural world", "human parts", "divine"
    vehicle_specific TEXT,     -- e.g., "lion", "heart", "shepherd"
    ground_level_1 TEXT,       -- e.g., "moral quality", "physical quality", "status"
    ground_specific TEXT,      -- e.g., "strength", "courage", "leadership"

    -- Core metadata
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    figurative_text_in_hebrew_stripped TEXT,
    explanation TEXT,
    speaker TEXT,
    purpose TEXT,
    original_detection_types TEXT,   -- Comma-separated list of originally detected types

    -- Split deliberation system (token-efficient)
    tagging_analysis_deliberation TEXT,  -- LLM reasoning about hierarchical tag selection

    -- Validation audit trail (per type)
    validation_decision_simile TEXT CHECK(validation_decision_simile IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_metaphor TEXT CHECK(validation_decision_metaphor IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_personification TEXT CHECK(validation_decision_personification IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_idiom TEXT CHECK(validation_decision_idiom IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_hyperbole TEXT CHECK(validation_decision_hyperbole IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_metonymy TEXT CHECK(validation_decision_metonymy IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_decision_other TEXT CHECK(validation_decision_other IN ('VALID', 'INVALID', 'RECLASSIFIED', NULL)),
    validation_reason_simile TEXT,
    validation_reason_metaphor TEXT,
    validation_reason_personification TEXT,
    validation_reason_idiom TEXT,
    validation_reason_hyperbole TEXT,
    validation_reason_metonymy TEXT,
    validation_reason_other TEXT,
    validation_response TEXT,        -- Full validator response
    validation_error TEXT,           -- Any validation errors
    model_used TEXT DEFAULT 'gemini-2.5-flash',  -- Track which AI model processed this instance
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (verse_id) REFERENCES verses (id)
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Verses indexes
CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses (reference);
CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses (book, chapter);
CREATE INDEX IF NOT EXISTS idx_verses_llm_restriction ON verses (llm_restriction_error);

-- Figurative language indexes (all types)
CREATE INDEX IF NOT EXISTS idx_figurative_language ON figurative_language (figurative_language);
CREATE INDEX IF NOT EXISTS idx_figurative_simile ON figurative_language (simile);
CREATE INDEX IF NOT EXISTS idx_figurative_metaphor ON figurative_language (metaphor);
CREATE INDEX IF NOT EXISTS idx_figurative_personification ON figurative_language (personification);
CREATE INDEX IF NOT EXISTS idx_figurative_idiom ON figurative_language (idiom);
CREATE INDEX IF NOT EXISTS idx_figurative_hyperbole ON figurative_language (hyperbole);
CREATE INDEX IF NOT EXISTS idx_figurative_metonymy ON figurative_language (metonymy);
CREATE INDEX IF NOT EXISTS idx_figurative_other ON figurative_language (other);

-- Final validated types indexes
CREATE INDEX IF NOT EXISTS idx_final_figurative_language ON figurative_language (final_figurative_language);
CREATE INDEX IF NOT EXISTS idx_final_simile ON figurative_language (final_simile);
CREATE INDEX IF NOT EXISTS idx_final_metaphor ON figurative_language (final_metaphor);
CREATE INDEX IF NOT EXISTS idx_final_personification ON figurative_language (final_personification);
CREATE INDEX IF NOT EXISTS idx_final_idiom ON figurative_language (final_idiom);
CREATE INDEX IF NOT EXISTS idx_final_hyperbole ON figurative_language (final_hyperbole);
CREATE INDEX IF NOT EXISTS idx_final_metonymy ON figurative_language (final_metonymy);
CREATE INDEX IF NOT EXISTS idx_final_other ON figurative_language (final_other);

-- Metadata indexes
CREATE INDEX IF NOT EXISTS idx_figurative_confidence ON figurative_language (confidence);
CREATE INDEX IF NOT EXISTS idx_figurative_speaker ON figurative_language (speaker);
CREATE INDEX IF NOT EXISTS idx_figurative_purpose ON figurative_language (purpose);
CREATE INDEX IF NOT EXISTS idx_figurative_original_detection_types ON figurative_language (original_detection_types);

-- =============================================================================
-- UTILITY VIEWS
-- =============================================================================

-- Complete verse analysis view (includes ALL verses, both with and without figurative language)
CREATE VIEW IF NOT EXISTS v_complete_verse_analysis AS
SELECT
    v.id as verse_id,
    v.reference,
    v.book,
    v.chapter,
    v.verse,
    v.hebrew_text,
    v.english_text,
    v.word_count,
    v.figurative_detection_deliberation,  -- Available for ALL verses
    v.instances_detected,
    CASE WHEN fl.id IS NOT NULL THEN 'yes' ELSE 'no' END as has_figurative_language,
    fl.id as figurative_instance_id,
    fl.final_figurative_language,
    fl.final_simile,
    fl.final_metaphor,
    fl.final_personification,
    fl.final_idiom,
    fl.final_hyperbole,
    fl.final_metonymy,
    fl.final_other,
    fl.confidence,
    fl.figurative_text,
    fl.explanation,
    fl.target,  -- JSON array
    fl.vehicle, -- JSON array
    fl.ground,  -- JSON array
    fl.posture, -- JSON array
    fl.tagging_analysis_deliberation
FROM verses v
LEFT JOIN figurative_language fl ON v.id = fl.verse_id
ORDER BY v.book, v.chapter, v.verse;

-- Figurative language statistics view
CREATE VIEW IF NOT EXISTS v_figurative_statistics AS
SELECT
    book,
    COUNT(*) as total_verses,
    SUM(CASE WHEN instances_detected > 0 THEN 1 ELSE 0 END) as verses_with_figurative,
    SUM(instances_detected) as total_instances,
    ROUND(AVG(CASE WHEN instances_detected > 0 THEN instances_detected ELSE NULL END), 2) as avg_instances_per_figurative_verse,
    ROUND((SUM(CASE WHEN instances_detected > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*)), 2) as figurative_verse_percentage
FROM verses
GROUP BY book
ORDER BY figurative_verse_percentage DESC;