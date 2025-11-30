#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Proverbs 3:11-18 with detailed logging"""

import sys
import os
import logging
import json
from datetime import datetime

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add source paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'private/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'private'))

from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient
from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Create output directory if it doesn't exist
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Setup logging to both console and file
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(output_dir, f'proverbs_3_11-18_{timestamp}_log.txt')
results_file = os.path.join(output_dir, f'proverbs_3_11-18_{timestamp}_results.json')

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("TESTING PROVERBS 3:11-18")
print("=" * 80)
print(f"Log file: {log_file}")
print(f"Results file: {results_file}")
print("=" * 80)

# Fetch verses from Sefaria
print("\nFetching verses from Sefaria API...")
sefaria = SefariaClient()
verses, api_time = sefaria.extract_hebrew_text("Proverbs.3.11-18")

print(f"\nRetrieved {len(verses)} verses in {api_time:.2f}s")
print("\nVerses to test:")
for v in verses:
    print(f"  {v['reference']}: {v['english'][:60]}...")

# Initialize client
print("\nInitializing FlexibleTaggingGeminiClient...")
client = FlexibleTaggingGeminiClient("", logger=logger)

# Process each verse
results = []
total_cost = 0.0
total_time = 0.0
total_detected = 0

for verse_data in verses:
    reference = verse_data['reference']
    hebrew = verse_data['hebrew']
    english = verse_data['english']

    print(f"\n{'='*80}")
    print(f"Processing: {reference}")
    print(f"Hebrew: {hebrew}")
    print(f"English: {english}")
    print(f"{'='*80}")

    # Get chapter context (simplified - in production this would be full chapter)
    chapter_context = f"Proverbs 3 context (verse {verse_data['verse']} of chapter)"

    # Analyze verse
    start_time = datetime.now()
    result, error, metadata = client.analyze_figurative_language_flexible(
        hebrew, english, "Proverbs", 3, chapter_context=chapter_context
    )
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Extract results
    detected_count = len(metadata.get('all_detected_instances', []))
    cost = metadata.get('total_cost', 0.0)
    model_used = metadata.get('model_used', 'unknown')

    total_detected += detected_count
    total_cost += cost
    total_time += processing_time

    print(f"\nResults:")
    print(f"  Model: {model_used}")
    print(f"  Detected: {detected_count} instances")
    print(f"  Cost: ${cost:.4f}")
    print(f"  Time: {processing_time:.1f}s")

    if detected_count > 0:
        print(f"  Instances:")
        for i, inst in enumerate(metadata['all_detected_instances'], 1):
            print(f"    {i}. {inst.get('type', 'unknown')}: {inst.get('text', 'N/A')}")

    # Store result
    verse_result = {
        'reference': reference,
        'hebrew': hebrew,
        'english': english,
        'detected_count': detected_count,
        'instances': metadata.get('all_detected_instances', []),
        'model_used': model_used,
        'cost': cost,
        'processing_time': processing_time,
        'error': error
    }
    results.append(verse_result)

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Total verses: {len(verses)}")
print(f"Total detected: {total_detected} instances")
print(f"Detection rate: {total_detected/len(verses):.1f} instances/verse")
print(f"Total cost: ${total_cost:.4f}")
print(f"Total time: {total_time:.1f}s ({total_time/len(verses):.1f}s/verse)")
print(f"Average cost: ${total_cost/len(verses):.4f}/verse")
print("=" * 80)

# Save results to JSON
output_data = {
    'test_info': {
        'passage': 'Proverbs 3:11-18',
        'timestamp': timestamp,
        'total_verses': len(verses),
        'total_detected': total_detected,
        'total_cost': total_cost,
        'total_time': total_time
    },
    'verses': results
}

with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\nResults saved to: {results_file}")
print(f"Logs saved to: {log_file}")
