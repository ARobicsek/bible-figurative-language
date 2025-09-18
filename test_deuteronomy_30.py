#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test enhanced pipeline on Deuteronomy 30
Goal: Validate all new features including idiom/hyperbole detection, subcategorization, speaker identification
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from src.hebrew_figurative_db.pipeline import FigurativeLanguagePipeline
from src.hebrew_figurative_db.text_extraction.hebrew_utils import HebrewTextProcessor
from src.hebrew_figurative_db.ai_analysis.llm_manager import LLMUsageMonitor


def test_hebrew_processor():
    """Test Hebrew text processing capabilities"""
    print("=== Testing Hebrew Text Processor ===\n")

    processor = HebrewTextProcessor()

    # Test Hebrew stripping
    test_hebrew = "וַיֹּאמֶר יְהוָה אֱלֹהִים"
    stripped = processor.strip_diacritics(test_hebrew)
    print(f"Original: {test_hebrew}")
    print(f"Stripped: {stripped}")

    # Test speaker identification
    test_cases = [
        "And God said, 'Let there be light'",
        "Moses spoke to the people",
        "The Lord called to Moses",
        "Now this is a narrative passage"
    ]

    print("\nSpeaker identification tests:")
    for text in test_cases:
        speaker = processor.identify_speaker_patterns(text, "")
        print(f"'{text}' -> Speaker: {speaker}")

    print()


def test_enhanced_detector():
    """Test enhanced figurative language detection"""
    print("=== Testing Enhanced Figurative Language Detection ===\n")

    from src.hebrew_figurative_db.ai_analysis import FigurativeLanguageDetector
    detector = FigurativeLanguageDetector()

    # Test cases for new features
    test_cases = [
        "Your heart will return to the LORD your God",  # Should detect metaphor/body
        "For this commandment is not hidden from you, neither is it far off",  # Should detect hyperbole
        "It is not in heaven, that you should say, 'Who will go up to heaven'",  # Should detect hyperbole
        "The word is very near you, in your mouth and in your heart",  # Should detect metaphor/body
        "God will circumcise your heart",  # Should detect metaphor/body
        "He will gather you from all the nations",  # Should detect hyperbole
        "As the LORD rejoiced over your ancestors",  # Should detect personification/divine
        "The LORD will again take delight in prospering you",  # Should detect personification/divine
    ]

    print("Detection results:")
    for i, text in enumerate(test_cases, 1):
        result = detector.detect_figurative_language(text, "")
        if result['type']:
            print(f"{i}. '{text[:50]}...'")
            print(f"   Type: {result['type']}")
            print(f"   Subcategory: {result.get('subcategory', 'None')}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Explanation: {result.get('explanation', 'None')}")
            print(f"   Reasoning: {result.get('reasoning', 'None')}")
        else:
            print(f"{i}. '{text[:50]}...' -> No figurative language detected")
        print()


def test_llm_monitor():
    """Test LLM usage monitoring"""
    print("=== Testing LLM Usage Monitoring ===\n")

    monitor = LLMUsageMonitor("test_llm_usage.json")

    # Simulate some usage
    monitor.log_usage('claude', 'claude-3.5-sonnet', 150, True, 0.5)
    monitor.log_usage('claude', 'claude-3.5-sonnet', 200, True, 0.7)
    monitor.log_usage('gemini', 'gemini-pro', 100, True, 0.3)

    # Get summary
    summary = monitor.get_usage_summary()

    print("Usage Summary:")
    for provider, data in summary.items():
        if provider != 'overall':
            print(f"{provider.capitalize()}:")
            print(f"  Tokens: {data['total_tokens']}")
            print(f"  Cost: ${data['total_cost']:.4f}")
            print(f"  Requests: {data['total_requests']}")
            print(f"  Success Rate: {data['success_rate']:.1f}%")
            print(f"  Limit Usage: {data['limit_usage_percent']:.1f}%")
            print()

    print(f"Current Provider: {summary['overall']['current_provider']}")
    print()


def main():
    """Main testing function"""
    print("🔬 TESTING ENHANCED PIPELINE FEATURES")
    print("="*60)

    # Test individual components
    test_hebrew_processor()
    test_enhanced_detector()
    test_llm_monitor()

    # Test full pipeline on Deuteronomy 30
    print("=== Testing Full Pipeline on Deuteronomy 30 ===\n")

    try:
        pipeline = FigurativeLanguagePipeline('test_deuteronomy_30.db')

        print("Processing Deuteronomy 30 (metaphor-rich chapter)...")
        results = pipeline.process_verses('Deuteronomy.30', drop_existing=True)

        print(f"\n📊 DEUTERONOMY 30 RESULTS:")
        print(f"Total verses processed: {results['processed_verses']}")
        print(f"Figurative instances found: {results['figurative_found']}")
        print(f"Detection rate: {results['statistics']['detection_rate']:.1f}%")
        print(f"Average confidence: {results['statistics']['avg_confidence']:.2f}")

        print(f"\nType breakdown:")
        for fig_type, count in results['statistics']['type_breakdown'].items():
            print(f"  {fig_type}: {count}")

        if results['success']:
            print(f"\n✅ Enhanced pipeline test PASSED!")
        else:
            print(f"\n⚠️ Enhanced pipeline test completed with warnings")

    except Exception as e:
        print(f"❌ Pipeline test FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()