# 📊 Interactive Sankey Visualization Roadmap

## Project Overview
Create an interactive Sankey diagram visualizing figurative language patterns in biblical Hebrew texts, showing the flow from **Target** → **Vehicle** relationships with conceptual grouping and rich interactive features.

**Data Source**: Deuteronomy database (950 validated figurative language instances)
**Goal**: Publication-ready visualization tool for biblical scholarship and linguistic research

---

## 🎯 Project Phases & Checklist

### **Phase 1: Data Preprocessing & Cleanup** ✅ COMPLETED
**Timeline**: Week 1-2 ✅ **Completed: Sept 22, 2025**

#### Data Standardization ✅
- [x] Analyze and normalize `target_level_1` capitalization inconsistencies ✅ (31→12 categories)
- [x] Analyze and normalize `vehicle_level_1` capitalization inconsistencies ✅ (35→15 categories)
- [x] Clean and validate `target_specific` entries for consistency ✅
- [x] Clean and validate `vehicle_specific` entries for consistency ✅
- [x] Handle multi-type instances (create separate flows for metaphor+idiom, etc.) ✅ (950→1,287 flows)
- [x] Create data quality report identifying any remaining issues ✅

#### Data Export Module ✅
- [x] Create SQLite → structured JSON export function ✅
- [x] Include hover detail data (Hebrew text, English text, deliberation, types) ✅
- [x] Pre-aggregate basic statistics for performance ✅
- [x] Test export with full Deuteronomy dataset ✅
- [x] Validate data integrity in exported format ✅

**Deliverables** ✅:
- `data_processor.py` - Clean, validated dataset in JSON format ✅
- `clean_deuteronomy_data.json` - 1,287 flows from 626 verses ✅
- Data quality report with statistics ✅

**Phase 1 Results**:
- **950 figurative instances** → **1,287 visualization flows** (multi-type expansion)
- **Target categories**: 31 → 12 (61% reduction through normalization)
- **Vehicle categories**: 35 → 15 (57% reduction through normalization)
- **Data integrity**: 100% preservation with enhanced structure
- **Multi-type support**: 667 flows handle combined figurative types
- **Hebrew text**: UTF-8 encoding preserved throughout

---

### **Phase 2: LLM-Based Conceptual Grouping** ✅ COMPLETED
**Timeline**: Week 2-3 ✅ **Completed: Sept 22, 2025**

#### Conceptual Grouping System ✅
- [x] Design `ConceptualGrouper` class with Gemini API integration ✅
- [x] Create target grouping method (cluster similar entities) ✅
- [x] Create vehicle grouping method (cluster by semantic domains) ✅
- [x] Implement batch processing to minimize API calls ✅
- [x] Add caching system to avoid re-processing ✅
- [x] Test grouping quality with sample data ✅

#### LLM Prompt Engineering ✅
- [x] Design target grouping prompt template ✅
- [x] Design vehicle grouping prompt template ✅
- [x] Test prompts with diverse examples ✅
- [x] Implement validation and refinement loops ✅
- [x] Document optimal prompting strategies ✅

#### Target Conceptual Groups (Examples)
- [ ] Biblical Figures: Joseph, Jacob, Moses, etc.
- [ ] Natural Objects: tree, mountain, river, etc.
- [ ] Abstract Concepts: laws, covenants, blessings, etc.
- [ ] Divine Attributes: God's power, anger, mercy, etc.
- [ ] Social Entities: tribes, nations, families, etc.

#### Vehicle Conceptual Groups (Examples)
- [ ] Flying Creatures: bees, eagles, birds, etc.
- [ ] Metals & Materials: copper, iron, gold, etc.
- [ ] Body Parts: heart, hand, eye, etc.
- [ ] Natural Forces: fire, water, wind, etc.
- [ ] Human Actions: walking, carrying, building, etc.

**Deliverables** ✅:
- `conceptual_grouper.py` - LLM-based clustering system ✅
- `clean_deuteronomy_data_grouped_20250922_180421.json` - Enhanced dataset with conceptual groups ✅
- `conceptual_grouping_report_20250922_180421.json` - Quality validation report ✅
- `detailed_groupings_20250922_180421.json` - Complete grouping mappings ✅

**Phase 2 Results**:
- **1,287 flows enhanced** with conceptual group assignments
- **Target groupings**: 9/11 categories successful (81% success rate)
- **Vehicle groupings**: 12/15 categories successful (80% success rate)
- **80 total conceptual groups** created with 95% average confidence
- **API efficiency**: 26 requests, intelligent caching system implemented
- **Processing time**: 9m 42s with full logging and error resilience

---

### **Phase 3: Sankey Visualization Architecture** 📈
**Timeline**: Week 3-4

#### Technology Stack Setup
- [ ] Choose between Plotly.js vs D3.js for Sankey implementation
- [ ] Set up Python Flask/FastAPI backend for data API
- [ ] Create optimized SQLite query functions
- [ ] Choose UI framework (Streamlit for prototyping → production framework)
- [ ] Set up development environment and dependencies

#### Four-Layer Sankey Implementation
- [ ] Implement Target Specific (clustered) layer
- [ ] Implement Target Level 1 (existing categories) layer
- [ ] Implement Vehicle Level 1 (existing categories) layer
- [ ] Implement Vehicle Specific (clustered) layer
- [ ] Create smooth flow connections between all layers
- [ ] Implement proper data aggregation for flows

#### Core Visualization Features
- [ ] Basic Sankey diagram rendering
- [ ] Color coding for different figurative types
- [ ] Proportional flow thickness based on frequency
- [ ] Responsive design for different screen sizes
- [ ] Performance optimization for 950+ data points

**Deliverables**:
- `sankey_generator.py` - Core visualization engine
- Working prototype with basic Sankey diagram

---

### **Phase 4: Interactive Features** 🖱️
**Timeline**: Week 4-5

#### Navigation & Interaction
- [ ] Implement zoom/pan functionality
- [ ] Add click-to-expand/collapse for conceptual clusters
- [ ] Create filtering by figurative type (metaphor, simile, etc.)
- [ ] Add filtering by confidence score ranges
- [ ] Implement filtering by book chapters/verses
- [ ] Add search functionality for specific targets/vehicles

#### Rich Hover Tooltips
- [ ] Display full verse reference and text
- [ ] Show Hebrew and English figurative text
- [ ] Include detected figurative language types
- [ ] Display LLM deliberation excerpts
- [ ] Show confidence scores and validation details
- [ ] Format tooltips for readability

#### User Experience Enhancements
- [ ] Add loading indicators for data processing
- [ ] Implement smooth transitions and animations
- [ ] Create intuitive control panels
- [ ] Add help/tutorial system
- [ ] Ensure accessibility compliance

**Deliverables**:
- Fully interactive Sankey visualization
- User interface with comprehensive controls

---

### **Phase 5: Statistics & Analytics Dashboard** 📊
**Timeline**: Week 5

#### High-Level Statistics
- [ ] Calculate distribution percentages for each level
- [ ] Create cross-tabulation analysis (Target Level 1 × Vehicle Level 1)
- [ ] Analyze figurative type frequency distributions
- [ ] Generate confidence score statistics
- [ ] Create pattern discovery reports

#### Dynamic Statistics Panel
- [ ] Real-time statistics updates based on current filters
- [ ] Comparative analysis displays ("23% of 'Social Group' targets...")
- [ ] Click-to-filter integration with statistics
- [ ] Export statistics to CSV/JSON
- [ ] Create printable summary reports

#### Advanced Analytics
- [ ] Identify most common Target→Vehicle patterns
- [ ] Analyze figurative type co-occurrence patterns
- [ ] Generate insights about biblical figurative language usage
- [ ] Create academic summary visualizations
- [ ] Implement trend analysis across chapters

**Deliverables**:
- `statistics_engine.py` - Comprehensive analytics system
- Interactive dashboard with real-time statistics

---

### **Phase 6: Production Polish & Performance** ✨
**Timeline**: Week 6

#### Performance Optimization
- [ ] Implement pre-computed aggregations for large datasets
- [ ] Add lazy loading for detailed hover data
- [ ] Optimize client-side caching strategies
- [ ] Implement progressive disclosure (overview → details)
- [ ] Conduct performance testing with full dataset

#### Export & Sharing Features
- [ ] Generate publication-ready PNG/PDF exports
- [ ] Create interactive HTML exports for sharing
- [ ] Implement data export functionality
- [ ] Add citation generation for academic use
- [ ] Create shareable URL system with filters

#### Documentation & Testing
- [ ] Write comprehensive user documentation
- [ ] Create developer documentation for code maintenance
- [ ] Implement automated testing suite
- [ ] Conduct user acceptance testing
- [ ] Create video tutorials/demos

**Deliverables**:
- Production-ready Sankey visualization tool
- Complete documentation and testing suite

---

## 🔧 Technical Architecture

### File Structure
```
sankey_visualization/
├── data_processor.py      # Database → clean data pipeline
├── conceptual_grouper.py  # LLM-based semantic clustering
├── sankey_generator.py    # Plotly/D3 visualization engine
├── statistics_engine.py   # Analytics and insights calculation
├── web_app.py            # Flask/FastAPI web interface
├── config.py             # Configuration and settings
├── utils.py              # Helper functions and utilities
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── data/                 # Processed data files
├── cache/                # LLM grouping cache
└── exports/              # Generated visualizations
```

### Dependencies
- **Core**: Python 3.9+, SQLite, Pandas
- **Visualization**: Plotly/D3.js, Flask/FastAPI
- **AI**: Google Gemini API (existing integration)
- **UI**: Streamlit (prototyping), HTML/CSS/JS (production)

---

## 📈 Success Metrics

### Functionality
- [ ] All 950 figurative language instances properly visualized
- [ ] Intuitive conceptual groupings (validated by domain expert)
- [ ] Sub-second response time for all interactions
- [ ] Rich hover details with complete biblical context

### Academic Value
- [ ] Publication-ready figure generation
- [ ] Meaningful statistics revealing linguistic patterns
- [ ] Exportable data for further research
- [ ] Integration with existing biblical scholarship workflows

### Technical Excellence
- [ ] Responsive design across devices
- [ ] Robust error handling and data validation
- [ ] Comprehensive documentation
- [ ] Maintainable, well-structured codebase

---

## 🚀 Getting Started

**Next Steps**: Begin Phase 1 with data preprocessing and cleanup
**Key Dependencies**: Ensure Gemini API access for conceptual grouping
**Timeline**: 6 weeks total, with MVP available after 2 weeks

---

## 📝 Notes & Decisions

### Design Decisions
- **Four-layer structure**: Provides optimal balance of detail and clarity
- **LLM grouping**: Leverages existing AI infrastructure for semantic clustering
- **Progressive disclosure**: Ensures performance while maintaining rich detail access

### Potential Challenges
- **Performance**: 950+ instances require careful optimization
- **Grouping quality**: LLM clustering needs validation and refinement
- **Hebrew text display**: UTF-8 handling across all components
- **Academic requirements**: Ensure scholarly rigor in all features

### Future Enhancements
- **Multi-book comparison**: Extend to Genesis, Exodus, etc.
- **Temporal analysis**: Track patterns across biblical chronology
- **Cross-reference integration**: Link to external biblical databases
- **Machine learning insights**: Pattern prediction and discovery