#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Proverbs 3:11-18 with MEDIUM reasoning effort - Compare cost/quality with HIGH"""

import sys
import os
import logging
import json
from datetime import datetime
import concurrent.futures
from typing import List, Dict

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
log_file = os.path.join(output_dir, f'proverbs_medium_{timestamp}_log.txt')
results_file = os.path.join(output_dir, f'proverbs_medium_{timestamp}_results.json')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def extract_primary_type(instance: Dict) -> str:
    """Extract the primary figurative type from yes/no fields"""
    type_priority = ['metaphor', 'simile', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']

    for type_name in type_priority:
        if instance.get(type_name) == 'yes':
            return type_name

    return 'unknown'

def format_hierarchy(arr: List[str]) -> str:
    """Format hierarchical array for display"""
    if not arr:
        return "N/A"
    return " > ".join(arr)

print("=" * 80)
print("MEDIUM REASONING TEST: Proverbs 3:11-18 (6 workers)")
print("=" * 80)
print(f"Log file: {log_file}")
print(f"Results file: {results_file}")
print("=" * 80)

# Fetch verses
print("\nFetching Proverbs 3 from Sefaria...")
sefaria = SefariaClient()
all_verses, api_time = sefaria.extract_hebrew_text("Proverbs.3")
verses = [v for v in all_verses if 11 <= v['verse'] <= 18]

print(f"\nFiltered to verses 11-18: {len(verses)} verses\n")

# Chapter context
chapter_hebrew = "\n".join([f"{v['verse']}. {v['hebrew']}" for v in all_verses])
chapter_english = "\n".join([f"{v['verse']}. {v['english']}" for v in all_verses])
full_chapter_context = f"""=== Proverbs Chapter 3 ===

Hebrew:
{chapter_hebrew}

English:
{chapter_english}
"""

# IMPORTANT: Monkey-patch the unified client to use MEDIUM reasoning effort
# This is done by modifying the reasoning_effort parameter before calling
import importlib
unified_llm = importlib.import_module('hebrew_figurative_db.ai_analysis.unified_llm_client')

# Backup the original _call_gpt51 method
original_call_gpt51 = unified_llm.UnifiedLLMClient._call_gpt51

def _call_gpt51_medium(self, prompt: str, hebrew_text: str, english_text: str):
    """Modified _call_gpt51 that uses MEDIUM reasoning effort"""
    max_retries = 3
    metadata = {'model_used': 'gpt-5.1'}

    for attempt in range(max_retries):
        try:
            # Call GPT-5.1 with MEDIUM reasoning effort (was HIGH)
            response = self.openai_client.chat.completions.create(
                model='gpt-5.1',
                messages=[
                    {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=65536,
                reasoning_effort="medium"  # ← CHANGED FROM "high"
            )

            result_text = response.choices[0].message.content

            # Extract token usage and calculate cost
            if hasattr(response, 'usage'):
                metadata['input_tokens'] = getattr(response.usage, 'prompt_tokens', 0)
                metadata['output_tokens'] = getattr(response.usage, 'completion_tokens', 0)
                metadata['reasoning_tokens'] = getattr(response.usage, 'reasoning_tokens', 0)

                # Update totals
                self.gpt_tokens['input'] += metadata['input_tokens']
                self.gpt_tokens['output'] += metadata['output_tokens']
                self.gpt_tokens['reasoning'] += metadata['reasoning_tokens']

                # Calculate cost (GPT-5.1: $1.25/M input, $10/M output)
                cost = (metadata['input_tokens'] / 1_000_000 * 1.25 +
                       metadata['output_tokens'] / 1_000_000 * 10.0)
                self.total_cost += cost
                metadata['cost'] = cost
                metadata['reasoning_effort'] = 'medium'

                if self.logger:
                    self.logger.info(f"GPT-5.1 (MEDIUM): {metadata['input_tokens']} input, "
                                   f"{metadata['output_tokens']} output, "
                                   f"{metadata['reasoning_tokens']} reasoning tokens, ${cost:.4f}")

            return result_text, None, metadata

        except Exception as e:
            if attempt < max_retries - 1:
                if self.logger:
                    self.logger.warning(f"GPT-5.1 attempt {attempt + 1} failed: {str(e)}, retrying...")
                continue
            else:
                error_msg = f"GPT-5.1 failed after {max_retries} attempts: {str(e)}"
                if self.logger:
                    self.logger.error(error_msg)
                return "", error_msg, metadata

    return "", "Max retries exceeded", metadata

# Apply the monkey patch
unified_llm.UnifiedLLMClient._call_gpt51 = _call_gpt51_medium

def process_verse_worker(worker_id: int, verses_to_process: List[Dict]) -> List[Dict]:
    """Worker that processes multiple verses"""
    worker_logger = logging.getLogger(f"Worker-{worker_id}")
    worker_logger.info(f"Worker {worker_id} starting with {len(verses_to_process)} verses")

    client = FlexibleTaggingGeminiClient("", logger=worker_logger)
    results = []

    for verse_data in verses_to_process:
        reference = verse_data['reference']
        hebrew = verse_data['hebrew']
        english = verse_data['english']

        print(f"[Worker {worker_id}] Processing: {reference}")

        start_time = datetime.now()
        result, error, metadata = client.analyze_figurative_language_flexible(
            hebrew, english, "Proverbs", 3, chapter_context=full_chapter_context
        )
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()

        # Extract results
        detected_count = len(metadata.get('all_detected_instances', []))
        cost = metadata.get('cost', 0.0)
        total_cost = metadata.get('total_cost', 0.0)
        model_used = metadata.get('model_used', 'unknown')

        print(f"[Worker {worker_id}] {reference}: {detected_count} instances, "
              f"${cost:.4f} (total: ${total_cost:.4f}), {processing_time:.1f}s")

        # Process instances with type extraction
        instances_detailed = []
        for inst in metadata.get('all_detected_instances', []):
            primary_type = extract_primary_type(inst)
            inst['primary_type'] = primary_type
            instances_detailed.append(inst)

        verse_result = {
            'reference': reference,
            'hebrew': hebrew,
            'english': english,
            'detected_count': detected_count,
            'instances': instances_detailed,
            'model_used': model_used,
            'cost': cost,
            'total_cost': total_cost,
            'processing_time': processing_time,
            'error': error,
            'worker_id': worker_id
        }
        results.append(verse_result)

    return results

# Parallel processing
print(f"\n{'='*80}")
print("Starting parallel processing with 6 workers...")
print(f"{'='*80}\n")

max_workers = 6
all_results = []
start_time = datetime.now()

verses_per_worker = max(1, len(verses) // max_workers)

with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = []

    for i in range(max_workers):
        start_idx = i * verses_per_worker
        if i == max_workers - 1:
            end_idx = len(verses)
        else:
            end_idx = start_idx + verses_per_worker

        worker_verses = verses[start_idx:end_idx]
        if worker_verses:
            future = executor.submit(process_verse_worker, i+1, worker_verses)
            futures.append(future)

    for future in concurrent.futures.as_completed(futures):
        try:
            worker_results = future.result()
            all_results.extend(worker_results)
        except Exception as e:
            logger.error(f"Worker failed: {e}")

end_time = datetime.now()
total_time = (end_time - start_time).total_seconds()

# Sort results by verse number
all_results.sort(key=lambda x: int(x['reference'].split(':')[1]))

# Calculate summary
total_detected = sum(r['detected_count'] for r in all_results)
total_cost = max(r.get('total_cost', 0.0) for r in all_results)

print("\n" + "=" * 80)
print("SUMMARY - MEDIUM REASONING EFFORT")
print("=" * 80)
print(f"Verses processed: {len(all_results)}")
print(f"Total instances detected: {total_detected}")
print(f"Detection rate: {total_detected/len(all_results):.1f} instances/verse")
print(f"Total cost: ${total_cost:.4f}")
print(f"Average cost: ${total_cost/len(all_results):.4f}/verse")
print(f"Total time: {total_time:.1f}s ({total_time/len(all_results):.1f}s/verse)")
print("=" * 80)

print("\nDetailed results:")
for r in all_results:
    print(f"\n{r['reference']}:")
    print(f"  {r['english']}")
    print(f"  Detected: {r['detected_count']} instances")

    for i, inst in enumerate(r['instances'], 1):
        primary_type = inst.get('primary_type', 'unknown')
        text = inst.get('english_text', 'N/A')
        target = format_hierarchy(inst.get('target', []))
        vehicle = format_hierarchy(inst.get('vehicle', []))
        ground = format_hierarchy(inst.get('ground', []))
        posture = format_hierarchy(inst.get('posture', []))

        print(f"\n  Instance {i} [{primary_type}]: {text}")
        print(f"    Target:  {target}")
        print(f"    Vehicle: {vehicle}")
        print(f"    Ground:  {ground}")
        print(f"    Posture: {posture}")

# Save results
output_data = {
    'test_info': {
        'passage': 'Proverbs 3:11-18',
        'reasoning_effort': 'MEDIUM',
        'timestamp': timestamp,
        'total_verses': len(all_results),
        'total_detected': total_detected,
        'total_cost': total_cost,
        'total_time': total_time,
        'workers_used': len(futures)
    },
    'verses': all_results
}

with open(results_file, 'w', encoding='utf-8') as f:
    json.dump(output_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print(f"Results saved to: {results_file}")
print(f"Logs saved to: {log_file}")
print(f"{'='*80}")
