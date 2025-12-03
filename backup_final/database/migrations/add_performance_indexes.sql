-- Performance Optimization Migration
-- Adds indexes to speed up metadata searches and complex queries
-- Created: 2025-09-30
--
-- Expected Impact: 10-100x speedup on metadata searches (target/vehicle/ground/posture)
-- Safe to run: Uses IF NOT EXISTS to prevent errors on re-run
-- Reversible: See drop_performance_indexes.sql to rollback

-- =============================================================================
-- METADATA SEARCH INDEXES
-- These dramatically speed up searches on target, vehicle, ground, posture fields
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_fl_target ON figurative_language(target);
CREATE INDEX IF NOT EXISTS idx_fl_vehicle ON figurative_language(vehicle);
CREATE INDEX IF NOT EXISTS idx_fl_ground ON figurative_language(ground);
CREATE INDEX IF NOT EXISTS idx_fl_posture ON figurative_language(posture);

-- =============================================================================
-- JOIN OPTIMIZATION INDEXES
-- Speed up joins between verses and figurative_language tables
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_fl_verse_id ON figurative_language(verse_id);

-- =============================================================================
-- BOOK/CHAPTER FILTER INDEXES
-- Speed up filtering by book and chapter
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_verses_book ON verses(book);
CREATE INDEX IF NOT EXISTS idx_verses_book_chapter ON verses(book, chapter);

-- =============================================================================
-- FIGURATIVE TYPE FILTER INDEXES
-- Speed up filtering by specific figurative language types
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_fl_final_figurative ON figurative_language(final_figurative_language);
CREATE INDEX IF NOT EXISTS idx_fl_final_metaphor ON figurative_language(final_metaphor);
CREATE INDEX IF NOT EXISTS idx_fl_final_simile ON figurative_language(final_simile);
CREATE INDEX IF NOT EXISTS idx_fl_final_personification ON figurative_language(final_personification);
CREATE INDEX IF NOT EXISTS idx_fl_final_idiom ON figurative_language(final_idiom);
CREATE INDEX IF NOT EXISTS idx_fl_final_hyperbole ON figurative_language(final_hyperbole);
CREATE INDEX IF NOT EXISTS idx_fl_final_metonymy ON figurative_language(final_metonymy);
CREATE INDEX IF NOT EXISTS idx_fl_final_other ON figurative_language(final_other);

-- =============================================================================
-- VERIFICATION QUERIES
-- Run these to verify indexes were created successfully
-- =============================================================================

-- List all indexes on figurative_language table
-- SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='figurative_language';

-- List all indexes on verses table
-- SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='verses';

-- Check query plans to verify index usage (example):
-- EXPLAIN QUERY PLAN SELECT * FROM figurative_language WHERE vehicle LIKE '%lion%';
