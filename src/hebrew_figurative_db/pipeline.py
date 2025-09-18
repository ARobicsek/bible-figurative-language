#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main pipeline for Hebrew figurative language processing
"""
import time
from typing import Dict, List, Tuple
from .text_extraction import SefariaClient
from .text_extraction.hebrew_utils import HebrewTextProcessor
from .ai_analysis import FigurativeLanguageDetector
from .ai_analysis.hybrid_detector import HybridFigurativeDetector
from .database import DatabaseManager


class FigurativeLanguagePipeline:
    """Complete pipeline for processing Hebrew figurative language"""

    def __init__(self, db_path: str = 'figurative_language_pipeline.db',
                 use_llm_detection: bool = True, use_actual_llm: bool = False):
        self.sefaria_client = SefariaClient()
        self.hebrew_processor = HebrewTextProcessor()
        self.db_path = db_path
        self.use_llm_detection = use_llm_detection

        if use_llm_detection:
            self.detector = HybridFigurativeDetector(prefer_llm=True, use_actual_llm=use_actual_llm, allow_rule_fallback=False)
            print(f"    [PIPELINE] Using LLM-only detection (Hebrew+English analysis, no rule-based fallback)")
        else:
            self.detector = FigurativeLanguageDetector()
            print(f"    [PIPELINE] Using rule-based detection (English only)")

    def process_verses(self, verses_range: str, drop_existing: bool = False) -> Dict:
        """
        Process a range of verses through the complete pipeline

        Args:
            verses_range: Range like "Genesis.1" or "Genesis.1.1-10"
            drop_existing: Whether to drop existing database tables

        Returns:
            Dictionary with processing results and statistics
        """
        print(f"=== Processing {verses_range} through pipeline ===")

        start_time = time.time()

        # Step 1: Extract Hebrew text
        print(f"\n[STEP 1] Extracting Hebrew text...")
        verses, api_time = self.sefaria_client.extract_hebrew_text(verses_range)

        # Step 2: Setup database
        print(f"\n[STEP 2] Setting up database...")
        with DatabaseManager(self.db_path) as db:
            db.setup_database(drop_existing=drop_existing)

            # Step 3: Process each verse
            print(f"\n[STEP 3] Processing {len(verses)} verses...")

            processed_verses = 0
            figurative_found = 0
            processing_errors = 0

            for verse in verses:
                try:
                    # Process Hebrew text
                    hebrew_stripped = self.hebrew_processor.strip_diacritics(verse['hebrew'])
                    speaker = self.hebrew_processor.identify_speaker_patterns(verse['english'], verse['hebrew'])

                    # Enhance verse data
                    enhanced_verse = {
                        **verse,
                        'hebrew_stripped': hebrew_stripped,
                        'speaker': speaker
                    }

                    # Insert verse into database
                    verse_id = db.insert_verse(enhanced_verse)
                    processed_verses += 1

                    # AI analysis for figurative language - now returns a list
                    if self.use_llm_detection:
                        # LLM detector expects (english, hebrew) order
                        detection_results = self.detector.detect_figurative_language(
                            verse['english'], verse['hebrew']
                        )
                    else:
                        # Rule-based detector expects (english, hebrew) order but returns different format
                        detection_results = self.detector.detect_figurative_language(
                            verse['english'], verse['hebrew']
                        )

                    if detection_results:
                        for i, detection_result in enumerate(detection_results):
                            # Clean and validate type
                            fig_type = detection_result['type'].lower().strip()
                            valid_types = ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy']
                            if fig_type not in valid_types:
                                fig_type = 'other'

                            # Prepare figurative language data
                            figurative_data = {
                                'type': fig_type,
                                'subcategory': detection_result.get('subcategory'),
                                'confidence': detection_result['confidence'],
                                'figurative_text': detection_result.get('figurative_text') or detection_result.get('english_text'),  # English figurative text from LLM
                                'figurative_text_in_hebrew': detection_result.get('hebrew_source') or detection_result.get('hebrew_text'),  # Hebrew figurative text from LLM
                                'explanation': detection_result.get('explanation')
                            }

                            # Insert figurative language record
                            db.insert_figurative_language(verse_id, figurative_data)
                            figurative_found += 1

                            subcategory_text = f" [{detection_result.get('subcategory', 'uncat')}]" if detection_result.get('subcategory') else ""
                            speaker_text = f" (Speaker: {speaker})" if speaker else ""
                            instance_text = f" #{i+1}" if len(detection_results) > 1 else ""
                            print(f"  {verse['reference']}{instance_text}: {detection_result['type']}{subcategory_text} ({detection_result['confidence']:.2f}){speaker_text}")
                            print(f"    Text: '{detection_result.get('figurative_text', 'N/A')}'")
                            print(f"    Why: {detection_result.get('explanation', 'N/A')}")
                    else:
                        speaker_text = f" (Speaker: {speaker})" if speaker else ""
                        print(f"  {verse['reference']}: No figurative language detected{speaker_text}")

                except Exception as e:
                    print(f"  ERROR processing {verse.get('reference', 'unknown')}: {e}")
                    processing_errors += 1

            # Commit all changes
            db.commit()

            # Step 4: Generate statistics
            print(f"\n[STEP 4] Generating statistics...")
            stats = db.get_statistics()
            top_findings = db.get_top_findings()

        total_time = time.time() - start_time

        # Compile results
        results = {
            'verses_range': verses_range,
            'processing_time': total_time,
            'api_time': api_time,
            'processed_verses': processed_verses,
            'figurative_found': figurative_found,
            'processing_errors': processing_errors,
            'error_rate': (processing_errors / len(verses) * 100) if len(verses) > 0 else 0,
            'statistics': stats,
            'top_findings': top_findings,
            'success': processing_errors < len(verses) * 0.05  # Less than 5% error rate
        }

        self._print_results(results)
        return results

    def _print_results(self, results: Dict):
        """Print processing results"""
        print(f"\n{'='*60}")
        print(f"📊 PIPELINE RESULTS")
        print(f"{'='*60}")
        print(f"Verses processed: {results['processed_verses']}")
        print(f"Figurative language instances: {results['figurative_found']}")
        print(f"Processing errors: {results['processing_errors']} ({results['error_rate']:.1f}%)")
        print(f"Total processing time: {results['processing_time']:.2f}s")
        print(f"API time: {results['api_time']:.2f}s")

        stats = results['statistics']
        print(f"\nDetection rate: {stats['detection_rate']:.1f}%")
        print(f"Average confidence: {stats['avg_confidence']:.2f}")

        print(f"\nBreakdown by type:")
        for fig_type, count in stats['type_breakdown'].items():
            print(f"  {fig_type}: {count}")

        print(f"\nTop findings:")
        for ref, fig_type, confidence, snippet in results['top_findings']:
            print(f"  {ref}: {fig_type} ({confidence:.2f}) - '{snippet[:30]}...'")

        if results['success']:
            print(f"\n✅ Pipeline completed successfully!")
        else:
            print(f"\n⚠️ Pipeline completed with warnings (high error rate)")