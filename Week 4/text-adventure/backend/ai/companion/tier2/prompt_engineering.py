"""
Text Adventure - Prompt Engineering

This module provides functionality for creating effective prompts for local language models.
It includes templates and strategies for different types of requests and complexity levels.
"""

import json
import logging
from typing import Dict, Any, Optional

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    IntentCategory,
    ComplexityLevel
)

logger = logging.getLogger(__name__)


class PromptEngineering:
    """
    Creates effective prompts for local language models.
    
    This class provides methods for creating prompts that are tailored to the
    specific needs of the request, including the intent, complexity, and
    extracted entities.
    """
    
    def __init__(self):
        """Initialize the prompt engineering module."""
        logger.debug("Initialized PromptEngineering")
    
    def create_prompt(self, request: ClassifiedRequest) -> str:
        """
        Create a prompt for a language model based on the request.
        
        Args:
            request: The classified request
            
        Returns:
            A prompt string for the language model
        """
        # Start with the base prompt
        prompt = self._create_base_prompt(request)
        
        # Add context information if available
        if request.game_context:
            prompt += self._add_game_context(request)
        
        # Add intent-specific instructions
        prompt += self._add_intent_instructions(request)
        
        # Add complexity-specific instructions
        prompt += self._add_complexity_instructions(request)
        
        # Add request type-specific instructions
        prompt += self._add_request_type_instructions(request)
        
        # Add extracted entities
        if request.extracted_entities:
            prompt += self._add_extracted_entities(request)
        
        # Add final instructions
        prompt += self._add_final_instructions(request)
        
        logger.debug(f"Created prompt for request {request.request_id}")
        logger.debug(f"Full prompt:\n{prompt}")
        return prompt
    
    def _create_base_prompt(self, request: ClassifiedRequest) -> str:
        """
        Create a base prompt for the request.
        """
        # Standard intro
        prompt = f"""Please provide a concise response that addresses the player's question directly.
Format your response exactly as follows:

        CRITICAL RESPONSE CONSTRAINTS:
        1. Length: Keep responses under 3 sentences
        2. Language Level: Strictly JLPT N5 vocabulary and grammar only
        3. Format: Always include both Japanese and English
        4. Style: Simple, friendly, and encouraging
        
        JLPT N5 GUIDELINES:
        - Use only basic particles: は, が, を, に, で, へ
        - Basic verbs: います, あります, いきます, みます
        - Simple adjectives: いい, おおきい, ちいさい
        - Common nouns: でんしゃ, えき, きっぷ
        - Basic greetings: こんにちは, すみません
        
        GAME INTERACTION RULES:
        1. Focus on immediate, practical responses
        2. One new Japanese concept per response
        3. Always write Japanese in hiragana (no kanji)
        4. Include basic pronunciation hints
        5. Relate to station navigation or tickets
        
        RESPONSE STRUCTURE:
        1. English answer (1 sentence)
        2. Japanese phrase (with hiragana)
        3. Quick pronunciation guide
        
        Example Response:
        "The ticket gate is on your right. In Japanese: きっぷうりば は みぎ です。(kippu-uriba wa migi desu)"

        The player has asked: "{request.player_input}"

        This is a {request.request_type} request with intent: {request.intent.value}.
        
        Remember to be helpful and concise in your responses."""
    
    def _add_game_context(self, request: ClassifiedRequest) -> str:
        """Add game context information to the prompt."""
        context = request.game_context
        context_str = "Current game context:\n"
        
        if context.player_location:
            context_str += f"- Player location: {context.player_location}\n"
        
        if context.current_objective:
            context_str += f"- Current objective: {context.current_objective}\n"
        
        if context.nearby_npcs:
            context_str += f"- Nearby NPCs: {', '.join(context.nearby_npcs)}\n"
        
        if context.nearby_objects:
            context_str += f"- Nearby objects: {', '.join(context.nearby_objects)}\n"
        
        if context.player_inventory:
            context_str += f"- Player inventory: {', '.join(context.player_inventory)}\n"
        
        if context.language_proficiency:
            context_str += "- Language proficiency:\n"
            for lang, level in context.language_proficiency.items():
                context_str += f"  - {lang}: {level}\n"
        
        return context_str + "\n"
    
    def _add_intent_instructions(self, request: ClassifiedRequest) -> str:
        """Add intent-specific instructions to the prompt."""
        intent = request.intent
        
        if intent == IntentCategory.VOCABULARY_HELP:
            return """VOCABULARY RESPONSE FORMAT:
            - Explain the meaning of the word clearly
            - New word in hiragana
            - English meaning
            - Simple example sentence
            Example: "Ticket is きっぷ (kippu). You can say: きっぷ を ください (kippu wo kudasai) for 'ticket please.'"
            """
        elif intent == IntentCategory.GRAMMAR_EXPLANATION:
            return """GRAMMAR RESPONSE FORMAT:
            - One N5 grammar point
            - Simple example
            - Station context
            Example: "Use を (wo) for tickets. きっぷ を かいます (kippu wo kaimasu) means 'I buy a ticket.'"
            """
        elif intent == IntentCategory.TRANSLATION_CONFIRMATION:
            return """TRANSLATION RESPONSE FORMAT:
            - Simple English translation
            - Japanese in hiragana
            - Basic pronunciation guide
            Example: "Yes, that's right! 'Excuse me' is すみません (sumimasen)."
            """
        elif intent == IntentCategory.DIRECTION_GUIDANCE:
            return """NAVIGATION RESPONSE FORMAT:
            - Direction in English
            - Basic Japanese direction word
            - Simple station phrase
            Example: "Turn left at the gate. Left is ひだり (hidari). You can say: ひだり に いきます (hidari ni ikimasu)."
            """
        else:
            return """Please provide a simple, N5-level response that addresses the player's question directly.
            Include both English and Japanese (in hiragana) with pronunciation.
            """
    
    def _add_complexity_instructions(self, request: ClassifiedRequest) -> str:
        """Add complexity-specific instructions to the prompt."""
        complexity = request.complexity
        
        if complexity == ComplexityLevel.SIMPLE:
            return """SIMPLE RESPONSE GUIDELINES:
            - Use only basic JLPT N5 vocabulary
            - Keep sentences very short and direct
            - Focus on one concept at a time
            - Use common station-related words
            - Provide clear pronunciation guides
            """
        elif complexity == ComplexityLevel.COMPLEX:
            return """COMPLEX RESPONSE GUIDELINES:
            - Use more detailed JLPT N5 vocabulary
            - Include multiple related concepts
            - Provide additional context and examples
            - Connect to other station vocabulary
            - Add cultural notes when relevant
            """
        else:  # MODERATE
            return """MODERATE RESPONSE GUIDELINES:
            - Use standard JLPT N5 vocabulary
            - Balance detail with clarity
            - Include helpful context
            - Keep focus on practical usage
            - Ensure clear pronunciation
            """
    
    def _add_request_type_instructions(self, request: ClassifiedRequest) -> str:
        """Add request type-specific instructions to the prompt."""
        request_type = request.request_type
        
        if request_type == "translation":
            return """For this translation request:
- Provide the Japanese translation with both kanji/kana and romaji
- Ensure the translation is natural and appropriate for the context
- Note any cultural considerations for this phrase

"""
        elif request_type == "vocabulary":
            return """For this vocabulary request:
- Explain the meaning, usage, and provide example sentences
- Include the word in kanji, hiragana, and romaji
- Note any common collocations or expressions
- Mention any homophones or easily confused words

"""
        elif request_type == "grammar":
            return """For this grammar request:
- Explain the grammar point clearly with examples and usage notes
- Show how the grammar changes with different verb forms
- Provide common patterns and expressions
- Note any exceptions or special cases

"""
        elif request_type == "culture":
            return """For this cultural request:
- Provide accurate cultural information with historical context if relevant
- Explain modern practices and attitudes
- Note regional variations if applicable
- Connect to language usage where relevant

"""
        elif request_type == "directions":
            return """For this directions request:
- Provide clear, concise directions
- Use landmarks and station names
- Include useful phrases for asking for help
- Note any cultural etiquette for navigating or asking for directions

"""
        else:
            return ""
    
    def _add_extracted_entities(self, request: ClassifiedRequest) -> str:
        """Add extracted entities to the prompt."""
        entities = request.extracted_entities
        
        if not entities:
            return ""
        
        entities_str = "Extracted entities from the request:\n"
        
        for key, value in entities.items():
            entities_str += f"- {key}: {value}\n"
        
        return entities_str + "\n"
    
    def _add_final_instructions(self, request: ClassifiedRequest) -> str:
        """Add final instructions to the prompt."""
        return """REMEMBER:
        1. Keep response under 3 sentences
        2. Use only JLPT N5 level Japanese
        3. Write Japanese in hiragana only
        4. Include pronunciation guide
        5. Focus on practical station use
        6. One new concept per response
        """ 