"""
Router for companion-related endpoints.
"""

import logging
import uuid
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException

from backend.api.models.companion_assist import CompanionAssistRequest, CompanionAssistResponse
from backend.api.adapters.base import AdapterFactory
from backend.ai.companion.core.player_history_manager import PlayerHistoryManager

# Create a logger
logger = logging.getLogger(__name__)

# Create a router
router = APIRouter(
    prefix="/companion",
    tags=["companion"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Initialize the player history manager
player_history_manager = PlayerHistoryManager()


@router.post("/assist", response_model=CompanionAssistResponse)
async def companion_assist(request: CompanionAssistRequest):
    """
    Process a request for assistance from the companion dog (Hachi).
    
    Args:
        request: The companion assist request
        
    Returns:
        The companion's response
    """
    try:
        # Log the incoming request
        request_id = str(uuid.uuid4())
        logger.info(f"Received companion assist request for player {request.playerId} (request_id: {request_id})")
        logger.debug(f"Request details - type: {request.request.type}, text: {request.request.text}, location: {request.gameContext.location}")
        
        # Get the request adapter
        logger.debug(f"Getting request adapter for companion_assist (request_id: {request_id})")
        request_adapter = AdapterFactory.get_request_adapter("companion_assist")
        if not request_adapter:
            logger.error(f"Request adapter not found for companion_assist (request_id: {request_id})")
            raise HTTPException(status_code=500, detail="Request adapter not found")
        
        # Transform the request to internal format
        logger.debug(f"Adapting request to internal format (request_id: {request_id})")
        internal_request = request_adapter.adapt(request)
        
        # Add player history to the request's additional_params
        player_id = request.playerId
        player_history = player_history_manager.get_player_history(player_id)
        internal_request.additional_params["player_history"] = player_history
        internal_request.additional_params["player_id"] = player_id
        internal_request.additional_params["session_id"] = request.sessionId
        
        # If conversationId is provided, add it to additional_params
        if hasattr(request, 'conversationId') and request.conversationId:
            internal_request.additional_params["conversation_id"] = request.conversationId
            
        logger.debug(f"Internal request created with ID: {internal_request.request_id}")
        
        # Process the request
        try:
            # Try to import and use the actual process_companion_request function
            logger.debug(f"Attempting to process request with companion AI (request_id: {request_id})")
            from backend.ai.companion import process_companion_request
            internal_response = await process_companion_request(internal_request)
            logger.debug(f"Successfully processed request with companion AI (request_id: {request_id})")
            
            # Store the interaction in player history
            player_history_manager.add_interaction(
                player_id=player_id,
                user_query=request.request.text or "",
                assistant_response=internal_response.response_text,
                session_id=request.sessionId,
                metadata={
                    "location": request.gameContext.location,
                    "request_type": request.request.type,
                    "language": request.request.language if request.request.language else "english",
                    "processing_tier": internal_response.processing_tier
                }
            )
        except (ImportError, TypeError) as e:
            # If the function is not available or not properly implemented,
            # create a mock response for testing
            logger.warning(f"Using mock response for companion assist request due to error: {str(e)} (request_id: {request_id})")
            from backend.ai.companion.core.models import CompanionResponse, IntentCategory, ProcessingTier
            internal_response = CompanionResponse(
                request_id=internal_request.request_id,
                response_text=f"Woof! 切符 (kippu) means 'ticket' in Japanese. You'll need this word when buying your ticket to Odawara.",
                intent=IntentCategory.VOCABULARY_HELP,
                processing_tier=ProcessingTier.TIER_1,
                suggested_actions=["How do I buy a ticket?", "What is 'platform' in Japanese?"],
                learning_cues={
                    "japanese_text": "切符",
                    "pronunciation": "kippu",
                    "learning_moments": ["vocabulary_ticket"],
                    "vocabulary_unlocked": ["切符"]
                },
                emotion="helpful",
                confidence=0.9,
                debug_info={
                    "animation": "tail_wag",
                    "highlights": [
                        {
                            "id": "ticket_machine_1",
                            "effect": "pulse",
                            "duration": 3000
                        }
                    ]
                }
            )
            
            # Store the mock interaction in player history
            player_history_manager.add_interaction(
                player_id=player_id,
                user_query=request.request.text or "",
                assistant_response=internal_response.response_text,
                session_id=request.sessionId,
                metadata={
                    "location": request.gameContext.location,
                    "request_type": request.request.type,
                    "language": request.request.language if request.request.language else "english",
                    "processing_tier": "TIER_1",
                    "is_mock": True
                }
            )
        
        # Get the response adapter
        logger.debug(f"Getting response adapter for companion_assist (request_id: {request_id})")
        response_adapter = AdapterFactory.get_response_adapter("companion_assist")
        if not response_adapter:
            logger.error(f"Response adapter not found for companion_assist (request_id: {request_id})")
            raise HTTPException(status_code=500, detail="Response adapter not found")
        
        # Transform the response to API format
        logger.debug(f"Adapting internal response to API format (request_id: {request_id})")
        api_response = response_adapter.adapt(internal_response)
        
        # Log the response
        logger.info(f"Processed companion assist request for player {request.playerId} (request_id: {request_id})")
        logger.debug(f"Response details - dialogue length: {len(api_response.dialogue.text)}, processing tier: {api_response.meta.processingTier}")
        
        return api_response
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing companion assist request: {str(e)}", exc_info=True)
        
        # Raise an HTTP exception
        raise HTTPException(
            status_code=500,
            detail=f"Error processing companion assist request: {str(e)}"
        ) 