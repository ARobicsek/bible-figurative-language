#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-model LLM API wrapper using UnifiedLLMClient

This module now delegates to the UnifiedLLMClient which provides:
- GPT-5.1 (Primary)
- Claude Opus 4.5 (Fallback 1)
- Gemini 3.0 Pro (Fallback 2)

Maintains backward compatibility with the original MultiModelGeminiClient interface.
"""
import os
import json
from typing import List, Dict, Optional, Tuple
from enum import Enum

# Import the new unified client
try:
    from .unified_llm_client import UnifiedLLMClient, TextContext
except ImportError:
    # Fallback for when running as main
    import sys
    sys.path.append(os.path.dirname(__file__))
    from unified_llm_client import UnifiedLLMClient, TextContext


# Keep these for backward compatibility
class FinishReason(Enum):
    SAFETY = 'SAFETY'
    RECITATION = 'RECITATION'
    OTHER = 'OTHER'


# Legacy constants - no longer used but kept for compatibility
PRIMARY_MODEL = 'gpt-5.1'  # Updated to reflect new primary model
FALLBACK_MODEL = 'claude-opus-4-5'


class MultiModelGeminiClient:
    """
    Multi-model LLM client wrapper

    This class now delegates to UnifiedLLMClient which uses:
    - GPT-5.1 (Primary)
    - Claude Opus 4.5 (Fallback 1)
    - Gemini 3.0 Pro (Fallback 2)
    """

    def __init__(self, api_key: str, validator=None, logger=None, db_manager=None):
        """
        Initialize multi-model LLM client

        Args:
            api_key: Legacy parameter (no longer used, kept for compatibility)
            validator: MetaphorValidator instance
            logger: Logger instance
            db_manager: DatabaseManager instance for logging
        """
        # Delegate to the new UnifiedLLMClient
        self.unified_client = UnifiedLLMClient(
            validator=validator,
            logger=logger,
            db_manager=db_manager
        )

        # Keep references for backward compatibility
        self.validator = validator
        self.logger = logger
        self.db_manager = db_manager

        # Legacy attributes for compatibility
        self.api_key = api_key
        self.primary_model_name = 'gpt-5.1'
        self.fallback_model_name = 'claude-opus-4-5'
        self.restriction_reasons = []

    def analyze_figurative_language(self, hebrew_text: str, english_text: str,
                                  book: str = "", chapter: int = 0) -> Tuple[str, Optional[str], Dict]:
        """
        Analyze Hebrew text for figurative language using multi-model approach

        Args:
            hebrew_text: Original Hebrew text
            english_text: English translation
            book: Book name for context-aware prompting
            chapter: Chapter number for context-aware prompting

        Returns:
            Tuple of (JSON string with analysis results, error message if restricted, metadata)
        """
        # Delegate to unified client
        return self.unified_client.analyze_figurative_language(hebrew_text, english_text, book, chapter)

    def insert_and_validate_instances(self, verse_id: int, all_instances: List[Dict],
                                     hebrew_text: str, english_text: str) -> int:
        """
        Insert all detected instances into database with validation data

        Delegates to unified client.
        """
        return self.unified_client.insert_and_validate_instances(
            verse_id, all_instances, hebrew_text, english_text
        )

    def get_usage_info(self) -> Dict:
        """Get comprehensive usage statistics (delegated to unified client)"""
        return self.unified_client.get_usage_info()

    def test_api_connection(self) -> Dict:
        """Test API connections (delegated to unified client)"""
        return self.unified_client.test_api_connections()

    # Legacy properties for backward compatibility
    @property
    def request_count(self) -> int:
        """Total request count"""
        return self.unified_client.request_count

    @property
    def primary_success_count(self) -> int:
        """Primary model success count (GPT-5.1)"""
        return self.unified_client.gpt_success_count

    @property
    def fallback_count(self) -> int:
        """Total fallback count"""
        return self.unified_client.gpt_fallback_count + self.unified_client.claude_fallback_count

    @property
    def server_error_fallback_count(self) -> int:
        """Server error fallback count (for backward compatibility)"""
        return 0  # No longer tracked separately

    @property
    def total_input_tokens(self) -> int:
        """Total input tokens across all models"""
        gpt = self.unified_client.gpt_tokens['input']
        claude = self.unified_client.claude_tokens['input']
        gemini = self.unified_client.gemini_tokens['input']
        return gpt + claude + gemini

    @property
    def total_output_tokens(self) -> int:
        """Total output tokens across all models"""
        gpt = self.unified_client.gpt_tokens['output']
        claude = self.unified_client.claude_tokens['output']
        gemini = self.unified_client.gemini_tokens['output']
        return gpt + claude + gemini

    # Legacy methods - kept as stubs for compatibility
    def _determine_text_context(self, book: str, chapter: int) -> str:
        """Legacy method - delegated to UnifiedLLMClient"""
        return self.unified_client._determine_text_context(book, chapter)

    def _create_context_aware_prompt(self, hebrew_text: str, english_text: str, context: str) -> str:
        """Legacy method - delegated to UnifiedLLMClient"""
        return self.unified_client._build_prompt(hebrew_text, english_text, context)

    def _is_restriction_error(self, error_msg: str) -> bool:
        """Legacy method - no longer used"""
        return 'restricted' in str(error_msg).lower()

    def _is_truncation_error(self, error_msg: str) -> bool:
        """Legacy method - no longer used"""
        return 'truncation' in str(error_msg).lower()

    def _is_server_error(self, error_msg: str) -> bool:
        """Legacy method - no longer used"""
        return '500' in str(error_msg) or 'server error' in str(error_msg).lower()

    def _is_restriction_reason(self, finish_reason) -> bool:
        """Legacy method - delegated to UnifiedLLMClient"""
        return self.unified_client._is_restriction_reason(finish_reason)

    def _clean_response(self, response_text: str, hebrew_text: str, english_text: str):
        """Legacy method - delegated to UnifiedLLMClient"""
        return self.unified_client._clean_response(response_text, hebrew_text, english_text)

    def _extract_json_array(self, response_text: str) -> str:
        """Legacy method - delegated to UnifiedLLMClient"""
        return self.unified_client._extract_json_array(response_text)


if __name__ == "__main__":
    # Test the multi-model system
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    # api_key parameter is legacy - no longer used
    client = MultiModelGeminiClient(api_key="", logger=logger)

    print("=== TESTING MULTI-MODEL LLM CLIENT (via wrapper) ===\n")

    # Test API connections
    print("Testing API connections...")
    connections = client.test_api_connection()
    for model, status in connections.items():
        if status['working']:
            print(f"✅ {model}: Connected")
        else:
            print(f"❌ {model}: Failed - {status.get('error', 'Unknown error')}")

    # Test Genesis 49 verse (should detect figurative language)
    print("\n--- Genesis 49:9 Test (should detect metaphor) ---")
    hebrew = "גּוּר אַרְיֵה יְהוּדָה מִטֶּרֶף בְּנִי עָלִיתָ כָּרַע רָבַץ כְּאַרְיֵה וּכְלָבִיא מִי יְקִימֶנּוּ"
    english = "Judah is a lion's whelp; On prey, my son, have you grown. He crouches, lies down like a lion, Like a lioness—who dare rouse him?"

    result, error, metadata = client.analyze_figurative_language(hebrew, english, "Genesis", 49)
    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    if error:
        print(f"Error: {error}")

    # Test Genesis 1:2 (should be conservative)
    print("\n--- Genesis 1:2 Test (should be literal) ---")
    hebrew = "וְהָאָרֶץ הָיְתָה תֹהוּ וָבֹהוּ וְחֹשֶׁךְ עַל־פְּנֵי תְהוֹם"
    english = "Now the earth was unformed and void, and darkness was over the surface of the deep"

    result, error, metadata = client.analyze_figurative_language(hebrew, english, "Genesis", 1)
    print(f"Result: {result}")
    print(f"Metadata: {metadata}")
    if error:
        print(f"Error: {error}")

    print(f"\n--- Usage Statistics ---")
    print(json.dumps(client.get_usage_info(), indent=2))
