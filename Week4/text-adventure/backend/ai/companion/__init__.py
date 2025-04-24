"""
Text Adventure - Companion AI Module

This module implements the companion dog AI that assists the player
with Japanese language learning and navigation through the railway station.
"""

__version__ = "0.1.0"

import logging

# Create a logger
logger = logging.getLogger(__name__)

# Import core components for easier access
# These imports will be uncommented as we implement each component
from backend.ai.companion.core.request_handler import RequestHandler
from backend.ai.companion.core.intent_classifier import IntentClassifier
from backend.ai.companion.core.processor_framework import ProcessorFactory
from backend.ai.companion.core.response_formatter import ResponseFormatter
from backend.ai.companion.core.models import CompanionResponse, IntentCategory, ProcessingTier
from backend.ai.companion.core.player_history_manager import PlayerHistoryManager

# Initialize the player history manager (singleton)
player_history_manager = PlayerHistoryManager()

# Main function to process companion requests
async def process_companion_request(request_data, game_context=None):
    """
    Process a request to the companion AI.
    
    Args:
        request_data: Dictionary containing the request data
        game_context: Optional game context information
        
    Returns:
        Dictionary containing the companion's response
    """
    request_id = getattr(request_data, 'request_id', 'unknown')
    player_id = getattr(request_data.additional_params, 'player_id', None)
    
    logger.info(f"Processing companion request: {request_id}")
    logger.debug(f"Request data: player_input='{getattr(request_data, 'player_input', '')}', request_type='{getattr(request_data, 'request_type', '')}'")
    
    try:
        # Create the required components
        logger.debug(f"Creating companion AI components for request: {request_id}")
        intent_classifier = IntentClassifier()
        processor_factory = ProcessorFactory(player_history_manager=player_history_manager)
        response_formatter = ResponseFormatter()
        
        # Create a request handler with the components
        logger.debug(f"Creating request handler for request: {request_id}")
        handler = RequestHandler(
            intent_classifier=intent_classifier,
            processor_factory=processor_factory,
            response_formatter=response_formatter,
            player_history_manager=player_history_manager
        )
        
        # Add player history to request if player_id is available but history isn't already in additional_params
        if player_id and 'player_history' not in request_data.additional_params:
            player_history = player_history_manager.get_player_history(player_id)
            request_data.additional_params['player_history'] = player_history
            logger.debug(f"Added {len(player_history)} player history entries to request: {request_id}")
        
        # Process the request to get the response text
        logger.debug(f"Handling request with request handler: {request_id}")
        response_text = await handler.handle_request(request_data, game_context)
        logger.debug(f"Received response text from handler (length: {len(response_text)}): {request_id}")
        
        # Get the intent and tier from the classifier
        logger.debug(f"Classifying request: {request_id}")
        intent, complexity, tier, confidence, entities = intent_classifier.classify(request_data)
        logger.debug(f"Request classified as intent={intent.name}, complexity={complexity.name}, tier={tier.name}, confidence={confidence}: {request_id}")
        
        # Create a CompanionResponse object
        logger.debug(f"Creating CompanionResponse object: {request_id}")
        response = CompanionResponse(
            request_id=request_data.request_id,
            response_text=response_text,
            intent=intent,
            processing_tier=tier,
            suggested_actions=["How do I buy a ticket?", "What is 'platform' in Japanese?"],
            learning_cues={
                "japanese_text": entities.get("word", ""),
                "pronunciation": entities.get("pronunciation", ""),
                "learning_moments": [intent.value],
                "vocabulary_unlocked": [entities.get("word", "")]
            },
            emotion="helpful",
            confidence=confidence,
            debug_info={
                "complexity": complexity.value,
                "tier": tier.value,
                "entities": entities
            }
        )
        
        # Store the interaction in player history if not already done by a processor
        if player_id:
            player_history_manager.add_interaction(
                player_id=player_id,
                user_query=request_data.player_input,
                assistant_response=response_text,
                session_id=request_data.additional_params.get('session_id'),
                metadata={
                    "processing_tier": tier.value,
                    "intent": intent.value,
                    "complexity": complexity.value
                }
            )
            logger.debug(f"Added interaction to player history for {player_id}: {request_id}")
        
        logger.info(f"Successfully processed companion request: {request_id}")
        return response
    except Exception as e:
        logger.error(f"Error processing companion request: {str(e)}", exc_info=True)
        raise 