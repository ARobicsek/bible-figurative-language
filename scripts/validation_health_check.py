#!/usr/bin/env python3
"""
Validation Health Check Script

This script generates comprehensive validation health reports for databases.
Use it to monitor validation coverage and identify chapters that need recovery.

Usage:
    python validation_health_check.py --database path/to/database.db
    python validation_health_check.py --database private/isaiah_c10_multi_v_parallel_20251204_1449.db --output validation_report.json
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List
import sqlite3

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.hebrew_figurative_db.database.db_manager import DatabaseManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('validation_health.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def get_all_chapters(db_manager: DatabaseManager) -> List[Dict]:
    """Get all chapters with figurative language instances"""
    db_manager.cursor.execute("""
        SELECT DISTINCT v.book, v.chapter, COUNT(*) as instance_count
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        GROUP BY v.book, v.chapter
        ORDER BY v.book, v.chapter
    """)
    return db_manager.cursor.fetchall()


def check_chapter_validation_health(db_manager: DatabaseManager, book: str, chapter: int) -> Dict:
    """Check validation health for a specific chapter"""
    try:
        # Use the existing verification method
        verification = db_manager.verify_validation_data_for_chapter(book, chapter)

        # Add health status classification
        if verification.get('error'):
            health_status = 'ERROR'
        elif verification.get('validation_coverage_rate', 0) >= 95:
            health_status = 'HEALTHY'
        elif verification.get('validation_coverage_rate', 0) >= 80:
            health_status = 'WARNING'
        else:
            health_status = 'CRITICAL'

        verification['health_status'] = health_status
        return verification

    except Exception as e:
        logger.error(f"Error checking chapter {book} {chapter}: {e}")
        return {
            'book': book,
            'chapter': chapter,
            'health_status': 'ERROR',
            'error': str(e),
            'needs_recovery': True
        }


def generate_validation_health_report(database_path: str) -> Dict:
    """Generate comprehensive validation health report"""
    logger.info(f"Generating validation health report for: {database_path}")

    report = {
        'database_path': database_path,
        'timestamp': str(datetime.now()),
        'chapters': [],
        'summary': {
            'total_chapters': 0,
            'healthy_chapters': 0,
            'warning_chapters': 0,
            'critical_chapters': 0,
            'error_chapters': 0,
            'total_instances': 0,
            'validated_instances': 0,
            'overall_coverage_rate': 0
        }
    }

    try:
        with DatabaseManager(database_path) as db_manager:
            # Get all chapters
            chapters = get_all_chapters(db_manager)
            logger.info(f"Found {len(chapters)} chapters to check")

            # Check each chapter
            for chapter_info in chapters:
                book = chapter_info['book']
                chapter = chapter_info['chapter']
                instance_count = chapter_info['instance_count']

                logger.info(f"Checking {book} chapter {chapter} ({instance_count} instances)...")

                metrics = check_chapter_validation_health(db_manager, book, chapter)
                metrics['instance_count'] = instance_count
                report['chapters'].append(metrics)

                # Update summary
                report['summary']['total_chapters'] += 1
                report['summary']['total_instances'] += instance_count

                if metrics.get('error'):
                    report['summary']['error_chapters'] += 1
                else:
                    report['summary']['validated_instances'] += metrics.get('instances_with_validation', 0)

                    health_status = metrics.get('health_status', 'ERROR')
                    if health_status == 'HEALTHY':
                        report['summary']['healthy_chapters'] += 1
                    elif health_status == 'WARNING':
                        report['summary']['warning_chapters'] += 1
                    elif health_status == 'CRITICAL':
                        report['summary']['critical_chapters'] += 1

            # Calculate overall coverage rate
            if report['summary']['total_instances'] > 0:
                report['summary']['overall_coverage_rate'] = (
                    report['summary']['validated_instances'] /
                    report['summary']['total_instances'] * 100
                )

            # Add recommendations
            report['recommendations'] = generate_recommendations(report)

    except Exception as e:
        logger.error(f"Error generating report: {e}")
        report['error'] = str(e)

    return report


def generate_recommendations(report: Dict) -> List[str]:
    """Generate recommendations based on health report"""
    recommendations = []

    critical_count = report['summary']['critical_chapters']
    warning_count = report['summary']['warning_chapters']
    error_count = report['summary']['error_chapters']
    coverage = report['summary']['overall_coverage_rate']

    if error_count > 0:
        recommendations.append(
            f"URGENT: {error_count} chapters have errors. Check database integrity."
        )

    if critical_count > 0:
        recommendations.append(
            f"CRITICAL: {critical_count} chapters have <80% validation coverage. "
            "Run validation recovery immediately."
        )

    if warning_count > 0:
        recommendations.append(
            f"WARNING: {warning_count} chapters have 80-95% validation coverage. "
            "Consider running validation recovery."
        )

    if coverage < 90:
        recommendations.append(
            f"Overall validation coverage is only {coverage:.1f}%. "
            "Run validation recovery on the entire database."
        )

    if critical_count == 0 and warning_count == 0 and error_count == 0:
        recommendations.append(
            "All chapters have healthy validation coverage. Continue monitoring."
        )

    return recommendations


def print_report_summary(report: Dict):
    """Print a formatted summary of the health report"""
    print("\n" + "="*60)
    print("VALIDATION HEALTH REPORT SUMMARY")
    print("="*60)

    summary = report['summary']
    print(f"Database: {report['database_path']}")
    print(f"Total Chapters: {summary['total_chapters']}")
    print(f"Total Instances: {summary['total_instances']}")
    print(f"\nCoverage Statistics:")
    print(f"  Overall Validation Coverage: {summary['overall_coverage_rate']:.1f}%")
    print(f"  Validated Instances: {summary['validated_instances']:,}")

    print(f"\nChapter Health Status:")
    print(f"  ✅ Healthy (≥95%): {summary['healthy_chapters']}")
    print(f"  ⚠️  Warning (80-95%): {summary['warning_chapters']}")
    print(f"  🚨 Critical (<80%): {summary['critical_chapters']}")
    print(f"  ❌ Error: {summary['error_chapters']}")

    if report.get('recommendations'):
        print(f"\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")

    # List critical chapters
    critical_chapters = [c for c in report['chapters'] if c.get('health_status') == 'CRITICAL']
    if critical_chapters:
        print(f"\nCritical Chapters (require immediate attention):")
        for chapter in critical_chapters[:10]:  # Show first 10
            coverage = chapter.get('validation_coverage_rate', 0)
            print(f"  - {chapter['book']} {chapter['chapter']}: {coverage:.1f}% coverage")
        if len(critical_chapters) > 10:
            print(f"  ... and {len(critical_chapters) - 10} more")

    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Check validation health for figurative language database')
    parser.add_argument('--database', required=True, help='Path to SQLite database')
    parser.add_argument('--output', help='Output JSON file for detailed report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Generate report
    report = generate_validation_health_report(args.database)

    # Print summary
    print_report_summary(report)

    # Save detailed report if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        logger.info(f"Detailed report saved to: {args.output}")

    # Exit with error code if critical issues found
    exit_code = 0
    if report['summary']['critical_chapters'] > 0 or report['summary']['error_chapters'] > 0:
        exit_code = 1

    sys.exit(exit_code)


if __name__ == '__main__':
    from datetime import datetime
    main()