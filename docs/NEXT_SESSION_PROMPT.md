# Next Session Prompt

**Last Updated**: 2025-11-30
**Session**: 6
**Priority**: OPTIMIZE COST - Detection Quality is Good, But Too Expensive

---

## ✅ COMPLETED IN LAST SESSION

1. **Fixed Architecture**: FlexibleTaggingGeminiClient now uses `analyze_with_custom_prompt()`
2. **Fixed Cost Tracking**: metadata now shows actual costs (`total_cost` field added)
3. **Confirmed NEW Format**: Hierarchical arrays working perfectly (target/vehicle/ground/posture)
4. **Cost Analysis**: HIGH reasoning = $0.09/verse, MEDIUM = $0.02/verse

**Key Files Modified**:
- [unified_llm_client.py](../private/src/hebrew_figurative_db/ai_analysis/unified_llm_client.py) - Added custom prompt method
- [flexible_tagging_gemini_client.py](../private/flexible_tagging_gemini_client.py) - Now builds and passes custom prompt

---

## 🎯 CRITICAL NEXT STEPS

### Priority 1: Implement Cost-Effective Detection Strategy

**Problem**: GPT-5.1 costs $80.70 for full Proverbs (915 verses)

**Solution**: Two-tier approach:
1. **Gemini 2.5 Flash** for initial detection ($0.00004/1K tokens)
2. **GPT-5.1** for validation of detected instances only

**Expected Cost**: $1-2 for detection + ~$10-15 for validation = **~$11-17 total** (vs $81 current)

**Implementation**:
```python
# In flexible_tagging_gemini_client.py:

def analyze_figurative_language_flexible(...):
    # Step 1: Fast detection with Gemini Flash
    flash_result = self.gemini_flash_client.detect(custom_prompt)

    # Step 2: If instances found, validate with GPT-5.1
    if flash_instances:
        validated = self.unified_client.validate_with_custom_prompt(
            custom_prompt, flash_instances
        )
        return validated

    return flash_result
```

**Files to Create/Modify**:
1. Add Gemini Flash client initialization in flexible_tagging_gemini_client.py
2. Create validation-only method in unified_llm_client.py
3. Update test script to use two-tier approach

---

### Priority 2: Add Validation Step to Pipeline

**Missing**: MetaphorValidator integration in test scripts

**Current Test Flow**:
```
Detection → Database (incomplete)
```

**Production Flow** (from Pentateuch/Psalms):
```
Detection → Validation → Database (complete with final_* fields)
```

**Implementation**:
```python
# In test script:

from hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

# After detection:
validator = MetaphorValidator()
validation_results = validator.validate_verse_instances(
    instances, hebrew_text, english_text
)

# Update instances with validation results:
for instance in instances:
    validation = validation_results[instance['id']]
    instance['validation_decision_*'] = validation['decision']
    instance['validation_reason_*'] = validation['reason']
    if validation['decision'] == 'VALID':
        instance['final_*'] = 'yes'
```

**Files to Modify**:
- test_proverbs_3_11_18_batched.py - Add validation step
- Create new test: test_proverbs_with_validation.py

---

### Priority 3: Optimize Chapter Context

**Current**: 5364 chars (full Hebrew + English chapter)
**Issue**: May be overwhelming the model, slowing processing

**Proposed Optimization**:
```python
# Instead of full chapter, provide:
1. Theme summary (100-200 chars)
2. Surrounding verses (±2 verses)
3. Total: ~1000 chars

Example for Proverbs 3:13:
"""
Proverbs 3 Theme: The value of wisdom and God's discipline

...
3:11 Do not reject the LORD's discipline
3:12 For whom the LORD loves, He rebukes
3:13 Happy is the man who finds wisdom  ← ANALYZING THIS VERSE
3:14 Her value is better than silver
3:15 She is more precious than rubies
...
"""
```

**Expected Benefits**:
- Faster processing (less tokens to process)
- Better focus (model isn't distracted by full chapter)
- Lower cost (fewer input tokens)

**Files to Modify**:
- interactive_parallel_processor.py - Update chapter context generation
- flexible_tagging_gemini_client.py - Accept compressed context

---

## 📋 TASK LIST FOR NEXT SESSION

### Phase 1: Test Gemini Flash Detection (30-45 minutes)
- [ ] Add Gemini Flash (2.5) client to flexible_tagging_gemini_client.py
- [ ] Create method: `detect_with_gemini_flash()`
- [ ] Test on Proverbs 3:11-18 to measure detection quality
- [ ] Compare with GPT-5.1 HIGH results
- [ ] Expected cost: ~$0.001 for 8 verses

### Phase 2: Implement Two-Tier Validation (45-60 minutes)
- [ ] Create `validate_with_gpt51()` method that only validates pre-detected instances
- [ ] Test: Gemini Flash detection → GPT-5.1 validation
- [ ] Measure total cost vs current approach
- [ ] Expected cost: ~$0.005-0.010 for 8 verses

### Phase 3: Add MetaphorValidator Integration (30 minutes)
- [ ] Import MetaphorValidator in test script
- [ ] Call `validate_verse_instances()` after detection
- [ ] Store validation results in output JSON
- [ ] Verify `final_*` fields are populated

### Phase 4: Run Full Proverbs Test (If Time Permits)
- [ ] **ONLY IF** two-tier approach shows good quality AND low cost
- [ ] Estimate: 915 verses × $0.015/verse = ~$14
- [ ] Processing time: ~2-3 hours with 6 workers
- [ ] **Get user approval before running**

---

## 🚨 IMPORTANT REMINDERS

### UTF-8 Encoding
Always add to test scripts:
```python
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
```

### Output Directory
All test outputs go to `output/` directory (not root)

### Database Schema
Final output must match Pentateuch_Psalms_fig_language.db schema:
- target, vehicle, ground, posture: JSON arrays
- validation_decision_*, validation_reason_*: From MetaphorValidator
- final_*: Post-validation classifications

---

## 📊 COST PROJECTIONS

### Current Approach (GPT-5.1 HIGH):
- Cost/verse: $0.0882
- Full Proverbs: **$80.70**
- Time: ~1.8 hours (6 workers)

### Proposed Approach (Gemini Flash + GPT-5.1 Validation):
- Detection (Flash): $0.002/verse
- Validation (GPT-5.1): $0.010/verse (only detected instances)
- Full Proverbs: **~$11-15**
- Savings: **$65-70 (81-87% reduction)**

### Even Cheaper Approach (Gemini Flash + Gemini Pro Validation):
- Detection (Flash): $0.002/verse
- Validation (Pro): $0.003/verse
- Full Proverbs: **~$4-5**
- Savings: **~$75 (94% reduction)**
- Trade-off: Slightly lower validation quality

---

## 🎯 SUCCESS CRITERIA

### Quality Benchmarks:
- Detection rate: ≥1.0 instance/verse (target: 1.5 like Pentateuch/Psalms)
- False positive rate: ≤10%
- Hierarchical arrays: Complete (3-4 levels each)
- Validation: VALID decisions ≥70%

### Cost Benchmarks:
- Target: ≤$15 for full Proverbs (915 verses)
- Stretch goal: ≤$10 for full Proverbs

### Speed Benchmarks:
- ≤30s per verse average (including validation)
- Total time ≤2 hours for full Proverbs (6 workers)

---

## 📁 REFERENCE FILES

### Code:
- Production pipeline: [interactive_parallel_processor.py](../private/interactive_parallel_processor.py)
- Detection client: [flexible_tagging_gemini_client.py](../private/flexible_tagging_gemini_client.py)
- LLM client: [unified_llm_client.py](../private/src/hebrew_figurative_db/ai_analysis/unified_llm_client.py)
- Validator: [metaphor_validator.py](../private/src/hebrew_figurative_db/ai_analysis/metaphor_validator.py)

### Documentation:
- This session: [SESSION_SUMMARY.md](SESSION_SUMMARY.md)
- Issues found: [ISSUES_FOUND_AND_FIXES.md](ISSUES_FOUND_AND_FIXES.md)
- Database schema: [DATABASE_SCHEMA.md](DATABASE_SCHEMA.md)

### Test Results:
- HIGH reasoning: [output/proverbs_3_11-18_batched_20251130_075050_results.json](../output/proverbs_3_11-18_batched_20251130_075050_results.json)
- MEDIUM reasoning: [output/proverbs_medium_20251129_193819_results.json](../output/proverbs_medium_20251129_193819_results.json)

---

## 🎓 NOTES FOR NEXT SESSION

1. **Gemini Flash Pricing**: $0.000040/1K input, $0.000120/1K output (200x cheaper than GPT-5.1)
2. **Quality vs Cost**: Flash detection quality needs testing - may need GPT-5.1 for complex verses
3. **Validation Approach**: Can validate in bulk (all instances in a verse at once) for efficiency
4. **Context Optimization**: Test with shorter context first to verify quality doesn't suffer

---

## 💡 IF THINGS GO WRONG

### If Gemini Flash Detection Quality is Poor:
- Try Gemini Pro (2.5) instead (10x cheaper than GPT-5.1, better than Flash)
- Use GPT-5.1 MEDIUM reasoning for detection (83% cheaper than HIGH)
- Hybrid: Flash for simple verses, GPT-5.1 for complex wisdom literature

### If Validation Costs Too Much:
- Use Gemini Pro for validation instead of GPT-5.1
- Skip validation for high-confidence detections (>0.9)
- Batch validation (multiple verses at once)

### If Detection Rate Still Low:
- Add more Proverbs-specific examples to prompt
- Reduce reasoning effort but add explicit criteria
- Try different temperature/sampling settings
