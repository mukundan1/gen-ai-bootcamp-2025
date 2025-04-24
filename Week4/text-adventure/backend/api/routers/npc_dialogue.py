"""
Router for the NPC Dialogue API.
"""

import logging
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from backend.api.models.npc_dialogue import (
    NPCDialogueRequest,
    NPCDialogueResponse,
    ErrorResponse
)
from backend.api.adapters.base import AdapterFactory
from backend.data.npc_dialogue import (
    process_dialogue,
    npc_exists,
    player_exists,
    is_supported_language
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/npc/dialogue",
    tags=["npc_dialogue"],
    responses={
        404: {"model": ErrorResponse, "description": "Not found"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)


@router.post(
    "",
    response_model=NPCDialogueResponse,
    responses={
        200: {"description": "Successful dialogue processing"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        404: {"model": ErrorResponse, "description": "NPC or player not found"},
        422: {"model": ErrorResponse, "description": "Unsupported language"}
    }
)
async def process_npc_dialogue(request: NPCDialogueRequest):
    """
    Process dialogue with an NPC.
    
    Args:
        request: The dialogue request.
        
    Returns:
        The NPC's response.
        
    Raises:
        HTTPException: If the NPC or player is not found, or if the language is not supported.
    """
    try:
        # Check if the NPC exists
        if not npc_exists(request.npcId):
            logger.warning(f"NPC with ID {request.npcId} not found")
            return JSONResponse(
                status_code=404,
                content={"error": "not_found", "message": f"NPC with ID {request.npcId} not found"}
            )
        
        # Check if the player exists
        if not player_exists(request.playerContext.playerId):
            logger.warning(f"Player with ID {request.playerContext.playerId} not found")
            return JSONResponse(
                status_code=404,
                content={"error": "not_found", "message": f"Player with ID {request.playerContext.playerId} not found"}
            )
        
        # Check if the language is supported
        if not is_supported_language(request.playerInput.language):
            logger.warning(f"Unsupported language: {request.playerInput.language}")
            return JSONResponse(
                status_code=422,
                content={"error": "unsupported_language", "message": f"Language '{request.playerInput.language}' is not supported"}
            )
        
        # Process the dialogue
        response_data, game_state_changes = process_dialogue(
            npc_id=request.npcId,
            player_context=request.playerContext.model_dump(),
            game_context=request.gameContext.model_dump(),
            player_input=request.playerInput.model_dump(),
            conversation_context=request.conversationContext.model_dump()
        )
        
        # Adapt the response
        adapter = AdapterFactory.get_response_adapter("npc_dialogue")
        response = adapter.adapt(response_data)
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing NPC dialogue: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_server_error", "message": "An unexpected error occurred"}
        ) 