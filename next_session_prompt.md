# Next Session Context

## Current Project Status - DUAL SYSTEM ARCHITECTURE COMPLETE ✅
We have successfully implemented TWO complementary Hebrew figurative language processing systems:

1. **ORIGINAL Multi-Model Pipeline**: Proven conservative system using `interactive_multi_model_processor.py`
   - Uses hierarchical target/vehicle/ground categories (12/15/6 categories)
   - Proven results: 33 instances detected in Deuteronomy 30
   - Database uses categorical fields
   - **STATUS**: Stable and production-ready

2. **NEW Flexible Tagging Pipeline**: Revolutionary system using `interactive_flexible_tagging_processor.py`
   - Uses hierarchical JSON arrays for tagging (e.g., ["specific target", "target category", "general domain"])
   - Enhanced with split deliberations for token efficiency (figurative_detection vs tagging_analysis)
   - Database schema v3 with JSON fields
   - **VERIFIED RESULTS**: 21 instances detected from Deuteronomy 30 with complete hierarchical metadata
   - **STATUS**: Fully operational and tested

## Recent Session Achievements (Sept 25, 2025) - COMPLETE ✅
- ✅ **Enhanced JSON Parsing**: Fixed bracket matching and validation in `flexible_tagging_gemini_client.py`
- ✅ **Split Deliberations**: Separate fields for figurative detection vs tagging analysis reasoning
- ✅ **Increased Token Limits**: 15,000 tokens to prevent truncation (vs 10,000 in multi-model)
- ✅ **Database Schema Update**: Added hierarchical JSON fields (target, vehicle, ground, posture) and split deliberation fields
- ✅ **Removed Underscores**: Updated prompt to use spaces in hierarchical tags ("positive sentiment" not "positive_sentiment")
- ✅ **Verified Storage**: Confirmed 21 instances properly stored in `deuteronomy_30_all_v_flexible_20250925_1221.db` with full metadata
- ✅ **Campground Cleanup**: Removed 6 obsolete files to declutter project
- ✅ **Documentation Update**: Updated README.md to reflect dual-system architecture

## Current System Architecture - STABLE ✅

### Core Files (KEEP - ACTIVE SYSTEMS)
- `interactive_flexible_tagging_processor.py` - **NEW** main system entry point (hierarchical tagging)
- `interactive_multi_model_processor.py` - **ORIGINAL** main system entry point (conservative detection)
- `flexible_tagging_gemini_client.py` - NEW AI client with hierarchical tagging and enhanced parsing
- `src/hebrew_figurative_db/` - Core library (used by both systems)
- `schema_v3_flexible.sql` - Current database schema with JSON fields

### Recently Cleaned Files (DELETED Sept 25, 2025)
- `flexible_tagging_gemini_client_fixed.py` - Obsolete duplicate
- `initial_tag_taxonomy.sql`, `schema_v2.sql` - Old schemas
- `simple_test_results.py` - Basic test utility
- `run_deuteronomy_multi_model.py`, `run_genesis_multi_model.py` - Obsolete runners

### Remaining Files for Future Investigation
- Conceptual grouping system: `conceptual_grouper.py`, `run_full_conceptual_grouping.py`, `test_conceptual_grouper.py`
- Utility tools: `analyze_db.py`, `data_processor.py`, `create_tag_system.py`

## Both Systems Ready for Production Use 🚀

### Flexible Hierarchical System
- **Command**: `python interactive_flexible_tagging_processor.py`
- **Output**: Hierarchical JSON arrays with rich semantic tagging
- **Best for**: Advanced research requiring detailed categorization
- **Database**: Schema v3 with JSON fields and split deliberations

### Original Multi-Model System
- **Command**: `python interactive_multi_model_processor.py`
- **Output**: Categorical fields with proven conservative detection
- **Best for**: Reliable, consistent figurative language detection
- **Database**: Traditional categorical schema

## Next Steps / Future Work Ideas
- Run full book processing with flexible system to build comprehensive hierarchical datasets
- Compare detection patterns between conservative vs flexible approaches
- Develop visualization tools for hierarchical tag exploration and search
- Consider integration with conceptual grouping for advanced Sankey diagram preparation
- Extend flexible system to Genesis and other biblical books

## Technical Notes - CURRENT CONFIG ✅
- Both systems: Gemini 2.5 Flash primary with 1.5 Flash fallback
- Flexible system: 15,000 token limit (enhanced for hierarchical analysis)
- Multi-model system: 10,000 token limit (proven sufficient for categorical detection)
- Database: Proper transaction commits after each chapter
- Validation: Full MetaphorValidator integration in both systems
- Unicode: All systems handle Hebrew text properly with diacritic stripping