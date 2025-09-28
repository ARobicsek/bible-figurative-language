#!/usr/bin/env python3
"""
Pipeline Testing Script for Flexible Tag-Based Figurative Language System

Tests the new flexible tagging framework on selected biblical passages
to validate:
1. Dynamic tag generation following rule-based taxonomy
2. Hierarchical tagging principles (specific → general)
3. Speaker posture analysis accuracy
4. Scholarly research utility of generated tags
"""

import sys
import os
import json
import logging
from datetime import datetime

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from hebrew_figurative_db.text_extraction.sefaria_client import SefariaClient
from hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient

class FlexibleTaggingTester:
    def __init__(self):
        self.sefaria = SefariaClient()
        self.ai_client = None
        self.logger = self.setup_logging()
        self.tag_rules = self.load_tag_rules()

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def load_tag_rules(self):
        """Load the flexible tagging rules"""
        try:
            with open('tag_taxonomy_rules.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.error("tag_taxonomy_rules.json not found!")
            return {}

    def create_flexible_tagging_prompt(self, hebrew_text, english_text, context):
        """Create enhanced prompt using flexible tagging rules"""

        prompt = f"""
# BIBLICAL FIGURATIVE LANGUAGE ANALYSIS WITH FLEXIBLE TAGGING

## REVOLUTIONARY APPROACH
Apply the **flexible rule-based tag generation system** following structured principles for scholarly research utility.

## TEXT TO ANALYZE
**Hebrew:** {hebrew_text}
**English:** {english_text}
**Context:** {context}

## FLEXIBLE TAGGING FRAMEWORK

Apply the **THREE-DIMENSIONAL ANALYSIS** with **HIERARCHICAL TAGGING**:

### TARGET DIMENSION (What is being described figuratively)
- Tag from specific to general: specific_identity → role → broader_category → domain
- Example: ["moses", "prophet", "leader", "human_individual"]
- Enable both specific searches ("moses") and broad searches ("human_individual")

### VEHICLE DIMENSION (What imagery is used)
- Tag from specific to general: specific_image → type → broader_category → domain
- Example: ["wolf", "predator", "wild_animal", "animal", "fierce_creature"]
- Capture precise imagery and source domain

### GROUND DIMENSION (What target qualities are illuminated + Speaker's posture)
**REQUIRED**: Include speaker posture analysis
- Target qualities being highlighted
- Speaker's attitude/stance toward the target
- Example: ["fierce_behavior", "predatory_instincts", "physical_power", "exasperation_frustration"]

## SPEAKER POSTURE CATEGORIES (Choose appropriate ones):
- reverence_awe, affection_love, anger_indignation, disappointment_grief
- warning_correction, celebration_praise, lament_mourning, exasperation_frustration
- protective_defensive, condemnation_judgment, yearning_longing, shame_regret
- hope_expectation, neutral_descriptive

## OUTPUT FORMAT
For each figurative language instance found, provide:

```json
{{
  "figurative_instances": [
    {{
      "verse": "Deuteronomy 30:5",
      "figurative_text": "[Hebrew phrase with figurative language]",
      "english_text": "[English translation of figurative phrase]",
      "type": "metaphor|simile|personification|hyperbole|metonymy|idiom",
      "explanation": "Detailed explanation of why this is figurative",
      "tags": {{
        "target": ["specific_term", "broader_category", "domain"],
        "vehicle": ["specific_imagery", "imagery_type", "source_domain"],
        "ground": ["target_quality1", "target_quality2", "speaker_posture_X"]
      }},
      "confidence": "high|medium|low",
      "scholarly_research_notes": "How these tags enable research discovery"
    }}
  ]
}}
```

## RESEARCH-FOCUSED VALIDATION
Ensure tags will help scholars:
- Find patterns across biblical books
- Compare similar imagery types
- Analyze rhetorical strategies
- Study speaker attitudes/stances

Analyze the provided text for figurative language using this flexible tagging approach.
"""
        return prompt

    def test_passage(self, book, chapter, verse_range):
        """Test flexible tagging on a specific passage"""

        self.logger.info(f"=== TESTING: {book} {chapter}:{verse_range} ===")

        try:
            # Initialize AI client with API key
            api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"  # From existing scripts
            self.ai_client = MultiModelGeminiClient(api_key)

            results = []

            for verse_num in verse_range:
                verse_ref = f"{book} {chapter}:{verse_num}"
                self.logger.info(f"Processing {verse_ref}")

                # Get Hebrew and English text using correct Sefaria format
                sefaria_ref = f"{book}.{chapter}.{verse_num}"
                try:
                    verses_data, api_time = self.sefaria.extract_hebrew_text(sefaria_ref)
                    if not verses_data:
                        self.logger.warning(f"Could not retrieve text for {verse_ref}")
                        continue

                    verse_data = verses_data[0]  # Should be single verse
                    hebrew_text = verse_data.get('hebrew', '')
                    english_text = verse_data.get('english', '')

                except Exception as e:
                    self.logger.error(f"Error retrieving {verse_ref}: {e}")
                    continue

                # Create context for better analysis
                context = f"This is verse {verse_num} from {book} chapter {chapter}. " \
                         f"This passage discusses God's restoration and circumcision of hearts."

                # Generate flexible tagging prompt
                prompt = self.create_flexible_tagging_prompt(hebrew_text, english_text, context)

                # Analyze with AI
                try:
                    analysis_result = self.ai_client.analyze_figurative_language(
                        hebrew_text, english_text, book, chapter
                    )

                    if analysis_result and isinstance(analysis_result, tuple) and len(analysis_result) >= 3:
                        # Unpack the tuple: (response_text, raw_json, parsed_data)
                        response_text, raw_json, parsed_data = analysis_result

                        results.append({
                            'verse_reference': verse_ref,
                            'hebrew_text': hebrew_text,
                            'english_text': english_text,
                            'analysis': parsed_data,  # Use the parsed dictionary
                            'response_text': response_text,
                            'raw_json': raw_json,
                            'timestamp': datetime.now().isoformat()
                        })

                        self.logger.info(f"Successfully analyzed {verse_ref}")
                    else:
                        self.logger.warning(f"No figurative language detected in {verse_ref}")

                except Exception as e:
                    self.logger.error(f"Analysis failed for {verse_ref}: {e}")

            return results

        except Exception as e:
            self.logger.error(f"Test failed: {e}")
            return []

    def validate_hierarchical_tagging(self, results):
        """Validate that tags follow hierarchical principles"""
        self.logger.info("=== VALIDATING HIERARCHICAL TAGGING ===")

        validation_results = []

        for result in results:
            analysis = result.get('analysis', {})
            instances = analysis.get('figurative_instances', [])

            for instance in instances:
                tags = instance.get('tags', {})
                verse_ref = result['verse_reference']

                validation = {
                    'verse': verse_ref,
                    'figurative_text': instance.get('figurative_text', ''),
                    'hierarchical_validation': {},
                    'research_utility_score': 0
                }

                # Check each dimension for hierarchical structure
                for dimension in ['target', 'vehicle', 'ground']:
                    dim_tags = tags.get(dimension, [])
                    validation['hierarchical_validation'][dimension] = {
                        'tag_count': len(dim_tags),
                        'has_specific_terms': any(len(tag.split('_')) >= 2 for tag in dim_tags),
                        'has_general_terms': any(tag in ['human_individual', 'animal', 'divine'] for tag in dim_tags),
                        'enables_research': len(dim_tags) >= 2  # Multiple levels enable research
                    }

                # Check for required speaker posture
                ground_tags = tags.get('ground', [])
                has_posture = any('posture_' in tag or any(posture in tag for posture in [
                    'reverence', 'affection', 'anger', 'disappointment', 'warning',
                    'celebration', 'lament', 'exasperation', 'protective', 'condemnation',
                    'yearning', 'shame', 'hope', 'neutral'
                ]) for tag in ground_tags)

                validation['has_speaker_posture'] = has_posture
                validation['research_utility_score'] = self.calculate_research_utility(tags)

                validation_results.append(validation)

        return validation_results

    def calculate_research_utility(self, tags):
        """Calculate research utility score based on tag structure"""
        score = 0

        # Points for hierarchical structure in each dimension
        for dimension, dim_tags in tags.items():
            if len(dim_tags) >= 2:
                score += 2  # Multiple levels
            if len(dim_tags) >= 3:
                score += 1  # Rich tagging

        # Points for speaker posture analysis
        ground_tags = tags.get('ground', [])
        if any('posture' in tag or any(p in tag for p in ['reverence', 'anger', 'celebration']) for tag in ground_tags):
            score += 3

        return min(score, 10)  # Cap at 10

    def print_test_results(self, results, validation_results):
        """Print comprehensive test results"""

        print("\n" + "="*80)
        print("FLEXIBLE TAGGING PIPELINE TEST RESULTS")
        print("="*80)

        print(f"\nSUMMARY:")
        print(f"Verses processed: {len(results)}")
        total_instances = sum(len(r.get('analysis', {}).get('figurative_instances', [])) for r in results)
        print(f"Figurative instances found: {total_instances}")

        print(f"\nDETAILED ANALYSIS:")

        for i, result in enumerate(results):
            analysis = result.get('analysis', {})
            instances = analysis.get('figurative_instances', [])

            print(f"\n--- {result['verse_reference']} ---")
            print(f"Hebrew: {result['hebrew_text']}")
            print(f"English: {result['english_text']}")

            if instances:
                for j, instance in enumerate(instances, 1):
                    print(f"\n  Instance {j}:")
                    print(f"    Figurative Text: {instance.get('figurative_text', 'N/A')}")
                    print(f"    Type: {instance.get('type', 'N/A')}")
                    print(f"    Confidence: {instance.get('confidence', 'N/A')}")

                    tags = instance.get('tags', {})
                    print(f"    Tags:")
                    for dimension, dim_tags in tags.items():
                        print(f"      {dimension.upper()}: {dim_tags}")

                    print(f"    Research Notes: {instance.get('scholarly_research_notes', 'N/A')}")
            else:
                print("    No figurative language detected")

        print(f"\nHIERARCHICAL VALIDATION:")
        if validation_results:
            avg_research_score = sum(v['research_utility_score'] for v in validation_results) / len(validation_results)
            posture_coverage = sum(1 for v in validation_results if v['has_speaker_posture']) / len(validation_results) * 100

            print(f"Average Research Utility Score: {avg_research_score:.1f}/10")
            print(f"Speaker Posture Coverage: {posture_coverage:.1f}%")

            print(f"\nDetailed Validation:")
            for validation in validation_results:
                print(f"  {validation['verse']}: Research Score {validation['research_utility_score']}/10")
                if validation['has_speaker_posture']:
                    print(f"    [✓] Speaker posture identified")
                else:
                    print(f"    [X] Missing speaker posture analysis")

def main():
    """Main testing function"""
    tester = FlexibleTaggingTester()

    print("FLEXIBLE TAGGING PIPELINE TESTER")
    print("Testing Deuteronomy 30:5-10 (God's restoration and heart circumcision)")

    # Test the passage
    results = tester.test_passage("Deuteronomy", 30, range(5, 11))  # verses 5-10

    if results:
        # Validate hierarchical tagging
        validation_results = tester.validate_hierarchical_tagging(results)

        # Print comprehensive results
        tester.print_test_results(results, validation_results)

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"flexible_tagging_test_results_{timestamp}.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'test_metadata': {
                    'passage': 'Deuteronomy 30:5-10',
                    'timestamp': timestamp,
                    'system': 'flexible_tag_generation'
                },
                'results': results,
                'validation': validation_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\nResults saved to: {output_file}")

    else:
        print("No results generated. Check logs for errors.")

if __name__ == "__main__":
    main()