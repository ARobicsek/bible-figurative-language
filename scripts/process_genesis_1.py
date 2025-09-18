#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process complete Genesis 1 (31 verses) using refactored pipeline
"""
import sys
import os
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hebrew_figurative_db.pipeline import FigurativeLanguagePipeline


def main():
    """Process Genesis 1 through the pipeline"""
    print("=== Phase 1: Processing Complete Genesis 1 ===")
    print("Target: 31 verses, 20+ figurative instances, <5% error rate")

    # Initialize pipeline
    pipeline = FigurativeLanguagePipeline('genesis_1_pipeline.db')

    # Process Genesis 1 (all 31 verses)
    results = pipeline.process_verses('Genesis.1', drop_existing=True)

    # Validate against Phase 1 success criteria
    print(f"\n{'='*60}")
    print(f"🎯 PHASE 1 SUCCESS CRITERIA VALIDATION")
    print(f"{'='*60}")

    criteria = {
        'Process 31 verses automatically': results['processed_verses'] >= 31,
        'Identify 20+ figurative instances': results['figurative_found'] >= 20,
        '<5% data processing errors': results['error_rate'] < 5.0,
        'Database queries execute quickly': results['processing_time'] < 30.0  # Reasonable for 31 verses
    }

    all_passed = True
    for criterion, passed in criteria.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {criterion}")
        if not passed:
            all_passed = False

    print(f"\n{'='*60}")
    if all_passed:
        print("🎉 PHASE 1 SUCCESS: All criteria met!")
        print("✅ Ready to proceed to speed/error measurement")
    else:
        print("⚠️ PHASE 1 PARTIAL SUCCESS: Some criteria not met")
        print("Need to address issues before proceeding")

    return results


if __name__ == "__main__":
    results = main()