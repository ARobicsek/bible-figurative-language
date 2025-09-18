#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Gemini API integration for figurative language detection
"""
import google.generativeai as genai
import json
import time
from typing import List, Dict, Optional


class GeminiAPIClient:
    """Real Gemini API client for figurative language analysis"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini API client

        Args:
            api_key: Gemini API key
        """
        self.api_key = api_key
        genai.configure(api_key=api_key)

        # Configure the model - using Gemini 1.5 Flash (2.5 has stricter safety filters)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Generation config for consistent JSON output
        self.generation_config = {
            'temperature': 0.1,  # Low temperature for consistent analysis
            'top_p': 0.8,
            'top_k': 40,
            'max_output_tokens': 2048,
        }

        # Usage tracking
        self.request_count = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def analyze_figurative_language(self, hebrew_text: str, english_text: str) -> str:
        """
        Analyze Hebrew text for figurative language using Gemini

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation

        Returns:
            JSON string with analysis results
        """
        prompt = self._create_analysis_prompt(hebrew_text, english_text)

        try:
            # Make API call to Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            # Track usage
            self.request_count += 1
            if hasattr(response, 'usage_metadata'):
                self.total_input_tokens += getattr(response.usage_metadata, 'prompt_token_count', 0)
                self.total_output_tokens += getattr(response.usage_metadata, 'candidates_token_count', 0)

            # Extract text from response
            if response.text:
                return response.text.strip()
            else:
                return "[]"  # Empty result

        except Exception as e:
            print(f"Gemini API error: {e}")
            return "[]"  # Return empty on error

    def _create_analysis_prompt(self, hebrew_text: str, english_text: str) -> str:
        """Create the analysis prompt for Gemini"""

        prompt = f"""You are a biblical Hebrew scholar expert in identifying figurative language. Analyze this Hebrew biblical verse for ALL instances of figurative language.

Hebrew: {hebrew_text}
English: {english_text}

EXAMPLES of what to look for:

Example 1:
Hebrew: יְהוָה רֹעִי לֹא אֶחְסָר
English: The LORD is my shepherd; I shall not want
Analysis: [{{"type": "metaphor", "hebrew_text": "יְהוָה רֹעִי", "english_text": "The LORD is my shepherd", "explanation": "God is metaphorically compared to a shepherd who guides and protects his flock", "subcategory": "pastoral", "confidence": 0.95}}]

Example 2:
Hebrew: וַיֹּאמֶר אֱלֹהִים
English: And God said
Analysis: [{{"type": "personification", "hebrew_text": "וַיֹּאמֶר אֱלֹהִים", "english_text": "And God said", "explanation": "God is given the human characteristic of speech and verbal communication", "subcategory": "divine", "confidence": 0.9}}]

Example 3:
Hebrew: כַּאֲשֶׁר שָׂשׂ עַל־אֲבֹתֶיךָ
English: as he delighted in your ancestors
Analysis: [{{"type": "simile", "hebrew_text": "כַּאֲשֶׁר", "english_text": "as he delighted", "explanation": "Direct comparison using Hebrew כַּאֲשֶׁר (ka-asher) meaning 'as/like'", "subcategory": "comparative", "confidence": 0.9}}]

TYPES to identify:
- metaphor: Direct comparison without "like/as" (X is Y)
- simile: Comparison using "like/as" or Hebrew כְּ/כַּאֲשֶׁר
- personification: Human characteristics given to non-human entities (especially God)
- idiom: Expressions with meaning different from literal interpretation
- hyperbole: Deliberate exaggeration for emphasis
- metonymy: Substituting name with something closely associated

SUBCATEGORIES:
- divine: God's actions, nature, characteristics
- pastoral: Shepherding, guidance, care imagery
- body: Human body parts (heart, hand, eye, etc.)
- natural: Earth, mountains, water, fire elements
- familial: Family relationships, father/mother/child
- comparative: Direct comparisons and similes
- agricultural: Farming, planting, harvest imagery

IMPORTANT:
- Work primarily from the HEBREW text, using English for context
- Look for Hebrew-specific patterns like כְּ (simile marker), divine names (יהוה, אלהים)
- Find ALL instances - don't stop at the first one
- Be scholarly and precise in explanations
- Pay special attention to God performing human actions (personification)
- Identify the SPEAKER: "God", "Moses", "Narrator", "Abraham", etc.

Provide analysis as valid JSON array. Each object must have: type, hebrew_text, english_text, explanation, subcategory, confidence (0.0-1.0), speaker.

If no figurative language found, return: []

Analysis:"""

        return prompt

    def get_usage_info(self) -> Dict:
        """Get current usage statistics"""
        return {
            'request_count': self.request_count,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'total_tokens': self.total_input_tokens + self.total_output_tokens
        }

    def test_api_connection(self) -> bool:
        """Test if API connection is working"""
        try:
            response = self.model.generate_content("Test message", generation_config=self.generation_config)
            return response.text is not None
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False


def test_gemini_api():
    """Test the Gemini API with sample Hebrew text"""

    # Initialize client
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    client = GeminiAPIClient(api_key)

    print("=== TESTING REAL GEMINI API ===")

    # Test connection
    if not client.test_api_connection():
        print("❌ API connection failed")
        return

    print("✅ API connection successful")

    # Test cases
    test_cases = [
        {
            "name": "Psalm 23:1 - Shepherd metaphor",
            "hebrew": "יְהוָה רֹעִי לֹא אֶחְסָר",
            "english": "The LORD is my shepherd; I shall not want"
        },
        {
            "name": "Deuteronomy 30:9 - God delighting (personification + simile)",
            "hebrew": "כִּי יָשׁוּב יְהוָה לָשׂוּשׂ עָלֶיךָ לְטוֹב כַּאֲשֶׁר שָׂשׂ עַל־אֲבֹתֶיךָ",
            "english": "For the LORD will again delight in your well-being as he delighted in your ancestors"
        }
    ]

    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"Hebrew: {case['hebrew']}")
        print(f"English: {case['english']}")

        # Call Gemini API
        start_time = time.time()
        result = client.analyze_figurative_language(case['hebrew'], case['english'])
        api_time = time.time() - start_time

        print(f"API Response Time: {api_time:.2f}s")
        print(f"Raw Response: {result}")

        # Try to parse JSON
        try:
            parsed = json.loads(result)
            print(f"Parsed Analysis: {len(parsed) if isinstance(parsed, list) else 0} instances found")

            if isinstance(parsed, list):
                for i, instance in enumerate(parsed, 1):
                    if isinstance(instance, dict):
                        print(f"  {i}. {instance.get('type', 'unknown')} ({instance.get('confidence', 0):.2f})")
                        print(f"     {instance.get('explanation', 'No explanation')}")
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {e}")


if __name__ == "__main__":
    test_gemini_api()