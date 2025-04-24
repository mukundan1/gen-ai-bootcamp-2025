"""
Router for player-related endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Path

from backend.api.adapters.base import AdapterFactory
from backend.api.adapters.player_progress import InvalidPlayerIdError, PlayerNotFoundError
from backend.api.models.player_progress import PlayerProgressResponse
from backend.data.player_progress import player_progress_service

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/player",
    tags=["player"],
    responses={
        404: {
            "description": "Not found",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "message": "Player with ID player123 not found",
                        "details": None
                    }
                }
            }
        },
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Bad Request",
                        "message": "Invalid player ID format",
                        "details": None
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "error": "Internal Server Error",
                        "message": "An unexpected error occurred while retrieving player progress",
                        "details": None
                    }
                }
            }
        }
    }
)


@router.get("/progress/{player_id}", response_model=PlayerProgressResponse)
async def get_player_progress(
    player_id: str = Path(..., description="Unique identifier for the player")
):
    """
    Get the player's Japanese language learning progress.
    
    Args:
        player_id: The unique identifier for the player
        
    Returns:
        The player's progress information
    """
    try:
        logger.info(f"Received request for player progress: player_id={player_id}")
        
        # Validate and transform the request
        request_adapter = AdapterFactory.get_request_adapter("player_progress")
        internal_request = request_adapter.adapt(player_id)
        
        # Retrieve player progress data
        player_progress_data = await player_progress_service.get_player_progress(internal_request)
        
        # Transform the response
        response_adapter = AdapterFactory.get_response_adapter("player_progress")
        api_response = response_adapter.adapt(player_progress_data)
        
        logger.info(f"Successfully processed player progress request for player_id={player_id}")
        
        return api_response
        
    except PlayerNotFoundError as e:
        logger.warning(f"Player not found: {str(e)}")
        raise HTTPException(
            status_code=404,
            detail={
                "error": "Not Found",
                "message": str(e),
                "details": None
            }
        )
    except InvalidPlayerIdError as e:
        logger.warning(f"Invalid player ID: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Bad Request",
                "message": str(e),
                "details": None
            }
        )
    except Exception as e:
        logger.error(f"Error retrieving player progress: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An unexpected error occurred while retrieving player progress",
                "details": None
            }
        ) 