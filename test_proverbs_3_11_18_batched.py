#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Proverbs 3:11-18 with BATCHED processing - context provided once per worker"""

import sys
import os
import logging
import json
from datetime import datetime
import concurrent.futures
from typing import List, Dict, Tuple

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

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(output_dir, f'proverbs_3_11-18_batched_{timestamp}_log.txt')
results_file = os.path.join(output_dir, f'proverbs_3_11-18_batched_{timestamp}_results.json')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

print("=" * 80)
print("BATCHED TEST: PROVERBS 3:11-18 (6 parallel workers)")
print("=" * 80)
print(f"Log file: {log_file}")
print(f"Results file: {results_file}")
print("=" * 80)

# Fetch FULL chapter from Sefaria for context
print("\nFetching full Proverbs 3 from Sefaria API...")
sefaria = SefariaClient()
all_verses, api_time = sefaria.extract_hebrew_text("Proverbs.3")

# Filter to verses 11-18 only
verses = [v for v in all_verses if 11 <= v['verse'] <= 18]

print(f"\nRetrieved {len(all_verses)} verses in {api_time:.2f}s")
print(f"Filtered to verses 11-18: {len(verses)} verses\n")

# Create full chapter context (Hebrew + English)
chapter_hebrew = "\n".join([f"{v['verse']}. {v['hebrew']}" for v in all_verses])
chapter_english = "\n".join([f"{v['verse']}. {v['english']}" for v in all_verses])
full_chapter_context = f"""=== Proverbs Chapter 3 (FULL CHAPTER for context) ===

Hebrew:
{chapter_hebrew}

English:
{chapter_english}
"""

print(f"Full chapter context: {len(full_chapter_context)} chars")
print("\nVerses to analyze (11-18):")
for v in verses:
    print(f"  {v['reference']}: {v['english'][:60]}...")

def process_verse_worker(worker_id: int, verses_to_process: List[Dict]) -> List[Dict]:
    """Worker that processes multiple verses with shared context"""
    worker_logger = logging.getLogger(f"Worker-{worker_id}")
    worker_logger.info(f"Worker {worker_id} starting with {len(verses_to_process)} verses")

    # Initialize client for this worker
    client = FlexibleTaggingGeminiClient("", logger=worker_logger)

    results = []

    for verse_data in verses_to_process:
        reference = verse_data['reference']
        hebrew = verse_data['hebrew']
        english = verse_data['english']

        worker_logger.info(f"Worker {worker_id}: Processing {reference}")
        print(f"[Worker {worker_id}] Processing: {reference}")

        # Analyze verse with full chapter context
        start_time = datetime.now()
        result, error, metadata = client.analyze_figurative_language_flexible(
            hebrew, english, "Proverbs", 3, chapter_context=full_chapter_context
        )
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Extract results
        detected_count = len(metadata.get('all_detected_instances', []))
        cost = metadata.get('total_cost', 0.0)
        model_used = metadata.get('model_used', 'unknown')

        worker_logger.info(f"Worker {worker_id}: {reference} -> {detected_count} instances, ${cost:.4f}, {processing_time:.1f}s")
        print(f"[Worker {worker_id}] {reference}: {detected_count} instances, ${cost:.4f}, {processing_time:.1f}s")

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
            'error': error,
            'worker_id': worker_id
        }
        results.append(verse_result)

    worker_logger.info(f"Worker {worker_id} completed {len(results)} verses")
    return results

# Parallel processing with 6 workers
print(f"\n{'='*80}")
print("Starting parallel processing with 6 workers...")
print(f"{'='*80}\n")

max_workers = 6
all_results = []
start_time = datetime.now()

# Distribute verses across workers
verses_per_worker = len(verses) // max_workers
if verses_per_worker == 0:
    verses_per_worker = 1
    max_workers = len(verses)

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []

    for i in range(max_workers):
        start_idx = i * verses_per_worker
        if i == max_workers - 1:
            # Last worker gets remaining verses
            end_idx = len(verses)
        else:
            end_idx = start_idx + verses_per_worker

        worker_verses = verses[start_idx:end_idx]
        if worker_verses:  # Only submit if there are verses to process
            future = executor.submit(process_verse_worker, i+1, worker_verses)
            futures.append(future)

    # Collect results
    for future in concurrent.futures.as_completed(futures):
        try:
            worker_results = future.result()
            all_results.extend(worker_results)
        except Exception as e:
            logger.error(f"Worker failed with error: {e}")
            print(f"ERROR: Worker failed: {e}")

end_time = datetime.now()
total_time = (end_time - start_time).total_seconds()

# Sort results by verse number
all_results.sort(key=lambda x: int(x['reference'].split(':')[1]))

# Calculate summary
total_detected = sum(r['detected_count'] for r in all_results)
total_cost = sum(r['cost'] for r in all_results)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Verses processed: {len(all_results)}")
print(f"Total instances detected: {total_detected}")
print(f"Detection rate: {total_detected/len(all_results):.1f} instances/verse")
print(f"Total cost: ${total_cost:.4f}")
print(f"Average cost: ${total_cost/len(all_results):.4f}/verse")
print(f"Total time: {total_time:.1f}s ({total_time/len(all_results):.1f}s/verse)")
print(f"Workers used: {len(futures)}")
print("=" * 80)

print("\nDetailed results by verse:")
for r in all_results:
    print(f"\n{r['reference']} (Worker {r['worker_id']}):")
    print(f"  English: {r['english']}")
    print(f"  Detected: {r['detected_count']} instances")
    if r['detected_count'] > 0:
        for i, inst in enumerate(r['instances'], 1):
            fig_type = inst.get('type', 'unknown')
            text = inst.get('english_text', inst.get('text', 'N/A'))
            print(f"    {i}. {fig_type}: {text}")

# Save results to JSON
output_data = {
    'test_info': {
        'passage': 'Proverbs 3:11-18',
        'approach': 'BATCHED - Full chapter context provided once per worker',
        'timestamp': timestamp,
        'total_verses': len(all_results),
        'total_detected': total_detected,
        'total_cost': total_cost,
        'total_time': total_time,
        'workers_used': len(futures),
        'chapter_context_size': len(full_chapter_context)
    },
    'full_chapter_context': full_chapter_context,
    'verses': all_results
}

with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Results saved to: {results_file}")
print(f"Logs saved to: {log_file}")
print(f"{'='*80}")
