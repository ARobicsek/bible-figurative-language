#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Real Gemini API integration for figurative language detection
"""
import google.generativeai as genai
import os
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

    def analyze_figurative_language(self, hebrew_text: str, english_text: str) -> tuple[str, Optional[str]]:
        """
        Analyze Hebrew text for figurative language using Gemini

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation

        Returns:
            Tuple of (JSON string with analysis results, error message if restricted)
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

            # Check for safety restrictions or blocked content
            if hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'finish_reason') and candidate.finish_reason:
                    # Check if content was blocked by safety filters or other restrictions
                    finish_reason = candidate.finish_reason
                    if hasattr(finish_reason, 'name') and finish_reason.name in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Content restricted: {finish_reason.name}"
                        return "[]", error_msg
                    elif str(finish_reason) in ['SAFETY', 'RECITATION', 'OTHER']:
                        error_msg = f"Content restricted: {finish_reason}"
                        return "[]", error_msg

            # Extract text from response
            if response.text:
                return response.text.strip(), None
            else:
                return "[]", "No response text generated"  # Empty result

        except Exception as e:
            error_msg = f"Gemini API error: {str(e)}"
            print(error_msg)
            return "[]", error_msg  # Return empty on error

    def _create_analysis_prompt(self, hebrew_text: str, english_text: str) -> str:
        """Create the analysis prompt for Gemini"""

        prompt = f"""You are a biblical Hebrew scholar expert in identifying figurative language.

Hebrew: {hebrew_text}
English: {english_text}

🚨 **CRITICAL EXCLUSIONS - READ FIRST** 🚨
**DO NOT MARK THE FOLLOWING AS FIGURATIVE LANGUAGE:**

**CREATION NARRATIVES (Genesis 1-3) - BE EXTREMELY CONSERVATIVE:**
• "unformed and void" (תֹ֙הוּ֙וָבֹ֔הוּ) = LITERAL primordial state description
• "darkness over the surface of the deep" = LITERAL description of pre-creation
• "lights" and "signs for set times" = LITERAL celestial function descriptions
• "earth brought forth" = LITERAL creation action (NOT personification)
• "breath of life" (נִשְׁמַת חַיִּים) = TECHNICAL theological term
• "living being" (נֶפֶשׁ חַיָּה) = TECHNICAL term for living creature
• "dominate/rule" celestial bodies = LITERAL functional descriptions
• "flow/mist from ground" = LITERAL irrigation description
• Divine creating, speaking, blessing = STANDARD creation actions

**NEVER CLASSIFY AS FIGURATIVE:**
• Divine standard actions: God spoke, blessed, created, made, saw, heard
• Technical religious terms: holy, clean, unclean, offering, covenant
• Literal historical statements: "we were slaves", "brought out of Egypt"
• Straightforward descriptions: "good land", "evil generation", "great nation"
• Literal geographic/physical descriptions
• Standard biblical narrative language
• Technical theological terminology
• Procedural/instructional language using "as/like"

**NARRATIVE STATEMENTS - ALWAYS LITERAL:**
• Character actions with literal agency: "serpent duped me" = LITERAL fact
• Relationship descriptions: "enmity between you and woman" = LITERAL relationship
• Physical appearance: "delight to the eyes" = LITERAL attractiveness
• Factual character descriptions in narrative context

**EXTREMELY HIGH THRESHOLD FOR FIGURATIVE DETECTION:**
Only mark as figurative if there is CLEAR cross-domain comparison or obvious human traits given to non-human entities. When in doubt, classify as LITERAL.

📋 **METAPHOR vs PERSONIFICATION - SIMPLE RULES** 📋

**METAPHOR:** Compares two different kinds of things
• "God is a shepherd" = God compared to pastoral role
• "mighty hand of God" = divine power compared to human body part
• Cross-domain comparisons where A is described as B

**PERSONIFICATION:** Gives human actions/qualities to non-human things
• "shrewdest of beasts" = animal given human intelligence trait
• "land spewed out inhabitants" = land given human action of vomiting
• Non-human entities acting/feeling like humans

**KEY DISTINCTION:**
- METAPHOR = X is like Y (comparison)
- PERSONIFICATION = non-human X does/feels human thing Y (attribution)

IF YOU'RE NOT SURE → CLASSIFY AS LITERAL

✅ **WHEN TO MARK AS FIGURATIVE - ONLY THESE:**

**CLEAR METAPHORS:**
• Cross-domain comparisons: "God is shepherd" (divine ↔ pastoral)
• Divine body parts: "mighty hand" (God has no literal body)
• A is B statements where A and B are genuinely different categories

**CLEAR PERSONIFICATION:**
• Non-human entities given human actions: "land vomited out inhabitants"
• Divine emotions beyond standard actions: God angry, jealous, regretful
• Abstract concepts acting as agents: Wisdom speaks, Death swallows

**CLEAR SIMILES:**
• UNLIKE things compared with "like/as": "numerous as stars"
• NOT procedural instructions or historical precedents

**ONLY MARK IF:**
1. CLEAR cross-domain transfer OR obvious human traits to non-human
2. Confidence > 0.7
3. NOT in the exclusion lists above
4. Would NOT be understood as literal by ancient readers

**SIMPLE CLASSIFICATION:**
For any figurative language found, use basic categories:
- Vehicle: "nature", "human", "divine", "abstract"
- Tenor: "God", "people", "nation", "covenant"
- Keep explanations short and clear

🔍 **ANALYSIS INSTRUCTIONS:**
- "Ritual and Worship" - for religious practices, ceremonial activities, and covenantal symbols

VEHICLE LEVEL 2 (Specific Domain):
THE NATURAL WORLD:
  - animal: characteristics/behavior of creatures (lion, eagle, sheep, etc.)
  - agricultural: farming, crops, livestock (vineyard, shepherd, harvest, etc.)
  - elemental: forces of nature (fire, wind, water, light, storm, etc.)
  - geological: earth features (rock, mountain, spring, foundation, etc.)
  - celestial: sky and heavenly bodies (stars, sun, moon, heaven, etc.)

HUMAN INSTITUTIONS AND RELATIONSHIPS:
  - familial: direct family relationships (father, mother, brother, inheritance, etc.)
  - military: warfare, weapons (shield, sword, warrior, battle, conquest, etc.)
  - architectural: buildings, structures (fortress, refuge, tower, house, etc.)
  - political-legal: power, authority, leadership, judicial actions (king, judge, dominance, rule, etc.)
  - interpersonal: general human relationships and interactions (face to face, serve, etc.)
  - social-status: hierarchical position, social standing (head and tail, high above, treading on backs, etc.)

ABSTRACT AND INTERNAL STATES:
  - psychological-cognitive: mental states, thoughts, understanding (gain insight, harden heart, etc.)
  - moral-spiritual: sin, righteousness, wickedness (no-gods, treacherous breed, etc.)
  - temporal: time, duration (ancient, eternal, brief, seasons, etc.)
  - economic: trade, prosperity (wealth, poverty, lending, etc.)
  - industrial: craftsmanship, labor (refining, metalwork, etc.)

BODY AND ANATOMY:
  - anthropomorphic-divine: God's body parts representing power/presence (hand, arm, face, eyes, etc.)
  - human-body: human body parts for actions/emotions (heart for will, hand for action, etc.)

RITUAL AND WORSHIP:
  - sacrificial: offerings, ritual sacrifice imagery (in your nostrils, etc.)
  - priestly: ceremonial functions (Thummim and Urim, etc.)
  - covenantal: blessing, curse, covenant symbols and practices

TENOR CLASSIFICATION - Two-Level System:
These represent the major thematic domains of the Pentateuch:

TENOR LEVEL 1 (Broad Categories):
- "Divine-Human Relationship" - God's nature, character, actions; humanity/Israel's identity
- "Covenant & Its Consequences" - blessings for obedience, curses for disobedience

TENOR LEVEL 2 (Specific Subcategories):
DIVINE-HUMAN RELATIONSHIP:
  - Divine Sovereignty: God as Creator, ultimate ruler, judge, authority
  - Divine Presence: God's tangible manifestations, closeness, theophany
  - Divine Provision: God as sustainer, provider, deliverer, nurturer
  - Israel's Identity: Israel's unique covenantal status as YHWH's chosen people
  - Humanity's Status: general human nature, purpose, moral character
  - Moral & Spiritual State: internal spiritual/moral dispositions, heart/soul metaphors

COVENANT & ITS CONSEQUENCES:
  - Blessing: rewards of obedience - material prosperity, social elevation
  - Curse: consequences of disobedience - material destitution, humiliation, subjugation
  - Idolatry: false worship, spiritual adultery, no-gods
  - Wisdom & Discernment: understanding, foolishness, intellectual/spiritual insight

[CLASSIFICATION EXAMPLES WITH IMPROVED CATEGORIES]:

Example 1 - Military Vehicle for Divine Action:
Hebrew: "you shall tread upon their backs"
Analysis: [{{"type": "metaphor", "vehicle_level_1": "Human Institutions and Relationships", "vehicle_level_2": "military", "tenor_level_1": "Divine-Human Relationship", "tenor_level_2": "Divine Sovereignty", "explanation": "Military imagery of conquest for divine victory"}}]

Example 2 - Anthropomorphic Divine Body Part:
Hebrew: "My hand lays hold on judgment"
Analysis: [{{"type": "metaphor", "vehicle_level_1": "Body and Anatomy", "vehicle_level_2": "anthropomorphic-divine", "tenor_level_1": "Divine-Human Relationship", "tenor_level_2": "Divine Sovereignty", "explanation": "God's hand represents divine judicial power"}}]

Example 3 - Social Status for Covenant Blessing:
Hebrew: "head and not the tail"
Analysis: [{{"type": "metaphor", "vehicle_level_1": "Human Institutions and Relationships", "vehicle_level_2": "social-status", "tenor_level_1": "Covenant & Its Consequences", "tenor_level_2": "Blessing", "explanation": "Hierarchical positioning metaphor for covenant elevation"}}]

Example 4 - Idolatry Classification:
Hebrew: "sculptured image"
Analysis: [{{"type": "metaphor", "vehicle_level_1": "Abstract and Internal States", "vehicle_level_2": "moral-spiritual", "tenor_level_1": "Covenant & Its Consequences", "tenor_level_2": "Idolatry", "explanation": "False worship imagery representing spiritual corruption"}}]

Example 5 - Moral/Spiritual State:
Hebrew: "harden your heart"
Analysis: [{{"type": "metaphor", "vehicle_level_1": "Abstract and Internal States", "vehicle_level_2": "psychological-cognitive", "tenor_level_1": "Divine-Human Relationship", "tenor_level_2": "Moral & Spiritual State", "explanation": "Internal disposition metaphor for spiritual rebellion"}}]

Provide analysis as valid JSON array. Each object must have: type, hebrew_text, english_text, explanation, vehicle_level_1, vehicle_level_2, tenor_level_1, tenor_level_2, confidence (0.7-1.0), speaker, purpose.

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
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it before running.")

    client = GeminiAPIClient(api_key)

    print("=== TESTING REAL GEMINI API ===")

    # Test connection
    if not client.test_api_connection():
        print("[ERROR] API connection failed")
        return

    print("[OK] API connection successful")

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
        result, error = client.analyze_figurative_language(case['hebrew'], case['english'])
        api_time = time.time() - start_time

        print(f"API Response Time: {api_time:.2f}s")
        if error:
            print(f"LLM Restriction Error: {error}")
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
