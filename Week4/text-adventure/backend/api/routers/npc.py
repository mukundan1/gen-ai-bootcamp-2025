"""
Router for NPC endpoints.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from typing import Optional

from backend.api.adapters.base import AdapterFactory
from backend.api.models.npc import (
    NPCInformationResponse,
    NPCConfigurationResponse,
    NPCInteractionStateResponse,
    UpdateNPCConfigurationRequest,
    ErrorResponse
)
from backend.data.npc import (
    get_npc_information,
    get_npc_configuration,
    get_npc_interaction_state,
    update_npc_configuration,
    InvalidNPCIdError,
    NPCNotFoundError,
    PlayerNotFoundError,
    InteractionStateNotFoundError
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/npc",
    tags=["npc"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.get(
    "/{npc_id}",
    response_model=NPCInformationResponse,
    summary="Get NPC information",
    description="Get information about a specific NPC"
)
async def get_npc(
    npc_id: str = Path(..., description="Unique identifier for the NPC")
) -> NPCInformationResponse:
    """
    Get information about an NPC.
    
    Args:
        npc_id: The ID of the NPC.
        
    Returns:
        Information about the NPC.
        
    Raises:
        HTTPException: If an error occurs while retrieving NPC information.
    """
    try:
        logger.info(f"Getting information for NPC {npc_id}")
        
        # Get NPC information
        result = get_npc_information(npc_id)
        
        # Get the response adapter
        response_adapter = AdapterFactory.get_response_adapter("npc_information")
        
        # Transform result to API format
        response_data = response_adapter.adapt(result)
        
        logger.info(f"Retrieved information for NPC {npc_id}")
        
        return NPCInformationResponse(**response_data)
        
    except InvalidNPCIdError as e:
        logger.error(f"Invalid NPC ID: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except NPCNotFoundError as e:
        logger.error(f"NPC not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving NPC information: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving NPC information"
        )


@router.get(
    "/config/{npc_id}",
    response_model=NPCConfigurationResponse,
    summary="Get NPC configuration",
    description="Get the configuration for a specific NPC"
)
async def get_config(
    npc_id: str = Path(..., description="Unique identifier for the NPC")
) -> NPCConfigurationResponse:
    """
    Get the configuration for an NPC.
    
    Args:
        npc_id: The ID of the NPC.
        
    Returns:
        The configuration for the NPC.
        
    Raises:
        HTTPException: If an error occurs while retrieving NPC configuration.
    """
    try:
        logger.info(f"Getting configuration for NPC {npc_id}")
        
        # Get NPC configuration
        result = get_npc_configuration(npc_id)
        
        # Get the response adapter
        response_adapter = AdapterFactory.get_response_adapter("npc_configuration")
        
        # Transform result to API format
        response_data = response_adapter.adapt(result)
        
        logger.info(f"Retrieved configuration for NPC {npc_id}")
        
        return NPCConfigurationResponse(**response_data)
        
    except InvalidNPCIdError as e:
        logger.error(f"Invalid NPC ID: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except NPCNotFoundError as e:
        logger.error(f"NPC configuration not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving NPC configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving NPC configuration"
        )


@router.put(
    "/config/{npc_id}",
    response_model=NPCConfigurationResponse,
    summary="Update NPC configuration",
    description="Update the configuration for a specific NPC",
    responses={
        200: {"description": "NPC configuration updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        422: {"description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def update_config(
    npc_id: str = Path(..., description="Unique identifier for the NPC"),
    config_request: UpdateNPCConfigurationRequest = None
) -> NPCConfigurationResponse:
    """
    Update the configuration for an NPC.
    
    Args:
        npc_id: The ID of the NPC.
        config_request: The updated configuration data.
        
    Returns:
        The updated configuration for the NPC.
        
    Raises:
        HTTPException: If an error occurs while updating NPC configuration.
    """
    try:
        logger.info(f"Updating configuration for NPC {npc_id}")
        
        # Get the request adapter
        request_adapter = AdapterFactory.get_request_adapter("npc_configuration_update")
        
        # Transform request to internal format
        internal_request = request_adapter.adapt(config_request.model_dump())
        
        # Update NPC configuration
        result = update_npc_configuration(npc_id, internal_request)
        
        # Get the response adapter
        response_adapter = AdapterFactory.get_response_adapter("npc_configuration")
        
        # Transform result to API format
        response_data = response_adapter.adapt(result)
        
        logger.info(f"Updated configuration for NPC {npc_id}")
        
        return NPCConfigurationResponse(**response_data)
        
    except InvalidNPCIdError as e:
        logger.error(f"Invalid NPC ID: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except NPCNotFoundError as e:
        logger.error(f"NPC configuration not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating NPC configuration: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while updating NPC configuration: {str(e)}"
        )


@router.get(
    "/state/{player_id}/{npc_id}",
    response_model=NPCInteractionStateResponse,
    summary="Get NPC interaction state",
    description="Get the interaction state between a player and a specific NPC"
)
async def get_interaction_state(
    player_id: str = Path(..., description="Unique identifier for the player"),
    npc_id: str = Path(..., description="Unique identifier for the NPC")
) -> NPCInteractionStateResponse:
    """
    Get the interaction state between a player and an NPC.
    
    Args:
        player_id: The ID of the player.
        npc_id: The ID of the NPC.
        
    Returns:
        The interaction state between the player and the NPC.
        
    Raises:
        HTTPException: If an error occurs while retrieving NPC interaction state.
    """
    try:
        logger.info(f"Getting interaction state for player {player_id} and NPC {npc_id}")
        
        # Get NPC interaction state
        result = get_npc_interaction_state(player_id, npc_id)
        
        # Get the response adapter
        response_adapter = AdapterFactory.get_response_adapter("npc_interaction_state")
        
        # Transform result to API format
        response_data = response_adapter.adapt(result)
        
        logger.info(f"Retrieved interaction state for player {player_id} and NPC {npc_id}")
        
        return NPCInteractionStateResponse(**response_data)
        
    except InvalidNPCIdError as e:
        logger.error(f"Invalid ID: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except PlayerNotFoundError as e:
        logger.error(f"Player not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except NPCNotFoundError as e:
        logger.error(f"NPC not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except InteractionStateNotFoundError as e:
        logger.error(f"Interaction state not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error retrieving NPC interaction state: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while retrieving NPC interaction state"
        ) 