#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for ConceptualGrouper - Phase 2 validation
"""
import json
import os
import logging
from dotenv import load_dotenv
from conceptual_grouper import ConceptualGrouper

# Load environment variables from .env file
load_dotenv()

def create_test_sample():
    """Create a small test sample from the full dataset"""
    with open('clean_deuteronomy_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Take first 50 flows for testing
    test_flows = data['flows'][:50]

    # Print sample statistics
    print(f"Test sample: {len(test_flows)} flows")

    # Analyze target categories in sample
    target_categories = {}
    vehicle_categories = {}

    for flow in test_flows:
        target_cat = flow.get('target_level_1_normalized', 'unknown')
        vehicle_cat = flow.get('vehicle_level_1_normalized', 'unknown')
        target_spec = flow.get('target_specific', '').strip()
        vehicle_spec = flow.get('vehicle_specific', '').strip()

        if target_cat not in target_categories:
            target_categories[target_cat] = set()
        target_categories[target_cat].add(target_spec)

        if vehicle_cat not in vehicle_categories:
            vehicle_categories[vehicle_cat] = set()
        vehicle_categories[vehicle_cat].add(vehicle_spec)

    print("\nTarget categories in sample:")
    for cat, targets in target_categories.items():
        print(f"  {cat}: {len(targets)} targets - {list(targets)[:3]}{'...' if len(targets) > 3 else ''}")

    print("\nVehicle categories in sample:")
    for cat, vehicles in vehicle_categories.items():
        print(f"  {cat}: {len(vehicles)} vehicles - {list(vehicles)[:3]}{'...' if len(vehicles) > 3 else ''}")

    return test_flows

def test_conceptual_grouper():
    """Test the ConceptualGrouper with sample data"""

    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    # Get API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable not set")
        print("Please set your Gemini API key:")
        print("  export GEMINI_API_KEY='your-api-key-here'")
        return False

    # Create test sample
    print("Creating test sample...")
    test_flows = create_test_sample()

    # Initialize grouper
    print("\nInitializing ConceptualGrouper...")
    grouper = ConceptualGrouper(api_key=api_key, logger=logger, cache_dir="cache_test")

    try:
        # Test target grouping
        print("\n" + "="*60)
        print("TESTING TARGET GROUPING")
        print("="*60)
        target_groupings = grouper.group_targets_by_category(test_flows)

        print(f"\nTarget grouping results for {len(target_groupings)} categories:")
        for category, grouping in target_groupings.items():
            groups = grouping.get('groups', [])
            ungrouped = grouping.get('ungrouped', [])
            confidence = grouping.get('confidence', 0)

            print(f"\nCategory: {category}")
            print(f"  Confidence: {confidence}")
            print(f"  Groups created: {len(groups)}")
            for i, group in enumerate(groups, 1):
                print(f"    {i}. {group['name']}: {group['members']}")
                print(f"       Description: {group['description']}")
            if ungrouped:
                print(f"  Ungrouped: {ungrouped}")

        # Test vehicle grouping
        print("\n" + "="*60)
        print("TESTING VEHICLE GROUPING")
        print("="*60)
        vehicle_groupings = grouper.group_vehicles_by_category(test_flows)

        print(f"\nVehicle grouping results for {len(vehicle_groupings)} categories:")
        for category, grouping in vehicle_groupings.items():
            groups = grouping.get('groups', [])
            ungrouped = grouping.get('ungrouped', [])
            confidence = grouping.get('confidence', 0)

            print(f"\nCategory: {category}")
            print(f"  Confidence: {confidence}")
            print(f"  Groups created: {len(groups)}")
            for i, group in enumerate(groups, 1):
                print(f"    {i}. {group['name']}: {group['members']}")
                print(f"       Description: {group['description']}")
            if ungrouped:
                print(f"  Ungrouped: {ungrouped}")

        # Test applying groupings
        print("\n" + "="*60)
        print("TESTING GROUPING APPLICATION")
        print("="*60)
        enhanced_flows = grouper.apply_groupings_to_flows(test_flows, target_groupings, vehicle_groupings)

        print(f"Enhanced {len(enhanced_flows)} flows with conceptual groups")

        # Show a few examples
        print("\nExample enhanced flows:")
        for i, flow in enumerate(enhanced_flows[:3], 1):
            print(f"\nFlow {i}:")
            print(f"  Target: {flow.get('target_specific', 'N/A')} → {flow.get('target_conceptual_group', 'N/A')}")
            print(f"  Vehicle: {flow.get('vehicle_specific', 'N/A')} → {flow.get('vehicle_conceptual_group', 'N/A')}")
            print(f"  Figurative text: {flow.get('figurative_text', 'N/A')}")

        # Generate report
        print("\n" + "="*60)
        print("GENERATING QUALITY REPORT")
        print("="*60)
        report = grouper.generate_grouping_report(target_groupings, vehicle_groupings)

        # Save test results
        test_results = {
            'test_flows': enhanced_flows,
            'target_groupings': target_groupings,
            'vehicle_groupings': vehicle_groupings,
            'quality_report': report
        }

        with open('test_conceptual_grouping_results.json', 'w', encoding='utf-8') as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False)

        print(f"API Usage Summary:")
        print(f"  Total requests: {report['api_usage']['total_requests']}")
        print(f"  Cache hits: {report['api_usage']['cache_hits']}")
        print(f"  Cache hit rate: {report['api_usage']['cache_hit_rate']:.1%}")
        print(f"  Successful groupings: {report['api_usage']['successful_groupings']}")

        print(f"\nTarget Grouping Summary:")
        print(f"  Categories processed: {report['target_groupings']['categories_processed']}")
        print(f"  Total groups created: {report['target_groupings']['total_groups_created']}")
        print(f"  Average confidence: {report['target_groupings']['average_confidence']:.2f}")

        print(f"\nVehicle Grouping Summary:")
        print(f"  Categories processed: {report['vehicle_groupings']['categories_processed']}")
        print(f"  Total groups created: {report['vehicle_groupings']['total_groups_created']}")
        print(f"  Average confidence: {report['vehicle_groupings']['average_confidence']:.2f}")

        print("\n" + "="*60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("Results saved to: test_conceptual_grouping_results.json")

        return True

    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_conceptual_grouper()
    if success:
        print("\n[SUCCESS] ConceptualGrouper test passed! Ready for full dataset processing.")
    else:
        print("\n[FAILED] ConceptualGrouper test failed. Please check the error messages above.")