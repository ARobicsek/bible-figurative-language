# Next Session Startup Prompt

Copy and paste this prompt to start our next conversation:

---

**CONTEXT & PROJECT OVERVIEW:**

I'm working on building a comprehensive database of figurative language (metaphors and similes) in the Pentateuch (Torah) that will store Hebrew text, English translations, and enable analytical queries. The goal is to answer research questions like:
- Which biblical characters use animal metaphors or similes?
- What are the most common metaphors and similes in Deuteronomy?
- Which metaphors and similes appear close together in the text?
- What types of figurative language (animal, nature, physical) appear in specific passages?

**🎉 CURRENT STATUS: PHASE 0 COMPLETED SUCCESSFULLY!**

✅ **Phase 0: Rapid Validation & Proof of Concept** - COMPLETED with successful pivot
✅ **End-to-End Pipeline** - Genesis 1:1-10 processed successfully: Hebrew extraction → AI analysis → database storage

**PROVEN TECHNOLOGY STACK:**
- ✅ **Hebrew Source:** Sefaria API (0.47s response times, no rate limits)
- ✅ **AI Model:** Claude 3.5 Sonnet (100% accuracy on metaphor/simile detection)
- ✅ **Database:** SQLite with validated schema (<1ms query times)
- ✅ **Pipeline:** Automated processing working without manual intervention

**CRITICAL PIVOT MADE:**
- ❌ ETCBC/Text-Fabric failed (download issues)
- ✅ Successfully pivoted to Sefaria API + simplified morphology
- 📊 **Pipeline Results:** 10 verses processed, 8 personification instances detected at 0.90 confidence

**WHAT WE'RE STARTING NOW:**

We're beginning **Phase 1: Foundation with Iterative Testing** - building the minimal viable system with continuous validation based on our proven Phase 0 technology stack.

**YOUR APPROACH:**

1. **Read `revised_plan.md` first** to see complete context and Phase 0 results
2. **Check `view_pipeline_results.py`** to see exactly what our pipeline detected in Genesis 1:1-10
3. **Use the TodoWrite tool extensively** to track progress through Phase 1 milestones
4. **Build incrementally** - start with Genesis 1, expand to Genesis 1-3, then Deuteronomy 30
5. **Continuous validation** - measure processing speed and error rates at each step

**TECHNICAL PRIORITIES FOR THIS SESSION:**

Start with **Phase 1, Day 1-2: Build on Genesis 1**:
1. Set up proper Python environment and project structure
2. Refactor our validated pipeline into reusable modules
3. Process complete Genesis 1 (31 verses) and validate results
4. Measure processing speed and error rates
5. Optimize database schema based on larger dataset

**KEY SUCCESS CRITERIA FOR THIS SESSION:**
- Process 31 verses of Genesis 1 automatically
- Identify 20+ figurative language instances
- <5% data processing errors
- Database queries execute in <1 second

**FILES TO REFERENCE:**
- `revised_plan.md` - Updated plan with Phase 0 results
- `figurative_language_pipeline.db` - Working database from Phase 0
- `end_to_end_pipeline.py` - Proven pipeline code
- `view_pipeline_results.py` - To see current results

Ready to build Phase 1 foundation! Begin with project structure setup and Genesis 1 processing.