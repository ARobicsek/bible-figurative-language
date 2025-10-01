# Setup Guide

Complete setup instructions for Tzafun.

---

## Table of Contents

1. [Option 1: Use the Hosted Version](#option-1-use-the-hosted-version-recommended)
2. [Option 2: Run Locally](#option-2-run-locally)
3. [Option 3: Deploy Your Own](#option-3-deploy-your-own)
4. [Troubleshooting](#troubleshooting)
5. [System Requirements](#system-requirements)

---

## Option 1: Use the Hosted Version (Recommended)

The easiest way to use Tzafun is through our hosted version.

**[Access the live demo →](#)** *(Link will be added after deployment)*

**Features:**
- ✅ No installation required
- ✅ Always up-to-date
- ✅ Instant access from any device
- ✅ Full database access
- ✅ All search and filtering features

**Requirements:**
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection

---

## Option 2: Run Locally

Run the application on your local machine for offline access or development.

### Prerequisites

- **Python 3.8 or higher**
- Modern web browser
- 50 MB free disk space

### Installation Steps

#### 1. Clone or Download the Repository

```bash
# Using git
git clone https://github.com/[username]/bible-figurative-language-concordance.git
cd bible-figurative-language-concordance

# Or download and extract the ZIP file from GitHub
```

#### 2. Install Python Dependencies

```bash
# Install required packages
pip install -r web/requirements.txt
```

**Required packages:**
- Flask (web server)
- Flask-CORS (cross-origin requests)
- sqlite3 (included with Python)

#### 3. Verify Database

Ensure the database file exists:
```bash
# Check that the database file is present
ls database/torah_figurative_language.db
```

The database should be approximately 35 MB and contains all 5,846 verses.

#### 4. Start the Server

```bash
# Start the Flask API server
python web/api_server.py
```

You should see:
```
Starting Biblical Figurative Language API Server...
Database: [path]/database/torah_figurative_language.db
Access the interface at: http://localhost:5000
API Statistics: http://localhost:5000/api/statistics
```

#### 5. Access the Interface

Open your web browser and navigate to:
```
http://localhost:5000
```

### Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

### Using Different Databases

If you have multiple database files in the `database/` directory:

1. Access the interface at `http://localhost:5000`
2. Use the **Database** dropdown in the sidebar
3. Select your desired database
4. The interface will reload with the new database

---

## Option 3: Deploy Your Own

Deploy your own instance using Supabase (database) and Netlify (hosting).

### Architecture Overview

- **Frontend**: Static HTML/CSS/JavaScript (hosted on Netlify)
- **Database**: PostgreSQL via Supabase
- **API**: Direct Supabase client calls (no separate backend needed)

### Part A: Database Setup (Supabase)

#### 1. Create Supabase Project

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Note your project URL and API keys

#### 2. Create Database Schema

Execute this SQL in the Supabase SQL Editor:

```sql
-- Create verses table
CREATE TABLE verses (
    id INTEGER PRIMARY KEY,
    reference TEXT NOT NULL,
    book TEXT NOT NULL,
    chapter INTEGER NOT NULL,
    verse INTEGER NOT NULL,
    hebrew_text TEXT,
    hebrew_text_stripped TEXT,
    hebrew_text_non_sacred TEXT,
    english_text TEXT,
    english_text_non_sacred TEXT,
    figurative_detection_deliberation TEXT,
    model_used TEXT
);

-- Create figurative_language table
CREATE TABLE figurative_language (
    id INTEGER PRIMARY KEY,
    verse_id INTEGER REFERENCES verses(id),
    figurative_text TEXT,
    figurative_text_in_hebrew TEXT,
    figurative_text_in_hebrew_non_sacred TEXT,
    final_metaphor TEXT,
    final_simile TEXT,
    final_personification TEXT,
    final_idiom TEXT,
    final_hyperbole TEXT,
    final_metonymy TEXT,
    final_other TEXT,
    final_figurative_language TEXT,
    target TEXT,
    vehicle TEXT,
    ground TEXT,
    posture TEXT,
    explanation TEXT,
    speaker TEXT,
    confidence REAL,
    validation_reason_metaphor TEXT,
    validation_reason_simile TEXT,
    validation_reason_personification TEXT,
    validation_reason_idiom TEXT,
    validation_reason_hyperbole TEXT,
    validation_reason_metonymy TEXT,
    validation_reason_other TEXT,
    model_used TEXT
);

-- Create indexes for performance
CREATE INDEX idx_verses_book ON verses(book);
CREATE INDEX idx_verses_chapter ON verses(chapter);
CREATE INDEX idx_verses_verse ON verses(verse);
CREATE INDEX idx_figurative_verse_id ON figurative_language(verse_id);
CREATE INDEX idx_figurative_types ON figurative_language(
    final_metaphor, final_simile, final_personification,
    final_idiom, final_hyperbole, final_metonymy, final_other
);
```

#### 3. Import Data

**Option 3A: Using SQLite to PostgreSQL Migration**

```bash
# Install sqlite-to-postgres converter
npm install -g sqlite-to-postgres

# Convert the database
sqlite-to-postgres \
  --source database/torah_figurative_language.db \
  --target postgres://[user]:[password]@[host]/[database]
```

**Option 3B: Using CSV Export/Import**

```bash
# Export from SQLite
sqlite3 database/torah_figurative_language.db <<EOF
.mode csv
.output verses.csv
SELECT * FROM verses;
.output figurative_language.csv
SELECT * FROM figurative_language;
EOF

# Then import the CSV files using Supabase dashboard
# Go to: Database → Table Editor → Import CSV
```

#### 4. Configure Row-Level Security

Enable read-only public access:

```sql
-- Enable RLS
ALTER TABLE verses ENABLE ROW LEVEL SECURITY;
ALTER TABLE figurative_language ENABLE ROW LEVEL SECURITY;

-- Allow anonymous read access
CREATE POLICY "Allow public read access" ON verses
    FOR SELECT TO anon USING (true);

CREATE POLICY "Allow public read access" ON figurative_language
    FOR SELECT TO anon USING (true);
```

### Part B: Frontend Setup (Netlify)

#### 1. Prepare Frontend Files

Create a new directory for deployment:

```bash
mkdir -p deploy
cp web/biblical_figurative_interface.html deploy/index.html
```

#### 2. Update Supabase Configuration

Edit `deploy/index.html` and replace the API configuration section:

```javascript
// Find this line (around line 885):
const API_BASE = 'http://localhost:5000/api';

// Replace with Supabase configuration:
const SUPABASE_URL = 'https://[your-project].supabase.co';
const SUPABASE_ANON_KEY = '[your-anon-key]';

// Then update the API functions to use Supabase client
// (See the Supabase JavaScript documentation for query syntax)
```

#### 3. Deploy to Netlify

**Option 3A: Using Netlify CLI**

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd deploy
netlify deploy --prod
```

**Option 3B: Using Netlify Dashboard**

1. Go to [netlify.com](https://netlify.com)
2. Drag and drop the `deploy` folder
3. Or connect your GitHub repository for continuous deployment

#### 4. Configure Environment Variables

In Netlify dashboard:
1. Go to Site Settings → Environment Variables
2. Add:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_ANON_KEY`: Your Supabase anonymous key

### Part C: Post-Deployment

#### Test Your Deployment

1. Visit your Netlify URL
2. Verify database connection
3. Test search functionality
4. Check statistics endpoint

#### Update Documentation

Update these files with your deployment URLs:
- `README.md` (demo link)
- `CITATION.cff` (repository URL)
- Any other references to the live demo

---

## Troubleshooting

### Local Setup Issues

**Problem**: `pip install` fails
- **Solution**: Upgrade pip: `pip install --upgrade pip`
- Try: `pip install --user -r web/requirements.txt`

**Problem**: Database not found
- **Solution**: Verify the database path in `web/api_server.py`
- Check that `database/torah_figurative_language.db` exists

**Problem**: Port 5000 already in use
- **Solution**: Edit `web/api_server.py` and change the port:
  ```python
  app.run(debug=True, host='0.0.0.0', port=5001)
  ```

**Problem**: Browser shows blank page
- **Solution**: Check browser console for errors (F12)
- Verify the API server is running
- Check CORS settings in `api_server.py`

### Deployment Issues

**Problem**: Supabase queries timing out
- **Solution**: Add indexes to frequently queried columns
- Consider enabling query caching
- Check connection pooling settings

**Problem**: Database import fails
- **Solution**: Split large tables into smaller batches
- Verify data types match between SQLite and PostgreSQL
- Check character encoding (UTF-8)

**Problem**: Frontend can't connect to Supabase
- **Solution**: Verify Supabase URL and API key
- Check browser console for CORS errors
- Ensure RLS policies are correctly configured

### Performance Optimization

**For large result sets:**
1. Implement pagination in queries
2. Add database indexes for common searches
3. Enable query result caching
4. Consider using connection pooling

**For slow searches:**
1. Add indexes on Hebrew and English text columns
2. Use full-text search (FTS) for text queries
3. Optimize metadata JSON field queries

---

## System Requirements

### Local Setup

**Minimum:**
- CPU: 1 GHz dual-core
- RAM: 2 GB
- Storage: 100 MB free space
- Python 3.8+

**Recommended:**
- CPU: 2 GHz quad-core
- RAM: 4 GB
- Storage: 500 MB free space
- Python 3.10+

### Self-Hosted Deployment

**Supabase (Free Tier):**
- 500 MB database storage
- 2 GB bandwidth/month
- Unlimited API requests

**Netlify (Free Tier):**
- 100 GB bandwidth/month
- Unlimited sites
- Automatic HTTPS

### Browser Compatibility

**Fully Supported:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

**Partial Support:**
- Chrome 80-89
- Firefox 78-87
- Safari 13

---

## Additional Resources

### Documentation

- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) - Database structure
- [METHODOLOGY.md](docs/METHODOLOGY.md) - Analysis methodology
- [FEATURES.md](docs/FEATURES.md) - Interface guide
- [FAQ.md](docs/FAQ.md) - Frequently asked questions

### External Links

- [Supabase Documentation](https://supabase.com/docs)
- [Netlify Documentation](https://docs.netlify.com)
- [Flask Documentation](https://flask.palletsprojects.com)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### Community

- [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues)
- [GitHub Discussions](https://github.com/[username]/bible-figurative-language-concordance/discussions)

---

## Security Considerations

### Local Setup
- Server binds to all interfaces (`0.0.0.0`) for local network access
- No authentication required for local use
- Keep your Python packages updated

### Self-Hosted Deployment
- Enable Supabase RLS for read-only access
- Use environment variables for sensitive data
- Enable HTTPS (automatic with Netlify)
- Monitor API usage to prevent abuse
- Consider rate limiting for public deployments

---

## Next Steps

After setup, explore:
- [FEATURES.md](docs/FEATURES.md) for usage guide
- [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) for query examples
- [CONTRIBUTING.md](CONTRIBUTING.md) to contribute improvements

---

**Questions or issues?** Open an issue on [GitHub Issues](https://github.com/[username]/bible-figurative-language-concordance/issues)
