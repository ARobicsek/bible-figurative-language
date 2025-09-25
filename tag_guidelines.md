# Biblical Figurative Language Tagging Guidelines

## OVERVIEW

This document provides comprehensive guidelines for tagging biblical figurative language using the multi-dimensional tag-based system. The system replaces rigid single-category classification with flexible, multi-tag approaches that capture the rich complexity of biblical metaphors, similes, and other figurative language.

**Source Analysis:** Based on 1,958 figurative language instances from Genesis (1,008) and Deuteronomy (950)

---

## CORE PRINCIPLES

### 1. Multi-Dimensional Tagging
- **Target Dimension**: What is being described figuratively (the subject)
- **Vehicle Dimension**: What imagery is used to describe it (the source domain)
- **Ground Dimension**: The basis of comparison (shared qualities/relationships)

### 2. Multiple Tags Per Dimension
- Each dimension should typically have 2-6 tags per instance
- Tags capture different aspects of the same figurative element
- Avoid redundancy while ensuring comprehensive coverage

### 3. Primary + Secondary Structure
- One primary tag per dimension (backward compatibility)
- Multiple secondary tags for comprehensive analysis
- Primary tags map to original categorical system

---

## DIMENSION-SPECIFIC GUIDELINES

## TARGET DIMENSION TAGGING

**What to Tag**: The subject being described figuratively - who or what receives the figurative description.

### Divine Targets
```
Example: "The Spirit of God hovering over the waters"
Tags: ["god", "divine_presence", "spirit_of_god"]
- god: Primary divine reference
- divine_presence: God's manifesting presence
- spirit_of_god: Specific divine aspect
```

**Key Patterns:**
- **Divine Power**: Use both `god` + `divine_power` when emphasizing God's active intervention
- **Divine Anger**: Tag as `god` + `divine_anger` for wrath passages
- **Multiple Aspects**: Divine actions can have multiple valid tags

### Human Individual Targets
```
Example: "Jacob wrestling with the angel"
Tags: ["patriarch", "specific_person"]
- patriarch: Jacob's role in salvation history
- specific_person: Individual identity
```

**Frequency Patterns from Analysis:**
- `specific_person`: 156 instances (Genesis), 54 instances (Deuteronomy)
- `patriarch`: High frequency for Abraham, Isaac, Jacob, Joseph
- Tag both role and individual identity when relevant

### Human Collective Targets
```
Example: "Israel as a stubborn people"
Tags: ["israel", "nation", "community"]
- israel: Specific covenant people
- nation: National/ethnic identity
- community: Collective social unit
```

**Critical Distinctions:**
- `israel` vs `nation`: Use `israel` for covenant people, `nation` for general ethnic groups
- `family_clan` vs `community`: Family units vs broader social groups
- `generation` for temporal collective identity

### Action Targets
```
Example: "Sexual intercourse as 'knowing'"
Tags: ["sexual_intercourse", "covenant_action"]
- sexual_intercourse: Specific physical act
- covenant_action: Broader relational significance
```

**High-Frequency Patterns:**
- `sexual_intercourse`: 17 instances (Genesis), 5 instances (Deuteronomy)
- Often combined with relational or covenant tags

### State & Condition Targets
```
Example: "The famine in the land"
Tags: ["famine", "life_condition"]
- famine: Specific condition type
- life_condition: Broader circumstantial category
```

### Natural World Targets
```
Example: "The sun to rule the day"
Tags: ["celestial_body", "created_things", "natural_world"]
- celestial_body: Specific astronomical object
- created_things: Part of divine creation
- natural_world: Broader natural category
```

---

## VEHICLE DIMENSION TAGGING

**What to Tag**: The imagery, source domain, or metaphorical vehicle used to describe the target.

### Human Body Vehicles
```
Example: "The hand of God"
Tags: ["hand", "human_parts"]
- hand: Specific body part
- human_parts: General anatomical category
```

**Frequency Insights:**
- `hand`: 30 instances (Genesis), 224+ instances (Deuteronomy) - most common vehicle
- `face`: 24 instances (Genesis) - often for presence/attention
- `eyes`: 25 instances (Genesis) - for sight/awareness

### Human Action Vehicles
```
Example: "God hovering like a bird"
Tags: ["hovering_brooding", "nurturing_care", "animal_behavior"]
- hovering_brooding: Specific action type
- nurturing_care: Caring behavior category
- animal_behavior: Since it references bird behavior
```

### Animal Vehicles
```
Example: "Like an eagle stirring up its nest"
Tags: ["eagle", "bird", "animal"]
- eagle: Specific bird type
- bird: Bird category
- animal: General creature category
```

**Layered Specificity**: Tag from specific to general for comprehensive coverage.

### Natural World Vehicles
```
Example: "Organized like a host/army"
Tags: ["organized_host", "military_formation"]
- organized_host: Disciplined group imagery
- military_formation: Army-like organization
```

### Abstract Concept Vehicles
```
Example: "Time as a flowing river"
Tags: ["water_flow", "natural_element", "temporal_imagery"]
```

---

## GROUND DIMENSION TAGGING

**What to Tag**: The basis of comparison - what quality or relationship connects target and vehicle.

### Essential Nature Grounds
```
Example: "One flesh" (marriage unity)
Tags: ["holistic_unity", "shared_identity", "essential_nature"]
- holistic_unity: Complete, inseparable oneness
- shared_identity: Common being/identity
- essential_nature: Fundamental character category
```

**High-Value Patterns:**
- `preparatory_nurturing`: For protective, caring relationships
- `holistic_unity`: For complete union concepts
- `fundamental_character`: For core identity aspects

### Physical Quality Grounds
```
Example: "Vast as the host of heaven"
Tags: ["vastness_magnitude", "order_organization"]
- vastness_magnitude: Size/scope similarity
- order_organization: Disciplined arrangement
```

### Status & Authority Grounds
```
Example: "To rule/dominate the day"
Tags: ["primary_authority", "ordering_influence", "dominant_control"]
- primary_authority: Chief position
- ordering_influence: Power to organize
- dominant_control: Governing power
```

**Authority Patterns:**
- `primary_authority`: For chief/primary leadership
- `representative_authority`: For delegated power
- `servant_humility`: For subordinate status

### Relational Quality Grounds
```
Example: "Protective like a mother bird"
Tags: ["protective_care", "parental_care", "nurturing_relationship"]
- protective_care: Protective relationship aspect
- parental_care: Parent-child dynamic
- nurturing_relationship: Caring bond category
```

### Moral & Ethical Grounds
```
Example: "Accountability for actions"
Tags: ["accountability_responsibility", "moral_obligation"]
- accountability_responsibility: Being answerable
- moral_obligation: Ethical duty aspect
```

---

## TAGGING WORKFLOW

### Step 1: Identify the Figurative Instance
- Confirm final_figurative_language = "yes"
- Read figurative_text and explanation carefully
- Consider original categorical assignments

### Step 2: Target Analysis
- What is being described figuratively?
- What role/category does it serve?
- What additional aspects are relevant?
- Assign 2-4 target tags (typically)

### Step 3: Vehicle Analysis
- What imagery/source domain is used?
- What specific elements are highlighted?
- What broader categories apply?
- Assign 2-4 vehicle tags (typically)

### Step 4: Ground Analysis
- Why does this comparison work?
- What qualities are shared?
- What relationship is implied?
- Assign 2-5 ground tags (typically)

### Step 5: Validation
- Do tags capture the full meaning?
- Is there tag redundancy to eliminate?
- Are primary categories assigned?
- Do tags align with explanation text?

---

## COMMON TAGGING SCENARIOS

### Scenario 1: Divine Anthropomorphism
```
Text: "God's anger burned"
Target: ["god", "divine_anger", "divine_attributes"]
Vehicle: ["fire", "natural_element", "destructive_force"]
Ground: ["intense_emotion", "consuming_power", "purifying_judgment"]
```

### Scenario 2: Human Relationships
```
Text: "One flesh" (marriage)
Target: ["marital_union", "covenant_relationship", "state_condition"]
Vehicle: ["flesh_body", "human_parts", "physical_unity"]
Ground: ["holistic_unity", "intimate_connection", "essential_nature"]
```

### Scenario 3: Natural World Imagery
```
Text: "Like stars for number"
Target: ["israel", "nation", "descendants"]
Vehicle: ["celestial_body", "natural_world", "countless_multitude"]
Ground: ["vastness_magnitude", "innumerable_quantity", "visible_prominence"]
```

### Scenario 4: Abstract Concepts
```
Text: "Covenant as binding oath"
Target: ["covenant_concept", "legal_concept", "religious_concept"]
Vehicle: ["rope_cord", "binding_material", "constraining_force"]
Ground: ["permanent_bond", "unbreakable_commitment", "relational_obligation"]
```

---

## VALIDATION RULES

### Tag Naming Standards
- **Format**: lowercase_with_underscores
- **Length**: Maximum 30 characters
- **Descriptive**: Clear, specific meaning
- **No Numbers**: Avoid numeric characters
- **Consistent**: Use established vocabulary

### Tag Assignment Rules
- **Minimum**: 1 tag per dimension
- **Maximum**: 12 tags per dimension
- **Primary Required**: Each dimension must have one primary tag
- **Cross-Category Allowed**: Tags can span multiple categories within a dimension

### Quality Metrics
- **Coverage**: Every instance fully tagged across all three dimensions
- **Consistency**: Similar instances receive similar tag patterns
- **Accuracy**: Tags accurately reflect figurative meaning
- **Completeness**: No significant aspects left untagged

---

## NORMALIZATION GUIDELINES

### Case Handling
- All tags stored in lowercase
- Input normalized to lowercase during processing
- Case-insensitive searching supported

### Duplicate Management
- Merge variant spellings to most frequent form
- Map synonyms to primary tag name
- Handle capitalization variants automatically

### Synonym Mapping
```
Examples:
"divine_power" ← ["godly_power", "divine_strength", "gods_power"]
"celestial_body" ← ["heavenly_body", "astronomical_object", "star_sun_moon"]
"protective_care" ← ["nurturing_protection", "caring_protection", "guardian_care"]
```

### Tag Evolution
- New tags added as needed for novel patterns
- Existing tags refined based on usage analysis
- Taxonomy updated quarterly based on corpus growth
- Maintain backward compatibility with primary categories

---

## ERROR PREVENTION

### Common Mistakes to Avoid

1. **Over-Tagging**: Assigning too many redundant tags
   - ❌ Wrong: ["god", "deity", "divine_being", "divine_presence", "divine_power"] (too redundant)
   - ✅ Right: ["god", "divine_power"] (captures key aspects without redundancy)

2. **Under-Tagging**: Missing important aspects
   - ❌ Wrong: ["israel"] (misses collective and covenant aspects)
   - ✅ Right: ["israel", "covenant_people", "nation"] (comprehensive)

3. **Wrong Dimension**: Placing tags in incorrect dimension
   - ❌ Wrong: Target=["hand"] (hand is typically a vehicle, not target)
   - ✅ Right: Vehicle=["hand"] (correct placement)

4. **Inconsistent Specificity**: Mixing specific and general inconsistently
   - ❌ Wrong: ["eagle", "animal"] + ["bird"] (inconsistent level)
   - ✅ Right: ["eagle", "bird", "animal"] (consistent hierarchy)

### Quality Assurance Checklist
- [ ] All three dimensions tagged
- [ ] Primary category assigned per dimension
- [ ] Tags align with explanation text
- [ ] No redundant tag assignments
- [ ] Appropriate specificity level
- [ ] Consistent with similar instances

---

## RESEARCH APPLICATIONS

### Pattern Discovery Queries
```sql
-- Find instances where divine targets use animal imagery for protective relationships
SELECT * FROM v_figurative_with_tags
WHERE target_tags LIKE '%divine%'
  AND vehicle_tags LIKE '%animal%'
  AND ground_tags LIKE '%protective%';
```

### Comparative Analysis
```sql
-- Compare human body imagery usage between Genesis and Deuteronomy
SELECT book, COUNT(*)
FROM v_figurative_with_tags
WHERE vehicle_tags LIKE '%human_parts%'
GROUP BY book;
```

### Semantic Relationships
```sql
-- Find all instances with covenant-related grounds
SELECT figurative_text, target_tags, vehicle_tags, ground_tags
FROM v_figurative_with_tags
WHERE ground_tags LIKE '%covenant%' OR ground_tags LIKE '%bond%';
```

---

## MAINTENANCE & UPDATES

### Regular Reviews
- **Monthly**: Review new tag usage patterns
- **Quarterly**: Update taxonomy based on corpus analysis
- **Annually**: Comprehensive tag effectiveness review

### Tag Lifecycle Management
- **Creation**: New tags added via controlled process
- **Refinement**: Existing tags clarified/redefined as needed
- **Deprecation**: Rarely-used tags merged with related tags
- **Documentation**: All changes documented with rationale

### Community Feedback
- Tag suggestions from researchers welcome
- Usage patterns inform taxonomy evolution
- Academic review process for major changes

---

This tagging system enables unprecedented analysis of biblical figurative language patterns, supporting both computational analysis and traditional scholarship approaches.