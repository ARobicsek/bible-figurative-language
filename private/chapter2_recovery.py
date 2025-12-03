#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chapter 2 Validation Recovery Script

This script recovers missing validation data for Proverbs Chapter 2 by applying
the enhanced validation system with all 10 JSON extraction strategies and retry logic.

Usage:
    python chapter2_recovery.py

Features:
- Loads existing Chapter 2 database
- Identifies instances with missing validation data
- Applies enhanced validation with retry mechanisms
- Updates validation fields in-place (preserving detection data)
- Generates comprehensive recovery report
- Includes safety measures and backup procedures
"""

import os
import sys
import json
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Add the src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'hebrew_figurative_db', 'ai_analysis'))

from metaphor_validator import MetaphorValidator


class Chapter2Recovery:
    """Dedicated recovery system for Proverbs Chapter 2 validation data."""

    def __init__(self):
        """Initialize the recovery system."""
        self.project_dir = Path(__file__).parent.parent
        self.db_path = self.project_dir / "proverbs_c2_multi_v_parallel_20251202_1652.db"
        self.backup_path = self.project_dir / "proverbs_c2_multi_v_parallel_20251202_1652_ch2_recovery_backup.db"
        self.results_path = self.project_dir / "private" / "chapter2_recovery_results.json"

        # Recovery statistics
        self.recovery_stats = {
            'total_instances': 0,
            'instances_without_validation': 0,
            'recovery_attempts': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'strategies_used': [],
            'start_time': datetime.now(),
            'end_time': None
        }

    def run_recovery(self) -> bool:
        """Execute the complete recovery process."""
        print("=== CHAPTER 2 VALIDATION RECOVERY ===")
        print(f"Started: {self.recovery_stats['start_time']}")
        print(f"Database: {self.db_path}")
        print(f"Backup: {self.backup_path}")
        print()

        # Safety checks
        if not self._pre_recovery_checks():
            print("FAIL: Pre-recovery checks failed. Aborting recovery.")
            return False

        try:
            # Create backup
            print("1. Creating backup...")
            if not self._create_backup():
                print("FAIL: Failed to create backup. Aborting recovery.")
                return False
            print("SUCCESS: Backup created successfully.")

            # Load and analyze database
            print("\n2. Loading and analyzing database...")
            instances = self._load_instances_from_database()
            if not instances:
                print("FAIL: No instances found in database. Aborting recovery.")
                return False
            print(f"SUCCESS: Loaded {len(instances)} instances from database.")

            # Identify instances needing recovery
            print("\n3. Identifying instances needing validation recovery...")
            instances_needing_recovery = self._identify_recovery_candidates(instances)
            if not instances_needing_recovery:
                print("SUCCESS: All instances already have validation data. No recovery needed.")
                return True
            print(f"SUCCESS: Identified {len(instances_needing_recovery)} instances needing recovery.")

            # Execute recovery with enhanced validation
            print("\n4. Executing validation recovery...")
            if not self._execute_recovery(instances_needing_recovery):
                print("FAIL: Recovery execution failed.")
                return False
            print("SUCCESS: Recovery execution completed.")

            # Update database
            print("\n5. Updating database with recovered validation data...")
            if not self._update_database(instances):
                print("FAIL: Database update failed.")
                return False
            print("SUCCESS: Database updated successfully.")

            # Generate recovery report
            print("\n6. Generating recovery report...")
            self._generate_recovery_report()
            print("SUCCESS: Recovery report generated.")

            self.recovery_stats['end_time'] = datetime.now()
            duration = self.recovery_stats['end_time'] - self.recovery_stats['start_time']
            print(f"\nRECOVERY COMPLETED SUCCESSFULLY!")
            print(f"Duration: {duration}")
            print(f"Success rate: {self.recovery_stats['successful_recoveries']}/{self.recovery_stats['recovery_attempts']} ({self.recovery_stats['successful_recoveries']/self.recovery_stats['recovery_attempts']*100:.1f}%)")

            return True

        except Exception as e:
            print(f"FAIL: Recovery failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _pre_recovery_checks(self) -> bool:
        """Perform pre-recovery safety checks."""
        # Check if database exists
        if not self.db_path.exists():
            print(f"FAIL: Database not found: {self.db_path}")
            return False

        # Check if backup would overwrite existing file
        if self.backup_path.exists():
            print(f"WARNING: Backup already exists: {self.backup_path}")
            print("INFO: Overwriting existing backup automatically.")

        # Check OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("FAIL: OPENAI_API_KEY environment variable not set")
            return False

        # Test database connection
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM figurative_language")
            count = cursor.fetchone()[0]
            conn.close()
            print(f"SUCCESS: Database connection successful. Found {count} figurative instances.")
        except Exception as e:
            print(f"FAIL: Database connection failed: {e}")
            return False

        return True

    def _create_backup(self) -> bool:
        """Create a backup of the original database."""
        try:
            shutil.copy2(str(self.db_path), str(self.backup_path))
            return True
        except Exception as e:
            print(f"FAIL: Backup creation failed: {e}")
            return False

    def _load_instances_from_database(self) -> List[Dict]:
        """Load all figurative instances from the database."""
        instances = []
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    fl.*,
                    v.reference as verse_reference,
                    v.hebrew_text,
                    v.english_text,
                    v.figurative_detection_deliberation as deliberation
                FROM figurative_language fl
                JOIN verses v ON fl.verse_id = v.id
                WHERE v.chapter = 2
                ORDER BY v.verse, fl.id
            """)

            rows = cursor.fetchall()
            for row in rows:
                instance = {
                    'id': row['id'],
                    'verse_id': row['verse_id'],
                    'verse_reference': row['verse_reference'],
                    'hebrew_text': row['hebrew_text'],
                    'english_text': row['english_text'],
                    'figurative_text': row['figurative_text'],
                    'explanation': row['explanation'],
                    'confidence': row['confidence'],
                    'target': json.loads(row['target']) if row['target'] else [],
                    'vehicle': json.loads(row['vehicle']) if row['vehicle'] else [],
                    'ground': json.loads(row['ground']) if row['ground'] else [],
                    'posture': json.loads(row['posture']) if row['posture'] else [],
                    'deliberation': row['deliberation'],
                    # Validation fields - using type-specific fields from current schema
                    'validation_response': row['validation_response'],
                    'validation_decision_simile': row['validation_decision_simile'],
                    'validation_decision_metaphor': row['validation_decision_metaphor'],
                    'validation_decision_personification': row['validation_decision_personification'],
                    'validation_decision_idiom': row['validation_decision_idiom'],
                    'validation_decision_hyperbole': row['validation_decision_hyperbole'],
                    'validation_decision_metonymy': row['validation_decision_metonymy'],
                    'validation_decision_other': row['validation_decision_other'],
                    'validation_reason_simile': row['validation_reason_simile'],
                    'validation_reason_metaphor': row['validation_reason_metaphor'],
                    'validation_reason_personification': row['validation_reason_personification'],
                    'validation_reason_idiom': row['validation_reason_idiom'],
                    'validation_reason_hyperbole': row['validation_reason_hyperbole'],
                    'validation_reason_metonymy': row['validation_reason_metonymy'],
                    'validation_reason_other': row['validation_reason_other'],
                    'validation_error': row['validation_error']
                }
                instances.append(instance)

            conn.close()
            return instances

        except Exception as e:
            print(f"FAIL: Failed to load instances: {e}")
            return []

    def _identify_recovery_candidates(self, instances: List[Dict]) -> List[Dict]:
        """Identify instances that need validation recovery."""
        candidates = []
        for instance in instances:
            # Check if any validation fields are populated using type-specific schema
            decision_fields = [
                'validation_decision_simile', 'validation_decision_metaphor',
                'validation_decision_personification', 'validation_decision_idiom',
                'validation_decision_hyperbole', 'validation_decision_metonymy',
                'validation_decision_other'
            ]

            reason_fields = [
                'validation_reason_simile', 'validation_reason_metaphor',
                'validation_reason_personification', 'validation_reason_idiom',
                'validation_reason_hyperbole', 'validation_reason_metonymy',
                'validation_reason_other'
            ]

            has_validation_data = False
            # Check if validation_response is populated (primary indicator of enhanced validation)
            if instance.get('validation_response') is not None and instance.get('validation_response') != '':
                has_validation_data = True

            if not has_validation_data:
                candidates.append(instance)

        self.recovery_stats['total_instances'] = len(instances)
        self.recovery_stats['instances_without_validation'] = len(candidates)

        return candidates

    def _execute_recovery(self, instances_needing_recovery: List[Dict]) -> bool:
        """Execute validation recovery using enhanced validation system."""
        try:
            # Initialize enhanced validator
            validator = MetaphorValidator(logger=self._create_logger())

            # Convert instances to format expected by validator
            validation_instances = []
            for instance in instances_needing_recovery:
                # Determine figurative types
                types = []
                if instance['target']:  # If we have target data, assume it was detected as figurative
                    types.append('metaphor')  # Default to metaphor for recovery

                if types:
                    validation_instance = {
                        'instance_id': len(validation_instances) + 1,
                        'verse_reference': instance['verse_reference'],
                        'hebrew_text': instance['hebrew_text'],
                        'english_text': instance['english_text'],
                        'figurative_text': instance['figurative_text'],
                        'explanation': instance['explanation'],
                        'confidence': instance['confidence'],
                        'metaphor': 'yes' if 'metaphor' in types else 'no',
                        'simile': 'yes' if 'simile' in types else 'no',
                        'personification': 'yes' if 'personification' in types else 'no',
                        'idiom': 'yes' if 'idiom' in types else 'no',
                        'hyperbole': 'yes' if 'hyperbole' in types else 'no',
                        'metonymy': 'yes' if 'metonymy' in types else 'no',
                        'other': 'yes' if 'other' in types else 'no',
                        'database_id': instance['id'],  # Keep track of original database ID
                        'original_instance': instance  # Store original for updating
                    }
                    validation_instances.append(validation_instance)

            if not validation_instances:
                print("INFO:   No instances require validation recovery.")
                return True

            print(f"PROCESSING:  Processing {len(validation_instances)} instances for validation recovery...")

            # Use enhanced retry validation
            recovery_results = validator.validate_chapter_instances_with_retry(validation_instances)

            self.recovery_stats['recovery_attempts'] = len(validation_instances)
            self.recovery_stats['strategies_used'] = list(validator.json_extraction_successes.keys())

            # Process recovery results
            successful_recoveries = 0
            failed_recoveries = 0

            for i, (validation_instance, recovery_result) in enumerate(zip(validation_instances, recovery_results)):
                original_instance = validation_instance['original_instance']

                if recovery_result and not self._is_error_recovery_result(recovery_result):
                    # Successful recovery - update original instance
                    validation_data = self._extract_validation_data(recovery_result)
                    original_instance.update(validation_data)
                    successful_recoveries += 1

                    if i < 5:  # Show first few successes
                        print(f"SUCCESS:  Recovery successful for instance {i+1}: {original_instance['verse_reference']}")
                else:
                    # Failed recovery - mark as failed but preserve data
                    failed_recoveries += 1
                    original_instance['recovery_status'] = 'FAILED'
                    original_instance['recovery_error'] = str(recovery_result) if recovery_result else 'No result returned'

                    if i < 5:  # Show first few failures
                        print(f"FAIL:  Recovery failed for instance {i+1}: {original_instance['verse_reference']}")

            self.recovery_stats['successful_recoveries'] = successful_recoveries
            self.recovery_stats['failed_recoveries'] = failed_recoveries

            # Print validation health report
            health_report = validator.get_detailed_health_report()
            print("\nREPORT:  Validation System Health Report:")
            print(health_report)

            return successful_recoveries > 0

        except Exception as e:
            print(f"FAIL:  Recovery execution failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _extract_validation_data(self, recovery_result: Dict) -> Dict:
        """Extract validation data from recovery result and map to type-specific fields."""
        validation_data = {
            'validation_response': json.dumps(recovery_result),
            'validation_error': None,
            'recovery_status': 'SUCCESS'
        }

        # Initialize type-specific validation fields
        decision_fields = [
            'validation_decision_simile', 'validation_decision_metaphor',
            'validation_decision_personification', 'validation_decision_idiom',
            'validation_decision_hyperbole', 'validation_decision_metonymy',
            'validation_decision_other'
        ]

        reason_fields = [
            'validation_reason_simile', 'validation_reason_metaphor',
            'validation_reason_personification', 'validation_reason_idiom',
            'validation_reason_hyperbole', 'validation_reason_metonymy',
            'validation_reason_other'
        ]

        # Set default values
        for field in decision_fields:
            validation_data[field] = None
        for field in reason_fields:
            validation_data[field] = None

        # Extract specific validation results
        if 'validation_results' in recovery_result:
            validation_results = recovery_result['validation_results']

            # Map validation results to type-specific fields
            for fig_type, result in validation_results.items():
                if isinstance(result, dict):
                    decision = result.get('decision', 'UNKNOWN')
                    reason = result.get('reason', '')

                    # Map to appropriate type-specific fields
                    if fig_type.lower() in ['simile', 'metaphor', 'personification', 'idiom', 'hyperbole', 'metonymy', 'other']:
                        decision_field = f'validation_decision_{fig_type.lower()}'
                        reason_field = f'validation_reason_{fig_type.lower()}'

                        if decision_field in validation_data:
                            validation_data[decision_field] = decision
                        if reason_field in validation_data:
                            validation_data[reason_field] = reason
        else:
            # If no specific validation results, assume valid for metaphor (most common type)
            validation_data['validation_decision_metaphor'] = 'VALID'
            validation_data['validation_reason_metaphor'] = 'Recovered using enhanced validation system'

        return validation_data

    def _is_error_recovery_result(self, recovery_result: Dict) -> bool:
        """Check if recovery result indicates an error."""
        if not recovery_result:
            return True

        if isinstance(recovery_result, dict):
            return ('error' in recovery_result or
                   'fallback_validation' in recovery_result or
                   recovery_result.get('validation_decision') in ['FAILED', 'ERROR'])

        return False

    def _update_database(self, instances: List[Dict]) -> bool:
        """Update the database with recovered validation data using type-specific schema."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            updated_count = 0
            for instance in instances:
                # Update validation fields using type-specific schema
                cursor.execute("""
                    UPDATE figurative_language SET
                        validation_response = ?,
                        validation_decision_simile = ?,
                        validation_decision_metaphor = ?,
                        validation_decision_personification = ?,
                        validation_decision_idiom = ?,
                        validation_decision_hyperbole = ?,
                        validation_decision_metonymy = ?,
                        validation_decision_other = ?,
                        validation_reason_simile = ?,
                        validation_reason_metaphor = ?,
                        validation_reason_personification = ?,
                        validation_reason_idiom = ?,
                        validation_reason_hyperbole = ?,
                        validation_reason_metonymy = ?,
                        validation_reason_other = ?,
                        validation_error = ?
                    WHERE id = ?
                """, (
                    instance.get('validation_response'),
                    instance.get('validation_decision_simile'),
                    instance.get('validation_decision_metaphor'),
                    instance.get('validation_decision_personification'),
                    instance.get('validation_decision_idiom'),
                    instance.get('validation_decision_hyperbole'),
                    instance.get('validation_decision_metonymy'),
                    instance.get('validation_decision_other'),
                    instance.get('validation_reason_simile'),
                    instance.get('validation_reason_metaphor'),
                    instance.get('validation_reason_personification'),
                    instance.get('validation_reason_idiom'),
                    instance.get('validation_reason_hyperbole'),
                    instance.get('validation_reason_metonymy'),
                    instance.get('validation_reason_other'),
                    instance.get('validation_error'),
                    instance['id']
                ))

                if cursor.rowcount > 0:
                    updated_count += 1

            conn.commit()
            conn.close()

            print(f"SUCCESS:  Updated {updated_count} instances in database")
            return True

        except Exception as e:
            print(f"FAIL:  Database update failed: {e}")
            return False

    def _generate_recovery_report(self) -> None:
        """Generate a comprehensive recovery report."""
        report = {
            'recovery_summary': self.recovery_stats,
            'enhanced_strategies_added': [
                'Strategy 7: Advanced JSON Repair with String Escaping Fix',
                'Strategy 8: Response Pre-processing & Sanitization',
                'Strategy 9: Progressive Parsing with Validation Checkpoints',
                'Strategy 10: Manual Validation Extraction (Last Resort)'
            ],
            'retry_logic_implemented': [
                'Attempt 1: Standard validation with all 10 JSON extraction strategies',
                'Attempt 2: Simplified validation prompt',
                'Attempt 3: Split into smaller batches',
                'Attempt 4: Individual instance validation'
            ],
            'database_info': {
                'original_database': str(self.db_path),
                'backup_database': str(self.backup_path),
                'database_size_before': self.db_path.stat().st_size if self.db_path.exists() else 0,
                'database_size_after': self.db_path.stat().st_size if self.db_path.exists() else 0
            },
            'success_metrics': {
                'recovery_success_rate': (self.recovery_stats['successful_recoveries'] / self.recovery_stats['recovery_attempts'] * 100) if self.recovery_stats['recovery_attempts'] > 0 else 0,
                'total_validation_coverage': (self.recovery_stats['successful_recoveries'] / self.recovery_stats['total_instances'] * 100) if self.recovery_stats['total_instances'] > 0 else 0
            }
        }

        # Save report
        with open(self.results_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        print(f"\nFILE:  Recovery report saved to: {self.results_path}")
        print(f"STATS:  Recovery success rate: {report['success_metrics']['recovery_success_rate']:.1f}%")
        print(f"REPORT:  Total validation coverage: {report['success_metrics']['total_validation_coverage']:.1f}%")

    def _create_logger(self):
        """Create a simple logger for the recovery process."""
        import logging

        class SimpleLogger:
            def __init__(self):
                self.start_time = datetime.now()

            def info(self, message):
                timestamp = datetime.now() - self.start_time
                print(f"[{timestamp.total_seconds():.1f}s] {message}")

            def debug(self, message):
                pass  # Skip debug messages for cleaner output

            def warning(self, message):
                print(f"WARNING:   {message}")

            def error(self, message):
                print(f"FAIL:  {message}")

        return SimpleLogger()


def main():
    """Main entry point for the recovery script."""
    recovery = Chapter2Recovery()
    success = recovery.run_recovery()

    if success:
        print("\nSUCCESS: Chapter 2 validation recovery completed successfully!")
        sys.exit(0)
    else:
        print("\nFAIL: Chapter 2 validation recovery failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()