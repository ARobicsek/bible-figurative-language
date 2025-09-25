# LLM Deliberation Fields: Separation of Concerns

## OVERVIEW

The system now separates LLM reasoning into distinct analytical phases, each serving different purposes and stored in separate fields for clarity and targeted analysis.

## FIELD SEPARATION

### 1. **`llm_detection_deliberation`** (Verse-level)
**Location**: `verses` table
**Purpose**: Reasoning about WHETHER the verse contains figurative language
**Timing**: During initial figurative language detection phase

**Content Examples**:
```
"The phrase 'God's hand' could be literal (referring to divine anthropomorphism) or figurative (representing God's power). Given the context of salvation and the anthropomorphic language throughout Deuteronomy, this appears to be figurative language using human anatomy to describe divine action."

"While 'the heavens and earth' might seem like figurative language, in this creation context it appears to be literal description of the cosmic domains being created. No clear metaphorical vehicle is present."

"The phrase 'like an eagle' contains the explicit comparison marker 'like' and compares divine care to animal behavior, clearly indicating simile/figurative language."
```

### 2. **`tagging_deliberation`** (Instance-level)
**Location**: `figurative_language` table
**Purpose**: Reasoning about HOW to analyze and tag the figurative language
**Timing**: During classification and tagging phase (after figurative language is confirmed)

**Content Examples**:
```
"Target: 'Israel' as covenant people, not just ethnic group - tagging as ['israel', 'covenant_people', 'nation']. Vehicle: 'Eagle' imagery emphasizes protective care and elevated perspective - tagging as ['eagle', 'bird_of_prey', 'protective_creature', 'aerial_animal']. Ground: The comparison highlights God's protective care and superior vantage point, with speaker expressing reverent appreciation - tagging as ['protective_care', 'superior_perspective', 'divine_nurturing', 'reverence_awe']."

"Speaker posture assessment: Moses is expressing frustrated exasperation with Israel's complaints, evident in the rhetorical question format and the burden imagery. This is corrective but not condemning - tagging as 'exasperation_frustration' rather than 'condemnation_judgment'."

"Vehicle hierarchy consideration: 'wolf' is specific predator, but also need broader discoverability tags - including ['wolf', 'predator', 'wild_animal', 'animal', 'fierce_creature'] for multi-level search capability."
```

### 3. **Legacy `llm_deliberation`** (Verse-level)
**Location**: `verses` table
**Status**: Preserved for backward compatibility
**Migration**: Existing data remains; new processing uses separated fields

## ANALYTICAL BENEFITS

### **Detection Deliberation Analysis**
```sql
-- Analyze detection confidence patterns
SELECT
    CASE
        WHEN llm_detection_deliberation LIKE '%clearly%' THEN 'High Confidence'
        WHEN llm_detection_deliberation LIKE '%appears%' OR llm_detection_deliberation LIKE '%seems%' THEN 'Medium Confidence'
        WHEN llm_detection_deliberation LIKE '%might%' OR llm_detection_deliberation LIKE '%could%' THEN 'Low Confidence'
    END as confidence_level,
    COUNT(*) as instances
FROM verses
WHERE llm_detection_deliberation IS NOT NULL
GROUP BY confidence_level;
```

### **Classification Deliberation Analysis**
```sql
-- Analyze tagging reasoning patterns
SELECT
    speaker_posture_primary,
    COUNT(*) as instances,
    AVG(LENGTH(tagging_deliberation)) as avg_deliberation_length
FROM figurative_language
WHERE tagging_deliberation IS NOT NULL
GROUP BY speaker_posture_primary
ORDER BY instances DESC;
```

### **Quality Assurance Applications**
```sql
-- Find instances with detection uncertainty for manual review
SELECT reference, figurative_text, llm_detection_deliberation
FROM verses v
JOIN figurative_language fl ON v.id = fl.verse_id
WHERE llm_detection_deliberation LIKE '%uncertain%'
   OR llm_detection_deliberation LIKE '%difficult%'
   OR llm_detection_deliberation LIKE '%unclear%';
```

## PROMPT ENGINEERING IMPLICATIONS

### **Detection Phase Prompts**
Focus on:
- Identifying figurative vs literal language
- Recognizing metaphorical vehicles and targets
- Noting linguistic markers (like, as, etc.)
- Considering contextual literalness vs figuration

**Deliberation Request**:
```
"Explain your reasoning about whether this text contains figurative language. Consider:
- Are there clear metaphorical vehicles and targets?
- Are there linguistic comparison markers?
- Does the context suggest literal vs figurative interpretation?
- What makes this figurative rather than descriptive?"
```

### **Classification Phase Prompts**
Focus on:
- Target/vehicle/ground analysis
- Speaker posture assessment
- Hierarchical tagging decisions
- Tag selection rationale

**Deliberation Request**:
```
"Explain your tagging decisions:
- Why did you identify these specific target/vehicle/ground tags?
- What evidence supports your speaker posture assessment?
- How did you balance specificity vs discoverability in tag selection?
- What alternative interpretations did you consider?"
```

## RESEARCH APPLICATIONS

### **Detection Accuracy Studies**
Compare detection deliberations against validation results to identify:
- Common detection errors
- Linguistic patterns that cause uncertainty
- Context types that challenge figurative identification

### **Classification Consistency Analysis**
Analyze tagging deliberations to:
- Ensure consistent tagging logic across similar instances
- Identify cases where alternative tag sets might be valid
- Refine tagging guidelines based on LLM reasoning patterns

### **Methodological Transparency**
Enable researchers to:
- Understand the basis for figurative language identification
- Assess the reasoning behind specific tag assignments
- Replicate or challenge analytical decisions
- Improve prompt engineering based on deliberation quality

## MIGRATION STRATEGY

### **Backward Compatibility**
- Existing `llm_deliberation` data preserved
- New processing populates separated fields
- Old queries continue to function

### **Gradual Enhancement**
- New analyses use separated deliberation fields
- Existing data can be retrospectively processed to populate new fields
- Enhanced analytical capabilities become available progressively

This separation enables more targeted analysis, better quality assurance, and clearer understanding of the two-phase analytical process.