#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete test of ALL false positive and true positive cases
"""
import sys
import os
import csv
import time
import traceback

# Set UTF-8 encoding for console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.hebrew_figurative_db.ai_analysis.hybrid_detector import HybridFigurativeDetector


def parse_test_file(file_path):
    """Parse the TSV test files into a list of test cases"""
    test_cases = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # Skip the header
            lines = f.readlines()[1:]  # Skip first line (header)

            for line_num, line in enumerate(lines, 2):  # Start from line 2
                if not line.strip():
                    continue

                parts = line.strip().split('\t')
                if len(parts) >= 5:  # Minimum required columns
                    test_case = {
                        'id': parts[0] if len(parts) > 0 else '',
                        'reference': parts[1] if len(parts) > 1 else '',
                        'book': parts[2] if len(parts) > 2 else '',
                        'hebrew_text': parts[3] if len(parts) > 3 else '',
                        'english_text': parts[4] if len(parts) > 4 else '',
                        'type': parts[5] if len(parts) > 5 else '',
                        'subcategory_level_1': parts[7] if len(parts) > 7 else '',
                        'subcategory_level_2': parts[8] if len(parts) > 8 else '',
                        'confidence': float(parts[9]) if len(parts) > 9 and parts[9] else 0.0,
                        'figurative_text': parts[10] if len(parts) > 10 else '',
                        'explanation': parts[12] if len(parts) > 12 else ''
                    }
                    test_cases.append(test_case)

    except Exception as e:
        print(f"Error parsing file {file_path}: {e}")
        return []

    return test_cases


def safe_print(text):
    """Safely print text, handling Unicode issues"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace problematic characters
        safe_text = text.encode('ascii', 'replace').decode('ascii')
        print(safe_text)


def test_all_cases(detector, test_cases, dataset_name, expected_metaphor_detection):
    """Test ALL cases in a dataset"""

    safe_print(f"\n{'='*60}")
    safe_print(f"TESTING ALL {dataset_name.upper()} CASES")
    safe_print(f"{'='*60}")
    safe_print(f"Total test cases: {len(test_cases)}")
    safe_print(f"Expected metaphor detection: {expected_metaphor_detection}")

    results = {
        'total_cases': len(test_cases),
        'correct_predictions': 0,
        'false_positives': 0,
        'false_negatives': 0,
        'errors': 0,
        'metaphors_detected_count': 0,
        'test_details': []
    }

    for i, case in enumerate(test_cases, 1):
        safe_print(f"\nTest {i}/{len(test_cases)}: {case['reference']}")

        # Safely display English text
        try:
            english_preview = case['english_text'][:80] + "..." if len(case['english_text']) > 80 else case['english_text']
            safe_print(f"English: {english_preview}")
        except:
            safe_print(f"English: [text with encoding issues]")

        try:
            # Run detection
            detection_results, error = detector.detect_figurative_language(
                case['english_text'],
                case['hebrew_text']
            )

            if error:
                safe_print(f"  ERROR: {error}")
                results['errors'] += 1
                continue

            # Count metaphors detected
            metaphors_found = sum(1 for r in detection_results if r.get('type') == 'metaphor')

            safe_print(f"  Detected: {metaphors_found} metaphors")

            # Track statistics
            if metaphors_found > 0:
                results['metaphors_detected_count'] += 1

            # Determine if prediction was correct
            if expected_metaphor_detection:
                # This should detect metaphors (true positives dataset)
                if metaphors_found > 0:
                    results['correct_predictions'] += 1
                    safe_print(f"  RESULT: CORRECT (true positive)")
                else:
                    results['false_negatives'] += 1
                    safe_print(f"  RESULT: WRONG (false negative - missed metaphor)")
            else:
                # This should NOT detect metaphors (false positives dataset)
                if metaphors_found == 0:
                    results['correct_predictions'] += 1
                    safe_print(f"  RESULT: CORRECT (avoided false positive)")
                else:
                    results['false_positives'] += 1
                    safe_print(f"  RESULT: WRONG (false positive detected)")
                    # Show what was incorrectly detected
                    for result in detection_results:
                        if result.get('type') == 'metaphor':
                            figurative_text = result.get('figurative_text', 'N/A')
                            safe_print(f"    - {figurative_text}")

            # Store test details
            results['test_details'].append({
                'reference': case['reference'],
                'detected': metaphors_found,
                'correct': (metaphors_found > 0) == expected_metaphor_detection,
                'original_text': case.get('figurative_text', ''),
            })

        except Exception as e:
            safe_print(f"  EXCEPTION: {e}")
            results['errors'] += 1
            continue

    # Calculate performance metrics
    accuracy = (results['correct_predictions'] / results['total_cases']) * 100 if results['total_cases'] > 0 else 0

    safe_print(f"\n{'-'*60}")
    safe_print(f"{dataset_name.upper()} FINAL RESULTS:")
    safe_print(f"Total cases tested: {results['total_cases']}")
    safe_print(f"Correct predictions: {results['correct_predictions']}")
    safe_print(f"Accuracy: {accuracy:.1f}%")

    if expected_metaphor_detection:
        safe_print(f"True positives (correctly detected): {results['correct_predictions']}")
        safe_print(f"False negatives (missed): {results['false_negatives']}")
        recall = (results['correct_predictions'] / results['total_cases']) * 100
        safe_print(f"Recall: {recall:.1f}%")
    else:
        safe_print(f"True negatives (correctly avoided): {results['correct_predictions']}")
        safe_print(f"False positives (incorrectly detected): {results['false_positives']}")
        specificity = (results['correct_predictions'] / results['total_cases']) * 100
        safe_print(f"Specificity: {specificity:.1f}%")

    safe_print(f"Errors: {results['errors']}")

    return results


def main():
    """Main comprehensive test function"""

    safe_print("COMPREHENSIVE PIPELINE TEST - ALL CASES")
    safe_print("Testing ALL False Positives and True Positives")
    safe_print("="*80)

    # Initialize detector with two-stage validation
    api_key = "AIzaSyBjslLjCzAjarNfu0efWby6YHnqAXmaKIk"
    detector = HybridFigurativeDetector(
        prefer_llm=True,
        use_actual_llm=True,
        enable_metaphor_validation=True,
        gemini_api_key=api_key
    )

    # Load ALL test datasets
    safe_print("Loading ALL test datasets...")
    false_positives = parse_test_file("False_positives.md")
    true_positives = parse_test_file("True_positives.md")

    safe_print(f"Loaded {len(false_positives)} false positive cases")
    safe_print(f"Loaded {len(true_positives)} true positive cases")

    if not false_positives and not true_positives:
        safe_print("ERROR: No test cases loaded!")
        return

    start_time = time.time()

    # Test ALL false positives (should detect 0 metaphors for each)
    false_positive_results = None
    if false_positives:
        false_positive_results = test_all_cases(
            detector,
            false_positives,  # Test ALL false positives
            "False Positives",
            expected_metaphor_detection=False
        )

    # Test ALL true positives (should detect 1+ metaphors for each)
    true_positive_results = None
    if true_positives:
        true_positive_results = test_all_cases(
            detector,
            true_positives,  # Test ALL true positives
            "True Positives",
            expected_metaphor_detection=True
        )

    end_time = time.time()

    # Overall summary
    safe_print(f"\n{'='*80}")
    safe_print("COMPREHENSIVE PERFORMANCE SUMMARY")
    safe_print(f"{'='*80}")

    total_cases = 0
    total_correct = 0

    if false_positive_results:
        total_cases += false_positive_results['total_cases']
        total_correct += false_positive_results['correct_predictions']
        fp_accuracy = (false_positive_results['correct_predictions'] / false_positive_results['total_cases']) * 100
        safe_print(f"False Positive Prevention: {fp_accuracy:.1f}% ({false_positive_results['correct_predictions']}/{false_positive_results['total_cases']})")
        safe_print(f"False Positives Still Detected: {false_positive_results['false_positives']}")

    if true_positive_results:
        total_cases += true_positive_results['total_cases']
        total_correct += true_positive_results['correct_predictions']
        tp_accuracy = (true_positive_results['correct_predictions'] / true_positive_results['total_cases']) * 100
        safe_print(f"True Positive Detection: {tp_accuracy:.1f}% ({true_positive_results['correct_predictions']}/{true_positive_results['total_cases']})")
        safe_print(f"True Positives Missed: {true_positive_results['false_negatives']}")

    if total_cases > 0:
        overall_accuracy = (total_correct / total_cases) * 100
        safe_print(f"\nOVERALL ACCURACY: {overall_accuracy:.1f}% ({total_correct}/{total_cases})")

        # Performance assessment
        safe_print(f"\n{'-'*60}")
        safe_print("FINAL ASSESSMENT:")

        if overall_accuracy >= 85:
            safe_print("EXCELLENT: Two-stage validation pipeline is highly effective!")
        elif overall_accuracy >= 75:
            safe_print("GOOD: Two-stage validation pipeline is working well with room for improvement.")
        elif overall_accuracy >= 65:
            safe_print("FAIR: Two-stage validation pipeline shows promise but needs tuning.")
        else:
            safe_print("POOR: Two-stage validation pipeline needs significant improvement.")

        # Specific assessments
        if false_positive_results:
            fp_rate = (false_positive_results['false_positives'] / false_positive_results['total_cases']) * 100
            safe_print(f"\nFalse Positive Rate: {fp_rate:.1f}%")
            if fp_rate <= 10:
                safe_print("✓ Excellent false positive control")
            elif fp_rate <= 20:
                safe_print("~ Good false positive control")
            else:
                safe_print("✗ Poor false positive control")

        if true_positive_results:
            miss_rate = (true_positive_results['false_negatives'] / true_positive_results['total_cases']) * 100
            safe_print(f"True Positive Miss Rate: {miss_rate:.1f}%")
            if miss_rate <= 15:
                safe_print("✓ Excellent true positive preservation")
            elif miss_rate <= 30:
                safe_print("~ Good true positive preservation")
            else:
                safe_print("✗ Poor true positive preservation")

    # Print validation statistics
    try:
        detector.print_validation_summary()
    except Exception as e:
        safe_print(f"Could not print validation summary: {e}")

    # Time summary
    total_time = end_time - start_time
    safe_print(f"\nTotal test time: {total_time:.1f} seconds")
    if total_cases > 0:
        time_per_case = total_time / total_cases
        safe_print(f"Average time per case: {time_per_case:.2f} seconds")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Fatal error: {e}")
        traceback.print_exc()