#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Production script for full dataset conceptual grouping - Phase 2
Runs in background with resilience and progress tracking
"""
import json
import os
import logging
import time
from datetime import datetime
from dotenv import load_dotenv
from conceptual_grouper import ConceptualGrouper

# Load environment variables
load_dotenv()

def setup_production_logging():
    """Setup comprehensive logging for production run"""
    log_filename = f"conceptual_grouping_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename, encoding='utf-8'),
            logging.StreamHandler()  # Also log to console
        ]
    )

    return logging.getLogger(__name__), log_filename

def run_full_conceptual_grouping():
    """Run conceptual grouping on the complete dataset"""

    logger, log_filename = setup_production_logging()

    logger.info("="*80)
    logger.info("STARTING FULL CONCEPTUAL GROUPING - PHASE 2")
    logger.info("="*80)

    # Verify API key
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return False

    logger.info("✓ API key loaded successfully")

    # Verify input file
    input_file = 'clean_deuteronomy_data.json'
    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}")
        return False

    logger.info(f"✓ Input file found: {input_file}")

    # Load and analyze dataset
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    flows = data.get('flows', [])
    logger.info(f"✓ Loaded {len(flows)} flows for processing")

    # Analyze categories for progress estimation
    target_categories = set()
    vehicle_categories = set()

    for flow in flows:
        target_cat = flow.get('target_level_1_normalized', 'unknown')
        vehicle_cat = flow.get('vehicle_level_1_normalized', 'unknown')

        target_categories.add(target_cat)
        vehicle_categories.add(vehicle_cat)

    logger.info(f"Dataset contains {len(target_categories)} target categories and {len(vehicle_categories)} vehicle categories")

    # Estimate API calls needed (assuming some cache hits)
    estimated_calls = len(target_categories) + len(vehicle_categories)
    estimated_time = estimated_calls * 12  # ~12 seconds per call average

    logger.info(f"Estimated processing time: {estimated_time//60} minutes ({estimated_calls} API calls)")
    logger.info(f"Log file: {log_filename}")

    # Initialize grouper with production settings
    logger.info("Initializing ConceptualGrouper...")
    grouper = ConceptualGrouper(
        api_key=api_key,
        logger=logger,
        cache_dir="cache_production"
    )

    start_time = time.time()

    try:
        # Process target groupings
        logger.info("\n" + "="*60)
        logger.info("PHASE 2A: TARGET CONCEPTUAL GROUPING")
        logger.info("="*60)

        target_start = time.time()
        target_groupings = grouper.group_targets_by_category(flows)
        target_time = time.time() - target_start

        logger.info(f"✓ Target grouping completed in {target_time:.1f} seconds")
        logger.info(f"✓ Created groupings for {len(target_groupings)} target categories")

        # Process vehicle groupings
        logger.info("\n" + "="*60)
        logger.info("PHASE 2B: VEHICLE CONCEPTUAL GROUPING")
        logger.info("="*60)

        vehicle_start = time.time()
        vehicle_groupings = grouper.group_vehicles_by_category(flows)
        vehicle_time = time.time() - vehicle_start

        logger.info(f"✓ Vehicle grouping completed in {vehicle_time:.1f} seconds")
        logger.info(f"✓ Created groupings for {len(vehicle_groupings)} vehicle categories")

        # Apply groupings to flows
        logger.info("\n" + "="*60)
        logger.info("PHASE 2C: APPLYING GROUPINGS TO FLOWS")
        logger.info("="*60)

        apply_start = time.time()
        enhanced_flows = grouper.apply_groupings_to_flows(flows, target_groupings, vehicle_groupings)
        apply_time = time.time() - apply_start

        logger.info(f"✓ Groupings applied to {len(enhanced_flows)} flows in {apply_time:.1f} seconds")

        # Generate comprehensive report
        logger.info("\n" + "="*60)
        logger.info("PHASE 2D: GENERATING QUALITY REPORT")
        logger.info("="*60)

        report = grouper.generate_grouping_report(target_groupings, vehicle_groupings)

        # Save enhanced dataset
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        enhanced_data = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'source_file': input_file,
                'conceptual_grouping_applied': True,
                'total_flows': len(enhanced_flows),
                'processing_time_seconds': time.time() - start_time,
                'target_categories_grouped': len(target_groupings),
                'vehicle_categories_grouped': len(vehicle_groupings),
                'gemini_model': 'gemini-2.5-flash (primary), gemini-1.5-flash (fallback)',
                'api_requests_made': report['api_usage']['total_requests'],
                'cache_hit_rate': report['api_usage']['cache_hit_rate']
            },
            'flows': enhanced_flows
        }

        output_file = f'clean_deuteronomy_data_grouped_{timestamp}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

        # Save comprehensive report
        report_file = f'conceptual_grouping_report_{timestamp}.json'
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        # Save detailed groupings for reference
        groupings_file = f'detailed_groupings_{timestamp}.json'
        detailed_groupings = {
            'target_groupings': target_groupings,
            'vehicle_groupings': vehicle_groupings
        }
        with open(groupings_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_groupings, f, indent=2, ensure_ascii=False)

        total_time = time.time() - start_time

        # Final success report
        logger.info("\n" + "="*80)
        logger.info("CONCEPTUAL GROUPING COMPLETED SUCCESSFULLY!")
        logger.info("="*80)
        logger.info(f"Total processing time: {total_time//60:.0f}m {total_time%60:.0f}s")
        logger.info(f"Enhanced dataset: {output_file}")
        logger.info(f"Quality report: {report_file}")
        logger.info(f"Detailed groupings: {groupings_file}")

        # Print summary statistics
        logger.info("\n📊 FINAL STATISTICS:")
        logger.info(f"  • Total flows processed: {len(enhanced_flows):,}")
        logger.info(f"  • Target categories grouped: {len(target_groupings)}")
        logger.info(f"  • Vehicle categories grouped: {len(vehicle_groupings)}")
        logger.info(f"  • Total conceptual groups created: {report['target_groupings']['total_groups_created'] + report['vehicle_groupings']['total_groups_created']}")
        logger.info(f"  • API requests made: {report['api_usage']['total_requests']}")
        logger.info(f"  • Cache hit rate: {report['api_usage']['cache_hit_rate']:.1%}")
        logger.info(f"  • Average grouping confidence: {(report['target_groupings']['average_confidence'] + report['vehicle_groupings']['average_confidence'])/2:.2f}")

        logger.info("\n🎯 PHASE 2 COMPLETE - Ready for Phase 3 (Sankey Visualization)")

        return True

    except Exception as e:
        logger.error(f"Error during processing: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    print("Starting full conceptual grouping process...")
    print("This will process all 1,287 flows and may take 20-30 minutes.")
    print("Progress will be logged to console and saved to log file.")
    print("=" * 60)

    success = run_full_conceptual_grouping()

    if success:
        print("\n✅ SUCCESS: Conceptual grouping completed!")
        print("Check the output files for enhanced data and quality reports.")
    else:
        print("\n❌ FAILED: Check the log files for error details.")