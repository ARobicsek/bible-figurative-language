# Database Migration Plan: From Categorical to Tag-Based System

## MIGRATION OVERVIEW

**Objective:** Transform rigid single-category system to flexible tag-based approach while maintaining 100% backward compatibility and data integrity.

**Migration Type:** Additive Enhancement (no data loss, no breaking changes)

**Expected Duration:** 2-4 hours for complete corpus migration

---

## PRE-MIGRATION CHECKLIST

### 1. Backup Strategy
- [ ] Create full database backup before any schema changes
- [ ] Test backup restoration procedure
- [ ] Document rollback process

### 2. Environment Preparation
- [ ] Verify Python database libraries are available
- [ ] Test database connections to all target databases
- [ ] Ensure sufficient disk space (estimate 15-20% increase)

### 3. Validation Preparation
- [ ] Create test database with sample data
- [ ] Run migration on test database first
- [ ] Validate test results before production migration

---

## MIGRATION PHASES

## PHASE 1: SCHEMA ENHANCEMENT (Backward Compatible)

### 1.1 Add New Tables
```sql
-- Execute schema_v2.sql to add:
-- - tag_categories table
-- - tags table
-- - figurative_tags table (many-to-many)
-- - Enhanced indexes
-- - Views for querying
```

### 1.2 Add New Columns to Existing Tables
```sql
-- Add primary category columns to figurative_language table
ALTER TABLE figurative_language ADD COLUMN primary_target_category TEXT;
ALTER TABLE figurative_language ADD COLUMN primary_vehicle_category TEXT;
ALTER TABLE figurative_language ADD COLUMN primary_ground_category TEXT;
```

### 1.3 Populate Tag Taxonomy
```sql
-- Execute initial_tag_taxonomy.sql to populate:
-- - Tag categories for target/vehicle/ground dimensions
-- - Initial tag vocabulary based on existing data analysis
```

**Validation:**
- [ ] All new tables created successfully
- [ ] Existing data remains intact and accessible
- [ ] Original queries still function normally

---

## PHASE 2: DATA MAPPING AND MIGRATION

### 2.1 Categorical to Tag Mapping

**Target Dimension Mapping:**
```
Current target_level_1 → New tag system:
- "God" → tags: ["god", "deity", "divine_being"]
- "natural world" → tags: ["natural_world", "created_things", "celestial_body"]
- "state of being" → tags: ["state_of_being", "relational_condition"]
- "human parts" → tags: ["human_parts", "physical_being"]
```

**Vehicle Dimension Mapping:**
```
Current vehicle_level_1 → New tag system:
- "natural world" → tags: ["natural_element", "natural_phenomenon"]
- "human action" → tags: ["human_action", "governance_rule"]
- "human parts" → tags: ["human_parts", "flesh_body"]
- "animal" → tags: ["animal", "bird", "creature"]
```

**Ground Dimension Mapping:**
```
Current ground_level_1 → New tag system:
- "essential nature or identity" → tags: ["essential_nature", "fundamental_character"]
- "physical quality" → tags: ["physical_quality", "spatial_relationship"]
- "status" → tags: ["status_position", "authority_hierarchy"]
```

### 2.2 Migration SQL Scripts

#### Script 1: Populate Primary Categories
```sql
-- Map existing categorical data to primary categories
UPDATE figurative_language
SET primary_target_category =
    CASE target_level_1
        WHEN 'God' THEN 'deity'
        WHEN 'natural world' THEN 'natural_world'
        WHEN 'state of being' THEN 'state_of_being'
        WHEN 'human parts' THEN 'human_parts'
        ELSE 'abstract_concept'
    END
WHERE target_level_1 IS NOT NULL;
```

#### Script 2: Create Tag Assignments
```sql
-- For each figurative language instance, create appropriate tag assignments
-- This will be done via Python script with sophisticated mapping logic
```

### 2.3 Enhanced Tag Assignment Process

**Multi-Tag Assignment Logic:**
- Analyze `target_specific` for additional entity-specific tags
- Analyze `explanation` text for contextual tags
- Apply domain knowledge rules for comprehensive tagging

**Example Enhanced Assignment:**
```
Original: target_level_1="God", target_specific="The Spirit of God"
New Tags: ["god", "spirit_of_god", "divine_presence", "divine_breath"]

Original: vehicle_level_1="natural world", vehicle_specific="A bird hovering/brooding"
New Tags: ["animal", "bird", "eagle", "hovering_brooding", "protective_creature"]
```

---

## PHASE 3: VALIDATION AND QUALITY ASSURANCE

### 3.1 Data Integrity Validation
```sql
-- Verify no data loss
SELECT
    COUNT(*) as original_count,
    (SELECT COUNT(*) FROM figurative_language WHERE primary_target_category IS NOT NULL) as migrated_count,
    (SELECT COUNT(DISTINCT figurative_language_id) FROM figurative_tags) as tagged_count
FROM figurative_language;
```

### 3.2 Tag Coverage Analysis
```sql
-- Analyze tag distribution
SELECT
    dimension,
    COUNT(DISTINCT tag_id) as unique_tags_used,
    COUNT(*) as total_assignments,
    AVG(confidence) as avg_confidence
FROM figurative_tags
GROUP BY dimension;
```

### 3.3 Quality Metrics Validation
- [ ] **Coverage:** Every instance has primary categories AND tag assignments
- [ ] **Consistency:** Tag assignments align with original categorical data
- [ ] **Richness:** Average 5-8 tags per dimension per instance
- [ ] **Accuracy:** Manual spot-check of 50 random instances

---

## PHASE 4: SEARCH FUNCTIONALITY ENHANCEMENT

### 4.1 Tag-Based Query Functions
```python
def search_by_tags(target_tags=[], vehicle_tags=[], ground_tags=[], operator='AND'):
    """
    Search figurative language instances by tag combinations

    Args:
        target_tags: List of target dimension tags
        vehicle_tags: List of vehicle dimension tags
        ground_tags: List of ground dimension tags
        operator: 'AND' or 'OR' logic for tag matching

    Returns:
        List of matching figurative language instances with full tag data
    """
```

### 4.2 Backwards Compatibility Layer
```python
def search_by_legacy_categories(target_level_1=None, vehicle_level_1=None, ground_level_1=None):
    """
    Maintain compatibility with existing categorical searches
    Internally converts to tag-based queries
    """
```

---

## ROLLBACK PROCEDURES

### Emergency Rollback (if migration fails)
```sql
-- 1. Restore from backup
-- 2. Drop new tables if they exist
DROP TABLE IF EXISTS figurative_tags;
DROP TABLE IF EXISTS tags;
DROP TABLE IF EXISTS tag_categories;

-- 3. Remove added columns
ALTER TABLE figurative_language DROP COLUMN primary_target_category;
ALTER TABLE figurative_language DROP COLUMN primary_vehicle_category;
ALTER TABLE figurative_language DROP COLUMN primary_ground_category;
```

### Selective Rollback (if tag data issues found)
```sql
-- Keep schema but clear tag data for re-migration
DELETE FROM figurative_tags;
UPDATE figurative_language SET
    primary_target_category = NULL,
    primary_vehicle_category = NULL,
    primary_ground_category = NULL;
```

---

## SUCCESS CRITERIA

### Quantitative Validation
- [ ] **100% Data Preservation:** All original data intact and accessible
- [ ] **95%+ Tag Coverage:** Every instance has comprehensive tag assignments
- [ ] **5-8 Tags Average:** Rich multi-dimensional tagging achieved
- [ ] **Query Performance:** Tag-based searches perform within 2x of categorical searches

### Qualitative Validation
- [ ] **Search Enhancement:** Complex queries now possible (e.g., "deity + animal imagery + protective relationship")
- [ ] **Pattern Discovery:** New semantic relationships become visible
- [ ] **Research Value:** Scholars can conduct more sophisticated analysis
- [ ] **Backwards Compatibility:** All existing code continues to function

---

## POST-MIGRATION TASKS

### 1. Documentation Updates
- [ ] Update README.md with tag-based search examples
- [ ] Create user guide for new tag-based functionality
- [ ] Document tag taxonomy and expansion procedures

### 2. System Enhancements
- [ ] Update LLM prompts to generate tags directly
- [ ] Enhance validation system for tag accuracy
- [ ] Create tag management tools for taxonomy expansion

### 3. Research Applications
- [ ] Conduct pattern analysis using new tag system
- [ ] Compare research outcomes vs. categorical system
- [ ] Publish methodology for biblical figurative language analysis

---

## RISK MITIGATION

### High-Risk Scenarios
1. **Data Corruption During Migration**
   - Mitigation: Comprehensive backups, test environment validation

2. **Performance Degradation**
   - Mitigation: Optimized indexes, query performance testing

3. **Tag Assignment Inconsistency**
   - Mitigation: Extensive validation, manual spot-checking

4. **Search Complexity Overwhelming Users**
   - Mitigation: Maintain simple search interface, progressive disclosure

### Monitoring and Alerts
- [ ] Database size monitoring during migration
- [ ] Query performance benchmarks
- [ ] Tag assignment quality metrics
- [ ] User adoption tracking

---

This migration plan ensures a smooth transition to the revolutionary tag-based system while maintaining complete backward compatibility and data integrity.