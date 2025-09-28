#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM-Based Conceptual Grouper for Sankey Visualization
Phase 2: Semantic clustering of targets and vehicles using Gemini API
"""
import google.generativeai as genai
import os
import json
import time
from typing import List, Dict, Optional, Tuple, Set
import hashlib
from dataclasses import dataclass
from collections import defaultdict, Counter
import re

# Import existing Gemini API for consistent integration
try:
    from src.hebrew_figurative_db.ai_analysis.gemini_api_multi_model import MultiModelGeminiClient
except ImportError:
    # Fallback path structure for standalone execution
    import sys
    sys.path.append('src/hebrew_figurative_db/ai_analysis')
    from gemini_api_multi_model import MultiModelGeminiClient


@dataclass
class ConceptualGroup:
    """Represents a conceptual grouping of targets or vehicles"""
    name: str
    description: str
    members: List[str]
    confidence: float
    rationale: str


class ConceptualGrouper:
    """LLM-based semantic clustering system for targets and vehicles"""

    def __init__(self, api_key: str, logger=None, cache_dir: str = "cache"):
        """
        Initialize the ConceptualGrouper with Gemini API integration

        Args:
            api_key: Gemini API key
            logger: Logger instance
            cache_dir: Directory for caching grouping results
        """
        self.api_key = api_key
        self.logger = logger
        self.cache_dir = cache_dir

        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)

        # Initialize Gemini client using existing multi-model architecture
        self.gemini_client = MultiModelGeminiClient(
            api_key=api_key,
            logger=logger
        )

        # Generation config optimized for clustering tasks
        self.clustering_config = {
            'temperature': 0.1,  # Low temperature for consistency
            'top_p': 0.8,
            'top_k': 25,
            'max_output_tokens': 8000,
        }

        # Tracking metrics
        self.grouping_requests = 0
        self.cache_hits = 0
        self.successful_groupings = 0

        # Cache file paths
        self.target_cache_file = os.path.join(cache_dir, "target_groupings.json")
        self.vehicle_cache_file = os.path.join(cache_dir, "vehicle_groupings.json")

        # Load existing cache
        self.target_cache = self._load_cache(self.target_cache_file)
        self.vehicle_cache = self._load_cache(self.vehicle_cache_file)

    def _load_cache(self, cache_file: str) -> Dict:
        """Load grouping cache from file"""
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
                if self.logger:
                    self.logger.info(f"Loaded cache from {cache_file} with {len(cache)} entries")
                return cache
            except Exception as e:
                if self.logger:
                    self.logger.warning(f"Failed to load cache from {cache_file}: {e}")
        return {}

    def _save_cache(self, cache: Dict, cache_file: str):
        """Save grouping cache to file"""
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2, ensure_ascii=False)
            if self.logger:
                self.logger.info(f"Saved cache to {cache_file} with {len(cache)} entries")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to save cache to {cache_file}: {e}")

    def _generate_cache_key(self, items: List[str], category: str) -> str:
        """Generate a consistent cache key for a set of items"""
        sorted_items = sorted(set(items))  # Remove duplicates and sort
        content = f"{category}:{','.join(sorted_items)}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def _create_target_grouping_prompt(self, targets: List[str], category: str) -> str:
        """Create optimized prompt for target semantic clustering"""
        return f"""You are a biblical Hebrew scholar organizing figurative language targets for visualization.

**Task**: Create intuitive conceptual groups for TARGET entities in the "{category}" category.

**Targets to group**:
{', '.join(sorted(set(targets)))}

**Grouping Guidelines**:
• Create 3-6 conceptual groups that capture semantic relationships
• Each group should have 2+ members (unless a target is truly unique)
• Use clear, descriptive group names that enhance visualization clarity
• Focus on semantic similarity, not just literal categorization
• Consider biblical/theological relationships and common usage patterns

**Example groupings for reference**:
- Biblical Figures: Abraham, Moses, Jacob, David
- Natural Objects: tree, mountain, river, stone
- Divine Attributes: God's power, God's mercy, God's anger
- Social Entities: tribe, nation, family, household

**Required JSON format**:
{{
  "groups": [
    {{
      "name": "Group Name",
      "description": "Brief explanation of the semantic relationship",
      "members": ["target1", "target2", "target3"],
      "rationale": "Why these targets belong together conceptually"
    }}
  ],
  "ungrouped": ["target_that_is_unique"],
  "confidence": 0.85,
  "methodology": "Brief explanation of grouping approach used"
}}

**Critical Requirements**:
• Every target must appear in exactly one group OR in ungrouped
• Group names should be intuitive for visualization users
• Descriptions should be concise but informative
• Rationale should explain the semantic basis for grouping
• Return ONLY valid JSON, no other text"""

    def _create_vehicle_grouping_prompt(self, vehicles: List[str], category: str) -> str:
        """Create optimized prompt for vehicle semantic clustering"""
        return f"""You are a biblical Hebrew scholar organizing figurative language vehicles for visualization.

**Task**: Create intuitive conceptual groups for VEHICLE entities in the "{category}" category.

**Vehicles to group**:
{', '.join(sorted(set(vehicles)))}

**Grouping Guidelines**:
• Create 3-6 conceptual groups based on semantic domains
• Each group should have 2+ members (unless a vehicle is truly unique)
• Use clear, descriptive group names that enhance visualization clarity
• Focus on functional/semantic similarity in figurative usage
• Consider how these vehicles work metaphorically in biblical contexts

**Example groupings for reference**:
- Flying Creatures: eagle, dove, bird, bee
- Body Parts: heart, hand, eye, mouth
- Natural Forces: fire, water, wind, storm
- Metals & Materials: gold, silver, iron, bronze
- Human Actions: walking, building, carrying, fighting

**Required JSON format**:
{{
  "groups": [
    {{
      "name": "Group Name",
      "description": "Brief explanation of the semantic domain",
      "members": ["vehicle1", "vehicle2", "vehicle3"],
      "rationale": "Why these vehicles share functional/semantic properties"
    }}
  ],
  "ungrouped": ["vehicle_that_is_unique"],
  "confidence": 0.85,
  "methodology": "Brief explanation of grouping approach used"
}}

**Critical Requirements**:
• Every vehicle must appear in exactly one group OR in ungrouped
• Group names should reflect semantic/functional domains
• Descriptions should explain the domain clearly
• Rationale should explain the functional basis for grouping
• Return ONLY valid JSON, no other text"""

    def _call_gemini_for_grouping(self, prompt: str, cache_key: str, cache_dict: Dict) -> Optional[Dict]:
        """Make API call to Gemini for grouping with caching"""

        # Check cache first
        if cache_key in cache_dict:
            self.cache_hits += 1
            if self.logger:
                self.logger.info(f"Cache hit for grouping key: {cache_key[:12]}...")
            return cache_dict[cache_key]

        # Make API call
        self.grouping_requests += 1
        if self.logger:
            self.logger.info(f"Making Gemini API call for conceptual grouping (request #{self.grouping_requests})")

        try:
            # Use the existing multi-model client's _make_request method pattern
            model = self.gemini_client.primary_model
            response = model.generate_content(
                prompt,
                generation_config=self.clustering_config
            )

            if response and response.text:
                response_text = response.text.strip()

                # Extract JSON from response
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    grouping_result = json.loads(json_str)

                    # Cache the result
                    cache_dict[cache_key] = grouping_result
                    self.successful_groupings += 1

                    if self.logger:
                        self.logger.info(f"Successfully created conceptual grouping with {len(grouping_result.get('groups', []))} groups")

                    return grouping_result
                else:
                    if self.logger:
                        self.logger.error("No valid JSON found in Gemini response")
                    return None
            else:
                if self.logger:
                    self.logger.error("Empty response from Gemini API")
                return None

        except json.JSONDecodeError as e:
            if self.logger:
                self.logger.error(f"JSON parsing error in grouping response: {e}")
            return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Gemini API error during grouping: {e}")
            return None

    def group_targets_by_category(self, flows: List[Dict]) -> Dict[str, Dict]:
        """
        Group targets by semantic similarity within each normalized category

        Args:
            flows: List of flow dictionaries from clean_deuteronomy_data.json

        Returns:
            Dict mapping category names to grouping results
        """
        if self.logger:
            self.logger.info("Starting target conceptual grouping by category")

        # Group targets by normalized category
        targets_by_category = defaultdict(set)
        for flow in flows:
            category = flow.get('target_level_1_normalized', 'unknown')
            target = flow.get('target_specific', '').strip()
            if target:
                targets_by_category[category].add(target)

        results = {}

        total_categories = len(targets_by_category)
        processed_count = 0

        for category, targets in targets_by_category.items():
            processed_count += 1

            if len(targets) < 2:
                # Skip categories with only one target
                if self.logger:
                    self.logger.info(f"Skipping target category '{category}' with only {len(targets)} target(s) ({processed_count}/{total_categories})")
                continue

            target_list = list(targets)
            cache_key = self._generate_cache_key(target_list, f"target_{category}")

            if self.logger:
                self.logger.info(f"Processing target category '{category}' with {len(targets)} targets ({processed_count}/{total_categories})")

            prompt = self._create_target_grouping_prompt(target_list, category)
            grouping_result = self._call_gemini_for_grouping(prompt, cache_key, self.target_cache)

            # Save cache after every successful grouping to prevent data loss
            if grouping_result:
                self._save_cache(self.target_cache, self.target_cache_file)

            if grouping_result:
                results[category] = grouping_result
                # Validate that all targets are accounted for (case-insensitive)
                def normalize_text(text):
                    return text.lower().strip()

                grouped_targets = set()
                for group in grouping_result.get('groups', []):
                    grouped_targets.update(normalize_text(member) for member in group.get('members', []))
                grouped_targets.update(normalize_text(member) for member in grouping_result.get('ungrouped', []))

                normalized_target_list = {normalize_text(t) for t in target_list}
                missing = normalized_target_list - grouped_targets
                extra = grouped_targets - normalized_target_list

                if missing or extra:
                    if self.logger:
                        self.logger.warning(f"Target grouping validation issues for '{category}': missing={missing}, extra={extra}")
            else:
                if self.logger:
                    self.logger.error(f"Failed to create target grouping for category '{category}'")

        # Save updated cache
        self._save_cache(self.target_cache, self.target_cache_file)

        if self.logger:
            self.logger.info(f"Completed target grouping for {len(results)} categories")

        return results

    def group_vehicles_by_category(self, flows: List[Dict]) -> Dict[str, Dict]:
        """
        Group vehicles by semantic domains within each normalized category

        Args:
            flows: List of flow dictionaries from clean_deuteronomy_data.json

        Returns:
            Dict mapping category names to grouping results
        """
        if self.logger:
            self.logger.info("Starting vehicle conceptual grouping by category")

        # Group vehicles by normalized category
        vehicles_by_category = defaultdict(set)
        for flow in flows:
            category = flow.get('vehicle_level_1_normalized', 'unknown')
            vehicle = flow.get('vehicle_specific', '').strip()
            if vehicle:
                vehicles_by_category[category].add(vehicle)

        results = {}

        total_categories = len(vehicles_by_category)
        processed_count = 0

        for category, vehicles in vehicles_by_category.items():
            processed_count += 1

            if len(vehicles) < 2:
                # Skip categories with only one vehicle
                if self.logger:
                    self.logger.info(f"Skipping vehicle category '{category}' with only {len(vehicles)} vehicle(s) ({processed_count}/{total_categories})")
                continue

            vehicle_list = list(vehicles)
            cache_key = self._generate_cache_key(vehicle_list, f"vehicle_{category}")

            if self.logger:
                self.logger.info(f"Processing vehicle category '{category}' with {len(vehicles)} vehicles ({processed_count}/{total_categories})")

            prompt = self._create_vehicle_grouping_prompt(vehicle_list, category)
            grouping_result = self._call_gemini_for_grouping(prompt, cache_key, self.vehicle_cache)

            # Save cache after every successful grouping to prevent data loss
            if grouping_result:
                self._save_cache(self.vehicle_cache, self.vehicle_cache_file)

            if grouping_result:
                results[category] = grouping_result
                # Validate that all vehicles are accounted for (case-insensitive)
                def normalize_text(text):
                    return text.lower().strip()

                grouped_vehicles = set()
                for group in grouping_result.get('groups', []):
                    grouped_vehicles.update(normalize_text(member) for member in group.get('members', []))
                grouped_vehicles.update(normalize_text(member) for member in grouping_result.get('ungrouped', []))

                normalized_vehicle_list = {normalize_text(v) for v in vehicle_list}
                missing = normalized_vehicle_list - grouped_vehicles
                extra = grouped_vehicles - normalized_vehicle_list

                if missing or extra:
                    if self.logger:
                        self.logger.warning(f"Vehicle grouping validation issues for '{category}': missing={missing}, extra={extra}")
            else:
                if self.logger:
                    self.logger.error(f"Failed to create vehicle grouping for category '{category}'")

        # Save updated cache
        self._save_cache(self.vehicle_cache, self.vehicle_cache_file)

        if self.logger:
            self.logger.info(f"Completed vehicle grouping for {len(results)} categories")

        return results

    def apply_groupings_to_flows(self, flows: List[Dict], target_groupings: Dict[str, Dict],
                                vehicle_groupings: Dict[str, Dict]) -> List[Dict]:
        """
        Apply conceptual groupings to flow data, adding group assignments

        Args:
            flows: Original flow data
            target_groupings: Target grouping results by category
            vehicle_groupings: Vehicle grouping results by category

        Returns:
            Enhanced flows with conceptual group assignments
        """
        if self.logger:
            self.logger.info("Applying conceptual groupings to flow data")

        # Create lookup dictionaries for efficient mapping
        target_to_group = {}
        vehicle_to_group = {}

        # Build target lookup
        for category, grouping in target_groupings.items():
            for group in grouping.get('groups', []):
                for member in group.get('members', []):
                    target_to_group[member] = {
                        'category': category,
                        'conceptual_group': group['name'],
                        'group_description': group['description']
                    }
            # Handle ungrouped targets
            for ungrouped in grouping.get('ungrouped', []):
                target_to_group[ungrouped] = {
                    'category': category,
                    'conceptual_group': 'Ungrouped',
                    'group_description': 'Unique entity not grouped with others'
                }

        # Build vehicle lookup
        for category, grouping in vehicle_groupings.items():
            for group in grouping.get('groups', []):
                for member in group.get('members', []):
                    vehicle_to_group[member] = {
                        'category': category,
                        'conceptual_group': group['name'],
                        'group_description': group['description']
                    }
            # Handle ungrouped vehicles
            for ungrouped in grouping.get('ungrouped', []):
                vehicle_to_group[ungrouped] = {
                    'category': category,
                    'conceptual_group': 'Ungrouped',
                    'group_description': 'Unique entity not grouped with others'
                }

        # Apply groupings to flows
        enhanced_flows = []
        grouped_targets = 0
        grouped_vehicles = 0

        for flow in flows:
            enhanced_flow = flow.copy()

            # Add target conceptual group
            target_specific = flow.get('target_specific', '').strip()
            if target_specific in target_to_group:
                enhanced_flow.update({
                    'target_conceptual_group': target_to_group[target_specific]['conceptual_group'],
                    'target_group_description': target_to_group[target_specific]['group_description']
                })
                grouped_targets += 1
            else:
                enhanced_flow.update({
                    'target_conceptual_group': 'Unassigned',
                    'target_group_description': 'No conceptual group assigned'
                })

            # Add vehicle conceptual group
            vehicle_specific = flow.get('vehicle_specific', '').strip()
            if vehicle_specific in vehicle_to_group:
                enhanced_flow.update({
                    'vehicle_conceptual_group': vehicle_to_group[vehicle_specific]['conceptual_group'],
                    'vehicle_group_description': vehicle_to_group[vehicle_specific]['group_description']
                })
                grouped_vehicles += 1
            else:
                enhanced_flow.update({
                    'vehicle_conceptual_group': 'Unassigned',
                    'vehicle_group_description': 'No conceptual group assigned'
                })

            enhanced_flows.append(enhanced_flow)

        if self.logger:
            self.logger.info(f"Applied groupings to {len(enhanced_flows)} flows: "
                           f"{grouped_targets} targets grouped, {grouped_vehicles} vehicles grouped")

        return enhanced_flows

    def generate_grouping_report(self, target_groupings: Dict[str, Dict],
                               vehicle_groupings: Dict[str, Dict]) -> Dict:
        """
        Generate a comprehensive report on grouping quality and statistics

        Args:
            target_groupings: Target grouping results
            vehicle_groupings: Vehicle grouping results

        Returns:
            Detailed grouping quality report
        """
        report = {
            'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
            'api_usage': {
                'total_requests': self.grouping_requests,
                'cache_hits': self.cache_hits,
                'successful_groupings': self.successful_groupings,
                'cache_hit_rate': self.cache_hits / max(1, self.grouping_requests + self.cache_hits)
            },
            'target_groupings': {
                'categories_processed': len(target_groupings),
                'total_groups_created': sum(len(g.get('groups', [])) for g in target_groupings.values()),
                'average_confidence': sum(g.get('confidence', 0) for g in target_groupings.values()) / max(1, len(target_groupings)),
                'details': {}
            },
            'vehicle_groupings': {
                'categories_processed': len(vehicle_groupings),
                'total_groups_created': sum(len(g.get('groups', [])) for g in vehicle_groupings.values()),
                'average_confidence': sum(g.get('confidence', 0) for g in vehicle_groupings.values()) / max(1, len(vehicle_groupings)),
                'details': {}
            }
        }

        # Detailed target analysis
        for category, grouping in target_groupings.items():
            groups = grouping.get('groups', [])
            ungrouped = grouping.get('ungrouped', [])
            total_items = sum(len(g.get('members', [])) for g in groups) + len(ungrouped)

            report['target_groupings']['details'][category] = {
                'total_targets': total_items,
                'groups_created': len(groups),
                'ungrouped_count': len(ungrouped),
                'grouping_rate': (total_items - len(ungrouped)) / max(1, total_items),
                'confidence': grouping.get('confidence', 0),
                'group_names': [g.get('name', 'Unknown') for g in groups]
            }

        # Detailed vehicle analysis
        for category, grouping in vehicle_groupings.items():
            groups = grouping.get('groups', [])
            ungrouped = grouping.get('ungrouped', [])
            total_items = sum(len(g.get('members', [])) for g in groups) + len(ungrouped)

            report['vehicle_groupings']['details'][category] = {
                'total_vehicles': total_items,
                'groups_created': len(groups),
                'ungrouped_count': len(ungrouped),
                'grouping_rate': (total_items - len(ungrouped)) / max(1, total_items),
                'confidence': grouping.get('confidence', 0),
                'group_names': [g.get('name', 'Unknown') for g in groups]
            }

        return report

    def process_complete_dataset(self, data_file: str) -> Tuple[List[Dict], Dict]:
        """
        Complete processing pipeline for the entire dataset

        Args:
            data_file: Path to clean_deuteronomy_data.json

        Returns:
            Tuple of (enhanced_flows, grouping_report)
        """
        if self.logger:
            self.logger.info(f"Starting complete conceptual grouping pipeline for {data_file}")

        # Load data
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        flows = data.get('flows', [])

        if self.logger:
            self.logger.info(f"Loaded {len(flows)} flows for processing")

        # Perform groupings
        target_groupings = self.group_targets_by_category(flows)
        vehicle_groupings = self.group_vehicles_by_category(flows)

        # Apply groupings to flows
        enhanced_flows = self.apply_groupings_to_flows(flows, target_groupings, vehicle_groupings)

        # Generate report
        report = self.generate_grouping_report(target_groupings, vehicle_groupings)

        if self.logger:
            self.logger.info("Completed conceptual grouping pipeline")

        return enhanced_flows, report


def main():
    """Test the ConceptualGrouper with sample data"""
    import logging

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return

    # Initialize grouper
    grouper = ConceptualGrouper(api_key=api_key, logger=logger)

    # Process complete dataset
    try:
        enhanced_flows, report = grouper.process_complete_dataset('clean_deuteronomy_data.json')

        # Save enhanced data
        enhanced_data = {
            'metadata': {
                'generated_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'source_file': 'clean_deuteronomy_data.json',
                'conceptual_grouping_applied': True,
                'total_flows': len(enhanced_flows)
            },
            'flows': enhanced_flows
        }

        with open('clean_deuteronomy_data_grouped.json', 'w', encoding='utf-8') as f:
            json.dump(enhanced_data, f, indent=2, ensure_ascii=False)

        # Save report
        with open('conceptual_grouping_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info("Conceptual grouping completed successfully!")
        logger.info(f"Enhanced data saved to: clean_deuteronomy_data_grouped.json")
        logger.info(f"Report saved to: conceptual_grouping_report.json")

    except Exception as e:
        logger.error(f"Error during conceptual grouping: {e}")


if __name__ == '__main__':
    main()