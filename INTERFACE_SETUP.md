# Biblical Figurative Language HTML Interface Setup Guide

## Overview
This interface provides an interactive web-based visualization of figurative language in your Hebrew biblical text database. It features real-time filtering, search, and detailed annotation display with both sacred and non-sacred text versions.

## Files Created
- **`biblical_figurative_interface.html`** - Main frontend interface
- **`api_server.py`** - Flask backend API server
- **`interface_requirements.txt`** - Python dependencies
- **`INTERFACE_SETUP.md`** - This setup guide

## Prerequisites
- Python 3.7+ installed
- Your database file: `2books_c63_multi_v_parallel_20250928_0934.db`
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Setup Instructions

### 1. Install Python Dependencies
```bash
cd "C:\Users\ariro\OneDrive\Documents\Bible"
pip install -r interface_requirements.txt
```

### 2. Verify Database Path
Ensure your database file is at the expected location:
```
C:\Users\ariro\OneDrive\Documents\Bible\2books_c63_multi_v_parallel_20250928_0934.db
```

If your database is elsewhere, edit `api_server.py` line 29:
```python
DB_PATH = r"C:\Path\To\Your\Database.db"
```

### 3. Start the API Server
```bash
python api_server.py
```

You should see output like:
```
Starting Biblical Figurative Language API Server...
Database: C:\Users\ariro\OneDrive\Documents\Bible\2books_c63_multi_v_parallel_20250928_0934.db
Access the interface at: http://localhost:5000
API Statistics: http://localhost:5000/api/statistics
 * Serving Flask app 'api_server'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

**Note**: The Unicode encoding warnings about Windows console are normal and don't affect functionality.

### 4. Open the Interface
Navigate to: **http://localhost:5000** in your web browser

## Features Overview

### 📖 Text Display
- **Dual-column layout**: English (left) and Hebrew (right)
- **Right-to-left Hebrew rendering** with proper Unicode support
- **Sacred vs Non-Sacred text versions** for both languages
- **Chapter and verse numbers** clearly displayed

### 🎭 Figurative Language Annotations
- **Color-coded underlines** for different figurative language types:
  - 🔴 **Metaphor** (red)
  - 🔵 **Simile** (blue)
  - 🟣 **Personification** (purple)
  - 🟠 **Idiom** (orange)
  - 🟤 **Hyperbole** (dark orange)
  - 🟢 **Metonymy** (teal)
  - ⚫ **Other** (gray)

### 🔍 Advanced Search & Filtering
1. **Book/Chapter/Verse Selection**:
   - Select multiple books: "Leviticus,Numbers"
   - Ranges: "1,3,5-7,10"
   - Full books: "all"

2. **Figurative Type Filtering**:
   - Toggle individual types on/off
   - Visual color indicators

3. **Text Version Toggle**:
   - Sacred/Non-sacred Hebrew
   - Sacred/Non-sacred English

4. **Multi-field Search**:
   - Hebrew text search
   - Target/Vehicle/Ground/Posture metadata search
   - AND/OR logic combinations

### 📱 Interactive Features
- **Click any verse header** → See AI deliberation and model info
- **Click any annotated text** → See detailed analysis:
  - Target, Vehicle, Ground breakdown
  - Explanation and confidence score
  - Speaker identification
  - Validation reasons
- **Load more** button for pagination
- **Responsive design** works on tablets/phones

## Usage Examples

### Example 1: Find all metaphors in Leviticus chapter 1
1. Select "Leviticus" in Books
2. Enter "1" in Chapters
3. Uncheck all figurative types except "Metaphor"
4. Click "Load Verses"

### Example 2: Search for divine imagery
1. Enter "God" in the Target search field
2. Enter "divine" in the Vehicle search field
3. Set operator to "OR"
4. View results with divine metaphors

### Example 3: Compare sacred vs non-sacred texts
1. Load some verses
2. Toggle between "Sacred Names" and "Traditional Jewish" options
3. Notice the divine name modifications (יהוה → ה׳)

## API Endpoints (for advanced users)

### GET /api/verses
Main verse retrieval with filtering:
```
http://localhost:5000/api/verses?books=leviticus&chapters=1&figurative_types=metaphor,simile
```

### GET /api/statistics
Database statistics:
```
http://localhost:5000/api/statistics
```

### GET /api/search/suggestions
Autocomplete for search fields:
```
http://localhost:5000/api/search/suggestions?field=target&query=god
```

## Database Schema Compatibility
The interface works with your existing database schema:
- **verses table**: Basic verse information and deliberations
- **figurative_language table**: Annotations and metadata
- **JSON fields**: Target, Vehicle, Ground, Posture hierarchies
- **Model tracking**: Which AI model processed each verse

## Performance Notes
- **Pagination**: Loads 50 verses at a time by default
- **Client-side caching**: Minimizes repeated API calls
- **Efficient queries**: Indexed database searches
- **Responsive loading**: Visual feedback during data fetches

## Troubleshooting

### "Failed to load verses" error
1. Ensure `api_server.py` is running
2. Check database path in `api_server.py`
3. Verify database file exists and is readable

### Hebrew text not displaying properly
1. Ensure your browser supports Unicode
2. Check that Hebrew fonts are installed
3. Try a different browser (Chrome recommended)

### Search not working
1. Check API server console for errors
2. Verify search terms are not empty
3. Try simpler search queries first

### Performance issues
1. Reduce number of verses loaded (use chapter/verse filters)
2. Limit figurative types shown
3. Close other browser tabs

## Customization Options

### Change color scheme
Edit CSS variables in the `<style>` section of the HTML file:
```css
:root {
    --metaphor-color: #your-color;
    --simile-color: #your-color;
    /* etc. */
}
```

### Modify pagination
Change default page size in `api_server.py`:
```python
limit = int(request.args.get('limit', 100))  # Changed from 50
```

### Add new search fields
Extend the API in `api_server.py` and add corresponding HTML inputs.

## Future Enhancements
- Export to PDF/CSV functionality
- Audio pronunciation for Hebrew
- Advanced statistical dashboards
- User annotation capabilities
- Multi-book comparative analysis

## Support
For technical issues:
1. Check the browser console for JavaScript errors
2. Check the Python console for API errors
3. Verify database integrity with your existing tools
4. Test with a smaller dataset first

---

**🎉 Your biblical figurative language interface is now ready for scholarly research and exploration!**