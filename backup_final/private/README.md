# Private Processing Code

**Note:** This directory contains the AI processing pipeline code that is NOT included in the public release. These files are preserved locally for continued development and processing.

## Files Restored from Backup

- `interactive_parallel_processor.py` - Interactive parallel processing with flexible book/chapter/verse selection
  - **Updated:** Added Psalms (150 chapters) support
  - **Updated:** Fixed .env path to load from project root
- `claude_sonnet_client.py` - Claude Sonnet 4 API client
- `flexible_tagging_gemini_client.py` - Gemini API client with flexible tagging
- `src/` - Complete Hebrew figurative language processing package

## Usage

### Run Interactive Processor

```bash
cd private
python interactive_parallel_processor.py
```

This will guide you through:
1. **Selecting books** - Choose from:
   - Genesis (50 chapters)
   - Exodus (40 chapters)
   - Leviticus (27 chapters)
   - Numbers (36 chapters)
   - Deuteronomy (34 chapters)
   - **Psalms (150 chapters)** ✨

   Examples: `6` for Psalms, `1,6` for Genesis and Psalms, `all` for all books

2. **Selecting chapters** - Examples:
   - `full` - entire book
   - `1-10` - chapters 1 through 10
   - `1,5,23` - specific chapters
   - `1-5,10,20-23` - mixed ranges

3. **Selecting verses** - Same flexible format as chapters

4. **Configuring parallel workers** (1-12) - More workers = faster processing

5. Processing with automatic AI analysis and validation

### Requirements

Install dependencies:
```bash
pip install -r requirements.txt
```

Make sure your `.env` file in the project root contains:
```
GEMINI_API_KEY=your_gemini_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

## Important Notes

- This directory is in `.gitignore` and will NOT be committed to the repository
- All processing results are saved to the main `database/` directory
- The complete Torah database is already in `database/torah_figurative_language.db`
- Use this only for additional processing or updates to the dataset
