Hebrew Figurative Language Database: Tech Stack & Execution Plan



  Project Overview



  Building a comprehensive database of figurative language in the Pentateuch with Hebrew text primacy, AI-assisted annotation, and analytical query capabilities.



  Tech Stack



  Core Infrastructure



  - Language: Python 3.9+

  - Database: SQLite (local, portable, no server required)

  - Environment: Virtual environment with requirements.txt

  - Version Control: Git repository



  Data Sources & APIs



  - Hebrew Text: ETCBC BHSA dataset via Text-Fabric (morphological annotations)

  - Translations: Sefaria API (JPS, multiple English versions)

  - Commentaries: Sefaria API (Rashi, Ibn Ezra, Ramban, etc.)

  - Linguistic Data: Text-Fabric framework for Hebrew processing



  AI Model Integration (Flexible Architecture)



  AI Model Abstraction Layer

  ├── Cloud APIs

  │   ├── Anthropic Claude API (Pro subscription)

  │   ├── Google Gemini API (Pro subscription)

  │   └── OpenAI GPT API (future)

  ├── Specialized Models

  │   ├── BEREL (Hebrew ancient texts)

  │   └── MelBERT (English metaphor detection)

  └── Local SLM Interface

      └── Pluggable for future local models (Ollama, etc.)



  Core Libraries



  # Data & Database

  sqlite3, pandas, sqlalchemy



  # Hebrew & Biblical Text Processing

  text-fabric, requests, json



  # AI Integration

  anthropic, google-generativeai, openai

  transformers, torch (for specialized models)



  # Interface & Analysis

  jupyter, matplotlib, plotly

  streamlit (simple web interface)



  Database Architecture



  Core Tables



  -- Hebrew text with linguistic annotations

  hebrew_text (word_id, book, chapter, verse, word_order, hebrew, transliteration, pos, morphology)



  -- AI model suggestions with confidence scoring

  ai_suggestions (suggestion_id, word_id, model_name, confidence_score, suggestion_type, metadata)



  -- Human-reviewed annotations

  figurative_annotations (annotation_id, word_range, type, source_domain, target_domain, speaker, about_character, human_verified)



  -- Commentary integration

  commentary_refs (comment_id, annotation_id, source, text, relevance_score)



  -- Analysis views

  metaphor_networks, proximity_analysis, character_mappings



  Execution Plan



  Phase 1: Foundation (Weeks 1-2)



  1. Environment Setup

    - Python virtual environment

    - Install Text-Fabric, download ETCBC data

    - SQLite database creation

    - API credential configuration (Claude, Gemini)

  2. Data Pipeline

    - Sefaria API integration (Hebrew + English texts)

    - ETCBC data import and processing

    - Commentary API testing and integration

    - Basic database population (Genesis 1 as test)



  Phase 2: AI Integration (Weeks 3-4)



  1. AI Model Abstraction

    - Unified interface for Claude/Gemini/future models

    - Confidence scoring system

    - Prompt engineering for metaphor detection

    - Error handling and rate limiting

  2. Specialized Model Integration

    - BEREL Hebrew model setup (if feasible)

    - MelBERT English analysis

    - Model ensemble scoring

    - Performance benchmarking on sample texts



  Phase 3: Annotation Workflow (Weeks 5-6)



  1. Human Review Interface

    - Jupyter notebook-based review system

    - AI suggestion display with confidence scores

    - Accept/reject/modify workflow

    - Batch processing capabilities

  2. Quality Control

    - Inter-annotator agreement tracking

    - Consistency validation

    - Feedback loop to improve AI suggestions



  Phase 4: Analysis Engine (Weeks 7-8)



  1. Query System

    - Character-based metaphor tracking

    - Proximity analysis (co-occurring metaphors)

    - Domain categorization (animal, nature, physical, etc.)

    - Book-specific pattern analysis

  2. Visualization & Export

    - Network graphs of metaphor relationships

    - Statistical summaries

    - Export to CSV/JSON for external analysis



  Key Technical Decisions



  AI Model Strategy



  - Primary: Claude/Gemini for contextual understanding and classification

  - Secondary: Specialized Hebrew models for linguistic accuracy

  - Future: Local SLM integration via standardized interface

  - Ensemble: Combine multiple model outputs with weighted confidence



  Scalability Considerations



  - Modular design: Each component (data, AI, annotation, analysis) is independent

  - Incremental processing: Process by chapter/book to manage scope

  - Caching: Store AI results to avoid re-computation

  - Export flexibility: Multiple output formats for different use cases



  Development Priorities



  1. Proof of concept: Single chapter (Genesis 1) end-to-end

  2. Scale horizontally: Add more text systematically

  3. Improve AI: Refine prompts and add models based on results

  4. Enhanced analysis: Build sophisticated query capabilities



  Resource Requirements



  - Time: ~8 weeks for full implementation

  - API Costs: Minimal with Pro subscriptions (estimate <$50/month)

  - Storage: <1GB for complete database

  - Compute: Standard laptop sufficient



  This architecture provides maximum flexibility while maintaining scholarly rigor and allowing for future enhancements.