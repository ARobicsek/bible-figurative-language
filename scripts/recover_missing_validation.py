#!/usr/bin/env python3
"""
Recover Missing Validation Data Script

This script identifies and recovers missing validation data for figurative language instances.
It should be run when validation coverage is below 100% for any chapter.

Usage:
    python recover_missing_validation.py --database path/to/database.db [--book Book] [--chapter Chapter]
    python recover_missing_validation.py --database private/isaiah_c10_multi_v_parallel_20251204_1449.db

Requirements:
    - Python 3.8+
    - OpenAI API key
"""

import argparse
import json
import logging
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from private.src.hebrew_figurative_db.unified_llm_client import LLMClient
from private.src.hebrew_figurative_db.database_manager import DatabaseManager


class ValidationRecovery:
    """Recover missing validation data for figurative language instances"""

    def __init__(self, database_path: str, log_file: str = None):
        """
        Initialize validation recovery

        Args:
            database_path: Path to SQLite database
            log_file: Optional log file path
        """
        self.database_path = database_path
        self.db_manager = DatabaseManager(database_path)
        self.llm_client = LLMClient()

        # Setup logging
        self.setup_logging(log_file)

        # Track recovery statistics
        self.stats = {
            'total_instances': 0,
            'missing_validation': 0,
            'recovered': 0,
            'failed': 0,
            'errors': []
        }

    def setup_logging(self, log_file: str = None):
        """Setup logging configuration"""
        if log_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = f"validation_recovery_{timestamp}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def identify_missing_validation(self, book: str = None, chapter: int = None) -> List[Dict]:
        """
        Identify instances missing validation data

        Args:
            book: Optional book filter
            chapter: Optional chapter filter

        Returns:
            List of instances missing validation
        """
        self.logger.info("Identifying instances missing validation data...")

        query = """
        SELECT fl.id, fl.db_id, v.book, v.chapter, v.verse,
               fl.figurative_text, fl.figurative_text_in_hebrew,
               fl.figurative_text_in_hebrew_stripped,
               fl.explanation, fl.confidence,
               fl.simile, fl.metaphor, fl.personification,
               fl.idiom, fl.hyperbole, fl.metonymy, fl.other
        FROM figurative_language fl
        JOIN verses v ON fl.verse_id = v.id
        WHERE 1=1
        """

        params = []
        if book:
            query += " AND v.book = ?"
            params.append(book)
        if chapter:
            query += " AND v.chapter = ?"
            params.append(chapter)

        query += " ORDER BY v.book, v.chapter, v.verse"

        instances = self.db_manager.execute_query(query, params)
        missing_validation = []

        for instance in instances:
            # Check if ANY validation decision exists
            has_validation = any([
                instance.get(f'validation_decision_{fig_type}')
                for fig_type in ['simile', 'metaphor', 'personification',
                               'idiom', 'hyperbole', 'metonymy', 'other']
            ])

            if not has_validation:
                # Get figurative types for this instance
                fig_types = []
                for fig_type in ['simile', 'metaphor', 'personification',
                               'idiom', 'hyperbole', 'metonymy', 'other']:
                    if instance.get(fig_type) == 'yes':
                        fig_types.append(fig_type)

                missing_validation.append({
                    'id': instance['id'],
                    'db_id': instance['db_id'],
                    'book': instance['book'],
                    'chapter': instance['chapter'],
                    'verse': instance['verse'],
                    'reference': f"{instance['book']} {instance['chapter']}:{instance['verse']}",
                    'figurative_text': instance.get('figurative_text', ''),
                    'hebrew_text': instance.get('figurative_text_in_hebrew_stripped', ''),
                    'explanation': instance.get('explanation', ''),
                    'confidence': instance.get('confidence', 0.0),
                    'detected_types': fig_types
                })

        self.stats['total_instances'] = len(instances) if instances else 0
        self.stats['missing_validation'] = len(missing_validation)

        self.logger.info(f"Found {len(missing_validation)} instances missing validation "
                        f"out of {self.stats['total_instances']} total")

        return missing_validation

    def create_validation_request(self, instances: List[Dict]) -> str:
        """
        Create validation request for batch of instances

        Args:
            instances: List of instances to validate

        Returns:
            Formatted validation request
        """
        # Format instances for validation API
        formatted_instances = []
        for i, instance in enumerate(instances, 1):
            formatted_instances.append({
                "instance_id": i,  # Use sequential ID for validation
                "verse_reference": instance['reference'],
                "hebrew_text": instance['hebrew_text'],
                "english_text": instance['figurative_text'],
                "figurative_text": instance['figurative_text'],
                "explanation": instance['explanation'],
                "confidence": instance['confidence'],
                "types": instance['detected_types']
            })

        # Create validation prompt
        validation_prompt = f"""You are a biblical Hebrew scholar validating a list of detected figurative language instances.

DETECTED INSTANCES TO VALIDATE:
```json
{json.dumps(formatted_instances, indent=2)}
```

For EACH instance above, validate the detected figurative language types. Consider:

1. Is the figure actually present in the text?
2. Is the classification correct?
3. Is the explanation accurate?

For each instance, return a JSON object with:
- instance_id: Sequential ID from the list above
- validation_results: Object with each figurative type as key
  - decision: "VALID", "INVALID", or "RECLASSIFIED"
  - reason: Brief explanation of decision
  - reclassified_type: If RECLASSIFIED, what it should be

Return only a JSON array of validation results:
[
  {{
    "instance_id": 1,
    "validation_results": {{
      "metaphor": {{
        "decision": "VALID",
        "reason": "Clear metaphor comparing X to Y"
      }},
      "simile": {{
        "decision": "INVALID",
        "reason": "No comparison marker present"
      }}
    }}
  }},
  ...
]"""

        return validation_prompt

    def process_validation_response(self, response: str, instances: List[Dict]) -> List[Dict]:
        """
        Process validation response and prepare for database update

        Args:
            response: Validation API response
            instances: Original instances (for ID mapping)

        Returns:
            List of validation updates ready for database
        """
        try:
            # Parse JSON response
            validation_results = json.loads(response)

            if not isinstance(validation_results, list):
                raise ValueError("Response is not a JSON array")

            # Map validation results back to instance IDs
            updates = []
            instance_map = {i+1: instance for i, instance in enumerate(instances)}

            for result in validation_results:
                instance_id = result.get('instance_id')
                if not instance_id or instance_id not in instance_map:
                    self.logger.warning(f"Skipping validation result with invalid instance_id: {instance_id}")
                    continue

                instance = instance_map[instance_id]
                validation_data = {'db_id': instance['db_id']}

                # Process each figurative type validation
                for fig_type, validation in result.get('validation_results', {}).items():
                    if isinstance(validation, dict):
                        decision = validation.get('decision', 'INVALID')
                        reason = validation.get('reason', '')
                        reclassified_type = validation.get('reclassified_type', '')

                        # Set validation decision
                        validation_data[f'validation_decision_{fig_type}'] = decision
                        validation_data[f'validation_reason_{fig_type}'] = reason

                        # Set final figurative type based on validation
                        if decision == 'VALID':
                            validation_data[f'final_{fig_type}'] = 'yes'
                        elif decision == 'RECLASSIFIED' and reclassified_type:
                            validation_data[f'final_{reclassified_type}'] = 'yes'
                            validation_data[f'validation_reason_{fig_type}'] = f"Reclassified to {reclassified_type}: {reason}"

                updates.append(validation_data)
                self.logger.info(f"Processed validation for instance {instance_id} ({instance['reference']})")

            return updates

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse validation response as JSON: {e}")
            self.stats['errors'].append(f"JSON parse error: {str(e)}")
            return []
        except Exception as e:
            self.logger.error(f"Error processing validation response: {e}")
            self.stats['errors'].append(f"Processing error: {str(e)}")
            return []

    def update_database(self, updates: List[Dict]):
        """
        Update database with validation results

        Args:
            updates: List of validation updates
        """
        self.logger.info(f"Updating database with {len(updates)} validation results...")

        for update in updates:
            db_id = update['db_id']

            # Remove db_id from update dict
            validation_data = {k: v for k, v in update.items() if k != 'db_id'}

            try:
                # Set final_figurative_language flag if any validation is valid
                any_valid = any([
                    validation_data.get(f'validation_decision_{fig_type}') == 'VALID'
                    or validation_data.get(f'validation_decision_{fig_type}') == 'RECLASSIFIED'
                    for fig_type in ['simile', 'metaphor', 'personification',
                                   'idiom', 'hyperbole', 'metonymy', 'other']
                ])
                validation_data['final_figurative_language'] = 'yes' if any_valid else 'no'

                # Update database
                self.db_manager.update_validation_data(db_id, validation_data)
                self.stats['recovered'] += 1

            except Exception as e:
                self.logger.error(f"Failed to update database for ID {db_id}: {e}")
                self.stats['failed'] += 1
                self.stats['errors'].append(f"Database update error for ID {db_id}: {str(e)}")

    def recover_batch(self, instances: List[Dict], batch_size: int = 10) -> bool:
        """
        Recover validation for a batch of instances

        Args:
            instances: List of instances to recover
            batch_size: Number of instances to validate in one API call

        Returns:
            True if successful, False otherwise
        """
        if not instances:
            return True

        self.logger.info(f"Recovering validation for {len(instances)} instances "
                        f"(batch size: {batch_size})")

        # Process in batches
        for i in range(0, len(instances), batch_size):
            batch = instances[i:i + batch_size]

            self.logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} instances")

            # Create validation request
            request = self.create_validation_request(batch)

            try:
                # Call validation API
                response = self.llm_client.validate_figurative_language(request)

                if not response:
                    self.logger.error(f"No response from validation API for batch {i//batch_size + 1}")
                    self.stats['failed'] += len(batch)
                    continue

                # Process response
                updates = self.process_validation_response(response, batch)

                if updates:
                    # Update database
                    self.update_database(updates)
                else:
                    self.logger.warning(f"No valid updates from validation response for batch {i//batch_size + 1}")
                    self.stats['failed'] += len(batch)

                # Small delay to avoid rate limiting
                time.sleep(1)

            except Exception as e:
                self.logger.error(f"Error processing batch {i//batch_size + 1}: {e}")
                self.stats['errors'].append(f"Batch {i//batch_size + 1} error: {str(e)}")
                self.stats['failed'] += len(batch)

        return self.stats['failed'] == 0

    def generate_report(self) -> str:
        """Generate recovery report"""
        report = f"""
VALIDATION RECOVERY REPORT
========================
Database: {self.database_path}
Timestamp: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

SUMMARY:
--------
Total instances: {self.stats['total_instances']}
Missing validation: {self.stats['missing_validation']}
Successfully recovered: {self.stats['recovered']}
Failed to recover: {self.stats['failed']}
Recovery rate: {self.stats['recovered']/max(1, self.stats['missing_validation'])*100:.1f}%

ERRORS:
-------
"""

        if self.stats['errors']:
            for error in self.stats['errors'][:10]:  # Limit to first 10 errors
                report += f"- {error}\n"
        else:
            report += "No errors encountered\n"

        report += f"""
RECOMMENDATIONS:
---------------
"""

        if self.stats['failed'] > 0:
            report += f"- Review {self.stats['failed']} failed instances\n"
            report += "- Check validation API response format\n"
            report += "- Verify database connectivity\n"

        if self.stats['recovered'] > 0:
            report += f"- Success! {self.stats['recovered']} instances now have validation\n"

        if self.stats['missing_validation'] > 0:
            coverage = (self.stats['recovered'] / max(1, self.stats['missing_validation'])) * 100
            if coverage < 100:
                report += f"- {100-coverage:.1f}% of missing validation still needs recovery\n"
                report += "- Consider running recovery script again\n"

        return report

    def recover_all(self, book: str = None, chapter: int = None, batch_size: int = 10):
        """
        Recover all missing validation data

        Args:
            book: Optional book filter
            chapter: Optional chapter filter
            batch_size: Batch size for API calls
        """
        self.logger.info("Starting validation recovery...")

        # Identify instances missing validation
        missing_instances = self.identify_missing_validation(book, chapter)

        if not missing_instances:
            self.logger.info("No missing validation data found. All instances are validated!")
            return True

        # Group by chapter for organized recovery
        chapters = {}
        for instance in missing_instances:
            key = (instance['book'], instance['chapter'])
            if key not in chapters:
                chapters[key] = []
            chapters[key].append(instance)

        self.logger.info(f"Found missing validation in {len(chapters)} chapter(s)")

        # Recover each chapter
        overall_success = True
        for (book, chapter), instances in chapters.items():
            self.logger.info(f"\n{'='*50}")
            self.logger.info(f"Recovering {book} Chapter {chapter}")
            self.logger.info(f"Instances: {len(instances)}")

            success = self.recover_batch(instances, batch_size)
            if not success:
                overall_success = False
                self.logger.error(f"Failed to fully recover {book} {chapter}")

        # Generate and save report
        report = self.generate_report()
        self.logger.info("\n" + report)

        # Save report to file
        report_file = f"validation_recovery_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report)

        self.logger.info(f"\nReport saved to: {report_file}")

        return overall_success


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Recover missing validation data for figurative language instances"
    )
    parser.add_argument(
        "--database", "-d",
        required=True,
        help="Path to SQLite database file"
    )
    parser.add_argument(
        "--book", "-b",
        help="Book name to filter (e.g., Isaiah)"
    )
    parser.add_argument(
        "--chapter", "-c",
        type=int,
        help="Chapter number to filter"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=10,
        help="Batch size for validation API calls (default: 10)"
    )
    parser.add_argument(
        "--log-file",
        help="Optional log file path"
    )

    args = parser.parse_args()

    # Validate database exists
    if not os.path.exists(args.database):
        print(f"ERROR: Database file not found: {args.database}")
        return 1

    # Initialize recovery
    recovery = ValidationRecovery(args.database, args.log_file)

    # Run recovery
    success = recovery.recover_all(
        book=args.book,
        chapter=args.chapter,
        batch_size=args.batch_size
    )

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())