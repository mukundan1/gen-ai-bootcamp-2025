"""
Scenario detection module for Tier 3 processing.

This module provides functionality to detect specific scenarios in player requests
and route them to the appropriate specialized handlers.
"""

import enum
import logging
from typing import Dict, Any, Optional, List, Callable
import asyncio

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    CompanionResponse,
    IntentCategory
)
from backend.ai.companion.tier3.context_manager import ContextManager
from backend.ai.companion.tier3.bedrock_client import BedrockClient
from backend.ai.companion.tier3.specialized_handlers import (
    TicketPurchaseHandler,
    NavigationHandler,
    VocabularyHelpHandler,
    GrammarExplanationHandler,
    CulturalInformationHandler
)

# Set up logging
logger = logging.getLogger(__name__)


class ScenarioType(enum.Enum):
    """Enum representing different types of scenarios that can be detected."""
    
    TICKET_PURCHASE = "ticket_purchase"
    NAVIGATION = "navigation"
    VOCABULARY_HELP = "vocabulary_help"
    GRAMMAR_EXPLANATION = "grammar_explanation"
    CULTURAL_INFORMATION = "cultural_information"
    UNKNOWN = "unknown"


class ScenarioDetector:
    """
    Detects specific scenarios in player requests and routes them to specialized handlers.
    
    This class analyzes the intent, entities, and context of a request to determine
    if it matches a known scenario pattern. If a match is found, it routes the request
    to a specialized handler for that scenario.
    """
    
    def __init__(self):
        """Initialize the ScenarioDetector with handlers for each scenario type."""
        self._handlers = {
            ScenarioType.TICKET_PURCHASE: TicketPurchaseHandler(),
            ScenarioType.NAVIGATION: NavigationHandler(),
            ScenarioType.VOCABULARY_HELP: VocabularyHelpHandler(),
            ScenarioType.GRAMMAR_EXPLANATION: GrammarExplanationHandler(),
            ScenarioType.CULTURAL_INFORMATION: CulturalInformationHandler()
        }
        
        # Define scenario detection rules
        self._detection_rules = {
            ScenarioType.TICKET_PURCHASE: self._is_ticket_purchase_scenario,
            ScenarioType.NAVIGATION: self._is_navigation_scenario,
            ScenarioType.VOCABULARY_HELP: self._is_vocabulary_help_scenario,
            ScenarioType.GRAMMAR_EXPLANATION: self._is_grammar_explanation_scenario,
            ScenarioType.CULTURAL_INFORMATION: self._is_cultural_information_scenario
        }
    
    def detect_scenario(self, request: ClassifiedRequest) -> ScenarioType:
        """
        Detect the scenario type based on the classified request.
        
        Args:
            request: The classified request to analyze.
            
        Returns:
            The detected scenario type.
        """
        logger.debug(f"Detecting scenario for request: {request.request_id}")
        
        # Check each scenario type in priority order
        for scenario_type, detection_rule in self._detection_rules.items():
            if detection_rule(request):
                logger.info(f"Detected scenario: {scenario_type.value} for request: {request.request_id}")
                return scenario_type
        
        # If no scenario matches, return UNKNOWN
        logger.info(f"No specific scenario detected for request: {request.request_id}")
        return ScenarioType.UNKNOWN
    
    def get_scenario_handler(self, scenario_type: ScenarioType):
        """
        Get the handler for a specific scenario type.
        
        Args:
            scenario_type: The type of scenario to get a handler for.
            
        Returns:
            The handler for the specified scenario type, or None if no handler exists.
        """
        return self._handlers.get(scenario_type)
    
    async def handle_scenario(
        self,
        request: ClassifiedRequest,
        context_manager: ContextManager,
        bedrock_client: BedrockClient
    ) -> str:
        """
        Handle a request using the appropriate scenario handler.
        
        Args:
            request: The classified request to handle.
            context_manager: The context manager to use for retrieving and updating context.
            bedrock_client: The Bedrock client to use for generating responses.
            
        Returns:
            The response text from the handler.
        """
        # Detect the scenario
        scenario_type = self.detect_scenario(request)
        
        # Get the handler for the scenario
        handler = self.get_scenario_handler(scenario_type)
        
        if handler is None:
            logger.warning(f"No handler available for scenario: {scenario_type.value}")
            # Fall back to a generic response
            if asyncio.iscoroutinefunction(bedrock_client.generate_text):
                return await bedrock_client.generate_text(
                    prompt=f"The player asked: '{request.player_input}'. Provide a helpful response.",
                    max_tokens=300
                )
            else:
                return bedrock_client.generate_text(
                    prompt=f"The player asked: '{request.player_input}'. Provide a helpful response.",
                    max_tokens=300
                )
        
        # Get the conversation context
        context = context_manager.get_context(request.additional_params.get("conversation_id", ""))
        
        # Handle the scenario
        logger.info(f"Handling scenario: {scenario_type.value} with handler: {handler.__class__.__name__}")
        if asyncio.iscoroutinefunction(handler.handle):
            return await handler.handle(request, context, bedrock_client)
        else:
            return handler.handle(request, context, bedrock_client)
    
    # Scenario detection rules
    
    def _is_ticket_purchase_scenario(self, request: ClassifiedRequest) -> bool:
        """Check if the request is about purchasing a ticket."""
        # Check for ticket purchase keywords in the input
        ticket_keywords = ["ticket", "buy", "purchase", "fare", "kippu"]
        has_ticket_keyword = any(keyword in request.player_input.lower() for keyword in ticket_keywords)
        
        # Check for destination entity
        has_destination = "destination" in request.extracted_entities
        
        # Check intent
        is_transaction_intent = (
            request.intent == IntentCategory.GENERAL_HINT and
            has_ticket_keyword and
            has_destination
        )
        
        return is_transaction_intent
    
    def _is_navigation_scenario(self, request: ClassifiedRequest) -> bool:
        """Check if the request is about navigation or directions."""
        # Check for navigation keywords
        navigation_keywords = ["where", "how to get", "find", "platform", "exit", "entrance", "direction"]
        has_navigation_keyword = any(keyword in request.player_input.lower() for keyword in navigation_keywords)
        
        # Check for location entity
        has_location = "location" in request.extracted_entities
        
        # Check intent
        is_navigation_intent = (
            request.intent == IntentCategory.DIRECTION_GUIDANCE or
            (has_navigation_keyword and has_location)
        )
        
        return is_navigation_intent
    
    def _is_vocabulary_help_scenario(self, request: ClassifiedRequest) -> bool:
        """Check if the request is about vocabulary help."""
        # Check intent
        is_vocabulary_intent = request.intent == IntentCategory.VOCABULARY_HELP
        
        # Check for word entity
        has_word = "word" in request.extracted_entities
        
        # Check for vocabulary keywords
        vocabulary_keywords = ["mean", "translate", "what is", "what does", "definition"]
        has_vocabulary_keyword = any(keyword in request.player_input.lower() for keyword in vocabulary_keywords)
        
        return is_vocabulary_intent or (has_vocabulary_keyword and has_word)
    
    def _is_grammar_explanation_scenario(self, request: ClassifiedRequest) -> bool:
        """Check if the request is about grammar explanation."""
        # Check intent
        is_grammar_intent = request.intent == IntentCategory.GRAMMAR_EXPLANATION
        
        # Check for grammar point entity
        has_grammar_point = "grammar_point" in request.extracted_entities
        
        # Check for grammar keywords
        grammar_keywords = ["grammar", "structure", "conjugate", "form", "particle", "difference between"]
        has_grammar_keyword = any(keyword in request.player_input.lower() for keyword in grammar_keywords)
        
        return is_grammar_intent or (has_grammar_keyword and has_grammar_point)
    
    def _is_cultural_information_scenario(self, request: ClassifiedRequest) -> bool:
        """Check if the request is about cultural information."""
        # Check for cultural keywords
        cultural_keywords = ["culture", "custom", "tradition", "etiquette", "polite", "proper", "typical"]
        has_cultural_keyword = any(keyword in request.player_input.lower() for keyword in cultural_keywords)
        
        # Check for topic entity
        has_topic = "topic" in request.extracted_entities
        
        # For cultural information, we rely more on keywords than intent
        return has_cultural_keyword and has_topic 