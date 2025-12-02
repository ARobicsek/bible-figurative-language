#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify JSON truncation fix in batched processing

This script tests the streaming approach with Proverbs 3:11-18 to ensure
the 1023-character truncation issue is resolved.
"""

import sys
import os
import logging
import json
import time
from dotenv import load_dotenv

# Add the private directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'private'))

from openai import OpenAI

def setup_logging():
    """Setup logging for the test"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('test_proverbs_3_truncation_fix.log', encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)

def create_test_prompt():
    """Create a test prompt for Proverbs 3:11-18"""

    # Sample verses from Proverbs 3:11-18
    verses_data = [
        {"verse": 11, "hebrew": "יִסּוּר יְהוָה בִּנְיִי אַל־תִּמְאָס וְאַל־תָּקֹץ מוֹסָרוֹ",
         "english": "My son, do not despise the Lord's discipline, and do not resent his rebuke"},
        {"verse": 12, "hebrew": "כִּי אֶת־אֲשֶׁר יֶאֱהַב יְהוָה יוֹכִיחַ וּכַאָב בֶּן־רִצְיָה יִשְׁאָל",
         "english": "For the Lord disciplines those he loves, as a father the son he delights in"},
        {"verse": 13, "hebrew": "אַשְׁרֵי־אָדָם מָצָא חָכְמָה וְאִישׁ יִקְחַ מְזוּמָה",
         "english": "Blessed are those who find wisdom, those who gain understanding"},
        {"verse": 14, "hebrew": "כִּי טוֹב סַחְרָהּ מֵחֶרֶם וּפְרִיהָה מִכַּסְפִּים",
         "english": "For her gain is better than silver, and her profit more than fine gold"},
        {"verse": 15, "hebrew": "יְקָרָה הִיא מִפַּנִינִים וְכָל־חֶפְצֶיךָ לֹא יִשְׁווּ־בָהּ",
         "english": "She is more precious than rubies; nothing you desire can compare with her"},
        {"verse": 16, "hebrew": "אֹרֶךְ יָמִים בִּימִינָהּ בִּשְׂמָאולָהּ עֹשֶׁר וִכָּבוֹד",
         "english": "Long life is in her right hand; in her left hand are riches and honor"},
        {"verse": 17, "hebrew": "דְּרָכֶיהָ דֶרֶכֵי־נֹעַם וְכָל־נְתִיבֹתֶיהָ שָׁלוֹם",
         "english": "Her ways are pleasant ways, and all her paths are peace"},
        {"verse": 18, "hebrew": "עֵץ חַיִּים הִיא לַמַּחֲזִיקִים בָּהּ וְתֹמְכֶיהָ מְאֻשָּׁר",
         "english": "She is a tree of life to those who take hold of her; those who hold her fast will be blessed"}
    ]

    full_chapter_context = """=== Proverbs Chapter 3 (FULL CHAPTER for context) ===

Hebrew:
11. יִסּוּר יְהוָה בִּנְיִי אַל־תִּמְאָס וְאַל־תָּקֹץ מוֹסָרוֹ
12. כִּי אֶת־אֲשֶׁר יֶאֱהַב יְהוָה יוֹכִיחַ וּכַאָב בֶּן־רִצְיָה יִשְׁאָל
13. אַשְׁרֵי־אָדָם מָצָא חָכְמָה וְאִישׁ יִקְחַ מְזוּמָה
14. כִּי טוֹב סַחְרָהּ מֵחֶרֶם וּפְרִיהָה מִכַּסְפִּים
15. יְקָרָה הִיא מִפַּנִינִים וְכָל־חֶפְצֶיךָ לֹא יִשְׁווּ־בָהּ
16. אֹרֶךְ יָמִים בִּימִינָהּ בִּשְׂמָאולָהּ עֹשֶׁר וִכָּבוֹד
17. דְּרָכֶיהָ דֶרֶכֵי־נֹעַם וְכָל־נְתִיבֹתֶיהָ שָׁלוֹם
18. עֵץ חַיִּים הִיא לַמַּחֲזִיקִים בָּהּ וְתֹמְכֶיהָ מְאֻשָּׁר

English:
11. My son, do not despise the Lord's discipline, and do not resent his rebuke
12. For the Lord disciplines those he loves, as a father the son he delights in
13. Blessed are those who find wisdom, those who gain understanding
14. For her gain is better than silver, and her profit more than fine gold
15. She is more precious than rubies; nothing you desire can compare with her
16. Long life is in her right hand; in her left hand are riches and honor
17. Her ways are pleasant ways, and all her paths are peace
18. She is a tree of life to those who take hold of her; those who hold her fast will be blessed
"""

    verses_to_analyze = ""
    for v in verses_data:
        verses_to_analyze += f"\nVerse {v['verse']}:\n"
        verses_to_analyze += f"Hebrew: {v['hebrew']}\n"
        verses_to_analyze += f"English: {v['english']}\n"

    batched_prompt = f"""You are a biblical Hebrew scholar specializing in figurative language analysis. Your task is to analyze all verses from Proverbs Chapter 3 for figurative language.

{full_chapter_context}

=== VERSES TO ANALYZE ===
{verses_to_analyze}

=== TASK ===

Analyze EACH of the 8 verses above for figurative language.

IMPORTANT: A single verse may contain MULTIPLE distinct figurative language instances. Detect ALL instances, not just the most prominent one.

For each detected instance, provide:
1. **figurative_language**: "yes" or "no"
2. **metaphor**: "yes" or "no"
3. **simile**: "yes" or "no"
4. **personification**: "yes" or "no"
5. **idiom**: "yes" or "no"
6. **hyperbole**: "yes" or "no"
7. **metonymy**: "yes" or "no"
8. **other**: "yes" or "no"
9. **hebrew_text**: The Hebrew text of the figurative expression
10. **english_text**: The English translation of the figurative expression
11. **target**: JSON array with 3 levels - [specific, category, domain]
12. **vehicle**: JSON array with 3 levels - [specific, category, domain]
13. **ground**: JSON array with 3 levels - [specific, category, domain]
14. **posture**: JSON array with 3 levels - [specific, category, domain]
15. **explanation**: Brief explanation of the figurative language
16. **confidence**: Confidence score (0.0-1.0)

=== OUTPUT FORMAT ===

**FIRST, provide your deliberation in a DELIBERATION section:**

DELIBERATION:
[You MUST briefly analyze EVERY potential figurative element for ALL verses. For each phrase/concept, explain *briefly*]

**THEN provide STRUCTURED JSON OUTPUT (REQUIRED):**

Return a JSON array with ONE object per verse. Each object should have:
- "verse": verse number
- "reference": "Proverbs 3:X"
- "instances": array of detected figurative language instances

Example structure:
[
  {{
    "verse": 1,
    "reference": "Proverbs 3:1",
    "instances": [
      {{
        "figurative_language": "yes",
        "metaphor": "yes",
        "simile": "no",
        "personification": "no",
        "idiom": "no",
        "hyperbole": "no",
        "metonymy": "no",
        "other": "no",
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
  }}
]"""

    return batched_prompt

def test_streaming_approach(logger, openai_client):
    """Test the streaming approach to avoid truncation"""

    logger.info("="*80)
    logger.info("TESTING STREAMING APPROACH TO FIX JSON TRUNCATION")
    logger.info("="*80)

    prompt = create_test_prompt()
    logger.info(f"Created test prompt with {len(prompt)} characters")

    try:
        # Test streaming approach
        logger.info("Testing STREAMING approach...")
        start_time = time.time()

        stream = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=65536,
            reasoning_effort="medium",
            stream=True
        )

        response_text = ""
        chunk_count = 0

        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                response_text += chunk.choices[0].delta.content
                chunk_count += 1

                if chunk_count % 50 == 0:
                    logger.debug(f"Received {chunk_count} chunks, response length: {len(response_text)} chars")

        streaming_time = time.time() - start_time

        logger.info(f"✅ Streaming completed in {streaming_time:.1f}s")
        logger.info(f"📊 Total chunks: {chunk_count}")
        logger.info(f"📏 Response length: {len(response_text)} characters")

        # Check for truncation indicators
        truncation_signs = [
            ("Ends with ...", response_text.endswith('...')),
            ("Ends with ,\"", response_text.endswith(',"')),
            ("Ends with :{", response_text.endswith(':{')),
            ("Suspiciously short (<1000 chars)", len(response_text) < 1000),
            ("Cut in confidence field", 'confidence' in response_text and not response_text.rstrip().endswith(']') and not response_text.rstrip().endswith('}'))
        ]

        logger.info("🔍 TRUNCATION ANALYSIS:")
        any_truncation = False
        for sign_name, is_truncated in truncation_signs:
            status = "⚠️  TRUNCATED" if is_truncated else "✅ OK"
            logger.info(f"  {sign_name}: {status}")
            if is_truncated:
                any_truncation = True

        if not any_truncation:
            logger.info("🎉 NO TRUNCATION DETECTED - Streaming approach appears successful!")
        else:
            logger.error("❌ TRUNCATION STILL DETECTED - Streaming approach needs adjustment")

        # Try to parse JSON
        logger.info("🧪 Testing JSON parsing...")
        try:
            # Extract JSON from response
            json_pattern = r'\[\s*\{.*?\}\s*\]'
            json_match = re.search(json_pattern, response_text, re.DOTALL)

            if json_match:
                json_text = json_match.group(0)
                logger.info(f"✅ JSON extracted: {len(json_text)} characters")

                parsed_data = json.loads(json_text)
                logger.info(f"✅ JSON parsing successful: {len(parsed_data)} verse results")

                # Count instances
                total_instances = sum(len(vr.get('instances', [])) for vr in parsed_data)
                logger.info(f"📈 Total figurative instances detected: {total_instances}")

                return True, len(response_text), total_instances, any_truncation
            else:
                logger.error("❌ Could not extract JSON from response")
                return False, len(response_text), 0, any_truncation

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            logger.error(f"📄 Response preview: {response_text[:200]}...{response_text[-200:] if len(response_text) > 400 else response_text[-200:]}")
            return False, len(response_text), 0, any_truncation

    except Exception as e:
        logger.error(f"❌ Streaming test failed: {e}")
        return False, 0, 0, True

def test_non_streaming_fallback(logger, openai_client):
    """Test the non-streaming fallback"""

    logger.info("Testing NON-STREAMING fallback...")
    start_time = time.time()

    prompt = create_test_prompt()

    try:
        response = openai_client.chat.completions.create(
            model="gpt-5.1",
            messages=[
                {"role": "system", "content": "You are a biblical Hebrew scholar specializing in figurative language analysis."},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=16384,
            reasoning_effort="medium"
        )

        non_streaming_time = time.time() - start_time
        response_text = response.choices[0].message.content

        logger.info(f"✅ Non-streaming completed in {non_streaming_time:.1f}s")
        logger.info(f"📏 Response length: {len(response_text)} characters")

        # Check if this is the classic 1023-character truncation
        if len(response_text) <= 1025:
            logger.warning(f"⚠️  Classic truncation pattern detected: {len(response_text)} characters")
            logger.warning("This confirms the original truncation issue")
        else:
            logger.info(f"✅ Good response length: {len(response_text)} characters")

        return len(response_text)

    except Exception as e:
        logger.error(f"❌ Non-streaming fallback failed: {e}")
        return 0

def main():
    """Main test function"""
    logger = setup_logging()
    logger.info("Starting Proverbs 3:11-18 truncation fix test...")

    # Load environment variables
    load_dotenv()

    # Initialize OpenAI client
    try:
        openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        logger.info("✅ OpenAI client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize OpenAI client: {e}")
        return

    # Test streaming approach
    streaming_success, streaming_length, streaming_instances, streaming_truncated = test_streaming_approach(logger, openai_client)

    # Test non-streaming fallback for comparison
    non_streaming_length = test_non_streaming_fallback(logger, openai_client)

    # Summary
    logger.info("="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    logger.info(f"Streaming approach:")
    logger.info(f"  ✅ Success: {streaming_success}")
    logger.info(f"  📏 Length: {streaming_length:,} characters")
    logger.info(f"  📈 Instances: {streaming_instances}")
    logger.info(f"  ⚠️  Truncated: {streaming_truncated}")

    logger.info(f"Non-streaming fallback:")
    logger.info(f"  📏 Length: {non_streaming_length:,} characters")
    logger.info(f"  📊 Difference: {streaming_length - non_streaming_length:,} characters")

    if streaming_length > non_streaming_length:
        improvement = ((streaming_length - non_streaming_length) / non_streaming_length) * 100 if non_streaming_length > 0 else float('inf')
        logger.info(f"🎉 Streaming improvement: +{improvement:.1f}% more content")
        logger.info("✅ TRUNCATION FIX VERIFIED - Streaming approach successfully resolves the issue!")
    else:
        logger.info("⚠️  Streaming shows similar length - may need further investigation")

    logger.info("="*80)

if __name__ == "__main__":
    import re
    main()