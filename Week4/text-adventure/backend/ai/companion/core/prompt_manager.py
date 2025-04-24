"""
Text Adventure - Common Prompt Manager

This module provides a unified prompt management system that can be used by
both tier2 and tier3 processors, allowing for consistent prompting with
model-specific optimizations.
"""

import logging
import re
import json
from typing import Dict, Any, Optional, List

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    IntentCategory,
    ComplexityLevel
)

# Import the ConversationManager and ConversationState
from backend.ai.companion.core.conversation_manager import ConversationManager, ConversationState

# Import the PromptTemplateLoader
from backend.ai.companion.core.prompt.prompt_template_loader import PromptTemplateLoader

logger = logging.getLogger(__name__)


class PromptManager:
    """
    Creates and manages prompts for different LLM tiers.
    
    This class provides methods for creating prompts that are tailored to the
    specific needs of the request, including the intent, complexity, and
    extracted entities, while allowing for tier-specific optimizations.
    """
    
    def __init__(
        self, 
        tier_specific_config: Optional[Dict[str, Any]] = None,
        conversation_manager: Optional[ConversationManager] = None,
        vector_store: Optional[Any] = None,
        tokyo_knowledge_base_path: Optional[str] = None,
        profile_registry: Optional[Any] = None,
        prompt_templates_directory: Optional[str] = None
    ):
        """
        Initialize the prompt manager.
        
        Args:
            tier_specific_config: Optional configuration specific to the tier
                This can include:
                - optimize_prompt: Whether to optimize the prompt for token efficiency
                - max_prompt_tokens: Maximum tokens for the prompt
                - format_for_model: Specific formatting for the model (e.g., "bedrock", "ollama")
                - additional_instructions: Any additional instructions to add to the prompt
            conversation_manager: Optional conversation manager for handling conversation history
            vector_store: Optional vector store for game world context
            tokyo_knowledge_base_path: Optional path to tokyo-train-knowledge-base.json
            profile_registry: Optional registry for NPC personality profiles
            prompt_templates_directory: Optional path to directory containing prompt templates
        """
        self.tier_specific_config = tier_specific_config or {}
        self.conversation_manager = conversation_manager
        self.profile_registry = profile_registry
        
        # Initialize template loader if directory provided
        self.prompt_templates = None
        if prompt_templates_directory:
            self.prompt_templates = PromptTemplateLoader(prompt_templates_directory)
            logger.debug(f"Initialized prompt template loader from: {prompt_templates_directory}")
        
        # Initialize vector store either from provided one or from knowledge base file
        self.vector_store = None
        if vector_store:
            self.vector_store = vector_store
            logger.debug("Using provided vector store")
        elif tokyo_knowledge_base_path:
            # Import here to avoid circular imports
            from backend.ai.companion.core.vector.tokyo_knowledge_store import TokyoKnowledgeStore
            self.vector_store = TokyoKnowledgeStore.from_file(tokyo_knowledge_base_path)
            logger.debug(f"Created vector store from file: {tokyo_knowledge_base_path}")
        
        logger.debug("Initialized PromptManager with config: %s", self.tier_specific_config)
    
    def create_prompt(self, request: ClassifiedRequest) -> str:
        """
        Create a prompt for a language model based on the request.
        
        Args:
            request: A classified request with intent and complexity
            
        Returns:
            A prompt string for the model
        """
        # Get the intent-specific prompt template
        intent_prompt = self._get_base_prompt(request.intent, request.profile_id)
        
        # Get NPC profile if available and add specific personality context
        profile_context = self._get_profile_context(request)
        
        # Get request context including the question/input
        request_context = self._get_request_context(request)
        
        # Get relevant world context from vector store if available
        world_context = self._get_relevant_world_context(request)
        
        # Get profile-specific response format if available
        response_format = self._get_response_format(request)
        
        # Get instructions for desired response
        response_instructions = self._get_response_instructions(request)
        
        # Apply tier-specific optimizations
        if self.tier_specific_config.get("optimize_prompt", False):
            intent_prompt = self._optimize_prompt_for_token_efficiency(intent_prompt)
        
        # Add tier-specific instructions if provided
        additional_instructions = self.tier_specific_config.get("additional_instructions", "")
        
        # Combine all the parts into a single prompt
        full_prompt = f"""
{intent_prompt}

{profile_context}

{world_context}

{request_context}

{response_format}

{response_instructions}

{additional_instructions}
"""
        
        # Trim whitespace and remove extra newlines
        full_prompt = "\n".join(line for line in full_prompt.split("\n") if line.strip())
        
        logger.debug("Generated prompt with length %d characters", len(full_prompt))
        return full_prompt
    
    def _get_response_format(self, request: ClassifiedRequest) -> str:
        """
        Get a response format for the request based on the NPC profile.
        
        Args:
            request: The classified request
            
        Returns:
            A string with response format guidelines, or empty string
        """
        if not self.profile_registry:
            return ""
        
        profile = self.profile_registry.get_profile(request.profile_id)
        if not profile:
            return ""
        
        # Get format from profile
        format_text = profile.get_response_format(request.intent)
        if format_text:
            return f"RESPONSE FORMAT GUIDELINES:\n{format_text}"
        
        return ""
    
    def _get_relevant_world_context(self, request: ClassifiedRequest) -> str:
        """
        Get relevant world context from vector store based on the request.
        
        Args:
            request: The classified request
            
        Returns:
            A string with relevant world context, or empty string if none is found
        """
        if not self.vector_store:
            return ""
        
        try:
            # Search the vector store with the entire request object
            results = self.vector_store.contextual_search(
                request,
                top_k=3
            )
            
            if not results:
                return ""
            
            # Format the results
            context_parts = ["Relevant Game World Information:"]
            
            for idx, result in enumerate(results):
                text = result.get("document", result.get("text", ""))
                metadata = result.get("metadata", {})
                context_type = metadata.get("type", "Information")
                
                # Only add non-empty results
                if text.strip():
                    context_parts.append(f"[{context_type}] {text}")
            
            # Combine the parts
            if len(context_parts) > 1:  # If we have any actual results beyond the header
                return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error getting world context: {e}")
        
        return ""
    
    def _get_profile_context(self, request: ClassifiedRequest) -> str:
        """
        Get the NPC profile context for the prompt.
        
        Args:
            request: The classified request that may contain a profile_id
            
        Returns:
            A string with the profile context for the prompt
        """
        if not self.profile_registry:
            # If no profile registry is available, return a default companion context
            return """
You are Hachiko, a helpful and enthusiastic companion dog at Railway Station 
who assists travelers with Japanese language and navigation.

Text Adventure is a language learning game where you help players practice Japanese.
"""
        
        # Get the profile from the registry
        profile = self.profile_registry.get_profile(request.profile_id)
        if not profile:
            logger.warning(f"Profile not found for ID: {request.profile_id}, using default")
        
        # Get profile-specific prompt additions
        return profile.get_system_prompt_additions()
    
    def _get_base_prompt(self, intent: IntentCategory, profile_id: Optional[str] = None) -> str:
        """
        Get the base prompt for a given intent.
        
        Args:
            intent: The intent category
            profile_id: Optional profile ID to get profile-specific prompts
            
        Returns:
            A string with the base prompt for the intent
        """
        # If prompt templates are available, use them
        if self.prompt_templates:
            # Configure the template based on the profile type
            if profile_id == "companion_dog":
                self.prompt_templates.set_active_template("language_instructor_prompts")
            else:
                self.prompt_templates.set_active_template("default_prompts")
                
            prompt = self.prompt_templates.get_intent_prompt(intent, profile_id)
            if prompt:
                return prompt
        
        # Fallback to hard-coded prompts if templates not available or empty
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
    
    def _get_request_context(self, request: ClassifiedRequest) -> str:
        """
        Get the request context for the prompt.
        
        Args:
            request: The classified request
            
        Returns:
            A string with the request context
        """
        context = f"The player has asked: \"{request.player_input}\"\n\nThis is a {request.request_type} request with intent: {request.intent.value}."
        
        # Add extracted entities if any
        if request.extracted_entities:
            context += "\n\nExtracted entities:"
            for key, value in request.extracted_entities.items():
                context += f"\n- {key}: {value}"
                
        # Add game context if available
        if hasattr(request, 'game_context') and request.game_context:
            context += "\n\nGame Context:"
            
            # Handle special formatting for nested dictionaries
            for key, value in request.game_context.__dict__.items():
                if value:
                    # Special case for language_proficiency which is a dictionary
                    if key == 'language_proficiency' and isinstance(value, dict):
                        for lang, level in value.items():
                            context += f"\n- {lang}: {level}"
                    # Handle lists
                    elif isinstance(value, list):
                        context += f"\n- {key}: {value}"
                    # Handle other types
                    else:
                        context += f"\n- {key}: {value}"
                    
        # Add complexity information
        if hasattr(request, 'complexity') and request.complexity:
            complexity_str = request.complexity.value if hasattr(request.complexity, 'value') else str(request.complexity)
            context += f"\n\nRequest complexity: {complexity_str}"
                    
        return context
    
    def _get_response_instructions(self, request: ClassifiedRequest) -> str:
        """
        Get the response instructions for the prompt.
        
        Args:
            request: The classified request
            
        Returns:
            A string with the response instructions
        """
        # Basic instructions
        instructions = """Please be helpful, concise, and accurate when responding to the player.

STRICT TOPIC BOUNDARIES:
1. ONLY respond to questions about Japanese language
2. ONLY respond to questions about train station navigation
3. ONLY respond to questions about basic cultural aspects
4. ONLY respond to questions about how to play the game
5. If asked about ANY other topic, politely redirect

REDIRECTION EXAMPLES:
- "I'm just a station dog focused on helping you learn Japanese and navigate Tokyo Station."
- "I focus on helping you navigate the station and practice Japanese. Let's talk about that instead!"

REMEMBER:
1. Keep response under 3 sentences
2. Use only JLPT N5 level Japanese
3. Write Japanese in hiragana only
4. Include pronunciation guide
5. Focus on practical station use
6. One new concept per response
7. ONLY respond to game-relevant topics (Japanese language, station navigation, game mechanics)
8. Politely redirect ANY off-topic questions to game-relevant topics
"""
        
        return instructions
    
    def _optimize_prompt_for_token_efficiency(self, prompt: str) -> str:
        """
        Optimize the prompt for token efficiency.
        
        Args:
            prompt: The original prompt
            
        Returns:
            An optimized prompt
        """
        max_tokens = self.tier_specific_config.get('max_prompt_tokens', 800)
        
        # Estimate tokens (simple character-based estimation)
        avg_chars_per_token = 4
        estimated_tokens = max(1, len(prompt) // avg_chars_per_token)
        
        # If we're under the limit, return the original prompt
        if estimated_tokens <= max_tokens:
            return prompt
        
        # Otherwise, compress the prompt
        # Remove redundant spaces
        compressed = re.sub(r'\s+', ' ', prompt).strip()
        
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
        
        # If still too long, truncate less important parts
        estimated_tokens = max(1, len(compressed) // avg_chars_per_token)
        if estimated_tokens > max_tokens:
            # Prioritize the core instructions and player input
            # This is a simplified approach - a more sophisticated approach would
            # involve prioritizing different sections based on their importance
            max_chars = max_tokens * avg_chars_per_token
            compressed = compressed[:max_chars]
        
        return compressed

    async def create_contextual_prompt(self, request: ClassifiedRequest, conversation_id=None) -> str:
        """
        Create a prompt that includes conversation history context.
        
        Args:
            request: The classified request
            conversation_id: Optional conversation ID to retrieve history
            
        Returns:
            A prompt with conversation history context
        """
        # Start with the base prompt
        prompt = self.create_prompt(request)
        
        # If no conversation manager or conversation ID, just return the base prompt
        if not self.conversation_manager or not conversation_id:
            return f"{prompt}\n\nCurrent request: {request.player_input}\n\nYour response:"
        
        try:
            # Get the conversation context
            context = await self.conversation_manager.get_or_create_context(conversation_id)
            conversation_history = context.get("entries", [])
            
            # Detect the conversation state
            state = self.conversation_manager.detect_conversation_state(request, conversation_history)
            
            # Generate a contextual prompt from the conversation manager
            contextual_format = await self.conversation_manager.generate_contextual_prompt(
                request,
                conversation_history,
                state,
                prompt
            )
            
            return contextual_format
            
        except Exception as e:
            logger.error(f"Error creating contextual prompt: {e}")
            # Fallback to the base prompt if something goes wrong
            return f"{prompt}\n\nCurrent request: {request.player_input}\n\nYour response:" 