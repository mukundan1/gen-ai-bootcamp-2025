"""
Prompt optimization utilities for Amazon Bedrock.

This module provides utilities for optimizing prompts sent to Amazon Bedrock,
including token counting, prompt compression, and context management.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Any

from backend.ai.companion.core.models import CompanionRequest

# Set up logging
logger = logging.getLogger(__name__)

# Token estimation constants
AVG_CHARS_PER_TOKEN = 4  # Approximate average characters per token

class PromptOptimizer:
    """
    Utility class for optimizing prompts to minimize token usage.
    """
    
    def __init__(self, max_prompt_tokens: int = 800):
        """
        Initialize the prompt optimizer.
        
        Args:
            max_prompt_tokens: Maximum number of tokens to allow in a prompt
        """
        self.max_prompt_tokens = max_prompt_tokens
        self.logger = logging.getLogger(__name__)
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in a text string.
        
        This is a simple estimation based on character count.
        For production use, consider using a more accurate tokenizer.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        # Simple estimation based on character count
        return max(1, len(text) // AVG_CHARS_PER_TOKEN)
    
    def optimize_prompt(self, request: CompanionRequest, system_prompt: str) -> str:
        """
        Optimize a prompt for token efficiency.
        
        Args:
            request: The companion request
            system_prompt: The system prompt to use
            
        Returns:
            An optimized prompt
        """
        # Get the player input
        player_input = request.player_input
        
        # Estimate tokens
        system_tokens = self.estimate_tokens(system_prompt)
        input_tokens = self.estimate_tokens(player_input)
        
        self.logger.debug(f"Estimated tokens - System: {system_tokens}, Input: {input_tokens}")
        
        # If we're under the limit, use the full prompt
        if system_tokens + input_tokens <= self.max_prompt_tokens:
            return self._create_full_prompt(system_prompt, player_input)
        
        # Otherwise, we need to compress the prompt
        return self._create_compressed_prompt(system_prompt, player_input)
    
    def _create_full_prompt(self, system_prompt: str, player_input: str) -> str:
        """
        Create a full prompt with system instructions and player input.
        
        Args:
            system_prompt: The system prompt
            player_input: The player's input
            
        Returns:
            A formatted prompt
        """
        return f"{system_prompt} The player has asked: \"{player_input}\""
    
    def _create_compressed_prompt(self, system_prompt: str, player_input: str) -> str:
        """
        Create a compressed prompt when token count is a concern.
        
        Args:
            system_prompt: The system prompt
            player_input: The player's input
            
        Returns:
            A compressed prompt
        """
        # Compress the system prompt by removing unnecessary words
        compressed_system = self._compress_text(system_prompt)
        
        # If still too long, truncate the system prompt
        system_tokens = self.estimate_tokens(compressed_system)
        input_tokens = self.estimate_tokens(player_input)
        
        if system_tokens + input_tokens > self.max_prompt_tokens:
            # Prioritize the player input, allocate remaining tokens to system prompt
            available_system_tokens = max(100, self.max_prompt_tokens - input_tokens)
            compressed_system = self._truncate_to_tokens(compressed_system, available_system_tokens)
        
        return f"{compressed_system} Query: \"{player_input}\""
    
    def _compress_text(self, text: str) -> str:
        """
        Compress text by removing unnecessary words and characters.
        
        Args:
            text: The text to compress
            
        Returns:
            Compressed text
        """
        # Remove redundant spaces
        compressed = re.sub(r'\s+', ' ', text).strip()
        
        # Remove filler words
        filler_words = [
            r'\bvery\b', r'\breally\b', r'\bquite\b', r'\bjust\b', 
            r'\bsimply\b', r'\bbasically\b', r'\bactually\b'
        ]
        for word in filler_words:
            compressed = re.sub(word, '', compressed)
        
        # Simplify common phrases
        replacements = {
            'in order to': 'to',
            'due to the fact that': 'because',
            'for the purpose of': 'for',
            'in the event that': 'if',
            'in the process of': 'while',
            'a large number of': 'many',
            'a majority of': 'most',
            'a significant number of': 'many'
        }
        
        for phrase, replacement in replacements.items():
            compressed = compressed.replace(phrase, replacement)
        
        return compressed
    
    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """
        Truncate text to fit within a token limit.
        
        Args:
            text: The text to truncate
            max_tokens: Maximum number of tokens
            
        Returns:
            Truncated text
        """
        # Simple truncation based on character count
        max_chars = max_tokens * AVG_CHARS_PER_TOKEN
        
        if len(text) <= max_chars:
            return text
        
        # Try to truncate at a sentence boundary
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = ""
        
        for sentence in sentences:
            if self.estimate_tokens(result + sentence + " ") <= max_tokens:
                result += sentence + " "
            else:
                break
        
        # If we couldn't fit even one sentence, truncate mid-sentence
        if not result:
            result = text[:max_chars]
            
        return result.strip()


# System prompts for different complexity levels
SYSTEM_PROMPTS = {
    "low": "You are a helpful bilingual dog companion in a Japanese railway station. Provide simple language help.",
    "medium": "You are a helpful bilingual dog companion in a Japanese railway station. Assist with language help, directions, and basic cultural information.",
    "high": "You are a helpful bilingual dog companion in a Japanese railway station. Your role is to assist the player with language help, directions, and cultural information. Provide detailed explanations when appropriate."
}

def get_system_prompt(request: CompanionRequest) -> str:
    """
    Get an appropriate system prompt based on the request complexity.
    
    Args:
        request: The companion request
        
    Returns:
        A system prompt
    """
    # Get complexity from request parameters
    complexity = request.additional_params.get("complexity", "medium")
    
    # Default to medium if not a valid complexity
    if complexity not in SYSTEM_PROMPTS:
        complexity = "medium"
    
    return SYSTEM_PROMPTS[complexity]


def create_optimized_prompt(request: CompanionRequest, max_tokens: int = 800) -> str:
    """
    Create an optimized prompt for the given request.
    
    Args:
        request: The companion request
        max_tokens: Maximum tokens for the prompt
        
    Returns:
        An optimized prompt
    """
    # Get the appropriate system prompt
    system_prompt = get_system_prompt(request)
    
    # Create an optimizer and optimize the prompt
    optimizer = PromptOptimizer(max_prompt_tokens=max_tokens)
    
    return optimizer.optimize_prompt(request, system_prompt) 