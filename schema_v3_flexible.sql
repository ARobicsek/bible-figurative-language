-- Tag-Based Figurative Language Database Schema v3.0
-- FLEXIBLE RULE-BASED APPROACH
-- Supports dynamic tag generation following structured principles

-- =============================================================================
-- CORE TABLES (Enhanced from v2.0)
-- =============================================================================

-- Enhanced verses table (unchanged structure)
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
    llm_detection_deliberation TEXT,        -- NEW: Reasoning about whether text contains figurative language
    llm_classification_deliberation TEXT,   -- NEW: Reasoning about how to analyze/tag the figurative language
    instances_detected INTEGER,
    instances_recovered INTEGER,
    instances_lost_to_truncation INTEGER,
    truncation_occurred TEXT CHECK(truncation_occurred IN ('yes', 'no')) DEFAULT 'no',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Enhanced figurative language table with hybrid approach
CREATE TABLE IF NOT EXISTS figurative_language (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    verse_id INTEGER NOT NULL,

    -- Original type detection (preserved for compatibility)
    figurative_language TEXT CHECK(figurative_language IN ('yes', 'no')) DEFAULT 'no',
    simile TEXT CHECK(simile IN ('yes', 'no')) DEFAULT 'no',
    metaphor TEXT CHECK(metaphor IN ('yes', 'no')) DEFAULT 'no',
    personification TEXT CHECK(personification IN ('yes', 'no')) DEFAULT 'no',
    idiom TEXT CHECK(idiom IN ('yes', 'no')) DEFAULT 'no',
    hyperbole TEXT CHECK(hyperbole IN ('yes', 'no')) DEFAULT 'no',
    metonymy TEXT CHECK(metonymy IN ('yes', 'no')) DEFAULT 'no',
    other TEXT CHECK(other IN ('yes', 'no')) DEFAULT 'no',

    -- Final validated types (preserved for compatibility)
    final_figurative_language TEXT CHECK(final_figurative_language IN ('yes', 'no')) DEFAULT 'no',
    final_simile TEXT CHECK(final_simile IN ('yes', 'no')) DEFAULT 'no',
    final_metaphor TEXT CHECK(final_metaphor IN ('yes', 'no')) DEFAULT 'no',
    final_personification TEXT CHECK(final_personification IN ('yes', 'no')) DEFAULT 'no',
    final_idiom TEXT CHECK(final_idiom IN ('yes', 'no')) DEFAULT 'no',
    final_hyperbole TEXT CHECK(final_hyperbole IN ('yes', 'no')) DEFAULT 'no',
    final_metonymy TEXT CHECK(final_metonymy IN ('yes', 'no')) DEFAULT 'no',
    final_other TEXT CHECK(final_other IN ('yes', 'no')) DEFAULT 'no',

    -- PRIMARY CATEGORIES (Backward compatibility - single required category per dimension)
    primary_target_category TEXT,        -- Maps from target_level_1
    primary_vehicle_category TEXT,       -- Maps from vehicle_level_1
    primary_ground_category TEXT,        -- Maps from ground_level_1

    -- LEGACY CATEGORIES (Preserved for migration and compatibility)
    target_level_1 TEXT,
    target_specific TEXT,
    vehicle_level_1 TEXT,
    vehicle_specific TEXT,
    ground_level_1 TEXT,
    ground_specific TEXT,

    -- Core instance metadata (unchanged)
    confidence REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    figurative_text_in_hebrew_stripped TEXT,
    explanation TEXT,
    speaker TEXT,
    purpose TEXT,
    original_detection_types TEXT,

    -- NEW: Enhanced analysis fields
    speaker_posture_primary TEXT,        -- Primary speaker attitude/stance
    speaker_posture_secondary TEXT,      -- Secondary speaker attitude if applicable
    posture_confidence REAL CHECK(posture_confidence >= 0.0 AND posture_confidence <= 1.0) DEFAULT 1.0,
    tagging_deliberation TEXT,           -- NEW: LLM reasoning about tag choices and classification decisions

    -- Validation metadata (preserved)
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
    validation_response TEXT,
    validation_error TEXT,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (verse_id) REFERENCES verses (id)
);

-- =============================================================================
-- FLEXIBLE TAG SYSTEM TABLES
-- =============================================================================

-- Dynamic tags table - no predefined categories, just dimension constraints
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,
    dimension TEXT NOT NULL CHECK(dimension IN ('target', 'vehicle', 'ground')),
    description TEXT,
    category_hint TEXT,                  -- Suggested category for organization
    usage_count INTEGER DEFAULT 0,      -- Track frequency
    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active TEXT CHECK(active IN ('yes', 'no')) DEFAULT 'yes',
    created_by TEXT DEFAULT 'system',   -- Track tag origin

    UNIQUE(tag_name, dimension)
);

-- Many-to-many relationship: figurative language instances to tags
CREATE TABLE IF NOT EXISTS figurative_tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    figurative_language_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    dimension TEXT NOT NULL CHECK(dimension IN ('target', 'vehicle', 'ground')),
    confidence REAL CHECK(confidence >= 0.0 AND confidence <= 1.0) DEFAULT 1.0,
    is_primary TEXT CHECK(is_primary IN ('yes', 'no')) DEFAULT 'no',
    is_speaker_posture TEXT CHECK(is_speaker_posture IN ('yes', 'no')) DEFAULT 'no',  -- NEW: marks speaker posture tags
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(figurative_language_id, tag_id, dimension),
    FOREIGN KEY (figurative_language_id) REFERENCES figurative_language (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id)
);

-- Tag relationships (for capturing tag hierarchies and associations)
CREATE TABLE IF NOT EXISTS tag_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_tag_id INTEGER NOT NULL,
    child_tag_id INTEGER NOT NULL,
    relationship_type TEXT CHECK(relationship_type IN ('parent_child', 'synonym', 'related', 'antonym')),
    strength REAL CHECK(strength >= 0.0 AND strength <= 1.0) DEFAULT 1.0,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(parent_tag_id, child_tag_id, relationship_type),
    FOREIGN KEY (parent_tag_id) REFERENCES tags (id),
    FOREIGN KEY (child_tag_id) REFERENCES tags (id)
);

-- =============================================================================
-- PERFORMANCE INDEXES
-- =============================================================================

-- Existing indexes (preserved)
CREATE INDEX IF NOT EXISTS idx_verses_reference ON verses (reference);
CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses (book, chapter);

-- Enhanced figurative language indexes
CREATE INDEX IF NOT EXISTS idx_figurative_language ON figurative_language (figurative_language);
CREATE INDEX IF NOT EXISTS idx_final_figurative_language ON figurative_language (final_figurative_language);
CREATE INDEX IF NOT EXISTS idx_figurative_confidence ON figurative_language (confidence);
CREATE INDEX IF NOT EXISTS idx_primary_target_category ON figurative_language (primary_target_category);
CREATE INDEX IF NOT EXISTS idx_primary_vehicle_category ON figurative_language (primary_vehicle_category);
CREATE INDEX IF NOT EXISTS idx_primary_ground_category ON figurative_language (primary_ground_category);
CREATE INDEX IF NOT EXISTS idx_speaker_posture_primary ON figurative_language (speaker_posture_primary);

-- Flexible tag system indexes
CREATE INDEX IF NOT EXISTS idx_tags_dimension ON tags (dimension);
CREATE INDEX IF NOT EXISTS idx_tags_name_dimension ON tags (tag_name, dimension);
CREATE INDEX IF NOT EXISTS idx_tags_category_hint ON tags (category_hint);
CREATE INDEX IF NOT EXISTS idx_tags_usage_count ON tags (usage_count DESC);
CREATE INDEX IF NOT EXISTS idx_tags_active ON tags (active);

CREATE INDEX IF NOT EXISTS idx_figurative_tags_instance ON figurative_tags (figurative_language_id);
CREATE INDEX IF NOT EXISTS idx_figurative_tags_tag ON figurative_tags (tag_id);
CREATE INDEX IF NOT EXISTS idx_figurative_tags_dimension ON figurative_tags (dimension);
CREATE INDEX IF NOT EXISTS idx_figurative_tags_primary ON figurative_tags (is_primary);
CREATE INDEX IF NOT EXISTS idx_figurative_tags_speaker_posture ON figurative_tags (is_speaker_posture);
CREATE INDEX IF NOT EXISTS idx_figurative_tags_instance_dimension ON figurative_tags (figurative_language_id, dimension);

CREATE INDEX IF NOT EXISTS idx_tag_relationships_parent ON tag_relationships (parent_tag_id);
CREATE INDEX IF NOT EXISTS idx_tag_relationships_child ON tag_relationships (child_tag_id);
CREATE INDEX IF NOT EXISTS idx_tag_relationships_type ON tag_relationships (relationship_type);

-- =============================================================================
-- ENHANCED VIEWS FOR FLEXIBLE QUERYING
-- =============================================================================

-- Complete figurative language view with dynamic tags
CREATE VIEW IF NOT EXISTS v_figurative_with_dynamic_tags AS
SELECT
    fl.id as figurative_id,
    fl.verse_id,
    v.reference,
    v.book,
    v.chapter,
    v.verse,
    fl.figurative_text,
    fl.explanation,
    fl.confidence,
    fl.final_figurative_language,
    fl.speaker_posture_primary,
    fl.speaker_posture_secondary,
    fl.posture_confidence,
    -- Aggregated tags with counts
    (SELECT GROUP_CONCAT(t.tag_name || '(' || ft.confidence || ')', ', ')
     FROM figurative_tags ft
     JOIN tags t ON ft.tag_id = t.id
     WHERE ft.figurative_language_id = fl.id AND ft.dimension = 'target') as target_tags,
    (SELECT GROUP_CONCAT(t.tag_name || '(' || ft.confidence || ')', ', ')
     FROM figurative_tags ft
     JOIN tags t ON ft.tag_id = t.id
     WHERE ft.figurative_language_id = fl.id AND ft.dimension = 'vehicle') as vehicle_tags,
    (SELECT GROUP_CONCAT(t.tag_name || '(' || ft.confidence || ')', ', ')
     FROM figurative_tags ft
     JOIN tags t ON ft.tag_id = t.id
     WHERE ft.figurative_language_id = fl.id AND ft.dimension = 'ground') as ground_tags,
    -- Speaker posture tags specifically
    (SELECT GROUP_CONCAT(t.tag_name, ', ')
     FROM figurative_tags ft
     JOIN tags t ON ft.tag_id = t.id
     WHERE ft.figurative_language_id = fl.id AND ft.is_speaker_posture = 'yes') as speaker_posture_tags
FROM figurative_language fl
JOIN verses v ON fl.verse_id = v.id
WHERE fl.final_figurative_language = 'yes';

-- Dynamic tag usage statistics
CREATE VIEW IF NOT EXISTS v_dynamic_tag_statistics AS
SELECT
    t.id as tag_id,
    t.tag_name,
    t.dimension,
    t.category_hint,
    t.usage_count,
    COUNT(ft.id) as current_assignments,
    AVG(ft.confidence) as avg_confidence,
    COUNT(CASE WHEN ft.is_primary = 'yes' THEN 1 END) as primary_usage_count,
    COUNT(CASE WHEN ft.is_speaker_posture = 'yes' THEN 1 END) as speaker_posture_usage_count,
    t.first_used,
    t.last_used
FROM tags t
LEFT JOIN figurative_tags ft ON t.id = ft.tag_id
GROUP BY t.id, t.tag_name, t.dimension, t.category_hint, t.usage_count, t.first_used, t.last_used;

-- Speaker posture analysis view
CREATE VIEW IF NOT EXISTS v_speaker_posture_analysis AS
SELECT
    v.book,
    fl.speaker_posture_primary,
    COUNT(*) as instances,
    AVG(fl.posture_confidence) as avg_confidence,
    GROUP_CONCAT(DISTINCT t.tag_name) as related_posture_tags
FROM figurative_language fl
JOIN verses v ON fl.verse_id = v.id
LEFT JOIN figurative_tags ft ON fl.id = ft.figurative_language_id AND ft.is_speaker_posture = 'yes'
LEFT JOIN tags t ON ft.tag_id = t.id
WHERE fl.final_figurative_language = 'yes'
GROUP BY v.book, fl.speaker_posture_primary
ORDER BY instances DESC;