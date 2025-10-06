# Maintenance Scripts

This directory contains utility scripts for database maintenance and updates.

## Scripts

### `refresh_english_text.py`
Interactive script to refresh English text from Sefaria API with footnote removal and divine names modification.

**Features:**
- Fetches fresh English text from Sefaria API
- Removes footnotes and applies improved text cleaning (including `<br>` → space fix)
- Creates/updates `english_text_clean` and `english_text_clean_non_sacred` columns
- Includes user confirmation prompt before running

**Usage:**
```bash
python scripts/refresh_english_text.py
```

### `refresh_english_text_auto.py`
Non-interactive version of the refresh script for automated runs.

**Features:**
- Same functionality as `refresh_english_text.py` but without user prompts
- Used for the October 5, 2025 spacing fix that updated all 8,373 verses
- Runs immediately when executed

**Usage:**
```bash
python scripts/refresh_english_text_auto.py
```

## Notes

- Both scripts require the `private/` module to be available
- Scripts include rate limiting (0.5s delay between API calls) to be respectful to Sefaria API
- The spacing fix (replacing `<br>` tags with spaces) is implemented in `sefaria_client.py:81`
