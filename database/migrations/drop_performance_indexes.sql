-- Rollback Script for Performance Indexes
-- Removes all indexes created by add_performance_indexes.sql
-- Created: 2025-09-30
--
-- Use this if indexes cause unexpected issues (unlikely)
-- Safe to run: Uses IF EXISTS to prevent errors

-- =============================================================================
-- DROP METADATA SEARCH INDEXES
-- =============================================================================

DROP INDEX IF EXISTS idx_fl_target;
DROP INDEX IF EXISTS idx_fl_vehicle;
DROP INDEX IF EXISTS idx_fl_ground;
DROP INDEX IF EXISTS idx_fl_posture;

-- =============================================================================
-- DROP JOIN OPTIMIZATION INDEXES
-- =============================================================================

DROP INDEX IF EXISTS idx_fl_verse_id;

-- =============================================================================
-- DROP BOOK/CHAPTER FILTER INDEXES
-- =============================================================================

DROP INDEX IF EXISTS idx_verses_book;
DROP INDEX IF EXISTS idx_verses_book_chapter;

-- =============================================================================
-- DROP FIGURATIVE TYPE FILTER INDEXES
-- =============================================================================

DROP INDEX IF EXISTS idx_fl_final_figurative;
DROP INDEX IF EXISTS idx_fl_final_metaphor;
DROP INDEX IF EXISTS idx_fl_final_simile;
DROP INDEX IF EXISTS idx_fl_final_personification;
DROP INDEX IF EXISTS idx_fl_final_idiom;
DROP INDEX IF EXISTS idx_fl_final_hyperbole;
DROP INDEX IF EXISTS idx_fl_final_metonymy;
DROP INDEX IF EXISTS idx_fl_final_other;

-- =============================================================================
-- VERIFICATION
-- =============================================================================

-- Verify indexes were dropped
-- SELECT name FROM sqlite_master WHERE type='index' AND tbl_name IN ('figurative_language', 'verses');
