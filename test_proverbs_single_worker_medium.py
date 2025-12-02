#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Proverbs 3:11-18 with SINGLE WORKER (sequential) - GPT-5.1 MEDIUM reasoning
Shows full model reasoning/deliberation for each verse to understand why instances are/aren't detected
"""

import sys
import os
import logging
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import time

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add source paths
sys.path.append(os.path.join(os.path.dirname(__file__), 'private/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'private'))

from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient
from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.unified_llm_client import UnifiedLLMClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Monkey-patch UnifiedLLMClient to use MEDIUM reasoning effort
original_call_gpt51 = UnifiedLLMClient._call_gpt51

def patched_call_gpt51(self, prompt: str, hebrew_text: str, english_text: str) -> Tuple[str, Optional[str], Dict]:
    """Modified version that uses reasoning_effort='medium' instead of 'high'"""
    max_retries = 3
    metadata = {'model_used': 'gpt-5.1-medium'}

    for attempt in range(max_retries):
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-5.1",
                messages=[
                    {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=65536,
                reasoning_effort="medium"  # CHANGED FROM "high"
            )

            # Extract token usage
            if hasattr(response, 'usage'):
                metadata['input_tokens'] = getattr(response.usage, 'prompt_tokens', 0)
                metadata['output_tokens'] = getattr(response.usage, 'completion_tokens', 0)
                metadata['reasoning_tokens'] = getattr(response.usage, 'reasoning_tokens', 0)

                # Update totals
                self.gpt_tokens['input'] += metadata['input_tokens']
                self.gpt_tokens['output'] += metadata['output_tokens']
                self.gpt_tokens['reasoning'] += metadata['reasoning_tokens']

                # Calculate cost
                cost = (metadata['input_tokens'] / 1_000_000 * 1.25 +
                       metadata['output_tokens'] / 1_000_000 * 10.0)
                self.total_cost += cost
                metadata['cost'] = cost

            # Extract response text
            response_text = response.choices[0].message.content

            # Parse and validate the response
            cleaned_response, all_instances, deliberation, truncation_info = self._clean_response(
                response_text, hebrew_text, english_text
            )

            metadata['all_detected_instances'] = all_instances
            metadata['truncation_info'] = truncation_info
            metadata['retries'] = attempt
            metadata['raw_response'] = response_text
            metadata['deliberation'] = deliberation

            return cleaned_response, None, metadata

        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                if "rate_limit" in error_msg.lower() or "429" in error_msg:
                    wait_time = (2 ** attempt) * 5
                    if self.logger:
                        self.logger.info(f"Rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue

            return "[]", f"GPT-5.1 error: {error_msg}", {'retries': attempt + 1}

    return "[]", "GPT-5.1 failed after retries", {'retries': max_retries}

# Apply the monkey patch
UnifiedLLMClient._call_gpt51 = patched_call_gpt51

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
log_file = os.path.join(output_dir, f'proverbs_3_11-18_single_medium_{timestamp}_log.txt')
results_file = os.path.join(output_dir, f'proverbs_3_11-18_single_medium_{timestamp}_results.json')

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
print("SINGLE WORKER TEST: PROVERBS 3:11-18 (GPT-5.1 MEDIUM reasoning)")
print("Purpose: Show full model reasoning to understand detection patterns")
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

# Initialize client ONCE for all verses
print(f"\n{'='*80}")
print("Initializing FlexibleTaggingGeminiClient (with MEDIUM reasoning patch)...")
print(f"{'='*80}\n")
client = FlexibleTaggingGeminiClient("", logger=logger)

# Process verses SEQUENTIALLY
all_results = []
start_time = datetime.now()

for i, verse_data in enumerate(verses, 1):
    reference = verse_data['reference']
    hebrew = verse_data['hebrew']
    english = verse_data['english']

    print(f"\n{'='*80}")
    print(f"[{i}/{len(verses)}] Processing: {reference}")
    print(f"{'='*80}")
    print(f"English: {english}")
    print()

    # Analyze verse with full chapter context
    verse_start = datetime.now()
    result, error, metadata = client.analyze_figurative_language_flexible(
        hebrew, english, "Proverbs", 3, chapter_context=full_chapter_context
    )
    verse_end = datetime.now()
    processing_time = (verse_end - verse_start).total_seconds()

    # Extract results
    detected_count = len(metadata.get('all_detected_instances', []))
    cost = metadata.get('total_cost', 0.0)
    model_used = metadata.get('model_used', 'unknown')
    raw_response = metadata.get('raw_response', '')
    deliberation = metadata.get('deliberation', '')

    print(f"Results: {detected_count} instances, ${cost:.4f}, {processing_time:.1f}s, model={model_used}")

    # Show deliberation/reasoning
    if deliberation:
        print(f"\n--- MODEL DELIBERATION ---")
        print(deliberation)
        print(f"--- END DELIBERATION ---\n")
    elif raw_response:
        print(f"\n--- MODEL RESPONSE (NO EXPLICIT DELIBERATION) ---")
        # Show first 1000 chars of response if no deliberation section
        print(raw_response[:1000] + ("..." if len(raw_response) > 1000 else ""))
        print(f"--- END RESPONSE ---\n")

    # Show detected instances (if any)
    if detected_count > 0:
        print(f"\nDetected instances:")
        for j, inst in enumerate(metadata.get('all_detected_instances', []), 1):
            fig_type = inst.get('type', inst.get('original_detection_types', 'unknown'))
            text = inst.get('english_text', inst.get('text', 'N/A'))
            explanation = inst.get('explanation', 'No explanation')
            print(f"  {j}. {fig_type}: {text}")
            print(f"     Explanation: {explanation}")

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
        'deliberation': deliberation,
        'raw_response': raw_response
    }
    all_results.append(verse_result)

end_time = datetime.now()
total_time = (end_time - start_time).total_seconds()

# Calculate summary
total_detected = sum(r['detected_count'] for r in all_results)
total_cost = sum(r['cost'] for r in all_results)

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Verses processed: {len(all_results)}")
print(f"Total instances detected: {total_detected}")
print(f"Detection rate: {total_detected/len(all_results):.2f} instances/verse")
print(f"Total cost: ${total_cost:.4f}")
print(f"Average cost: ${total_cost/len(all_results):.4f}/verse")
print(f"Total time: {total_time:.1f}s ({total_time/len(all_results):.1f}s/verse)")
print(f"Processing: Sequential (1 worker)")
print("=" * 80)

# Save results to JSON
output_data = {
    'test_info': {
        'passage': 'Proverbs 3:11-18',
        'approach': 'SINGLE WORKER - Sequential processing with GPT-5.1 MEDIUM reasoning',
        'reasoning_effort': 'medium',
        'timestamp': timestamp,
        'total_verses': len(all_results),
        'total_detected': total_detected,
        'total_cost': total_cost,
        'total_time': total_time,
        'workers_used': 1,
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
