#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-based figurative language detection for Hebrew biblical texts
"""
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class FigurativeInstance:
    """Represents a detected figurative language instance"""
    type: str
    confidence: float
    hebrew_text: str
    english_text: str
    explanation: str
    subcategory: Optional[str] = None


class LLMFigurativeDetector:
    """LLM-powered figurative language detection using few-shot prompting"""

    def __init__(self):
        self.system_prompt = """You are a biblical Hebrew scholar expert in identifying figurative language in ancient Hebrew texts. You analyze both Hebrew and English text to find metaphors, similes, personification, idioms, hyperbole, and other figurative language.

Your task is to identify ALL instances of figurative language in the given verse, working primarily from the Hebrew but using English for context. Be thorough but precise."""

        self.few_shot_examples = [
            {
                "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
                "english": "The LORD is my shepherd; I shall not want",
                "analysis": [
                    {
                        "type": "metaphor",
                        "hebrew_text": "יְהוָה רֹעִי",
                        "english_text": "The LORD is my shepherd",
                        "explanation": "God is metaphorically compared to a shepherd who cares for and guides his flock",
                        "subcategory": "pastoral",
                        "confidence": 0.95
                    }
                ]
            },
            {
                "hebrew": "וַיֹּאמֶר אֱלֹהִים נַעֲשֶׂה אָדָם בְּצַלְמֵנוּ כִּדְמוּתֵנוּ",
                "english": "And God said, \"Let us make humankind in our image, after our likeness\"",
                "analysis": [
                    {
                        "type": "personification",
                        "hebrew_text": "וַיֹּאמֶר אֱלֹהִים",
                        "english_text": "And God said",
                        "explanation": "God is given the human characteristic of speech",
                        "subcategory": "divine",
                        "confidence": 0.9
                    },
                    {
                        "type": "metaphor",
                        "hebrew_text": "בְּצַלְמֵנוּ",
                        "english_text": "in our image",
                        "explanation": "Humans are described as reflections or representations of divine nature",
                        "subcategory": "divine",
                        "confidence": 0.85
                    },
                    {
                        "type": "metaphor",
                        "hebrew_text": "כִּדְמוּתֵנוּ",
                        "english_text": "after our likeness",
                        "explanation": "Humans described as having similarity to divine form or essence",
                        "subcategory": "divine",
                        "confidence": 0.85
                    }
                ]
            },
            {
                "hebrew": "בְּרֵאשִׁית בָּרָא אֱלֹהִים אֵת הַשָּׁמַיִם וְאֵת הָאָרֶץ",
                "english": "In the beginning God created the heavens and the earth",
                "analysis": [
                    {
                        "type": "personification",
                        "hebrew_text": "בָּרָא אֱלֹהִים",
                        "english_text": "God created",
                        "explanation": "God is attributed the human-like action of creating or making",
                        "subcategory": "divine",
                        "confidence": 0.9
                    }
                ]
            }
        ]

        self.subcategories = {
            "body": "References to human body parts (hand, heart, eye, etc.)",
            "pastoral": "Shepherding, flocks, pastures, guidance imagery",
            "agricultural": "Farming, planting, harvesting, vineyard imagery",
            "familial": "Family relationships, father, mother, children",
            "architectural": "Building, foundation, house, temple imagery",
            "military": "War, battle, armor, weapons imagery",
            "natural": "Mountains, rivers, fire, wind, earth elements",
            "divine": "God's actions, characteristics, or nature",
            "zoological": "Animal comparisons and imagery",
            "commercial": "Trade, buying, selling, treasure imagery"
        }

    def create_analysis_prompt(self, hebrew_text: str, english_text: str) -> str:
        """Create the analysis prompt for the LLM"""

        examples_text = ""
        for i, example in enumerate(self.few_shot_examples, 1):
            examples_text += f"\nExample {i}:\n"
            examples_text += f"Hebrew: {example['hebrew']}\n"
            examples_text += f"English: {example['english']}\n"
            examples_text += f"Analysis: {json.dumps(example['analysis'], ensure_ascii=False, indent=2)}\n"

        prompt = f"""{self.system_prompt}

Here are examples of how to analyze figurative language:
{examples_text}

Types of figurative language to identify:
- metaphor: Direct comparison without "like/as" (X is Y)
- simile: Comparison using "like/as" or Hebrew כְּ
- personification: Human characteristics given to non-human entities
- idiom: Expressions with meaning different from literal interpretation
- hyperbole: Deliberate exaggeration for emphasis
- metonymy: Substituting the name of something with something closely associated

Subcategories available: {', '.join(self.subcategories.keys())}

Now analyze this verse:
Hebrew: {hebrew_text}
English: {english_text}

Provide your analysis as a JSON array of objects, each with:
- type: the figurative language type
- hebrew_text: the specific Hebrew words that are figurative
- english_text: the corresponding English text
- explanation: why this is figurative language and what it means
- subcategory: which domain this belongs to (from the list above)
- confidence: your confidence level (0.0-1.0)

Be thorough - find ALL instances of figurative language in this verse. If no figurative language is present, return an empty array [].

Analysis:"""

        return prompt

    def parse_llm_response(self, response_text: str) -> List[FigurativeInstance]:
        """Parse LLM JSON response into FigurativeInstance objects"""
        try:
            # Extract JSON from response (handle potential extra text)
            json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
            if not json_match:
                return []

            json_str = json_match.group(0)
            analysis_data = json.loads(json_str)

            instances = []
            for item in analysis_data:
                if not isinstance(item, dict):
                    continue

                instance = FigurativeInstance(
                    type=item.get('type', '').lower(),
                    confidence=float(item.get('confidence', 0.0)),
                    hebrew_text=item.get('hebrew_text', ''),
                    english_text=item.get('english_text', ''),
                    explanation=item.get('explanation', ''),
                    subcategory=item.get('subcategory', '')
                )

                # Validate the instance
                if instance.type and instance.confidence > 0:
                    instances.append(instance)

            return instances

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing LLM response: {e}")
            print(f"Response text: {response_text}")
            return []

    def detect_figurative_language(self, hebrew_text: str, english_text: str,
                                   use_actual_llm: bool = False) -> List[Dict]:
        """
        Detect figurative language using LLM analysis

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation for context
            use_actual_llm: Whether to use real LLM API or simulation

        Returns:
            List of detection results compatible with existing pipeline
        """
        # Create the prompt
        prompt = self.create_analysis_prompt(hebrew_text, english_text)

        if use_actual_llm:
            # Use actual LLM API
            llm_response = self._call_actual_llm(prompt)
        else:
            # Use simulation for testing
            llm_response = self._simulate_llm_response(hebrew_text, english_text)

        # Parse the response
        instances = self.parse_llm_response(llm_response)

        # Convert to pipeline-compatible format
        results = []
        for instance in instances:
            result = {
                'type': instance.type,
                'confidence': instance.confidence,
                'pattern': 'llm_detected',
                'figurative_text': instance.english_text,
                'explanation': instance.explanation,
                'subcategory': instance.subcategory,
                'hebrew_source': instance.hebrew_text
            }
            results.append(result)

        return results

    def _call_actual_llm(self, prompt: str) -> str:
        """Call actual LLM API (Claude, Gemini, etc.)"""
        try:
            # This would integrate with your LLM usage manager
            # For now, return a placeholder

            # Example integration:
            # from .llm_manager import LLMUsageMonitor, LLMApiClient
            # monitor = LLMUsageMonitor()
            # client = LLMApiClient(monitor)
            # response = client.call_llm(prompt)
            # return response['content']

            return self._simulate_llm_response("", "")  # Fallback to simulation

        except Exception as e:
            print(f"LLM API call failed: {e}")
            return "[]"  # Return empty result on failure

    def _simulate_llm_response(self, hebrew_text: str, english_text: str) -> str:
        """Simulate LLM response for testing (replace with actual API call)"""

        # Simulate realistic responses based on text content
        if "יהוה" in hebrew_text and ("said" in english_text.lower() or "speak" in english_text.lower()):
            return """[
                {
                    "type": "personification",
                    "hebrew_text": "יהוה",
                    "english_text": "the LORD",
                    "explanation": "God is given human characteristics of speech and communication",
                    "subcategory": "divine",
                    "confidence": 0.9
                }
            ]"""

        elif "כְּ" in hebrew_text or " as " in english_text or " like " in english_text:
            return """[
                {
                    "type": "simile",
                    "hebrew_text": "כְּ",
                    "english_text": "as/like comparison",
                    "explanation": "Direct comparison using Hebrew כְּ or English 'as/like'",
                    "subcategory": "comparative",
                    "confidence": 0.85
                }
            ]"""

        elif "צלם" in hebrew_text or "image" in english_text:
            return """[
                {
                    "type": "metaphor",
                    "hebrew_text": "צלם",
                    "english_text": "image",
                    "explanation": "Metaphorical concept of divine image - humans as reflections of God's nature",
                    "subcategory": "divine",
                    "confidence": 0.8
                }
            ]"""

        else:
            return "[]"  # No figurative language detected


def test_llm_detector():
    """Test the LLM-based detector"""
    detector = LLMFigurativeDetector()

    test_cases = [
        {
            "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
            "english": "The LORD is my shepherd; I shall not want"
        },
        {
            "hebrew": "וַיֹּאמֶר יְהוָה אֱלֹהִים",
            "english": "And the LORD God said"
        },
        {
            "hebrew": "בְּצַלְמֵנוּ כִּדְמוּתֵנוּ",
            "english": "in our image, after our likeness"
        }
    ]

    print("=== Testing LLM-Based Figurative Language Detection ===\n")

    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}:")
        print(f"Hebrew: {case['hebrew']}")
        print(f"English: {case['english']}")

        results = detector.detect_figurative_language(case['hebrew'], case['english'])

        if results:
            print(f"Found {len(results)} figurative language instances:")
            for j, result in enumerate(results, 1):
                print(f"  {j}. {result['type']} ({result['confidence']:.2f})")
                print(f"     Text: {result['figurative_text']}")
                print(f"     Explanation: {result['explanation']}")
                print(f"     Category: {result['subcategory']}")
        else:
            print("No figurative language detected.")

        print()


if __name__ == "__main__":
    test_llm_detector()