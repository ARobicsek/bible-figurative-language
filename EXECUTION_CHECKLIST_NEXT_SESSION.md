# Execution Checklist: Public Release of Hebrew Figurative Language Explorer

**Last Updated:** September 29, 2025
**Current Status:** Phase 0 Complete (Backup created, decisions documented)
**Next Session:** Begin Phase 1 - Repository Cleanup

---

## 🎯 Quick Start for Next Session

**Start here:**
1. Review decisions made (see bottom of this document)
2. If decisions are complete, begin with **Phase 1, Task 1** below
3. Check off each task as completed
4. Update this file as you progress

**Key Documents:**
- `PROJECT_OVERVIEW_AND_DECISIONS.md` - Full project context and decision points
- `PUBLIC_RELEASE_PLAN_UI_ONLY.md` - Detailed plan for UI-only release
- `backup-before-public-release-20250929` - Git branch with complete backup

---

## Phase 0: Preparation & Decisions ✅ COMPLETE

- [x] **0.1** Create backup of repository (`backup-before-public-release-20250929` branch)
- [x] **0.2** Document project overview and decision points
- [x] **0.3** Create execution checklist

### Decisions Made ✅

- [x] **DECISION 1:** License choice → **MIT (code) + CC BY 4.0 (data)**

- [x] **DECISION 2:** Repository name → **bible-figurative-language-concordance**

- [x] **DECISION 3:** Attribution format
  - [x] Author name: **Ari Robicsek**
  - [ ] Affiliation (if any): _________________
  - [x] Contact method: **GitHub issues**
  - [x] Citation format: **BibTeX format**

- [x] **DECISION 4:** Frontend architecture → **Direct Supabase client**

---

## Phase 1: Repository Cleanup (Estimated: 2-3 hours)

### Step 1.1: Create Clean Directory Structure
- [ ] **1.1.1** Create directories:
  ```bash
  mkdir -p web database docs
  ```
- [ ] **1.1.2** Verify directories created successfully

### Step 1.2: Move Files to Keep

#### Web Interface Files
- [ ] **1.2.1** Move `biblical_figurative_interface.html` → `web/`
- [ ] **1.2.2** Move `api_server.py` → `web/`
- [ ] **1.2.3** Move `interface_requirements.txt` → `web/requirements.txt`

#### Database Files
- [ ] **1.2.4** Copy `complete_torah_merged.db` → `database/torah_figurative_language.db`
- [ ] **1.2.5** Copy `schema_v4_current.sql` → `database/schema_v4.sql`
- [ ] **1.2.6** Verify database integrity:
  ```bash
  sqlite3 database/torah_figurative_language.db "SELECT COUNT(*) FROM verses;"
  # Should return 5846
  ```

#### Documentation Files
- [ ] **1.2.7** Move `non_sacred_hebrew_naming.md` → `docs/NON_SACRED_HEBREW.md`
- [ ] **1.2.8** Keep `SANKEY_VISUALIZATION_ROADMAP.md` in root
- [ ] **1.2.9** Keep `INTERFACE_SETUP.md` in root (will update later)

### Step 1.3: Delete Processing Code (NOT Sharing)

**IMPORTANT:** Double-check backup branch exists before deleting!
```bash
git log backup-before-public-release-20250929 -1
# Should show the backup commit
```

#### Delete Python Processing Scripts
- [ ] **1.3.1** Delete:
  ```bash
  rm interactive_parallel_processor.py
  rm interactive_multi_model_processor.py
  rm interactive_flexible_tagging_processor.py
  rm parallel_flexible_processor.py
  rm claude_sonnet_client.py
  rm flexible_tagging_gemini_client.py
  ```

#### Delete Entire src/ Package
- [ ] **1.3.2** Delete entire src/ directory:
  ```bash
  rm -rf src/
  ```
- [ ] **1.3.3** Verify deleted:
  ```bash
  ls src/  # Should show "No such file or directory"
  ```

#### Delete Archived Files
- [ ] **1.3.4** Delete archived_unused_files/:
  ```bash
  rm -rf archived_unused_files/
  ```

### Step 1.4: Delete Temporary Databases

- [ ] **1.4.1** List all .db files:
  ```bash
  ls -lh *.db
  ```

- [ ] **1.4.2** Delete all EXCEPT `complete_torah_merged.db`:
  ```bash
  rm deuteronomy_all_c_all_v_20250922_0959.db
  rm deuteronomy_all_c_all_v_flexible_20250925_2317.db
  rm exodus_all_c_all_v_20250922_0614.db
  rm exodus_all_c_all_v_parallel_20250928_0148.db
  rm genesis_all_c_all_v_20250922_1050.db
  rm genesis_all_c_all_v_parallel_20250926_1509.db
  rm genesis_all_c_all_v_parallel_20250926_1608.db
  rm 2books_c63_multi_v_parallel_20250928_0934.db
  rm 5books_c187_multi_v_parallel_20250928_1454.db
  rm deuteronomy_c31_multi_v_parallel_20250929_0907.db
  rm merged_5books_complete_deuteronomy.db
  rm deuteronomy_complete_final.db
  rm figurative_language_pipeline.db
  ```

- [ ] **1.4.3** Delete database project file:
  ```bash
  rm "bible database.sqbpro"
  ```

### Step 1.5: Delete Log Files and Temporary Data

- [ ] **1.5.1** Delete all log files:
  ```bash
  rm *_log.txt
  rm *.log
  ```

- [ ] **1.5.2** Delete JSON processing results:
  ```bash
  rm *_results.json
  rm *_processing_summary_*.json
  rm clean_deuteronomy_data.json
  rm clean_deuteronomy_data_grouped_*.json
  rm conceptual_grouping_report_*.json
  rm detailed_groupings_*.json
  rm data_quality_report.json
  rm tag_pattern_analysis.json
  rm tag_taxonomy.json
  rm tag_taxonomy_rules.json
  rm validation_set_200_verses.json
  ```

- [ ] **1.5.3** Delete temporary text files:
  ```bash
  rm test_output.txt
  rm db_results.txt
  rm char_analysis.txt
  ```

### Step 1.6: Delete Test/Debug Scripts

- [ ] **1.6.1** Delete check/test scripts:
  ```bash
  rm check_db.py check_db2.py check_db_schema.py
  rm check_genesis_verses.py
  rm check_model_usage.py check_model_usage_fixed.py
  rm test_search_bug.py
  ```

- [ ] **1.6.2** Delete debug files:
  ```bash
  rm debug_interface.html
  ```

### Step 1.7: Delete Internal Development Documentation

- [ ] **1.7.1** Delete internal docs:
  ```bash
  rm DEBUGGING_SUMMARY.md
  rm HANDOFF_SEPT_29_2025.md
  rm VALIDATION_DISPLAY_ISSUE_HANDOFF.md
  rm GENESIS_ANALYSIS_PREP.md
  rm migration_plan.md
  rm flexible_tag_guidelines.md
  rm llm_deliberation_fields.md
  rm tag_guidelines.md
  rm vehicle_subcategory_updates.md
  ```

- [ ] **1.7.2** Delete planning documents:
  ```bash
  rm PUBLIC_RELEASE_PLAN.md
  # Keep PUBLIC_RELEASE_PLAN_UI_ONLY.md for reference
  ```

### Step 1.8: Delete Cache Directories

- [ ] **1.8.1** Delete cache:
  ```bash
  rm -rf cache_production/
  rm -rf cache_test/
  ```

### Step 1.9: Delete Binary/Proprietary Files

- [ ] **1.9.1** Delete Word doc:
  ```bash
  rm "Figurative Language for God in Deuteronomy.docx"
  ```

### Step 1.10: Delete Original Unneeded Files

- [ ] **1.10.1** Delete old requirements.txt (was for processing):
  ```bash
  rm requirements.txt
  # Keep web/requirements.txt
  ```

- [ ] **1.10.2** Delete SQL query file:
  ```bash
  rm query_non_figurative_verses.sql
  ```

### Step 1.11: Verify Cleanup

- [ ] **1.11.1** List remaining files:
  ```bash
  ls -la
  ```

- [ ] **1.11.2** Should see approximately:
  ```
  web/
  database/
  docs/
  .gitignore
  .claude/
  README.md
  INTERFACE_SETUP.md
  SANKEY_VISUALIZATION_ROADMAP.md
  PUBLIC_RELEASE_PLAN_UI_ONLY.md
  PROJECT_OVERVIEW_AND_DECISIONS.md
  EXECUTION_CHECKLIST_NEXT_SESSION.md
  ```

### Step 1.12: Update .gitignore

- [ ] **1.12.1** Update .gitignore with comprehensive rules:
  ```gitignore
  # Python
  __pycache__/
  *.py[cod]
  *$py.class
  *.so
  .Python
  venv/
  env/
  ENV/

  # Environment
  .env
  .env.local

  # Databases (except sample)
  *.db
  *.db-journal
  !database/torah_figurative_language.db

  # Logs
  *.log
  *.log.*

  # IDE
  .vscode/
  .idea/
  *.swp
  .DS_Store

  # Cache
  cache_*/

  # Temporary
  tmp/
  temp/
  test_*.db
  *_test.db

  # Claude settings (keep for development)
  # .claude/
  ```

### Step 1.13: Test Interface Still Works

- [ ] **1.13.1** Update api_server.py database path:
  ```python
  # Change from:
  DATABASE_PATH = 'complete_torah_merged.db'
  # To:
  DATABASE_PATH = '../database/torah_figurative_language.db'
  ```

- [ ] **1.13.2** Test locally:
  ```bash
  cd web
  python api_server.py
  # Open http://localhost:5000 in browser
  ```

- [ ] **1.13.3** Verify:
  - [ ] Interface loads
  - [ ] Verses display
  - [ ] Search works
  - [ ] Filters work
  - [ ] Click interactions work

### Step 1.14: Commit Cleanup

- [ ] **1.14.1** Stage changes:
  ```bash
  git add -A
  ```

- [ ] **1.14.2** Review what will be committed:
  ```bash
  git status
  ```

- [ ] **1.14.3** Commit:
  ```bash
  git commit -m "refactor: Clean repository for public release (UI + database only)

  - Restructure: web/, database/, docs/ directories
  - Remove: All processing scripts and src/ package
  - Remove: Temporary databases, logs, test scripts
  - Remove: Internal development documentation
  - Keep: Interface, complete Torah database, public documentation
  - Update: .gitignore for public release

  This prepares the repository for public sharing as a research tool.
  Full backup preserved in backup-before-public-release-20250929 branch."
  ```

**Phase 1 Complete! 🎉**

---

## Phase 2: Create Public Documentation (Estimated: 3-4 hours)

### Step 2.1: Create Public README.md

- [ ] **2.1.1** Backup current README:
  ```bash
  cp README.md README_INTERNAL.md
  ```

- [ ] **2.1.2** Create new public README.md with structure:
  - Project title and tagline
  - Live demo link (TBD)
  - Features list
  - Quick start guide
  - Database statistics
  - Documentation links
  - Use cases
  - Citation format
  - License information
  - Acknowledgments
  - Limitations

- [ ] **2.1.3** Get database statistics for README:
  ```bash
  sqlite3 database/torah_figurative_language.db
  ```
  ```sql
  -- Total verses
  SELECT COUNT(*) FROM verses;

  -- Verses with figurative language
  SELECT COUNT(DISTINCT verse_id) FROM figurative_language WHERE final_figurative_language = 'yes';

  -- Total figurative instances
  SELECT COUNT(*) FROM figurative_language WHERE final_figurative_language = 'yes';

  -- By type
  SELECT
    SUM(CASE WHEN final_metaphor = 'yes' THEN 1 ELSE 0 END) as metaphors,
    SUM(CASE WHEN final_simile = 'yes' THEN 1 ELSE 0 END) as similes,
    SUM(CASE WHEN final_personification = 'yes' THEN 1 ELSE 0 END) as personifications,
    SUM(CASE WHEN final_idiom = 'yes' THEN 1 ELSE 0 END) as idioms,
    SUM(CASE WHEN final_hyperbole = 'yes' THEN 1 ELSE 0 END) as hyperboles,
    SUM(CASE WHEN final_metonymy = 'yes' THEN 1 ELSE 0 END) as metonymies,
    SUM(CASE WHEN final_other = 'yes' THEN 1 ELSE 0 END) as other
  FROM figurative_language
  WHERE final_figurative_language = 'yes';
  ```

- [ ] **2.1.4** Add statistics to README

### Step 2.2: Create SETUP.md

- [ ] **2.2.1** Create `SETUP.md` with sections:
  - Option 1: Use hosted version (link TBD)
  - Option 2: Run locally
    - Prerequisites
    - Installation steps
    - Running the server
    - Troubleshooting
  - Option 3: Deploy your own
    - Supabase setup
    - Database migration
    - Frontend updates
    - Netlify deployment
    - Testing

### Step 2.3: Create CONTRIBUTING.md

- [ ] **2.3.1** Create `CONTRIBUTING.md` focused on:
  - Ways to contribute (validation, bug reports, features, docs)
  - How to report classification errors
  - Issue templates and guidelines
  - Code of conduct
  - Recognition for contributors

### Step 2.4: Create LICENSE

- [ ] **2.4.1** Wait for DECISION 1 (license choice)

- [ ] **2.4.2** If MIT + CC BY 4.0:
  - Create `LICENSE-CODE.md` with MIT license text
  - Create `LICENSE-DATA.md` with CC BY 4.0 license text
  - Create `LICENSE` file referencing both

- [ ] **2.4.3** If GPL + CC BY-SA:
  - Create `LICENSE-CODE.md` with GPL v3 text
  - Create `LICENSE-DATA.md` with CC BY-SA 4.0 text

### Step 2.5: Create Database Documentation

- [ ] **2.5.1** Create `docs/DATABASE_SCHEMA.md`:
  - Table descriptions (verses, figurative_language)
  - Column descriptions with examples
  - Common queries
  - Relationship diagrams (text-based)
  - Indexes information

- [ ] **2.5.2** Create `docs/METHODOLOGY.md`:
  - High-level description of AI pipeline (without sharing code)
  - Three-tier architecture explanation
  - Validation process
  - Quality assurance
  - Limitations and known issues
  - Model transparency

- [ ] **2.5.3** Create `docs/FEATURES.md`:
  - Complete interface feature guide
  - Filter documentation
  - Search functionality
  - Keyboard shortcuts
  - Tips and tricks

### Step 2.6: Create Support Documentation

- [ ] **2.6.1** Update `INTERFACE_SETUP.md`:
  - Remove development-specific content
  - Focus on deployment and usage
  - Add screenshots (can add later)

- [ ] **2.6.2** Create `docs/FAQ.md`:
  - Common questions
  - Troubleshooting
  - Technical questions
  - Research methodology questions

### Step 2.7: Add GitHub Community Files

- [ ] **2.7.1** Create `.github/` directory:
  ```bash
  mkdir -p .github/ISSUE_TEMPLATE
  ```

- [ ] **2.7.2** Create issue templates:
  - `.github/ISSUE_TEMPLATE/bug_report.md`
  - `.github/ISSUE_TEMPLATE/classification_feedback.md`
  - `.github/ISSUE_TEMPLATE/feature_request.md`

- [ ] **2.7.3** Create `.github/PULL_REQUEST_TEMPLATE.md`

### Step 2.8: Commit Documentation

- [ ] **2.8.1** Test all documentation links work
- [ ] **2.8.2** Proofread all documents
- [ ] **2.8.3** Commit:
  ```bash
  git add -A
  git commit -m "docs: Add comprehensive public documentation

  - Public-facing README with project overview
  - SETUP.md with deployment instructions
  - CONTRIBUTING.md with contribution guidelines
  - LICENSE files (MIT + CC BY 4.0)
  - Database schema and methodology documentation
  - GitHub issue templates

  Documentation is now ready for public release."
  ```

**Phase 2 Complete! 🎉**

---

## Phase 3: Supabase Setup (Estimated: 2-3 hours)

### Step 3.1: Create Supabase Account

- [ ] **3.1.1** Go to https://supabase.com
- [ ] **3.1.2** Sign up for free account
- [ ] **3.1.3** Verify email

### Step 3.2: Create Supabase Project

- [ ] **3.2.1** Click "New Project"
- [ ] **3.2.2** Choose organization (or create new)
- [ ] **3.2.3** Set project name: [DECISION 2 repository name]
- [ ] **3.2.4** Set strong database password (save securely!)
- [ ] **3.2.5** Choose region (closest to expected users)
- [ ] **3.2.6** Click "Create new project"
- [ ] **3.2.7** Wait for provisioning (~2 minutes)

### Step 3.3: Note Credentials

- [ ] **3.3.1** Go to Settings → API
- [ ] **3.3.2** Note and save securely:
  - Project URL: `https://[project-ref].supabase.co`
  - `anon` `public` key: `eyJ...`
  - `service_role` `secret` key: `eyJ...` (DON'T share publicly)

### Step 3.4: Prepare PostgreSQL Schema

- [ ] **3.4.1** Create file `database/schema_v4_postgresql.sql`

- [ ] **3.4.2** Convert SQLite schema to PostgreSQL:
  ```sql
  -- Change INTEGER PRIMARY KEY AUTOINCREMENT to SERIAL PRIMARY KEY
  -- Change TEXT CHECK(...) to proper CHECK constraints
  -- Add proper indexes
  ```

- [ ] **3.4.3** Test conversion locally if possible:
  ```bash
  # Install PostgreSQL locally (optional)
  # Test schema creation
  ```

### Step 3.5: Create Tables in Supabase

- [ ] **3.5.1** In Supabase dashboard → SQL Editor
- [ ] **3.5.2** Paste schema_v4_postgresql.sql
- [ ] **3.5.3** Execute
- [ ] **3.5.4** Verify tables created: Table Editor → Check verses and figurative_language tables exist

### Step 3.6: Import Data to Supabase

**Option A: CSV Import (Easiest)**

- [ ] **3.6.1** Export SQLite to CSV:
  ```bash
  sqlite3 database/torah_figurative_language.db
  ```
  ```sql
  .headers on
  .mode csv
  .output verses.csv
  SELECT * FROM verses;
  .output figurative_language.csv
  SELECT * FROM figurative_language;
  .quit
  ```

- [ ] **3.6.2** In Supabase: Table Editor → verses → Import CSV
- [ ] **3.6.3** Upload verses.csv
- [ ] **3.6.4** Verify import successful (check row count)
- [ ] **3.6.5** Repeat for figurative_language.csv

**Option B: Python Migration Script (More Reliable)**

- [ ] **3.6.6** Create `scripts/migrate_to_supabase.py`:
  ```python
  import sqlite3
  from supabase import create_client

  # Read from SQLite
  # Write to Supabase in batches
  # Show progress
  ```

- [ ] **3.6.7** Install dependencies:
  ```bash
  pip install supabase
  ```

- [ ] **3.6.8** Run migration:
  ```bash
  python scripts/migrate_to_supabase.py
  ```

- [ ] **3.6.9** Verify all data migrated

### Step 3.7: Configure Row-Level Security (RLS)

- [ ] **3.7.1** In Supabase: Authentication → Policies
- [ ] **3.7.2** Enable RLS on verses table
- [ ] **3.7.3** Create policy "Public read access":
  ```sql
  CREATE POLICY "Public read access" ON verses
    FOR SELECT
    USING (true);
  ```

- [ ] **3.7.4** Enable RLS on figurative_language table
- [ ] **3.7.5** Create policy "Public read access":
  ```sql
  CREATE POLICY "Public read access" ON figurative_language
    FOR SELECT
    USING (true);
  ```

- [ ] **3.7.6** Test: Try reading data with anon key (should work)
- [ ] **3.7.7** Test: Try writing data with anon key (should fail)

### Step 3.8: Create Database Indexes

- [ ] **3.8.1** In SQL Editor, create indexes:
  ```sql
  CREATE INDEX idx_verses_book ON verses(book);
  CREATE INDEX idx_verses_reference ON verses(reference);
  CREATE INDEX idx_verses_chapter ON verses(chapter);
  CREATE INDEX idx_fl_verse_id ON figurative_language(verse_id);
  CREATE INDEX idx_fl_final_types ON figurative_language(
    final_simile, final_metaphor, final_personification,
    final_idiom, final_hyperbole, final_metonymy, final_other
  );
  ```

- [ ] **3.8.2** Verify indexes created

### Step 3.9: Test Supabase Database

- [ ] **3.9.1** Test query via Supabase dashboard
- [ ] **3.9.2** Test query via REST API:
  ```bash
  curl 'https://[project-ref].supabase.co/rest/v1/verses?select=*&limit=1' \
    -H "apikey: [anon-key]" \
    -H "Authorization: Bearer [anon-key]"
  ```

- [ ] **3.9.3** Verify response

**Phase 3 Complete! 🎉**

---

## Phase 4: Update Frontend for Supabase (Estimated: 2-4 hours)

### Step 4.1: Backup Current Interface

- [ ] **4.1.1** Create backup:
  ```bash
  cp web/biblical_figurative_interface.html web/biblical_figurative_interface_BACKUP.html
  ```

### Step 4.2: Add Supabase Client (If Direct Supabase - DECISION 4)

- [ ] **4.2.1** Add Supabase SDK to HTML `<head>`:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>
  ```

- [ ] **4.2.2** Initialize Supabase client:
  ```javascript
  const SUPABASE_URL = 'https://[project-ref].supabase.co';
  const SUPABASE_ANON_KEY = '[your-anon-key]';
  const supabase = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  ```

### Step 4.3: Replace API Calls with Supabase Queries

**Find and replace patterns:**

- [ ] **4.3.1** Replace verse fetching:
  ```javascript
  // OLD:
  fetch('/api/verses?book=Genesis&limit=50')

  // NEW:
  const { data, error } = await supabase
    .from('verses')
    .select(`
      *,
      figurative_language (*)
    `)
    .eq('book', 'Genesis')
    .range(0, 49);
  ```

- [ ] **4.3.2** Replace verse search:
  ```javascript
  // OLD:
  fetch(`/api/verses?search=${searchTerm}`)

  // NEW:
  const { data, error } = await supabase
    .from('verses')
    .select('*')
    .or(`hebrew_text.ilike.%${searchTerm}%,english_text.ilike.%${searchTerm}%`);
  ```

- [ ] **4.3.3** Replace filtering:
  ```javascript
  // OLD:
  fetch('/api/verses?book=Genesis&type=metaphor')

  // NEW:
  const { data, error } = await supabase
    .from('verses')
    .select(`
      *,
      figurative_language!inner (*)
    `)
    .eq('book', 'Genesis')
    .eq('figurative_language.final_metaphor', 'yes');
  ```

- [ ] **4.3.4** Update all other API endpoints

### Step 4.4: Handle Supabase Response Format

- [ ] **4.4.1** Update response handling:
  ```javascript
  // Supabase returns { data, error } not { verses, total }
  // Update all response handling code
  ```

- [ ] **4.4.2** Add error handling for Supabase errors

### Step 4.5: Test Locally with Supabase

- [ ] **4.5.1** Open HTML file directly in browser (no Flask needed)
- [ ] **4.5.2** Or use simple HTTP server:
  ```bash
  cd web
  python -m http.server 8000
  # Open http://localhost:8000
  ```

- [ ] **4.5.3** Test all functionality:
  - [ ] Verse loading
  - [ ] Pagination
  - [ ] Book filtering
  - [ ] Figurative type filtering
  - [ ] Search (Hebrew and English)
  - [ ] Metadata filtering
  - [ ] Sacred/non-sacred toggle
  - [ ] Click interactions

### Step 4.6: Optimize Queries

- [ ] **4.6.1** Review slow queries
- [ ] **4.6.2** Add proper indexes if needed
- [ ] **4.6.3** Use `.select()` to only fetch needed columns
- [ ] **4.6.4** Implement pagination properly

### Step 4.7: Remove Flask Dependency (If Direct Supabase)

- [ ] **4.7.1** Delete or archive `web/api_server.py`
- [ ] **4.7.2** Update `web/requirements.txt` (may only need for data migration now)

### Step 4.8: Commit Frontend Updates

- [ ] **4.8.1** Test one more time
- [ ] **4.8.2** Commit:
  ```bash
  git add -A
  git commit -m "feat: Migrate frontend to Supabase client

  - Add Supabase JavaScript SDK
  - Replace Flask API calls with Supabase queries
  - Remove Flask server dependency
  - Optimize queries with proper filtering and pagination

  Interface now connects directly to Supabase PostgreSQL database."
  ```

**Phase 4 Complete! 🎉**

---

## Phase 5: Netlify Deployment (Estimated: 1-2 hours)

### Step 5.1: Create Netlify Account

- [ ] **5.1.1** Go to https://netlify.com
- [ ] **5.1.2** Sign up (free tier)
- [ ] **5.1.3** Connect GitHub account

### Step 5.2: Prepare Repository for Netlify

- [ ] **5.2.1** Create `netlify.toml` in repository root:
  ```toml
  [build]
    publish = "web"

  [[redirects]]
    from = "/*"
    to = "/biblical_figurative_interface.html"
    status = 200
  ```

- [ ] **5.2.2** Create `web/index.html`:
  ```html
  <!DOCTYPE html>
  <html>
  <head>
    <meta http-equiv="refresh" content="0; url=biblical_figurative_interface.html">
  </head>
  <body>
    <p>Redirecting...</p>
  </body>
  </html>
  ```

- [ ] **5.2.3** Commit configuration:
  ```bash
  git add netlify.toml web/index.html
  git commit -m "config: Add Netlify deployment configuration"
  git push origin main
  ```

### Step 5.3: Deploy to Netlify

- [ ] **5.3.1** In Netlify dashboard: "Add new site" → "Import an existing project"
- [ ] **5.3.2** Connect to GitHub repository
- [ ] **5.3.3** Configure build settings:
  - Build command: (leave empty)
  - Publish directory: `web`
  - Branch: `main`

- [ ] **5.3.4** Click "Deploy site"
- [ ] **5.3.5** Wait for deployment (~1-2 minutes)

### Step 5.4: Configure Environment Variables (If Needed)

- [ ] **5.4.1** If you want to hide Supabase keys (optional but recommended):
  - Netlify dashboard → Site settings → Environment variables
  - Add `SUPABASE_URL` and `SUPABASE_ANON_KEY`
  - Update HTML to read from window.netlifyEnv or similar

### Step 5.5: Test Deployed Site

- [ ] **5.5.1** Open provided Netlify URL (e.g., `random-name-123.netlify.app`)
- [ ] **5.5.2** Test all features:
  - [ ] Site loads
  - [ ] Verses display
  - [ ] Filtering works
  - [ ] Search works
  - [ ] Hebrew text renders correctly
  - [ ] Click interactions work
  - [ ] Mobile view works

### Step 5.6: Configure Custom Domain (Optional)

- [ ] **5.6.1** If you have a custom domain:
  - Netlify dashboard → Domain settings
  - Add custom domain
  - Update DNS records as instructed

### Step 5.7: Enable HTTPS

- [ ] **5.7.1** Netlify should auto-provision SSL certificate
- [ ] **5.7.2** Verify site loads with https://
- [ ] **5.7.3** Enable "Force HTTPS" in domain settings

### Step 5.8: Update Documentation with Live URL

- [ ] **5.8.1** Update README.md with live demo link
- [ ] **5.8.2** Update SETUP.md with your deployment as example
- [ ] **5.8.3** Commit:
  ```bash
  git add README.md SETUP.md
  git commit -m "docs: Add live demo URL"
  git push origin main
  ```

**Phase 5 Complete! 🎉**

---

## Phase 6: Final Testing & Polish (Estimated: 2-3 hours)

### Step 6.1: Comprehensive Testing

- [ ] **6.1.1** Test on multiple browsers:
  - [ ] Chrome
  - [ ] Firefox
  - [ ] Safari
  - [ ] Edge

- [ ] **6.1.2** Test on multiple devices:
  - [ ] Desktop
  - [ ] Tablet
  - [ ] Mobile phone

- [ ] **6.1.3** Test all features systematically:
  - [ ] Load Genesis
  - [ ] Load each book
  - [ ] Filter by each figurative type
  - [ ] Search Hebrew text
  - [ ] Search English text
  - [ ] Metadata search (Target/Vehicle/Ground)
  - [ ] Sacred/non-sacred toggle
  - [ ] Hebrew keyboard
  - [ ] Click verse for deliberation
  - [ ] Click highlight for annotation
  - [ ] "Not Figurative" filter
  - [ ] "Select All" filter
  - [ ] Pagination

### Step 6.2: Performance Testing

- [ ] **6.2.1** Test load time (should be < 3 seconds)
- [ ] **6.2.2** Test search responsiveness
- [ ] **6.2.3** Check database query performance in Supabase logs
- [ ] **6.2.4** Verify lazy loading works

### Step 6.3: Accessibility Testing

- [ ] **6.3.1** Test keyboard navigation
- [ ] **6.3.2** Test with screen reader (if possible)
- [ ] **6.3.3** Verify color contrast meets WCAG standards
- [ ] **6.3.4** Check focus indicators

### Step 6.4: Create Demo Materials

- [ ] **6.4.1** Take screenshots of:
  - Home page with verses displayed
  - Filtering in action
  - Search results
  - Click interaction showing annotation
  - Hebrew keyboard
  - Mobile view

- [ ] **6.4.2** Create demo GIF or short video:
  - Screen recording showing key features
  - 1-2 minutes max
  - Upload to repository or YouTube

- [ ] **6.4.3** Add screenshots to README.md

### Step 6.5: Documentation Review

- [ ] **6.5.1** Proofread all documentation
- [ ] **6.5.2** Verify all links work
- [ ] **6.5.3** Check for broken images
- [ ] **6.5.4** Verify code examples are correct
- [ ] **6.5.5** Test setup instructions with fresh eyes

### Step 6.6: Security Review

- [ ] **6.6.1** Verify no secrets in repository (API keys, passwords)
- [ ] **6.6.2** Verify .gitignore is comprehensive
- [ ] **6.6.3** Check Supabase RLS policies are correct
- [ ] **6.6.4** Verify anon key is read-only

### Step 6.7: Final Commits

- [ ] **6.7.1** Commit any final changes
- [ ] **6.7.2** Create git tag for v1.0:
  ```bash
  git tag -a v1.0.0 -m "Version 1.0.0 - Initial public release"
  git push origin v1.0.0
  ```

**Phase 6 Complete! 🎉**

---

## Phase 7: Go Public! (Estimated: 1 hour + ongoing)

### Step 7.1: Make Repository Public

- [ ] **7.1.1** GitHub → Repository Settings → Danger Zone → Change visibility → Make public
- [ ] **7.1.2** Confirm making public

### Step 7.2: Configure Repository Settings

- [ ] **7.2.1** Add repository description
- [ ] **7.2.2** Add website URL (Netlify URL)
- [ ] **7.2.3** Add topics/tags:
  - `biblical-hebrew`
  - `figurative-language`
  - `digital-humanities`
  - `nlp`
  - `linguistics`
  - `biblical-studies`
  - `ai-analysis`
  - `research-tool`

- [ ] **7.2.4** Enable issues
- [ ] **7.2.5** Enable discussions (optional)

### Step 7.3: Create GitHub Release

- [ ] **7.3.1** GitHub → Releases → Create new release
- [ ] **7.3.2** Choose tag: v1.0.0
- [ ] **7.3.3** Release title: "v1.0.0 - Hebrew Figurative Language Explorer"
- [ ] **7.3.4** Description:
  ```markdown
  # First Public Release 🎉

  Complete interactive web interface for exploring AI-analyzed figurative language in the Hebrew Bible (Torah).

  ## Features
  - 5,846 analyzed verses from Genesis through Deuteronomy
  - [X] figurative language instances
  - Interactive filtering, search, and exploration
  - Hebrew and English dual-language support
  - Sacred and non-sacred text options

  ## Live Demo
  https://[your-netlify-url].netlify.app

  ## Installation
  See [SETUP.md](SETUP.md) for deployment instructions.

  ## Documentation
  - [README.md](README.md) - Project overview
  - [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database documentation
  - [METHODOLOGY.md](docs/METHODOLOGY.md) - Research methodology

  ## Citation
  [Include citation format from DECISION 3]
  ```

- [ ] **7.3.5** Attach database file (optional):
  - Create `torah_figurative_language_v1.0.0.db.zip`
  - Upload as release asset

- [ ] **7.3.6** Publish release

### Step 7.4: Announce (Week 1)

- [ ] **7.4.1** Day 1 - Reddit:
  - Post to r/DigitalHumanities
  - Post to r/biblestudy
  - Post to r/AcademicBiblical

- [ ] **7.4.2** Day 2 - Social Media:
  - Twitter/X
  - LinkedIn
  - Academic.edu profile

- [ ] **7.4.3** Day 3 - Academic Communities:
  - Email professors/researchers you know
  - Post in relevant Discord/Slack communities
  - Share on ResearchGate

- [ ] **7.4.4** Day 4 - Aggregators:
  - Submit to awesome-digital-humanities
  - Submit to awesome-bible-study (if exists)
  - Post on Hacker News "Show HN" (if appropriate)

- [ ] **7.4.5** Day 5 - Direct Outreach:
  - Email to specific scholars who might be interested
  - Contact digital humanities centers

### Step 7.5: Monitor & Respond

- [ ] **7.5.1** Set up GitHub notifications
- [ ] **7.5.2** Check issues daily
- [ ] **7.5.3** Respond to questions within 24-48 hours
- [ ] **7.5.4** Thank people for feedback and contributions
- [ ] **7.5.5** Track stars, forks, and website visits

### Step 7.6: First Week Maintenance

- [ ] **7.6.1** Fix any critical bugs immediately
- [ ] **7.6.2** Update FAQ based on common questions
- [ ] **7.6.3** Add contributors to CONTRIBUTORS.md
- [ ] **7.6.4** Create issues for suggested improvements
- [ ] **7.6.5** Blog post or Twitter thread about launch lessons

**Phase 7 Complete! Project is PUBLIC! 🎉🚀**

---

## Ongoing Maintenance Checklist

### Weekly
- [ ] Check and respond to GitHub issues
- [ ] Monitor Netlify analytics
- [ ] Check Supabase usage (ensure within free tier)
- [ ] Respond to emails/messages

### Monthly
- [ ] Review and merge community contributions
- [ ] Update documentation based on feedback
- [ ] Plan next version features
- [ ] Check for security updates

### Quarterly
- [ ] Major version update with bug fixes and improvements
- [ ] Blog post about project progress
- [ ] Reach out to academic institutions for partnerships
- [ ] Review and improve documentation

---

## Troubleshooting Common Issues

### Issue: Database migration fails
**Solution:** Export to CSV and import via Supabase dashboard instead

### Issue: Hebrew text not displaying on deployment
**Solution:** Verify font loading, check CORS, ensure UTF-8 encoding

### Issue: Slow query performance
**Solution:** Check indexes, optimize Supabase queries, add caching

### Issue: Netlify build fails
**Solution:** Verify `netlify.toml` is correct, check publish directory

### Issue: Supabase connection errors
**Solution:** Verify RLS policies, check API keys, confirm database is active

---

## Key Files Reference

| File | Purpose | Status |
|------|---------|--------|
| `PROJECT_OVERVIEW_AND_DECISIONS.md` | Decision guide | ✅ Complete |
| `PUBLIC_RELEASE_PLAN_UI_ONLY.md` | Detailed plan | ✅ Complete |
| `EXECUTION_CHECKLIST_NEXT_SESSION.md` | This file | ✅ Active |
| `backup-before-public-release-20250929` | Git backup branch | ✅ Complete |
| `web/biblical_figurative_interface.html` | Frontend | ⏳ Pending updates |
| `database/torah_figurative_language.db` | Database | ⏳ Pending creation |
| `README.md` | Public README | ⏳ Pending creation |

---

## Decision Tracking

Record decisions here as they're made:

| Decision | Choice | Date | Notes |
|----------|--------|------|-------|
| License | MIT + CC BY 4.0 | 09/30/2025 | Code under MIT, data under CC BY 4.0 |
| Repository Name | bible-figurative-language-concordance | 09/30/2025 | |
| Attribution | Ari Robicsek (BibTeX) | 09/30/2025 | Contact via GitHub issues |
| Architecture | Direct Supabase Client | 09/30/2025 | Simpler deployment |

---

## Session Notes

**Session 1 (Current - Sept 29, 2025):**
- ✅ Created backup branch
- ✅ Documented project overview and decisions
- ✅ Created execution checklist
- ⏹️ Next: Begin Phase 1 cleanup after decisions are made

**Session 2 (__/__/__):**
- Notes:

**Session 3 (__/__/__):**
- Notes:

---

## Quick Commands Reference

```bash
# Check backup exists
git log backup-before-public-release-20250929 -1

# Test database
sqlite3 database/torah_figurative_language.db "SELECT COUNT(*) FROM verses;"

# Run local server
cd web && python api_server.py

# Check git status
git status

# Commit progress
git add -A && git commit -m "progress: [description]"

# Deploy to Netlify (auto-deploys on push to main)
git push origin main
```

---

**Last Updated:** September 29, 2025
**Checklist Status:** Phase 0 complete, ready for Phase 1
**Next Action:** Review decisions, then begin Phase 1, Task 1.1