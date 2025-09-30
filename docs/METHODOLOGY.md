# AI Analysis Methodology

**How the Hebrew Figurative Language Database Was Created**

This document explains the AI analysis pipeline used to identify and classify figurative language in the Torah (Genesis through Deuteronomy).

---

## Table of Contents

1. [Overview](#overview)
2. [AI Model Strategy](#ai-model-strategy)
3. [Two-Stage Analysis Process](#two-stage-analysis-process)
4. [Classification Framework](#classification-framework)
5. [Quality Assurance](#quality-assurance)
6. [Transparency and Reproducibility](#transparency-and-reproducibility)
7. [Limitations and Known Issues](#limitations-and-known-issues)

---

## Overview

The database contains **5,846 verses** from the Torah, analyzed using advanced AI language models to identify and classify figurative language. The analysis identified **3,020 figurative language instances** across **2,307 verses** (39.5% of the corpus).

**Goals of this methodology:**
- Systematic identification of figurative language across the entire Torah
- Consistent classification using established linguistic categories
- Transparent AI reasoning with full audit trails
- Validation and quality assurance to minimize false positives

---

## AI Model Strategy

The analysis uses a **three-tier fallback strategy** to handle different levels of complexity:

### Primary Model: Gemini 2.5 Flash
- **Used for:** ~95% of all verses
- **Strengths:** Fast processing, excellent with straightforward cases
- **Both stages:** Handles both initial detection AND validation

### Fallback Model: Gemini 2.5 Pro
- **Used for:** Complex passages and token limit overruns
- **Strengths:** Better handling of nuanced theological language
- **Triggered when:** Flash encounters difficulty or exceeds capacity

### Final Fallback: Claude Sonnet 4
- **Used for:** Extremely complex passages
- **Strengths:** Superior reasoning for intricate multi-layered passages
- **Triggered when:** Both Gemini models are unable to process

**Model attribution:** Every verse in the database includes the `model_used` field, tracking which AI performed the analysis.

---

## Two-Stage Analysis Process

Each verse goes through **two independent AI analysis stages** to ensure accuracy:

### Stage 1: Detection
**Purpose:** Identify potential figurative language

The AI reads each verse and:
1. Determines if figurative language is present
2. Identifies the type(s) (metaphor, simile, idiom, etc.)
3. Extracts the figurative phrase in Hebrew and English
4. Explains the figurative meaning
5. Assigns confidence score (0.0-1.0)
6. Records complete reasoning in `figurative_detection_deliberation`

**Output:** Initial classifications with full reasoning

### Stage 2: Validation
**Purpose:** Verify and refine initial detections

The **same AI model** re-analyzes its own detection:
1. Reviews the initial classification
2. Confirms or reclassifies each figurative type
3. Validates the metadata (Target/Vehicle/Ground/Posture)
4. Documents validation reasoning for each type
5. Can reject false positives

**Output:** Final validated classifications with validation reasoning

**Why the same model?** Using the same model for validation ensures consistency in reasoning style while allowing the AI to catch its own errors with fresh analysis.

---

## Classification Framework

The analysis uses a **dual classification system**:

### 1. Figurative Type Classification

Seven standard categories of figurative language:

| Type | Description | Example |
|------|-------------|---------|
| **Metaphor** | Direct comparison without "like" or "as" | "Judah is a lion" |
| **Simile** | Comparison using "like" or "as" | "swift as an eagle" |
| **Personification** | Human qualities given to non-human entities | "the land vomited them out" |
| **Idiom** | Fixed expression with non-literal meaning | "to harden one's heart" |
| **Hyperbole** | Deliberate exaggeration | "every living thing died" |
| **Metonymy** | Substitution of associated concept | "the sword" (meaning war) |
| **Other** | Figurative language not fitting above categories | Rare edge cases |

**Multi-type classification:** A single phrase can be classified as multiple types simultaneously. For example, "God hardened Pharaoh's heart" is both a **metaphor** (heart = will) and an **idiom** (fixed expression).

### 2. Hierarchical Metadata Classification

Each figurative instance includes four metadata dimensions stored as **hierarchical JSON arrays** (specific → general):

#### TARGET
**What/who** the figurative language is about (the subject being described)

**Structure:** `[specific entity, category, broader category, ...]`

**Example:** `["Moses", "prophet", "religious leader", "person", "human being"]`

#### VEHICLE
**What** the target is being compared to or likened to

**Structure:** `[specific image, category, broader category, ...]`

**Example:** `["shepherd", "occupation", "caretaker", "person"]`

#### GROUND
**What quality** is being described (the shared characteristic between target and vehicle)

**Structure:** `[specific quality, quality type, broader quality, ...]`

**Example:** `["guidance", "leadership quality", "interpersonal quality"]`

#### POSTURE
**Speaker's attitude** or stance toward the subject

**Structure:** `[specific stance, emotional category, ...]`

**Example:** `["reassurance", "comfort", "positive sentiment"]`

**Why hierarchical?** The specific-to-general structure enables both precise and broad searches. Users can search for "David" specifically OR "kings" generally OR "people" broadly.

---

## Quality Assurance

### Three-Tier Validation Architecture

1. **Detection Stage**: Initial AI identification with confidence scoring
2. **Validation Stage**: Same model reviews and validates/corrects classifications
3. **Human Review**: Database includes interface for community feedback (see CONTRIBUTING.md)

### Confidence Scoring

Each instance includes a confidence score (0.0-1.0):
- **0.8-1.0**: High confidence, clear figurative language
- **0.6-0.8**: Medium confidence, may have alternative interpretations
- **0.0-0.6**: Low confidence, borderline cases or uncertain

**Note:** Low confidence instances are still included to ensure completeness. Users can filter by confidence level.

### Validation Reasoning

Every classification includes:
- `validation_reason_metaphor`: Why validated/rejected as metaphor
- `validation_reason_simile`: Why validated/rejected as simile
- *(and similarly for all other types)*

This creates a **complete audit trail** showing both detection and validation reasoning.

### Handling Reclassifications

During validation, the AI may:
- **Confirm** the original classification
- **Reclassify** to a different figurative type
- **Add** additional types not initially detected
- **Reject** as false positive (non-figurative)

All changes are documented in the validation reasoning fields.

---

## Transparency and Reproducibility

### Complete Deliberation Records

Every verse includes:
- **Detection deliberation**: Full AI reasoning from initial analysis
- **Validation reasoning**: Detailed explanation for each type classification
- **Model attribution**: Which AI model performed the analysis
- **Confidence scores**: Quantified assessment of reliability

**Users can view complete AI reasoning** for any classification directly in the interface.

### Source Text Attribution

All Hebrew and English texts are sourced from **Sefaria.org**, an open-source repository of Jewish texts. This ensures:
- Reproducible source material
- Community-vetted translations
- Consistent text versioning

### Limitations of Reproducibility

**Important:** While the database provides complete transparency, **exact reproducibility is not guaranteed** because:
- AI models are updated over time
- Prompts and parameters may have evolved during analysis
- Random factors in AI generation affect outputs

**The database preserves the complete analysis for reference**, but re-running the analysis today might produce different results.

---

## Limitations and Known Issues

### 1. AI Interpretation vs. Scholarly Consensus

**This database represents AI interpretation, not definitive scholarly consensus.**

- AI classifications may differ from traditional commentaries
- Multiple valid interpretations may exist for the same verse
- Cultural and historical context may be incompletely captured

**Recommendation:** Validate critical findings with traditional scholarly sources.

### 2. Translation Challenges

- English figurative language may not perfectly mirror Hebrew
- Some Hebrew idioms have no direct English equivalent
- Cultural context may be lost in translation

**The database includes both Hebrew and English** to enable cross-language verification.

### 3. Theological Sensitivity

- Figurative language involving divine names requires careful handling
- Non-sacred text option (abbreviations for divine names) is provided but should be reviewed by qualified authorities for ritual use
- Interpretations may have theological implications

**Recommendation:** Respect cultural and religious sensitivities when using this tool.

### 4. Multi-Type Classification Complexity

- A phrase can be multiple types simultaneously (e.g., metaphor + idiom)
- Type boundaries are sometimes fuzzy
- Different scholarly traditions may classify differently

**The database preserves the AI's multi-type classifications** to reflect this complexity.

### 5. Coverage Limitations

- **Current scope:** Torah only (Genesis through Deuteronomy)
- **Not included:** Prophets, Writings, Aramaic portions
- **Poetry vs. prose:** Different genres may have different figurative density

**Future expansion** to other biblical books is planned (see README.md roadmap).

### 6. Confidence Score Interpretation

- Scores are AI self-assessment, not external validation
- Low confidence instances may still be valid
- High confidence doesn't guarantee correctness

**Use confidence as one factor** among multiple validation criteria.

### 7. Metadata Consistency

- Target/Vehicle/Ground/Posture classifications follow AI interpretation
- Hierarchical specificity may vary between instances
- Some instances may have incomplete metadata

**Metadata search is best-effort** and should be verified.

---

## Research Integrity

### Appropriate Use Cases

✅ **Recommended:**
- Exploratory research and hypothesis generation
- Teaching figurative language concepts with real examples
- Comparative analysis of figurative patterns across books
- Supplementary evidence alongside traditional scholarship

❌ **Not Recommended:**
- Sole source for critical scholarly publications without verification
- Definitive theological claims without rabbinic consultation
- Ritual or liturgical use without qualified review

### Citation Requirements

**If you use this database in research or publications**, please:
1. Cite the database (see README.md for BibTeX)
2. Note that classifications are AI-generated
3. Validate critical findings with traditional sources
4. Acknowledge limitations in your methodology section

---

## Future Improvements

We are committed to ongoing quality improvements:

### Planned Enhancements
- Community validation interface for expert feedback
- Statistical analysis of inter-annotator agreement
- Integration with traditional commentaries
- Expansion to other biblical books
- Enhanced metadata consistency

### How to Contribute

**Report classification issues:**
- Use GitHub issue template: "Classification Feedback"
- Provide verse reference and specific concern
- Suggest alternative interpretation

**See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.**

---

## Conclusion

This database represents a **systematic AI-driven analysis** of figurative language in the Torah, with emphasis on:
- Transparency (complete AI reasoning)
- Validation (two-stage process)
- Reproducibility (full source attribution)
- Accessibility (open data, open source)

**While AI analysis provides valuable insights**, it should be used as a research tool to complement, not replace, traditional scholarship and human expertise.

---

## Related Documentation

- [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md) - Technical database structure
- [FEATURES.md](FEATURES.md) - How to use the interface
- [FAQ.md](FAQ.md) - Common questions about the analysis
- [CONTRIBUTING.md](../CONTRIBUTING.md) - How to report issues or contribute

---

## Questions or Feedback?

Open an issue on [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues) with the "question" label.
