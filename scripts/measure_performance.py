#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Measure processing speed and error rates on larger datasets
Test Genesis 1-3 (expanded dataset) per Phase 1 plan
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline
import time


def measure_performance():
    """Measure pipeline performance on Genesis 1-3"""
    print("=== Performance Measurement: Genesis 1-3 ===")

    pipeline = FigurativeLanguagePipeline('performance_test.db')

    # Test datasets in order of increasing size
    test_cases = [
        {'range': 'Genesis.1', 'name': 'Genesis 1', 'expected_verses': 31},
        {'range': 'Genesis.2', 'name': 'Genesis 2', 'expected_verses': 25},
        {'range': 'Genesis.3', 'name': 'Genesis 3', 'expected_verses': 24}
    ]

    performance_data = []

    for i, test_case in enumerate(test_cases):
        print(f"\n{'='*50}")
        print(f"Test {i+1}: {test_case['name']}")
        print(f"{'='*50}")

        start_time = time.time()

        # Process the chapter
        results = pipeline.process_verses(test_case['range'], drop_existing=(i==0))

        end_time = time.time()

        # Calculate metrics
        processing_speed = results['processed_verses'] / results['processing_time']  # verses/second
        api_efficiency = results['api_time'] / results['processing_time'] * 100  # % time spent on API

        performance_metrics = {
            'test_case': test_case['name'],
            'verses_range': test_case['range'],
            'total_verses': results['processed_verses'],
            'figurative_found': results['figurative_found'],
            'detection_rate': results['statistics']['detection_rate'],
            'error_rate': results['error_rate'],
            'total_time': results['processing_time'],
            'api_time': results['api_time'],
            'processing_speed': processing_speed,
            'api_efficiency': api_efficiency,
            'avg_confidence': results['statistics']['avg_confidence']
        }

        performance_data.append(performance_metrics)

        print(f"\n📊 Performance Metrics:")
        print(f"  Processing speed: {processing_speed:.1f} verses/second")
        print(f"  API efficiency: {api_efficiency:.1f}% (time spent on API calls)")
        print(f"  Error rate: {results['error_rate']:.1f}%")
        print(f"  Detection rate: {results['statistics']['detection_rate']:.1f}%")

    # Overall analysis
    print(f"\n{'='*60}")
    print(f"📈 OVERALL PERFORMANCE ANALYSIS")
    print(f"{'='*60}")

    total_verses = sum(p['total_verses'] for p in performance_data)
    total_figurative = sum(p['figurative_found'] for p in performance_data)
    avg_speed = sum(p['processing_speed'] for p in performance_data) / len(performance_data)
    max_error_rate = max(p['error_rate'] for p in performance_data)
    avg_detection_rate = sum(p['detection_rate'] for p in performance_data) / len(performance_data)

    print(f"Total verses processed: {total_verses}")
    print(f"Total figurative instances: {total_figurative}")
    print(f"Average processing speed: {avg_speed:.1f} verses/second")
    print(f"Maximum error rate: {max_error_rate:.1f}%")
    print(f"Average detection rate: {avg_detection_rate:.1f}%")

    # Performance benchmarks
    print(f"\n🎯 Performance Benchmarks:")
    benchmarks = {
        'Speed >= 30 verses/second': avg_speed >= 30,
        'Error rate < 5%': max_error_rate < 5.0,
        'Detection rate > 50%': avg_detection_rate > 50,
        'Total processing < 5 seconds': sum(p['total_time'] for p in performance_data) < 5.0
    }

    for benchmark, passed in benchmarks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} {benchmark}")

    # Scaling analysis
    print(f"\n📏 Scaling Analysis:")
    if len(performance_data) > 1:
        first_speed = performance_data[0]['processing_speed']
        last_speed = performance_data[-1]['processing_speed']
        speed_consistency = abs(first_speed - last_speed) / first_speed * 100

        print(f"  Speed consistency: {speed_consistency:.1f}% variation")
        if speed_consistency < 20:
            print(f"  ✅ Good scaling: consistent performance across different chapter sizes")
        else:
            print(f"  ⚠️ Variable scaling: performance varies significantly")

    return performance_data


if __name__ == "__main__":
    performance_data = measure_performance()