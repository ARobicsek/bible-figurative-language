# Interactive Biblical Text Processing Guide

## 🎯 Quick Start

### Run the Interactive Processor
```bash
python run_interactive_chapter.py
```

## 📋 How to Use

### 1. **Book Selection**
When you run the script, you'll see:
```
=== HEBREW FIGURATIVE LANGUAGE INTERACTIVE PROCESSOR ===

Available books:
  1. Genesis (50 chapters)
  2. Exodus (40 chapters)
  3. Leviticus (27 chapters)
  4. Numbers (36 chapters)
  5. Deuteronomy (34 chapters)

Select book (1-5) or type book name:
```

**Options:**
- Enter a number: `1` (for Genesis)
- Enter book name: `genesis` or `Genesis`

### 2. **Chapter Selection**
After selecting a book:
```
Selected: Genesis (1-50 chapters available)
Enter chapter number (1-50) or 'all' for all chapters:
```

**Options:**
- Single chapter: `37` (processes Genesis 37 only)
- All chapters: `all` (processes entire book)

### 3. **Processing**
The script will:
- ✅ Create a database with timestamp
- ✅ Create a detailed log file
- ✅ Process every verse (storing ALL verses, not just figurative ones)
- ✅ Show real-time progress
- ✅ Provide summary with figurative language details

## 📊 Example Sessions

### Example 1: Single Chapter
```
Select book (1-5) or type book name: 1
Selected: Genesis (1-50 chapters available)
Enter chapter number (1-50) or 'all' for all chapters: 37

✅ Processing complete!
📁 Database: genesis_37_fixed_20250920_203045.db
📄 Log file: genesis_37_log_20250920_203045.txt
📊 Results: 36 verses, 0 figurative instances
```

### Example 2: Multiple Chapters (Entire Book)
```
Select book (1-5) or type book name: deuteronomy
Selected: Deuteronomy (1-34 chapters available)
Enter chapter number (1-34) or 'all' for all chapters: all

✅ Processing complete!
📁 Database: deuteronomy_multiple_fixed_20250920_203045.db
📄 Log file: deuteronomy_multiple_log_20250920_203045.txt
📊 Results: 959 verses, 45 figurative instances
```

### Example 3: Book Name Input
```
Select book (1-5) or type book name: exodus
Selected: Exodus (1-40 chapters available)
Enter chapter number (1-40) or 'all' for all chapters: 15

✅ Processing complete!
📁 Database: exodus_15_fixed_20250920_203045.db
📄 Log file: exodus_15_log_20250920_203045.txt
📊 Results: 21 verses, 8 figurative instances
```

## 📁 Output Files

### Database Files
- **Single chapter**: `{book}_{chapter}_fixed_{timestamp}.db`
- **Multiple chapters**: `{book}_multiple_fixed_{timestamp}.db`

### Log Files
- **Single chapter**: `{book}_{chapter}_log_{timestamp}.txt`
- **Multiple chapters**: `{book}_multiple_log_{timestamp}.txt`

## 🔍 What Gets Processed

### ✅ Conservative API Features
- **Zero false positives** in Creation narratives (Genesis 1-3)
- **Genuine detection** of metaphors, similes, personification
- **Complete verse storage** - every verse stored regardless of figurative language
- **Detailed analysis** with vehicle/tenor classification

### 📊 Database Contents
- **`verses` table**: ALL processed verses (Hebrew + English)
- **`figurative_language` table**: Only verses with figurative language detected
- **Complete metadata**: Speaker, purpose, confidence, timestamps

## 🎯 Use Cases

### Research & Testing
```bash
# Test specific chapters known for figurative language
python run_interactive_chapter.py
# Select: Genesis, Chapter 49 (Jacob's blessings)
# Select: Deuteronomy, Chapter 32 (Song of Moses)
# Select: Exodus, Chapter 15 (Song of the Sea)
```

### Complete Book Analysis
```bash
# Process entire books for comprehensive analysis
python run_interactive_chapter.py
# Select: Genesis, all
# Select: Deuteronomy, all
```

### Comparative Studies
```bash
# Compare narrative vs. poetic chapters
python run_interactive_chapter.py
# Run Genesis 37 (narrative) vs Genesis 49 (poetic)
# Compare figurative language density
```

## 🛠️ Troubleshooting

### Common Issues
1. **Keyboard interrupt**: Press Ctrl+C to exit cleanly
2. **Invalid selection**: Script will prompt again
3. **API errors**: Logged with details for debugging
4. **Unicode issues**: Handled automatically

### Monitoring Progress
- **Real-time logging**: Watch progress in terminal
- **Log files**: Detailed processing information
- **Database verification**: Automatic count verification

### Performance Notes
- **Single chapter**: ~30 seconds - 2 minutes
- **Entire book**: 1-3 hours depending on size
- **Memory usage**: Minimal (verse-by-verse processing)
- **API rate limiting**: Built-in delays

## 📈 Expected Results

### Conservative API Behavior
- **Narrative chapters**: Low figurative language detection (0-5%)
- **Poetic chapters**: Higher detection (10-20%)
- **Legal chapters**: Minimal detection (0-2%)
- **Prophetic chapters**: Moderate detection (5-15%)

### Quality Indicators
- **High precision**: Few false positives
- **Balanced recall**: Catches genuine instances
- **Research-grade**: Suitable for academic analysis

## 🔗 Integration

### With Other Tools
```bash
# Monitor all databases
python monitor_processing.py

# Check specific results
python -c "
import sqlite3
conn = sqlite3.connect('genesis_37_fixed_TIMESTAMP.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM verses')
print('Total verses:', cursor.fetchone()[0])
cursor.execute('SELECT COUNT(*) FROM figurative_language')
print('Figurative instances:', cursor.fetchone()[0])
conn.close()
"
```

### Next Steps
1. **Run interactive processor** for your research needs
2. **Analyze results** using SQL queries or monitoring tools
3. **Compare chapters** or books for patterns
4. **Export data** for further analysis

---

**📞 Support**: Check log files for detailed error information and processing status.