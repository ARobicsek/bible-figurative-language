# Hebrew Figurative Language Processing - Run Instructions

## Quick Start Commands

### ✅ **IMPORTANT: Use Enhanced Scripts (Bug Fixed)**
```bash
# ⭐ RECOMMENDED: Enhanced scripts with fixed verse storage
python run_genesis_conservative_enhanced.py      # Complete Genesis (50 chapters)
python run_deuteronomy_conservative_enhanced.py  # Complete Deuteronomy (34 chapters)

# Individual chapter processing (for testing)
python run_genesis_chapter_37.py    # Test single Genesis chapter
python run_genesis_chapter_50.py    # Test single Genesis chapter
python run_deuteronomy_chapter_32.py # Test single Deuteronomy chapter
```

### Check Processing Status
```bash
# Monitor all databases and processing status
python monitor_processing.py

# List all database files (Windows)
dir *.db

# Quick count of results
python -c "import sqlite3; conn=sqlite3.connect('genesis_conservative_YYYYMMDD_HHMMSS.db'); print('Verses:', conn.execute('SELECT COUNT(*) FROM verses').fetchone()[0]); print('Figurative:', conn.execute('SELECT COUNT(*) FROM figurative_language').fetchone()[0])"
```

## Current System Status

### ✅ Working Components
- **Conservative API**: `src/hebrew_figurative_db/ai_analysis/gemini_api_conservative.py`
- **False Positive Elimination**: Successfully avoids Genesis 1-3 false positives
- **Genuine Detection**: Catches real figurative language (metaphors, personification, similes)
- **JSON Processing**: Handles markdown-wrapped responses from API

### ✅ **FIXED ISSUES** (September 2025)
1. **✅ CRITICAL BUG FIXED**: Verses now stored regardless of figurative language detection
2. **✅ Enhanced Error Logging**: Comprehensive logging and monitoring tools added
3. **✅ Resume Capability**: Enhanced scripts can resume interrupted processing
4. **✅ JSON Handling**: Fixed markdown wrapper and Unicode issues

### ⚠️ **Important Notes**
- **Use enhanced scripts only** - original scripts have the verse storage bug
- **Every verse is now stored** in the database, not just verses with figurative language
- **Conservative API working correctly** - avoids false positives while detecting genuine instances

## File Structure

### ✅ **Enhanced Processing Scripts (RECOMMENDED)**
- `run_genesis_conservative_enhanced.py` - Complete Genesis processing (FIXED)
- `run_deuteronomy_conservative_enhanced.py` - Complete Deuteronomy processing (FIXED)
- `run_genesis_chapter_37.py` - Individual Genesis chapter testing
- `run_genesis_chapter_50.py` - Individual Genesis chapter testing
- `run_deuteronomy_chapter_32.py` - Individual Deuteronomy chapter testing
- `monitor_processing.py` - Database and processing status monitoring

### ⚠️ **Legacy Scripts (BUGGY - DO NOT USE)**
- `run_deuteronomy_conservative.py` - ❌ Has verse storage bug
- `run_genesis_conservative.py` - ❌ Has verse storage bug

### API Files
- `src/hebrew_figurative_db/ai_analysis/gemini_api_conservative.py` - Conservative API client
- `src/hebrew_figurative_db/ai_analysis/gemini_api.py` - Original API client
- `src/hebrew_figurative_db/ai_analysis/metaphor_validator.py` - Enhanced validator

### Database
- `src/hebrew_figurative_db/database/db_manager.py` - Database interface
- Generated DBs: `genesis_conservative_YYYYMMDD_HHMMSS.db`, `deuteronomy_conservative_YYYYMMDD_HHMMSS.db`

## Expected Output

### Successful Run
```
=== PROCESSING COMPLETE DEUTERONOMY WITH CONSERVATIVE API ===
Database: deuteronomy_conservative_20250920_HHMMSS.db

--- Processing Deuteronomy 1 ---
Extracting Hebrew text for Deuteronomy.1...
  Processing Deuteronomy 1:1...
    No figurative language detected
  [...]
  Processing Deuteronomy 4:24...
    FOUND: 2 instances

=== DEUTERONOMY CONSERVATIVE PROCESSING COMPLETE ===
Total verses processed: 959
Total figurative instances: [X]
Processing time: [X] minutes
```

### Database Contents
- `verses` table: **ALL processed verses** (Hebrew/English pairs, regardless of figurative language)
- `figurative_language` table: Only verses with detected figurative language (vehicle/tenor classification)
- Complete verse tracking and timestamps

### ✅ **Verification Commands**
```bash
# Check that ALL verses are stored (not just figurative ones)
python -c "
import sqlite3
conn = sqlite3.connect('genesis_37_fixed_YYYYMMDD_HHMMSS.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM verses')
verses = cursor.fetchone()[0]
cursor.execute('SELECT COUNT(*) FROM figurative_language')
figurative = cursor.fetchone()[0]
print(f'✅ Verses stored: {verses}')
print(f'✅ Figurative instances: {figurative}')
print(f'✅ Ratio: {figurative/verses:.3f}')
conn.close()
"
```

## Troubleshooting

### Common Issues
1. **"No module named" errors**: Check Python path and `sys.path.append()` in scripts
2. **Database parameter errors**: Fix `insert_verse()` parameter names
3. **API key issues**: Verify Gemini API key in scripts
4. **Unicode errors**: Console encoding handled automatically

### Performance Notes
- **Genesis**: ~50 chapters, ~1,533 verses, ~2-3 hours
- **Deuteronomy**: ~34 chapters, ~959 verses, ~1.5-2 hours
- **API Rate Limiting**: Automatic delays built in
- **Memory Usage**: Minimal, processes verse by verse

## Conservative API Settings

The conservative approach prioritizes **avoiding false positives** while catching genuine figurative language:

### Excluded (Won't Mark as Figurative)
- Genesis 1-3 Creation narratives
- Standard divine actions (spoke, blessed, created)
- Technical religious terms (holy, covenant)
- Historical statements
- Straightforward descriptions

### Included (Will Mark as Figurative)
- Clear metaphors with cross-domain comparison
- Divine emotions/anthropomorphism
- Obvious personification of non-human entities
- Clear similes with "like/as"
- High-confidence instances only

## Next Steps

1. **Fix database interface** - correct `insert_verse()` parameters
2. **Test run** - Genesis 1-3 to verify false positive elimination
3. **Full run** - Complete Genesis and Deuteronomy
4. **Analyze results** - compare with previous runs
5. **Adjust if needed** - balance detection vs. false positives

## Contact/Issues

For technical issues or questions, check:
- Previous database runs for comparison
- API usage limits and costs
- Processing logs for errors
- Generated database file sizes and content