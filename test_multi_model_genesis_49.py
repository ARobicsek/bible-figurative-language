#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for multi-model API with Genesis 49 figurative language detection
Compares new multi-model approach vs. original conservative API
"""
import sys
import os
import json
import sqlite3
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
from src.hebrew_figurative_db.ai_analysis.gemini_api_conservative import GeminiAPIClient
from src.hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient


def test_genesis_49_detection():
    """Test Genesis 49 figurative language detection with both APIs"""

    print("TESTING MULTI-MODEL VS CONSERVATIVE API")
    print("=" * 60)

    # Initialize APIs
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    multi_model_client = MultiModelGeminiClient(api_key)
    conservative_client = GeminiAPIClient(api_key)
    sefaria_client = SefariaClient()

    print("Fetching Genesis 49 text...")
    verses_data, api_time = sefaria_client.extract_hebrew_text("Genesis.49")

    if not verses_data:
        print("FAILED to fetch Genesis 49 text")
        return

    print(f"Retrieved {len(verses_data)} verses from Genesis 49")
    print()

    # Key verses that should contain figurative language
    test_verses = [
        (3, "Reuben - 'unstable as water'"),
        (9, "Judah - 'lion's whelp'"),
        (14, "Issachar - animal imagery"),
        (17, "Dan - 'serpent by the road'"),
        (21, "Naphtali - 'hind let loose'"),
        (22, "Joseph - 'wild ass'"),
        (27, "Benjamin - 'ravenous wolf'")
    ]

    results_comparison = []

    for verse_num, description in test_verses:
        if verse_num <= len(verses_data):
            verse_data = verses_data[verse_num - 1]
            hebrew_text = verse_data['hebrew']
            english_text = verse_data['english']

            print(f"TESTING VERSE {verse_num}: {description}")
            print(f"English: {english_text}")
            print()

            # Test multi-model API
            print("Multi-Model API:")
            multi_result, multi_error, multi_metadata = multi_model_client.analyze_figurative_language(
                hebrew_text, english_text, "Genesis", 49
            )

            try:
                multi_detections = json.loads(multi_result)
                multi_count = len(multi_detections)
                print(f"   Detections: {multi_count}")
                if multi_detections:
                    for detection in multi_detections:
                        print(f"   - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
                print(f"   Model used: {multi_metadata.get('model_used', 'unknown')}")
                print(f"   Fallback used: {multi_metadata.get('fallback_used', False)}")
            except json.JSONDecodeError:
                multi_count = 0
                print(f"   Invalid JSON: {multi_result}")

            if multi_error:
                print(f"   Error: {multi_error}")
            print()

            # Test conservative API
            print("Conservative API:")
            conservative_result, conservative_error = conservative_client.analyze_figurative_language(
                hebrew_text, english_text
            )

            try:
                conservative_detections = json.loads(conservative_result)
                conservative_count = len(conservative_detections)
                print(f"   Detections: {conservative_count}")
                if conservative_detections:
                    for detection in conservative_detections:
                        print(f"   - {detection.get('type', 'unknown')}: {detection.get('english_text', 'N/A')}")
            except json.JSONDecodeError:
                conservative_count = 0
                print(f"   Invalid JSON: {conservative_result}")

            if conservative_error:
                print(f"   Error: {conservative_error}")

            # Record comparison
            results_comparison.append({
                'verse': verse_num,
                'description': description,
                'multi_model_count': multi_count,
                'conservative_count': conservative_count,
                'improvement': multi_count - conservative_count,
                'multi_model_used': multi_metadata.get('model_used', 'unknown'),
                'fallback_used': multi_metadata.get('fallback_used', False)
            })

            print("-" * 60)
            print()

    # Summary
    print("DETECTION SUMMARY")
    print("=" * 60)

    total_multi = sum(r['multi_model_count'] for r in results_comparison)
    total_conservative = sum(r['conservative_count'] for r in results_comparison)
    total_improvement = total_multi - total_conservative

    print(f"Multi-Model API Total: {total_multi} detections")
    print(f"Conservative API Total: {total_conservative} detections")
    print(f"Net Improvement: +{total_improvement} detections")
    print(f"Improvement Rate: {(total_improvement / max(1, total_conservative)) * 100:.1f}%")
    print()

    # Model usage statistics
    multi_usage = multi_model_client.get_usage_info()
    print("MULTI-MODEL USAGE STATISTICS")
    print(f"Primary Model: {multi_usage['primary_model']}")
    print(f"Fallback Model: {multi_usage['fallback_model']}")
    print(f"Primary Success Rate: {multi_usage['primary_success_rate'] * 100:.1f}%")
    print(f"Fallback Rate: {multi_usage['fallback_rate'] * 100:.1f}%")
    print(f"Total Tokens: {multi_usage['total_tokens']:,}")

    if multi_usage['restriction_reasons']:
        print("Restriction Reasons:")
        for reason in multi_usage['restriction_reasons']:
            print(f"  - {reason}")

    print()

    # Detailed comparison table
    print("DETAILED COMPARISON")
    print("Verse | Description                    | Multi | Cons | +/-  | Model Used")
    print("------|--------------------------------|-------|------|------|------------")

    for r in results_comparison:
        model_info = f"{r['multi_model_used'][:8]}"
        if r['fallback_used']:
            model_info += "*"

        print(f"{r['verse']:5} | {r['description'][:30]:30} | {r['multi_model_count']:5} | {r['conservative_count']:4} | {r['improvement']:+4} | {model_info}")

    print("\n* = Fallback model used")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = f"genesis_49_multi_model_test_{timestamp}.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_timestamp': timestamp,
            'summary': {
                'total_multi_model': total_multi,
                'total_conservative': total_conservative,
                'improvement': total_improvement,
                'improvement_rate': (total_improvement / max(1, total_conservative)) * 100
            },
            'usage_stats': multi_usage,
            'detailed_results': results_comparison
        }, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {results_file}")


if __name__ == "__main__":
    test_genesis_49_detection()