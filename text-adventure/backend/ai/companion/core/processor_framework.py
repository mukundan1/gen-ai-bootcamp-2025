"""
Text Adventure - Processor Framework

This module defines the abstract base class for processors and the factory
for creating processor instances.
"""

import abc
import logging
from typing import Dict, Any, Optional

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    ProcessingTier,
    IntentCategory
)

logger = logging.getLogger(__name__)


class Processor(abc.ABC):
    """
    Abstract base class for processors.
    
    A processor is responsible for generating a response to a classified request.
    Different processors use different techniques, from rule-based responses to
    local language models to cloud-based language models.
    """
    
    @abc.abstractmethod
    async def process(self, request: ClassifiedRequest) -> str:
        """
        Process a request and generate a response.
        
        Args:
            request: The classified request to process
            
        Returns:
            The generated response
        """
        pass


class Tier1Processor(Processor):
    """
    Tier 1 processor for the companion AI system.
    
    This processor uses rule-based techniques to generate responses to simple
    requests. It is the most limited but also the most reliable and fastest
    processor in the tiered processing framework.
    """
    
    def __init__(self):
        """Initialize the Tier 1 processor."""
        self.logger = logging.getLogger(__name__)
        self.decision_trees = {}
        self._load_default_trees()
        self.logger.debug("Initialized Tier1Processor")
    
    async def process(self, request: ClassifiedRequest) -> str:
        """
        Process a request using rule-based techniques.
        
        Args:
            request: The classified request to process
            
        Returns:
            The generated response
        """
        self.logger.info(f"Processing request {request.request_id} with Tier 1 processor")
        
        # Create a companion request from the classified request
        companion_request = self._create_companion_request(request)
        
        # Determine which decision tree to use based on the intent
        tree_name = self._get_tree_name_for_intent(request.intent)
        
        # Get the decision tree
        tree = self.decision_trees.get(tree_name)
        
        if not tree:
            self.logger.warning(f"No decision tree found for intent {request.intent.value}")
            return "I'm sorry, I don't know how to help with that."
        
        # Traverse the decision tree to generate a response
        response = self._traverse_tree(tree, companion_request)
        
        self.logger.info(f"Generated response for request {request.request_id}")
        return response
    
    def _get_tree_name_for_intent(self, intent: IntentCategory) -> str:
        """
        Get the name of the decision tree to use for a given intent.
        
        Args:
            intent: The intent of the request
            
        Returns:
            The name of the decision tree to use
        """
        # Map intents to decision tree names
        intent_to_tree = {
            IntentCategory.VOCABULARY_HELP: "vocabulary",
            IntentCategory.GRAMMAR_EXPLANATION: "grammar",
            IntentCategory.DIRECTION_GUIDANCE: "directions",
            IntentCategory.TRANSLATION_CONFIRMATION: "translation",
            IntentCategory.GENERAL_HINT: "general"
        }
        
        return intent_to_tree.get(intent, "general")
    
    def _traverse_tree(self, tree: Dict[str, Any], request: Any) -> str:
        """
        Traverse a decision tree to generate a response.
        
        Args:
            tree: The decision tree to traverse
            request: The companion request
            
        Returns:
            The generated response
        """
        # This is a simplified implementation
        # In a real system, this would be more complex
        return tree.get("default_response", "I'm sorry, I don't know how to help with that.")
    
    def _create_companion_request(self, request: ClassifiedRequest) -> Any:
        """
        Create a companion request from a classified request.
        
        Args:
            request: The classified request
            
        Returns:
            A companion request
        """
        # This is a simplified implementation
        # In a real system, this would create a proper companion request object
        return {
            "request_id": request.request_id,
            "player_input": request.player_input,
            "request_type": request.request_type,
            "intent": request.intent.value,
            "complexity": request.complexity.value,
            "extracted_entities": request.extracted_entities
        }
    
    def _load_default_trees(self):
        """Load the default decision trees."""
        # This is a simplified implementation
        # In a real system, this would load decision trees from files
        self.decision_trees = {
            "vocabulary": {
                "default_response": "That word means 'hello' in Japanese. In Japanese: こんにちは (konnichiwa)."
            },
            "grammar": {
                "default_response": "This grammar point is used to express a desire to do something. For example: 食べたい (tabetai) means 'I want to eat'."
            },
            "directions": {
                "default_response": "The ticket gate is straight ahead. In Japanese: きっぷうりば は まっすぐ です (kippu-uriba wa massugu desu)."
            },
            "translation": {
                "default_response": "Yes, that's correct! 'Thank you' in Japanese is ありがとう (arigatou)."
            },
            "general": {
                "default_response": "I'm Hachiko, your companion in Tokyo Train Station. How can I help you learn Japanese today?"
            }
        }
    
    def _create_prompt(self, request: ClassifiedRequest) -> str:
        """
        Create a prompt for the request.
        
        Args:
            request: The classified request
            
        Returns:
            A prompt string
        """
        # This is a simplified implementation
        # In a real system, this would create a more sophisticated prompt
        return f"Player asked: {request.player_input}\nIntent: {request.intent.value}\nComplexity: {request.complexity.value}"


class ProcessorFactory:
    """
    Factory for creating processors based on the processing tier.
    
    This class is responsible for creating and caching processors for different tiers.
    It ensures that only one instance of each processor type is created.
    """
    
    _instance = None
    _processors = {}
    _player_history_manager = None
    
    def __new__(cls, *args, **kwargs):
        """Create a singleton instance of the factory."""
        if cls._instance is None:
            cls._instance = super(ProcessorFactory, cls).__new__(cls)
            # Store the player history manager if provided
            if 'player_history_manager' in kwargs:
                cls._player_history_manager = kwargs['player_history_manager']
        return cls._instance
    
    def __init__(self, player_history_manager=None):
        """
        Initialize the factory.
        
        Args:
            player_history_manager: Optional player history manager to pass to processors
        """
        # Only set player_history_manager if it's not already set
        if player_history_manager and not self.__class__._player_history_manager:
            self.__class__._player_history_manager = player_history_manager
    
    @classmethod
    def clear_cache(cls):
        """Clear the processor cache. Used primarily for testing."""
        cls._processors = {}
    
    def get_processor(self, tier: ProcessingTier) -> Processor:
        """
        Get a processor for the specified tier.
        
        Args:
            tier: The processing tier
            
        Returns:
            A processor for the specified tier
            
        Raises:
            ValueError: If the tier is disabled in configuration or unknown
        """
        # If we already have a processor for this tier, return it
        if tier in self._processors:
            return self._processors[tier]
        
        # Import here to avoid circular imports
        from backend.ai.companion.config import get_config
        
        # Handle both string and ProcessingTier enum
        tier_value = tier.value if hasattr(tier, 'value') else tier
        
        # For string values, check if they're valid ProcessingTier values
        if isinstance(tier_value, str) and not any(tier_value == t.value for t in ProcessingTier):
            raise ValueError(f"Unknown processing tier: {tier}")
        
        # Map the tier value to the config section name
        # The config sections use 'tier1', 'tier2', 'tier3' format instead of 'tier_1', etc.
        config_section = tier_value.replace('_', '') if isinstance(tier_value, str) else tier_value
        
        # Check if the tier is enabled in configuration
        tier_config = get_config(config_section, {})
        
        logger.info(f"Tier {tier_value} config section '{config_section}': {tier_config}")
        
        # If tier config exists and enabled is explicitly False, raise an error
        if 'enabled' in tier_config and tier_config.get('enabled') is False:
            logger.warning(f"Tier {tier_value} is explicitly disabled in configuration, raising exception")
            raise ValueError(f"{tier} is disabled in configuration")
        
        # Create a new processor
        if tier == ProcessingTier.TIER_1:
            from backend.ai.companion.tier1.tier1_processor import Tier1Processor
            processor = Tier1Processor()
        elif tier == ProcessingTier.TIER_2:
            from backend.ai.companion.tier2.tier2_processor import Tier2Processor
            processor = Tier2Processor(player_history_manager=self.__class__._player_history_manager)
        elif tier == ProcessingTier.TIER_3:
            from backend.ai.companion.tier3.tier3_processor import Tier3Processor
            processor = Tier3Processor(player_history_manager=self.__class__._player_history_manager)
        elif tier == ProcessingTier.RULE:
            # Import the rule-based processor
            from backend.ai.companion.rule.rule_processor import RuleProcessor
            processor = RuleProcessor(player_history_manager=self.__class__._player_history_manager)
        else:
            raise ValueError(f"Unknown processing tier: {tier}")
        
        # Cache the processor
        self._processors[tier] = processor
        
        return processor 