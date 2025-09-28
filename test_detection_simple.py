#!/usr/bin/env python3
"""
Simple test of detection prompt on Deuteronomy 30:20
"""
import sys
import os
from dotenv import load_dotenv

# Add source path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from flexible_tagging_gemini_client import FlexibleTaggingGeminiClient

def test_detection():
    """Test detection on a sample verse with known figurative language"""

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not found")
        return

    # Deuteronomy 30:20 text (known to contain figurative language)
    hebrew_text = "לְאַהֲבָ֞ה אֶת־יְהוָ֤ה אֱלֹהֶ֙יךָ֙ לִשְׁמֹ֣עַ בְּקֹל֔וֹ וּלְדָבְקָה־בּ֖וֹ כִּ֣י ה֤וּא חַיֶּ֙יךָ֙ וְאֹ֣רֶךְ יָמֶ֔יךָ לָשֶׁ֣בֶת עַל־הָאֲדָמָ֗ה אֲשֶׁ֨ר נִשְׁבַּ֧ע יְהוָ֛ה לַאֲבֹתֶ֖יךָ לְאַבְרָהָ֥ם לְיִצְחָ֛ק וּלְיַעֲקֹ֖ב לָתֵ֥ת לָֽךְ"
    english_text = "to love the Lord your God, to obey him, and to hold fast to him. For he is your life and length of your days, that you may live in the land that the Lord swore to give to your fathers, to Abraham, Isaac, and Jacob."

    print("TESTING DETECTION PROMPT")
    print("Expected: Should detect 'hold fast to him' as metaphor")
    print("")

    client = FlexibleTaggingGeminiClient(api_key)

    print("Running detection...")
    detection_result, detection_error = client._call_detection_only(
        hebrew_text, english_text, "Deuteronomy", 30
    )

    if detection_error:
        print(f"FAILED: {detection_error}")
        return

    has_figurative = detection_result.get('has_figurative_language', False)
    instances = detection_result.get('instances', [])

    print(f"Has figurative language: {has_figurative}")
    print(f"Instances found: {len(instances)}")

    if instances:
        print("SUCCESS: Detected instances:")
        for i, instance in enumerate(instances, 1):
            english = instance.get('english_text', 'N/A')
            explanation = instance.get('explanation', 'N/A')
            fig_types = [k for k, v in instance.items()
                        if k in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']
                        and v == 'yes']
            print(f"  {i}. '{english}' - {fig_types}")
            print(f"     Explanation: {explanation}")

        # Check if 'hold fast' or 'cleave' was detected
        all_text = str(instances).lower()
        if "hold fast" in all_text or "cleave" in all_text or "cling" in all_text:
            print("SUCCESS: 'Hold fast/cleave' metaphor detected!")
        else:
            print("ISSUE: 'Hold fast/cleave' metaphor not detected")
    else:
        print("ISSUE: No figurative language detected")
        print("Expected to find: 'hold fast to him' metaphor")

if __name__ == "__main__":
    test_detection()