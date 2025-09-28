#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude Sonnet 4 Client for Hebrew Figurative Language Analysis
Serves as a high-quality fallback when Gemini models fail
"""
import anthropic
import os
import json
import re
import logging
from typing import Dict, List, Optional, Tuple, Any


class ClaudeSonnetClient:
    """Claude Sonnet 4 client for figurative language analysis"""

    def __init__(self, api_key: str = None, logger: logging.Logger = None):
        """Initialize Claude Sonnet client"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.logger = logger or logging.getLogger(__name__)
        self.model_name = "claude-sonnet-4-20250514"

        # Usage tracking
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0
        }

    def analyze_figurative_language_flexible(
        self,
        hebrew_text: str,
        english_text: str,
        book: str = "Unknown",
        chapter: int = 0,
        max_tokens: int = 8000
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """
        Analyze text for figurative language using Claude Sonnet 4
        Returns: (result_text, error, metadata)
        """

        prompt = self._create_flexible_analysis_prompt(hebrew_text, english_text, book, chapter)

        try:
            self.usage_stats["total_requests"] += 1

            self.logger.info("Making request to Claude Sonnet 4 for figurative language analysis")

            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Update usage statistics
            if hasattr(message, 'usage'):
                self.usage_stats["total_input_tokens"] += message.usage.input_tokens
                self.usage_stats["total_output_tokens"] += message.usage.output_tokens
                self.usage_stats["total_tokens"] += message.usage.input_tokens + message.usage.output_tokens

            self.usage_stats["successful_requests"] += 1

            # Extract JSON and metadata from response
            instances, deliberation, tagging_analysis = self._extract_json_and_metadata(response_text)

            metadata = {
                "flexible_instances": instances,
                "figurative_detection_deliberation": deliberation,
                "tagging_analysis_deliberation": tagging_analysis,
                "model_used": self.model_name,
                "truncation_detected": False,  # Claude Sonnet 4 with 8000 tokens should handle most cases
                "instances_count": len(instances)
            }

            self.logger.info(f"Claude Sonnet 4 analysis completed successfully: {len(instances)} instances found")

            return response_text, None, metadata

        except anthropic.APIError as e:
            self.usage_stats["failed_requests"] += 1
            error_msg = f"Claude Sonnet API error: {str(e)}"
            self.logger.error(error_msg)

            # Return empty result with error
            metadata = {
                "flexible_instances": [],
                "figurative_detection_deliberation": "",
                "tagging_analysis_deliberation": "",
                "model_used": self.model_name,
                "truncation_detected": False,
                "instances_count": 0
            }

            return "", error_msg, metadata

        except Exception as e:
            self.usage_stats["failed_requests"] += 1
            error_msg = f"Unexpected error in Claude Sonnet analysis: {str(e)}"
            self.logger.error(error_msg)

            metadata = {
                "flexible_instances": [],
                "figurative_detection_deliberation": "",
                "tagging_analysis_deliberation": "",
                "model_used": self.model_name,
                "truncation_detected": False,
                "instances_count": 0
            }

            return "", error_msg, metadata

    def _create_flexible_analysis_prompt(self, hebrew_text: str, english_text: str, book: str, chapter: int) -> str:
        """Create the analysis prompt for Claude Sonnet 4"""

        return f"""You are an expert in biblical Hebrew linguistics and figurative language analysis. I need you to analyze a verse from {book} {chapter} for figurative language using a CONSERVATIVE approach.

**Hebrew Text:** {hebrew_text}
**English Translation:** {english_text}

**TASK:** Identify ALL instances of figurative language in this verse using these guidelines:

**CONSERVATIVE DETECTION GUIDELINES:**
1. **MARK** physical verbs/concepts applied to spiritual/abstract concepts
2. **MARK** clear metaphors, similes, personification, idioms, hyperbole, metonymy
3. **BE CONSERVATIVE** with divine anthropomorphisms (only mark if clearly figurative beyond standard narrative language)
4. **EXCLUDE** proper names, standard titles, conventional expressions unless clearly figurative
5. **FOCUS** on Hebrew text primarily, use English for clarification

**OUTPUT FORMAT:**
First provide your **DETECTION DELIBERATION** - explain what you considered and why you included/excluded each potential figurative element.

Then provide **HIERARCHICAL TAGGING ANALYSIS** for any instances you found.

Finally, provide a **JSON array** with this structure for each instance:
```json
[
  {{
    "instance_id": 1,
    "figurative_language": "yes",
    "simile": "yes/no",
    "metaphor": "yes/no",
    "personification": "yes/no",
    "idiom": "yes/no",
    "hyperbole": "yes/no",
    "metonymy": "yes/no",
    "other": "yes/no",
    "confidence": 0.8,
    "english_text": "the relevant English phrase",
    "hebrew_text": "the relevant Hebrew phrase",
    "explanation": "detailed explanation of the figurative language",
    "speaker": "who is speaking",
    "purpose": "why this figurative language is used",
    "target": ["specific target", "target category", "general domain"],
    "vehicle": ["specific vehicle", "vehicle category", "general domain"],
    "ground": ["specific quality", "quality category", "general domain"],
    "posture": ["specific attitude", "attitude category", "general domain"]
  }}
]
```

**If NO figurative language is found, return an empty array: []**

Begin your analysis:"""

    def _extract_json_and_metadata(self, response_text: str) -> Tuple[List[Dict], str, str]:
        """Extract JSON instances and metadata from Claude's response"""

        # Split response into sections
        lines = response_text.split('\n')

        deliberation_lines = []
        tagging_lines = []
        json_started = False
        json_lines = []

        current_section = "deliberation"
        bracket_count = 0

        for line in lines:
            line_stripped = line.strip()

            # Look for section markers
            if "hierarchical tagging" in line_stripped.lower() or "tagging analysis" in line_stripped.lower():
                current_section = "tagging"
                continue
            elif line_stripped.startswith('[') or line_stripped.startswith('```json'):
                current_section = "json"
                json_started = True
                if line_stripped.startswith('['):
                    json_lines.append(line)
                    # Count brackets for proper closure detection
                    bracket_count += line_stripped.count('[') - line_stripped.count(']')
                continue
            elif line_stripped == '```' and json_started:
                break

            # Collect lines for each section
            if current_section == "deliberation" and not json_started:
                deliberation_lines.append(line)
            elif current_section == "tagging" and not json_started:
                tagging_lines.append(line)
            elif current_section == "json" and json_started:
                json_lines.append(line)
                # Count brackets to detect proper closure
                bracket_count += line.count('[') - line.count(']')
                if bracket_count <= 0 and ']' in line:
                    break

        deliberation = '\n'.join(deliberation_lines).strip()
        tagging_analysis = '\n'.join(tagging_lines).strip()
        json_text = '\n'.join(json_lines).strip()

        # Extract and parse JSON with robust handling
        instances = []
        if json_text:
            try:
                # Clean up JSON text
                json_text = re.sub(r'^```json\s*', '', json_text)
                json_text = re.sub(r'\s*```$', '', json_text)
                json_text = json_text.strip()

                # Attempt to repair incomplete JSON
                if json_text.startswith('[') and not json_text.endswith(']'):
                    # Check if we have complete objects but missing closing bracket
                    brace_count = json_text.count('{') - json_text.count('}')
                    if brace_count == 0:  # All objects are complete
                        json_text += '\n]'
                        self.logger.info("Repaired incomplete JSON array by adding closing bracket")
                    else:
                        # Try to close incomplete objects
                        json_text += '\n' + '  }' * brace_count + '\n]'
                        self.logger.info(f"Repaired incomplete JSON by adding {brace_count} closing braces and array bracket")

                if json_text.startswith('['):
                    instances = json.loads(json_text)
                    self.logger.debug(f"Successfully parsed {len(instances)} instances from Claude Sonnet response")
                else:
                    self.logger.warning("JSON response does not have proper array format")

            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON from Claude Sonnet response: {e}")
                self.logger.debug(f"Raw JSON text: {json_text}")

                # Try aggressive repair approach
                try:
                    # Extract just the JSON content using regex
                    json_match = re.search(r'\[\s*\{.*?\}\s*\]', response_text, re.DOTALL)
                    if json_match:
                        json_text = json_match.group(0)
                        instances = json.loads(json_text)
                        self.logger.info(f"Successfully repaired and parsed {len(instances)} instances using regex extraction")
                    else:
                        self.logger.warning("Could not extract valid JSON array from response")
                except:
                    self.logger.error("All JSON repair attempts failed")

        return instances, deliberation, tagging_analysis

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.usage_stats.copy()

    def reset_usage_stats(self):
        """Reset usage statistics"""
        self.usage_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0
        }


def test_claude_sonnet_client():
    """Test function for Claude Sonnet client"""
    import logging

    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    client = ClaudeSonnetClient(logger=logger)

    # Test with Genesis 14:20 (one of the problematic verses)
    hebrew_text = "וברוך אל עליון אשר־מגן צריך בידך ויתן־לו מעשר מכל"
    english_text = "And blessed be God Most High, Who has delivered your foes into your hand. And [Abram] gave him a tenth of everything."

    result, error, metadata = client.analyze_figurative_language_flexible(
        hebrew_text, english_text, "Genesis", 14
    )

    print(f"Error: {error}")
    print(f"Instances found: {len(metadata['flexible_instances'])}")
    print(f"Deliberation: {metadata['figurative_detection_deliberation'][:200]}...")
    print(f"Usage stats: {client.get_usage_stats()}")


if __name__ == "__main__":
    test_claude_sonnet_client()