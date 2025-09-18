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

        prompt = f"""You are a biblical Hebrew scholar expert in identifying figurative language. Analyze this Hebrew biblical verse for ALL instances of figurative language.

Hebrew: {hebrew_text}
English: {english_text}

⚠️ CRITICAL EXCLUSIONS - DO NOT mark as figurative:

TECHNICAL RELIGIOUS/CULTIC TERMS (these are literal/technical, not figurative):
- Holiness designations: קֹדֶשׁ קׇדָשִׁים ("most holy"), "holy to YHWH", שֶׁקֶל הַקֹּדֶשׁ
- Legal terms: חׇק־עוֹלָם ("perpetual statute"), זִמָּה ("depravity"), תּוֹעֵבָה ("abomination")
- Sacrificial terminology: "sin offering", "guilt offering", "wave offering", "expiation", קׇרְבָּן
- Ritual purity terms: טָהוֹר ("clean"), טָמֵא ("unclean")
- Actual ritual actions: eating sacred offerings, laying hands on sacrifices, measuring offerings

FORMULAIC EXPRESSIONS (standard biblical narrative, not personification):
- Divine speech introductions: וַיְדַבֵּר יְהוָה ("YHWH spoke"), "Thus says YHWH"
- Covenant formulas: "I am YHWH your God"
- Standard narrative: literal actions, movements, locations that actually occur in the text

LITERAL ACTIONS/PLACES/OBJECTS IN ANCIENT CONTEXT (NOT figurative):
- Physical actions that actually happened: נָקוּמָה וְנֵלֵכָה ("let us arise and go") - literal movement
- Actual places: מִחוּץ לַמַּחֲנֶה ("outside the camp") - real location
- Real people/objects: children (טַפֵּנוּ), inheritance shares (נַחֲלָה) - literal entities
- Ritual gestures: laying hands, stoning, bringing offerings - actual practices
- Geographic references: Waters of Meribah, specific locations - real places
- Legal procedures: execution, inheritance laws - actual ancient practices

PROCEDURAL/INSTRUCTIONAL COMPARISONS (NOT figurative):
- Ritual procedure comparisons: "just as it is removed from the ox" - comparing cultic procedures
- Legal process comparisons: "as you do with X, so do with Y" - instructional parallels
- Technical method descriptions: comparing one ritual technique to another
- Liturgical instructions: procedural steps using comparative language

LITERAL USAGE vs FIGURATIVE:
- Body parts performing literal functions (hands bringing offerings) = NOT metonymy
- Place names (Waters of Meribah) = NOT metonymy, they're proper nouns
- Actual objects/people doing literal things = NOT figurative substitutions
- Actions that ancient readers understood as real events = NOT metaphorical
- Procedural comparisons in ritual/legal contexts = NOT similes (they're instructions)

POSITIVE EXAMPLES of genuine figurative language:

Example 1 - TRUE METAPHOR (different categories):
Hebrew: יְהוָה רֹעִי לֹא אֶחְסָר
English: The LORD is my shepherd; I shall not want
Analysis: [{{"type": "metaphor", "hebrew_text": "יְהוָה רֹעִי", "english_text": "The LORD is my shepherd", "explanation": "True metaphor equating God with shepherd - genuinely different domains", "subcategory": "agricultural", "confidence": 0.95, "speaker": "David", "purpose": "express trust and reliance on God's guidance"}}]

Example 1b - NOT A METAPHOR (religious term):
Hebrew: אֱלֹהֵי הָאֱלֹהִים
English: God of gods
Analysis: [] (DO NOT mark as metaphor - this is a theological title emphasizing God's supremacy, not a figurative comparison)

Example 2 - LEGITIMATE PERSONIFICATION (beyond simple speech):
Hebrew: הָאָרֶץ קָאָה אֶת־יֹשְׁבֶיהָ
English: the land spewed out its inhabitants
Analysis: [{{"type": "personification", "hebrew_text": "הָאָרֶץ קָאָה", "english_text": "the land spewed out", "explanation": "The land is given human action of vomiting/spewing, expressing divine judgment through the land itself", "subcategory": "natural", "confidence": 0.9, "speaker": "Moses", "purpose": "emphasize the severity of moral corruption"}}]

Example 3 - TRUE SIMILE (unlike categories):
Hebrew: כְּכוֹכְבֵי הַשָּׁמַיִם לָרֹב
English: like the stars of heaven for multitude
Analysis: [{{"type": "simile", "hebrew_text": "כְּכוֹכְבֵי הַשָּׁמַיִם", "english_text": "like the stars of heaven", "explanation": "True figurative simile comparing people to stars - genuinely unlike things", "subcategory": "celestial", "confidence": 0.95, "speaker": "Moses", "purpose": "emphasize the vast number of descendants promised"}}]

Example 4 - NOT A SIMILE (same category/procedure):
Hebrew: כַּאֲשֶׁר מֵת אַהֲרֹן אָחִיךָ
English: as your brother Aaron died
Analysis: [] (DO NOT mark as simile - this describes the same method/manner of death, not a figurative comparison)

TYPES to identify (only when genuinely figurative):
- metaphor: Direct comparison without "like/as" (X is Y) - BUT ONLY when X and Y are genuinely different categories used figuratively.

⚠️ DO NOT classify as metaphor if it's:
• RELIGIOUS/DIVINE TITLES: "God of gods" (אֱלֹהֵי הָאֱלֹהִים) = theological title (NOT metaphor)
• TECHNICAL RELIGIOUS TERMS: "holy people" (עַם קָדוֹשׁ) = covenantal status (NOT metaphor)
• RITUAL OBJECTS: "molten calf" (עֵגֶל מַסֵּכָה) = actual idol description (NOT metaphor)
• LITERAL DESCRIPTIONS: "from the fire, cloud, thick darkness" = actual theophany description (NOT metaphor)
• EMOTIONAL/PHYSICAL STATES: "with joy and gladness of heart" = literal emotional state (NOT metaphor)
• GENERATIONAL TERMS: "this evil generation" = descriptive characterization (NOT metaphor)
• RELIGIOUS ACTIONS: "sinned against YHWH" = literal covenant violation (NOT metaphor)
• DIVINE ACTIONS: "turned curse into blessing" = actual divine intervention (NOT metaphor)

✅ ONLY mark as metaphor when genuinely different categories are equated figuratively:
• "YHWH is my shepherd" = God ↔ pastoral role (TRUE metaphor)
• "you are a stiff-necked people" = people ↔ stubborn animals (TRUE metaphor)
• "I will make you a light to the nations" = people ↔ illumination (TRUE metaphor)
- simile: Comparison using "like/as" or Hebrew כְּ/כַּאֲשֶׁר - BUT ONLY when comparing two UNLIKE things figuratively.

⚠️ DO NOT classify as simile if כְּ/כַּאֲשֶׁר is used for:
• PROCEDURAL/INSTRUCTIONAL: "do X as you do Y" = method instruction (NOT simile)
• HISTORICAL PRECEDENT: "X will happen as it did with Y" = historical pattern (NOT simile)
• MANNER DESCRIPTION: "die as brother Aaron died" = describing same method (NOT simile)
• RITUAL INSTRUCTION: "eat it as gazelle is eaten" = cultic procedure (NOT simile)
• LEGAL PRECEDENT: "treat him as you treated the other" = legal procedure (NOT simile)
• TEMPORAL SEQUENCE: "as in the days of..." = time reference (NOT simile)

✅ ONLY mark as simile when כְּ/כַּאֲשֶׁר compares UNLIKE categories:
• "like the stars of heaven" = people ↔ celestial objects (TRUE simile)
• "like water" = blood ↔ common liquid (TRUE simile)
• "as a lion" = person ↔ animal characteristics (TRUE simile)
- personification: Human characteristics given to non-human entities - NOT simple divine speech
- idiom: Expressions with meaning different from literal interpretation
- hyperbole: Deliberate exaggeration for emphasis - be conservative, many distances/numbers are literal
- metonymy: Substituting name with something closely associated - NOT literal usage

⚠️ ANCIENT NEAR EASTERN CONTEXT:
Remember that ancient readers understood these texts in their historical context:
- Religious/ritual terminology had specific technical meanings
- Legal procedures described actual ancient practices
- Geographic references were to real places
- Actions described often literally occurred
- Only mark as figurative what would have been understood as non-literal by ancient audiences

⚠️ QUALITY CONTROL - BEFORE MARKING AS FIGURATIVE, ASK:
1. Is this a technical religious/legal term from ancient Israelite practice?
2. Is this a formulaic expression standard in biblical narrative?
3. Could this be understood literally in its ancient ritual/legal/historical context?
4. Would an ancient Near Eastern reader have understood this as a real action/place/object?
5. Is this a procedural/instructional comparison (ritual technique vs. ritual technique)?
6. Am I confident this is genuinely figurative (confidence > 0.7)?

If YES to 1-5, or NO to 6 → DO NOT mark as figurative language.

IMPORTANT PROCESSING NOTES:
- Work primarily from the HEBREW text, using English for context
- Look for Hebrew-specific patterns like כְּ (simile marker), divine names (יהוה, אלהים)
- Find ALL genuine instances - don't stop at the first one
- Be scholarly and precise in explanations
- Distinguish between technical religious language and genuine figurative language
- Consider ancient context: what would ancient readers have understood as literal?
- Only mark personification when God/entities perform actions beyond simple speech
- Identify the SPEAKER: "God", "Moses", "Narrator", "Abraham", etc.
- Determine the PURPOSE: Why is this figurative language used?
- Minimum confidence threshold: 0.7 (if lower, do not include)

SUBCATEGORY GUIDANCE - Choose meaningful semantic domains based on the TARGET of the comparison:
• For metaphors/similes, identify the TARGET DOMAIN (what is being compared TO):
  - ARCHITECTURAL: fortress, refuge, tower, foundation, house
  - MILITARY: shield, sword, warrior, battle, victory
  - GEOLOGICAL: rock, mountain, spring, foundation
  - ELEMENTAL: fire, wind, water, light
  - AGRICULTURAL: vineyard, shepherd, flock, harvest
  - FAMILIAL: father, mother, brother, inheritance
  - NATURAL: lion, eagle, tree, river
  - CONCEPTUAL: futility, abomination, wisdom
  - EMOTIONAL: comfort, terror, joy, anger
  - TEMPORAL: ancient, eternal, brief
  - SPATIAL: height, depth, distance

Choose the most specific and analytically useful domain. Avoid generic terms like "divine" or "general."

Provide analysis as valid JSON array. Each object must have: type, hebrew_text, english_text, explanation, subcategory, confidence (0.7-1.0), speaker, purpose.

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