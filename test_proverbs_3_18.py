#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test Proverbs 3:18 with detailed logging to debug why nothing is detected"""

import sys
import os
import logging

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'private/src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'private'))

from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test verse - Proverbs 3:18
hebrew = "עֵץ־חַיִּ֣ים הִ֭יא לַמַּחֲזִיקִ֣ים בָּ֑הּ וְֽתֹמְכֶ֥יהָ מְאֻשָּֽׁר׃"
english = "She is a tree of life to those who grasp her, And whoever holds on to her is happy."

# Chapter context (abbreviated for testing)
chapter_context = """
Proverbs 3 (abbreviated context):
Hebrew: My son, do not forget my teaching...
...
Happy is the person who finds wisdom...
She is more precious than rubies...
Length of days is in her right hand...
She is a tree of life to those who grasp her... (THIS VERSE)
"""

print("=" * 80)
print("TESTING PROVERBS 3:18 - 'She is a tree of life'")
print("=" * 80)
print(f"\nHebrew: {hebrew}")
print(f"English: {english}")
print("\nThis MUST detect figurative language:")
print("  1. 'She' = Wisdom (personification)")
print("  2. 'tree of life' = metaphor")
print("  3. 'grasp her' = metaphorical action")
print("=" * 80)

# Initialize client
print("\nInitializing client...")
client = FlexibleTaggingGeminiClient("", logger=logger)

print("\nCalling analyze_figurative_language_flexible()...")
print("Book: Proverbs, Chapter: 3")
print(f"Chapter context length: {len(chapter_context)} chars")

result, error, metadata = client.analyze_figurative_language_flexible(
    hebrew, english, "Proverbs", 3, chapter_context=chapter_context
)

print("\n" + "=" * 80)
print("RESULTS:")
print("=" * 80)
print(f"Error: {error}")
print(f"Result JSON: {result}")
print(f"\nMetadata:")
for key, value in metadata.items():
    if key not in ['all_detected_instances']:
        print(f"  {key}: {value}")

if 'all_detected_instances' in metadata:
    instances = metadata['all_detected_instances']
    print(f"\nDetected instances: {len(instances)}")
    for i, inst in enumerate(instances, 1):
        print(f"\n  Instance {i}:")
        for k, v in inst.items():
            print(f"    {k}: {v}")

print("\n" + "=" * 80)
if not metadata.get('all_detected_instances'):
    print("❌ FAILURE: No figurative language detected!")
    print("This verse clearly has personification and metaphor.")
else:
    print("✓ SUCCESS: Figurative language detected!")
print("=" * 80)
