#!/usr/bin/env python3
"""
Test the improved validator on previously rejected cases
"""
from src.hebrew_figurative_db.ai_analysis.metaphor_validator import MetaphorValidator

def test_improved_validator():
    """Test specific cases that should now be validated"""
    print("TESTING IMPROVED VALIDATOR ON PREVIOUSLY REJECTED CASES")
    print("=" * 60)

    # Initialize validator
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    validator = MetaphorValidator(api_key)

    # Cases that should now be accepted
    test_cases = [
        {
            "name": "Mighty Hand (Divine Anthropomorphism)",
            "hebrew": "בְּיָ֤ד חֲזָקָה֙",
            "english": "by a mighty hand",
            "figurative_text": "mighty hand",
            "explanation": "God's power is metaphorically described as a strong hand",
            "confidence": 0.8,
            "should_accept": True
        },
        {
            "name": "Sword Devours (Divine Warfare)",
            "hebrew": "וְחַרְבִּ֖י תֹּאכַ֣ל בָּשָׂ֑ר",
            "english": "As My sword devours flesh",
            "figurative_text": "My sword devours flesh",
            "explanation": "God's sword is personified as consuming flesh",
            "confidence": 0.85,
            "should_accept": True
        },
        {
            "name": "Arrows Drunk with Blood (Divine Warfare)",
            "hebrew": "אַשְׁכִּ֤יר חִצַּי֙ מִדָּ֔ם",
            "english": "I will make My arrows drunk with blood",
            "figurative_text": "My arrows drunk with blood",
            "explanation": "Divine arrows are personified as being intoxicated",
            "confidence": 0.9,
            "should_accept": True
        },
        {
            "name": "Iron Blast Furnace (Cross-Domain)",
            "hebrew": "מִכּ֥וּר הַבַּרְזֶ֖ל",
            "english": "that iron blast furnace",
            "figurative_text": "iron blast furnace",
            "explanation": "Egypt is compared to an iron blast furnace",
            "confidence": 0.85,
            "should_accept": True
        },
        {
            "name": "First Fruit of Vigor (Agricultural to Human)",
            "hebrew": "רֵאשִׁ֣ית אֹנ֔וֹ",
            "english": "first fruit of his vigor",
            "figurative_text": "first fruit of his vigor",
            "explanation": "Son compared to agricultural first fruit",
            "confidence": 0.85,
            "should_accept": True
        },
        {
            "name": "Turn Right or Left (Spatial to Moral)",
            "hebrew": "יָמִ֣ין וּשְׂמֹ֑אול",
            "english": "right or to the left",
            "figurative_text": "right or to the left",
            "explanation": "Physical directions represent moral deviation",
            "confidence": 0.8,
            "should_accept": True
        },
        {
            "name": "Honest Weights (Should Still Reject)",
            "hebrew": "אֶ֣בֶן שְׁלֵמָ֤ה",
            "english": "completely honest weights",
            "figurative_text": "honest weights",
            "explanation": "Weights represent honesty and integrity",
            "confidence": 0.8,
            "should_accept": False
        }
    ]

    results = []
    for case in test_cases:
        print(f"\n--- {case['name']} ---")
        print(f"Text: '{case['figurative_text']}'")
        print(f"Should accept: {case['should_accept']}")

        is_valid, reason, error = validator.validate_metaphor(
            case['hebrew'],
            case['english'],
            case['figurative_text'],
            case['explanation'],
            case['confidence']
        )

        if error:
            print(f"ERROR: {error}")
            results.append("ERROR")
            continue

        print(f"Result: {'VALID' if is_valid else 'INVALID'}")
        print(f"Reason: {reason}")

        # Check if result matches expectation
        correct = (is_valid == case['should_accept'])
        status = "CORRECT" if correct else "WRONG"
        print(f"Assessment: {status}")

        results.append(status)

    # Summary
    correct_count = results.count("CORRECT")
    total_count = len([r for r in results if r != "ERROR"])
    print(f"\n=== SUMMARY ===")
    print(f"Correct assessments: {correct_count}/{total_count} ({(correct_count/total_count*100):.1f}%)")

    # Validation stats
    stats = validator.get_validation_stats()
    print(f"Total validations performed: {stats['total_validations']}")

if __name__ == "__main__":
    test_improved_validator()