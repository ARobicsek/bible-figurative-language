"""AI analysis module for figurative language detection"""
# Current production modules
from .gemini_api_multi_model import MultiModelGeminiClient
from .metaphor_validator import MetaphorValidator

__all__ = ['MultiModelGeminiClient', 'MetaphorValidator']