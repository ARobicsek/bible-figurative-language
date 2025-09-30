# Hebrew Figurative Language Explorer: Project Overview & Decision Points

## Executive Summary

This document provides a comprehensive overview of the Hebrew Figurative Language Explorer project, its technical architecture, scope, and strategic decision points for public release. Use this to discuss the project with collaborators, advisors, or stakeholders.

---

## 🎯 Project Vision & Goals

### Primary Goal
Create an accessible, web-based research tool that allows scholars, students, and enthusiasts to explore AI-analyzed figurative language patterns in the Hebrew Bible (Torah).

### Core Objectives
1. **Accessibility**: Make biblical Hebrew figurative language research accessible to non-programmers
2. **Transparency**: Provide complete AI reasoning and validation methodology for scholarly confidence
3. **Innovation**: Demonstrate advanced AI application in digital humanities and biblical studies
4. **Preservation**: Share high-quality research data that took significant computational resources to generate
5. **Community**: Enable validation, feedback, and collaborative improvement of classifications

### Target Audience
- **Biblical scholars**: Researching figurative language patterns in Hebrew scripture
- **Linguists**: Studying ancient Hebrew rhetoric and semantics
- **Digital humanities researchers**: Interested in AI-assisted textual analysis
- **Educators**: Teaching biblical Hebrew or figurative language
- **Students**: Working on research projects in biblical studies
- **General public**: Interested in exploring Hebrew Bible with modern tools

---

## 📊 Current Project State

### What We Have Built

#### 1. **Processing Pipeline (PRIVATE - Not Being Shared)**
- **Three-tier AI architecture**: Gemini 2.5 Flash → Gemini 2.5 Pro → Claude Sonnet 4
- **Automatic fallback system**: Handles truncation, complexity, API errors
- **Parallel processing**: 12-worker concurrent processing with intelligent load balancing
- **Complete validation pipeline**: Separate AI validation pass with reclassification
- **Model tracking**: Records which AI model processed each instance for transparency
- **Non-sacred text generation**: Automatic Hebrew divine name modification for traditional Jewish users

**Why not sharing:** API costs (~$X spent analyzing 5,846 verses). Cannot afford to provide public access to annotation pipeline.

#### 2. **Database (SHARING - Complete Torah)**
- **5,846 verses** analyzed from Genesis through Deuteronomy
- **3,020 figurative language instances** identified and validated (need to count)
- **7 figurative types**: Metaphor, Simile, Personification, Idiom, Hyperbole, Metonymy, Other
- **Dual-language support**: Hebrew with vowel points + English translations
- **Rich metadata**: Target, Vehicle, Ground, Posture hierarchical classifications
- **Complete audit trail**: Detection deliberation, validation reasoning, confidence scores
- **Model transparency**: Every instance tagged with the AI model that analyzed it

**Database size:** ~30 MB SQLite (~50 MB with indexes)

#### 3. **Web Interface (SHARING - Production Ready)**
- **Dual-column display**: Hebrew (RTL) and English side-by-side
- **Advanced filtering**:
  - By book, chapter, verse
  - By figurative type (with multi-select)
  - "Not Figurative" option to view verses WITHOUT figurative language
  - "Select All" to view ALL verses (figurative + non-figurative)
- **Dual-language search**: Hebrew and English text search with highlighting
- **Metadata search**: Filter by Target/Vehicle/Ground/Posture with multi-term support
- **Sacred/Non-sacred toggle**: Switch between original and modified Hebrew text versions
- **Interactive annotations**: Click verses for AI deliberations, click highlights for detailed analysis
- **Hebrew virtual keyboard**: On-screen keyboard for Hebrew input
- **Mobile responsive**: Works on all devices
- **Performance optimized**: Lazy loading, background counting, smart pagination

**Technologies:** HTML/CSS/JavaScript, Flask (Python backend), SQLite database

---

## 🏗️ Technical Architecture

### Current (Local Development)

```
User Browser
     ↓
biblical_figurative_interface.html (Frontend)
     ↓
api_server.py (Flask Backend)
     ↓
complete_torah_merged.db (SQLite)
```

**Pros:**
- Simple setup
- Works offline
- No ongoing costs

**Cons:**
- Requires Python installation
- Single-user only
- Not accessible to non-technical users

### Planned (Public Deployment)

#### Option A: Netlify + Supabase (RECOMMENDED)

```
User Browser
     ↓
Netlify (Static HTML + JS)
     ↓
Supabase Client (JavaScript SDK)
     ↓
Supabase PostgreSQL (Hosted Database)
```

**Pros:**
- **Zero cost** for expected traffic (free tier: 500MB DB, 5GB bandwidth/month)
- No server management required
- Global CDN for fast loading
- Automatic HTTPS
- Database automatically generates REST API
- Row-level security for read-only public access

**Cons:**
- Need to migrate SQLite → PostgreSQL
- Frontend code changes required (add Supabase client)
- Small vendor lock-in (but easy to export)

#### Option B: Netlify + Supabase + Netlify Functions (Hybrid)

```
User Browser
     ↓
Netlify (Static HTML)
     ↓
Netlify Functions (Serverless API)
     ↓
Supabase PostgreSQL
```

**Pros:**
- Keeps Flask-like API structure
- More control over queries
- Can add custom logic/validation

**Cons:**
- More complex to set up
- Additional code to maintain
- Slightly slower (extra hop)

**When to use:** If we need server-side processing or want to abstract database details

#### Option C: Alternative Stacks (Not Recommended for Now)

- **Vercel + PlanetScale**: Similar to Netlify + Supabase, MySQL instead of PostgreSQL
- **GitHub Pages + JSON**: Export database to static JSON (simple but slow, large file)
- **AWS Free Tier**: More complex, requires more technical knowledge

---

## 🎨 What Users Will Experience

### User Journey

1. **Discovery**: User finds project via GitHub, academic paper, or recommendation
2. **Access**: Clicks link to hosted demo → opens instantly in browser
3. **Exploration**:
   - Select book (Genesis, Exodus, etc.)
   - Apply filters (metaphors only, Deuteronomy chapters 1-5, etc.)
   - Search Hebrew or English text
   - Search by metadata (e.g., "all instances where God is the target")
4. **Deep Dive**:
   - Click verse to see full AI deliberation
   - Click highlighted text to see Target/Vehicle/Ground analysis
   - Toggle between sacred and non-sacred Hebrew text
5. **Export** (future): Download filtered results as CSV/JSON
6. **Feedback**: Report incorrect classifications via GitHub issues

### Key Features Showcase

**For Scholars:**
- "Show me all metaphors in Genesis where God is the target and a shepherd is the vehicle"
- "Find all instances of personification in legal texts (Leviticus)"
- "Compare figurative language density across different books"

**For Students:**
- "What figurative language appears in Genesis 1-3?"
- "How does the Hebrew text differ from English translation in this verse?"
- "What did the AI think about this classification?"

**For Jewish Users:**
- Toggle to non-sacred text for studying/printing without concern

---

## 📋 Decision Points for Discussion

### DECISION 1: License Choice

**Why it matters:** Determines how others can use your work and whether you get credit.

**Options:**

#### Option A: MIT License + CC BY 4.0 (RECOMMENDED)
- **MIT License** for code (interface, scripts)
  - Most permissive
  - Allows commercial use
  - Only requires attribution
  - Used by most open-source projects
- **CC BY 4.0** for database and documentation
  - Requires attribution when used in research
  - Standard for academic data sharing
  - Allows commercial use with credit

**Pros:**
- Maximum accessibility and reuse
- Encourages adoption and citation
- Industry standard
- Compatible with academic integrity requirements

**Cons:**
- Someone could commercialize without sharing profits (but must credit you)
- Cannot prevent misuse (but attribution required)

#### Option B: GPL v3 + CC BY-SA 4.0
- **GPL v3** for code
  - "Copyleft" - derivatives must also be open source
  - Prevents proprietary forks
- **CC BY-SA 4.0** for database
  - "ShareAlike" - derivatives must use same license

**Pros:**
- Ensures improvements stay open source
- Prevents proprietary commercial use
- Aligns with free software philosophy

**Cons:**
- More restrictive, may reduce adoption
- Not compatible with some academic uses
- Harder for commercial collaboration

#### Option C: Custom License
- Write your own terms

**Pros:**
- Complete control

**Cons:**
- Not standard, may confuse users
- Legal review recommended
- Lower trust from community

**Recommendation:** **MIT + CC BY 4.0** for maximum academic impact while ensuring attribution.

---

### DECISION 2: Repository Name

**Why it matters:** First impression, discoverability, branding.

**Options:**

#### Option A: `hebrew-figurative-language-explorer` (RECOMMENDED)
**Pros:**
- Descriptive and clear
- Good for SEO and search
- Professional tone

**Cons:**
- Long URL
- Not catchy/memorable

#### Option B: `torah-rhetoric-database`
**Pros:**
- Shorter
- Academic tone
- Emphasizes content

**Cons:**
- "Rhetoric" is less specific than "figurative language"
- May not be immediately clear what it contains

#### Option C: `biblical-hebrew-figures`
**Pros:**
- Short and memorable
- Broad appeal

**Cons:**
- Less specific
- Could be misunderstood

#### Option D: `hebrew-bible-ai-analysis`
**Pros:**
- Emphasizes AI innovation
- Broader scope (allows future expansion)

**Cons:**
- Less focused on figurative language specifically

**Recommendation:** **`hebrew-figurative-language-explorer`** - Clear, professional, descriptive.

**Note:** GitHub allows you to change repository name later, but it breaks existing links.

---

### DECISION 3: Attribution & Credit

**Why it matters:** How you're credited in academic papers, how to contact you, building reputation.

**What to decide:**

1. **Your name/affiliation:**
   - Real name vs. pseudonym?
   - Include current affiliation (institution, if applicable)?
   - Professional title or credentials?

2. **Citation format:**
   ```bibtex
   @software{hebrew_figurative_language_2025,
     author = {[YOUR NAME]},
     title = {Hebrew Figurative Language Explorer: An AI-Analyzed Database of Torah Figurative Language},
     year = {2025},
     url = {https://github.com/[username]/hebrew-figurative-language-explorer},
     note = {Version 1.0}
   }
   ```

3. **Contact method:**
   - GitHub issues only (most private)?
   - Professional email?
   - LinkedIn?
   - Academic profile page?

4. **Acknowledgments:**
   - Mention collaborators/advisors?
   - Funding sources?
   - Inspiration/prior work?

**Considerations:**
- **Academic career**: If you plan to publish papers using this, ensure proper citation format
- **Privacy**: GitHub username already public, but email/affiliation is optional
- **Collaboration**: If you want partnerships, provide professional contact method
- **Credit sharing**: If others contributed significantly, acknowledge them

---

### DECISION 4: Frontend Architecture (Flask vs. Direct Supabase)

**Why it matters:** Determines deployment complexity, maintenance burden, and what you need to learn.

#### Option A: Direct Supabase Client (RECOMMENDED)

**Architecture:**
```javascript
// In HTML file, directly call Supabase
const { data, error } = await supabase
  .from('verses')
  .select('*')
  .eq('book', 'Genesis');
```

**Pros:**
- **Simpler deployment**: Just HTML + Supabase (no backend server)
- **Lower latency**: One fewer hop
- **Less code to maintain**: No Flask server
- **Auto-generated API**: Supabase creates REST/GraphQL APIs automatically
- **Built-in features**: Real-time subscriptions, automatic caching

**Cons:**
- **Frontend changes required**: Rewrite all API calls
- **Less abstraction**: Database structure somewhat exposed
- **Learning curve**: Need to learn Supabase SDK (not difficult)

**When to use:** For most use cases. Recommended unless you need custom server logic.

#### Option B: Keep Flask + Supabase Backend

**Architecture:**
```
Frontend → Netlify Functions (Flask-like) → Supabase
```

**Pros:**
- **Minimal frontend changes**: Keep existing API calls mostly intact
- **Custom logic**: Can add validation, rate limiting, custom queries
- **Abstraction**: Hide database details from frontend
- **Familiar**: You already know Flask

**Cons:**
- **More complex**: Need to port Flask → Netlify Functions
- **Extra hop**: Slight latency increase
- **More code**: Additional layer to maintain
- **Serverless limits**: Functions have timeout/memory limits

**When to use:** If you need custom server-side logic or want to keep database structure hidden.

#### Option C: Hybrid Approach

**Architecture:**
- Simple queries: Direct Supabase client
- Complex queries: Netlify Functions

**When to use:** Best of both worlds, but most complex to set up.

**Recommendation:** **Option A (Direct Supabase)** - Simplest and most maintainable. The frontend changes are straightforward, and Supabase handles everything else.

---

## 🔮 Future Expansion Possibilities

### Phase 2 Features (After Initial Launch)
- **Sankey visualization**: Target→Vehicle flow diagrams (already planned in roadmap)
- **Data export**: CSV/JSON download of filtered results
- **Bookmarking**: Save favorite verses or searches
- **Comparison view**: Side-by-side comparison of multiple verses
- **Advanced analytics**: Statistics on figurative language distribution

### Phase 3 Features (Long-term)
- **User accounts**: Save personal annotations and notes
- **Community validation**: Crowdsourced verification of classifications
- **Expanded corpus**: Other biblical books (Prophets, Writings)
- **Multi-language**: Interface in other languages (Spanish, French, etc.)
- **API access**: Programmatic access for researchers
- **Integration**: Plugin for Bible study software (Logos, Accordance)

### Alternative Directions
- **Academic publication**: Publish methodology paper with dataset
- **Educational platform**: Structured curriculum for learning figurative language
- **Comparative analysis**: Expand to other ancient texts (Quran, ancient Greek texts)
- **Custom analysis**: Paid service for analyzing other texts

---

## 💰 Cost Analysis

### Development Costs (Already Spent)
- **Your time**: Significant (months of development and refinement)
- **API costs**:
  - Gemini API: ~$X for 5,846 verses
  - Claude API: ~$Y for fallback processing
  - Total: ~$Z
- **Development tools**: GitHub, local development environment (minimal/free)

### Ongoing Costs (Proposed Free Tier Setup)

#### Supabase Free Tier
- **Database**: 500 MB (our database: ~50 MB = ✅ fits comfortably)
- **Bandwidth**: 5 GB/month
- **API calls**: Unlimited on free tier
- **Storage**: 1 GB
- **Cost**: **$0/month**

**When you'd need to upgrade** (Supabase Pro: $25/month):
- Database grows beyond 500 MB (would need >5x more data)
- Traffic exceeds 5 GB/month (roughly 100,000 verse loads/month)

#### Netlify Free Tier
- **Bandwidth**: 100 GB/month
- **Build minutes**: 300/month (not relevant for static site)
- **Sites**: Unlimited
- **Cost**: **$0/month**

**When you'd need to upgrade** (Netlify Pro: $19/month):
- Traffic exceeds 100 GB/month (unlikely for this use case)

#### Total Monthly Cost
- **Free tier**: **$0/month** (sufficient for expected academic/research traffic)
- **If it becomes very popular**: $25-44/month (Supabase Pro + maybe Netlify Pro)
- **Scaling costs**: Grows with traffic, but you can add donation button or apply for grants

### Monetization Options (If Needed in Future)
1. **Donations**: Ko-fi, GitHub Sponsors, PayPal button
2. **Academic grants**: NEH Digital Humanities, NSF
3. **Institutional sponsorship**: Partner with seminary or university
4. **Freemium**: Basic free, premium features for $5-10/month
5. **Consulting**: Paid custom analysis services

---

## 🎓 Academic Impact Potential

### Publication Opportunities
- **Data paper**: Journal of Open Humanities Data, Digital Scholarship in the Humanities
- **Methodology paper**: Digital Humanities Quarterly, Journal of Biblical Literature
- **Application paper**: Computers and the Humanities, LLC Journal
- **Conference presentations**: Society of Biblical Literature (SBL), DH conferences

### Citation Value
- **Citeable dataset**: Zenodo DOI for the database
- **Citeable software**: GitHub release with DOI
- **Research applications**: Others can cite your work when using the data

### Scholarly Contributions
1. **Methodological innovation**: Three-tier AI architecture for biblical text analysis
2. **Dataset creation**: First comprehensive AI-analyzed Torah figurative language database
3. **Tool development**: Accessible interface for non-technical scholars
4. **Validation framework**: Transparent AI validation methodology
5. **Cultural sensitivity**: Non-sacred text feature for Jewish scholars

---

## ⚖️ Ethical Considerations

### AI Transparency
- **Full disclosure**: Clearly state AI-generated classifications
- **Methodology documentation**: Explain three-tier architecture and validation
- **Model tracking**: Every instance shows which model analyzed it
- **Limitations**: Acknowledge AI can make mistakes, human validation recommended

### Cultural Sensitivity
- **Jewish tradition**: Non-sacred text option respects traditional practices
- **Multiple interpretations**: Interface doesn't claim definitive interpretation
- **Source attribution**: All text from Sefaria (open-source Jewish texts)
- **Scholarly tone**: Avoid claims that might offend religious sensibilities

### Data Integrity
- **Audit trail**: Complete reasoning stored for every classification
- **Versioning**: Database tagged with version numbers for reproducibility
- **Corrections**: Process for community to report errors and corrections
- **Transparency**: Clear about what data is included and what isn't

### Access Equity
- **Free access**: No paywalls for basic functionality
- **Open source**: Code available for inspection and learning
- **No registration required**: Use without creating account (privacy-preserving)
- **Offline capable**: Can run locally for users without reliable internet

---

## 📈 Success Metrics

### Launch Goals (First 3 Months)
- [ ] 100+ GitHub stars
- [ ] 10+ citations or mentions in academic work
- [ ] 50+ weekly active users
- [ ] 5+ community contributions (bug reports, validation feedback)
- [ ] 0 major security or data integrity issues

### Long-term Goals (First Year)
- [ ] 500+ GitHub stars
- [ ] Published academic paper using the dataset
- [ ] 200+ weekly active users
- [ ] 20+ forks or derivatives
- [ ] Featured in digital humanities newsletter or blog
- [ ] Partnership with academic institution

### Impact Indicators
- **Academic citations**: Papers citing the dataset or methodology
- **Educational use**: Professors using in courses
- **Community engagement**: Active issues, discussions, contributions
- **Derivative work**: Others building on the platform
- **Media coverage**: Mentions in academic or tech media

---

## 🚀 Launch Strategy

### Pre-Launch
1. ✅ Complete repository cleanup
2. ✅ Create comprehensive documentation
3. ✅ Deploy to Netlify + Supabase
4. ✅ Test all features
5. ✅ Create demo video

### Launch Week
1. **Day 1**: Make repository public
2. **Day 2**: Post on r/DigitalHumanities, r/biblestudy
3. **Day 3**: Share on academic Twitter/X
4. **Day 4**: Submit to awesome-lists (awesome-digital-humanities, etc.)
5. **Day 5**: Email relevant professors/researchers personally
6. **Day 7**: Write blog post about methodology and lessons learned

### Post-Launch
- Monitor GitHub issues and respond within 24-48 hours
- Engage with community feedback
- Fix critical bugs immediately
- Plan first update (bug fixes, small improvements)
- Consider submitting to Product Hunt (if appropriate)

---

## 🤔 Questions for Discussion with Others

### Strategic Questions
1. Should this be positioned primarily as a **research tool** or **educational resource**?
2. Is there value in seeking **institutional partnership** (university, seminary) before launch?
3. Should we pursue **academic publication** simultaneously with public release?
4. What level of **support commitment** can you realistically provide (hours/week)?

### Technical Questions
1. Do you have someone who can review security/database design before launch?
2. Should we implement **analytics** (e.g., Google Analytics) to track usage, or prioritize privacy?
3. Is there a **backup plan** if hosting costs exceed free tier?

### Legal/Ethical Questions
1. Any concerns about **copyright** for Hebrew/English texts (Sefaria is open, but good to confirm)?
2. Should there be a **terms of use** or **disclaimer** about AI-generated content?
3. Any **institutional review** or approval needed (if affiliated with university)?

### Community Questions
1. Who are the **first 10 people** you'd want to share this with for feedback?
2. Are there specific **communities or forums** where this would be particularly welcome?
3. Should we do a **private beta** with select scholars before public launch?

---

## 📞 Next Steps: Decision-Making Process

### Recommended Approach

**Week 1: Information Gathering**
- Share this document with trusted advisors/colleagues
- Get feedback on strategic direction
- Research similar projects (how did they launch?)
- Check if any institutional policies apply

**Week 2: Decisions**
- Make final decisions on 4 decision points above
- Document rationale for each decision
- Get buy-in from any necessary stakeholders

**Week 3: Execution Prep**
- Set up Supabase account
- Create Netlify account
- Practice deployment with test database
- Finalize documentation

**Week 4: Launch**
- Execute launch checklist
- Monitor for issues
- Engage with early users

---

## 📝 Summary: What You Need to Decide

| Decision | Options | Recommendation | Impact |
|----------|---------|----------------|--------|
| **License** | MIT+CC BY 4.0 / GPL+CC BY-SA / Custom | MIT + CC BY 4.0 | Legal, reuse |
| **Repository Name** | hebrew-figurative-language-explorer / torah-rhetoric-database / biblical-hebrew-figures / other | hebrew-figurative-language-explorer | Branding, SEO |
| **Attribution** | Name, affiliation, contact method | Your choice | Credit, networking |
| **Architecture** | Direct Supabase / Flask proxy / Hybrid | Direct Supabase | Complexity, maintenance |

### Optional Decisions (Can Decide Later)
- Analytics: Yes or No?
- Private beta: Yes or No?
- Monetization: If yes, when and how?
- Academic publication: Simultaneously or after?

---

## 🎉 Why This Project Matters

This project represents:
- **Methodological innovation** in applying AI to ancient texts
- **Democratization** of biblical Hebrew scholarship
- **Transparency** in AI-assisted research
- **Cultural sensitivity** in digital humanities
- **Open scholarship** enabling future research

By sharing this work, you're contributing to:
1. Advancing digital humanities methods
2. Making biblical scholarship more accessible
3. Enabling future research on figurative language
4. Demonstrating responsible AI application
5. Building open-source tools for religious studies

The combination of rigorous methodology, cultural sensitivity, and accessibility makes this a valuable contribution to multiple fields.

---

**Document Version:** 1.0 (September 29, 2025)
**Status:** Ready for discussion and decision-making
**Next Review:** After decisions are made and before execution begins