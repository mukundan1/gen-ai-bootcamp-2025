"""
Text Adventure - Tier 2 Processor Module

This module contains the LLM-based processing components for the companion AI system.
It includes the Ollama client for interacting with local language models.
"""

from backend.ai.companion.tier2.ollama_client import OllamaClient
from backend.ai.companion.tier2.tier2_processor import Tier2Processor
from backend.ai.companion.tier2.prompt_engineering import PromptEngineering
from backend.ai.companion.tier2.response_parser import ResponseParser

__all__ = ['OllamaClient', 'Tier2Processor', 'PromptEngineering', 'ResponseParser'] 