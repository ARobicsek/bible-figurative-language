#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRUE BATCHED TEST: Proverbs 3:11-18 - ALL 8 verses in SINGLE API call

This script implements TRUE batching by:
1. Sending all 8 verses in ONE API call (not 8 separate calls)
2. Requesting JSON array output (one object per verse)
3. Saving ~79% of context tokens (chapter context + instructions sent ONCE)
4. Comparing GPT-5.1 MEDIUM vs GPT-5-mini

Token savings calculation:
- Per-verse approach: 8 calls × ~3,500 context tokens = ~28,000 tokens
- Batched approach: 1 call × ~6,000 context tokens = ~6,000 tokens
- Savings: ~22,000 tokens (79% reduction in context overhead)
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

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.unified_llm_client import UnifiedLLMClient
from dotenv import load_dotenv
from openai import OpenAI

# Load environment
load_dotenv()

# Create output directory
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

# Configuration
MODEL_NAME = "gpt-5-mini"  # Change to "gpt-5-mini" for GPT-5-mini testing
REASONING_EFFORT = "medium"  # "medium" or "high" for GPT-5.1; ignored for gpt-5-mini

# Setup logging
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
model_suffix = MODEL_NAME.replace(".", "_").replace("-", "_")
log_file = os.path.join(output_dir, f'proverbs_3_11-18_true_batched_{model_suffix}_{REASONING_EFFORT}_{timestamp}_log.txt')
results_file = os.path.join(output_dir, f'proverbs_3_11-18_true_batched_{model_suffix}_{REASONING_EFFORT}_{timestamp}_results.json')

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
print(f"TRUE BATCHED TEST: PROVERBS 3:11-18")
print(f"Model: {MODEL_NAME}")
if MODEL_NAME == "gpt-5.1":
    print(f"Reasoning Effort: {REASONING_EFFORT}")
print(f"Approach: ALL 8 verses in SINGLE API call")
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

# Build verses to analyze section
verses_to_analyze = ""
for v in verses:
    verses_to_analyze += f"\nVerse {v['verse']}:\n"
    verses_to_analyze += f"Hebrew: {v['hebrew']}\n"
    verses_to_analyze += f"English: {v['english']}\n"

print("\nVerses to analyze (11-18):")
for v in verses:
    print(f"  {v['reference']}: {v['english'][:60]}...")

# Build batched prompt
batched_prompt = f"""You are a biblical Hebrew scholar specializing in figurative language analysis. Your task is to analyze verses 11-18 from Proverbs Chapter 3 for figurative language.

{full_chapter_context}

=== VERSES TO ANALYZE (11-18) ===
{verses_to_analyze}

=== TASK ===

Analyze EACH of the 8 verses above (verses 11-18) for figurative language. For each verse, detect instances of:
- Metaphor
- Simile
- Personification
- Merism
- Synecdoche
- Metonymy
- Hyperbole
- Irony

For each detected instance, provide:
1. **figurative_language**: "yes" or "no"
2. **metaphor**: "yes" or "no" (specific to metaphor)
3. **hebrew_text**: The Hebrew text of the figurative expression
4. **english_text**: The English translation of the figurative expression
5. **target**: JSON array with 3 levels - [specific, category, domain]
6. **vehicle**: JSON array with 3 levels - [specific, category, domain]
7. **ground**: JSON array with 3 levels - [specific, category, domain]
8. **posture**: JSON array with 3 levels - [specific, category, domain]
9. **explanation**: Brief explanation of the figurative language
10. **confidence**: Confidence score (0.0-1.0)

=== OUTPUT FORMAT ===

Return a JSON array with ONE object per verse. Each object should have:
- "verse": verse number (11-18)
- "reference": "Proverbs 3:X"
- "instances": array of detected figurative language instances (empty array if none)

Example structure:
[
  {{
    "verse": 11,
    "reference": "Proverbs 3:11",
    "instances": [
      {{
        "figurative_language": "yes",
        "metaphor": "yes",
        "hebrew_text": "...",
        "english_text": "...",
        "target": ["specific", "category", "domain"],
        "vehicle": ["specific", "category", "domain"],
        "ground": ["specific", "category", "domain"],
        "posture": ["specific", "category", "domain"],
        "explanation": "...",
        "confidence": 0.9
      }}
    ]
  }},
  {{
    "verse": 12,
    "reference": "Proverbs 3:12",
    "instances": []
  }},
  ...
]

IMPORTANT: Return ONLY the JSON array. Do not include any explanatory text before or after the JSON.
"""

print(f"\n{'='*80}")
print("Calling API with batched prompt...")
print(f"{'='*80}\n")

# Call the API directly
start_time = datetime.now()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    # Build messages
    messages = [
        {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
        {"role": "user", "content": batched_prompt}
    ]

    # Call API with appropriate parameters
    if MODEL_NAME == "gpt-5.1":
        response = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=messages,
            max_completion_tokens=65536,
            reasoning_effort=REASONING_EFFORT
        )
    else:  # gpt-5-mini
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            max_completion_tokens=65536
        )

    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Extract token usage
    token_metadata = {}
    if hasattr(response, 'usage'):
        token_metadata['input_tokens'] = getattr(response.usage, 'prompt_tokens', 0)
        token_metadata['output_tokens'] = getattr(response.usage, 'completion_tokens', 0)
        token_metadata['reasoning_tokens'] = getattr(response.usage, 'reasoning_tokens', 0)
        token_metadata['total_tokens'] = token_metadata['input_tokens'] + token_metadata['output_tokens']

        # Calculate cost based on model
        if MODEL_NAME == "gpt-5.1":
            # GPT-5.1 pricing: $1.25/M input + $10.00/M output
            cost = (token_metadata['input_tokens'] / 1_000_000 * 1.25 +
                   token_metadata['output_tokens'] / 1_000_000 * 10.0)
        else:  # gpt-5-mini
            # GPT-5-mini pricing: $0.25/M input + $2.00/M output
            cost = (token_metadata['input_tokens'] / 1_000_000 * 0.25 +
                   token_metadata['output_tokens'] / 1_000_000 * 2.0)

        token_metadata['cost'] = cost

    # Extract response text
    response_text = response.choices[0].message.content

    print(f"API call completed in {processing_time:.1f}s")
    print(f"Token usage:")
    print(f"  Input tokens: {token_metadata.get('input_tokens', 0):,}")
    print(f"  Output tokens: {token_metadata.get('output_tokens', 0):,}")
    print(f"  Reasoning tokens: {token_metadata.get('reasoning_tokens', 0):,}")
    print(f"  Total tokens: {token_metadata.get('total_tokens', 0):,}")
    print(f"  Cost: ${token_metadata.get('cost', 0):.4f}")
    print()

    # Parse JSON response
    print("Parsing JSON response...")

    # Extract JSON array from response (handle potential markdown wrappers)
    json_text = response_text.strip()
    if json_text.startswith("```json"):
        json_text = json_text[7:]
    if json_text.startswith("```"):
        json_text = json_text[3:]
    if json_text.endswith("```"):
        json_text = json_text[:-3]
    json_text = json_text.strip()

    # Parse JSON
    verse_results = json.loads(json_text)

    if not isinstance(verse_results, list):
        raise ValueError(f"Expected JSON array, got {type(verse_results)}")

    print(f"Parsed {len(verse_results)} verse results")

    # Calculate summary statistics
    total_instances = sum(len(vr.get('instances', [])) for vr in verse_results)
    detection_rate = total_instances / len(verse_results) if verse_results else 0
    cost_per_verse = token_metadata.get('cost', 0) / len(verses) if verses else 0

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Model: {MODEL_NAME}")
    if MODEL_NAME == "gpt-5.1":
        print(f"Reasoning Effort: {REASONING_EFFORT}")
    print(f"Verses processed: {len(verse_results)}")
    print(f"Total instances detected: {total_instances}")
    print(f"Detection rate: {detection_rate:.2f} instances/verse")
    print(f"Total cost: ${token_metadata.get('cost', 0):.4f}")
    print(f"Cost per verse: ${cost_per_verse:.4f}/verse")
    print(f"Total time: {processing_time:.1f}s")
    print(f"API calls: 1 (TRUE BATCHING)")
    print("=" * 80)

    print("\nDetailed results by verse:")
    for vr in verse_results:
        verse_num = vr.get('verse', 'unknown')
        reference = vr.get('reference', f'Proverbs 3:{verse_num}')
        instances = vr.get('instances', [])

        # Find original verse data
        original_verse = next((v for v in verses if v['verse'] == verse_num), None)
        english = original_verse['english'] if original_verse else 'Unknown'

        print(f"\n{reference}:")
        print(f"  English: {english}")
        print(f"  Detected: {len(instances)} instances")

        if len(instances) > 0:
            for i, inst in enumerate(instances, 1):
                fig_type = "metaphor" if inst.get('metaphor') == 'yes' else 'figurative'
                text = inst.get('english_text', 'N/A')
                explanation = inst.get('explanation', 'No explanation')
                confidence = inst.get('confidence', 0.0)
                print(f"    {i}. {fig_type}: {text}")
                print(f"       Confidence: {confidence}")
                print(f"       {explanation}")

    # Save results to JSON
    output_data = {
        'test_info': {
            'passage': 'Proverbs 3:11-18',
            'approach': 'TRUE BATCHING - All 8 verses in SINGLE API call',
            'model': MODEL_NAME,
            'reasoning_effort': REASONING_EFFORT if MODEL_NAME == "gpt-5.1" else None,
            'timestamp': timestamp,
            'total_verses': len(verse_results),
            'total_detected': total_instances,
            'detection_rate': detection_rate,
            'total_cost': token_metadata.get('cost', 0),
            'cost_per_verse': cost_per_verse,
            'total_time': processing_time,
            'api_calls': 1,
            'token_usage': token_metadata,
            'chapter_context_size': len(full_chapter_context),
            'prompt_size': len(batched_prompt)
        },
        'full_chapter_context': full_chapter_context,
        'batched_prompt': batched_prompt,
        'raw_response': response_text,
        'verses': verse_results
    }

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Results saved to: {results_file}")
    print(f"Logs saved to: {log_file}")
    print(f"{'='*80}")

except Exception as e:
    logger.error(f"Error during batched analysis: {e}")
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
