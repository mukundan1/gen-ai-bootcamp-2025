"""
API routers package.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.api.routers.companion import router as companion_router
from backend.api.routers.dialogue import router as dialogue_router
from backend.api.routers.player import router as player_router
from backend.api.routers.game_state import router as game_state_router
from backend.api.routers.npc import router as npc_router
from backend.api.routers.npc_dialogue import router as npc_dialogue_router
from backend.api.routers.deepseek_parameters import router as deepseek_parameters_router

# Create the main API router
api_router = APIRouter(
    prefix="/api",
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)

# Include the routers
api_router.include_router(companion_router)
api_router.include_router(dialogue_router)
api_router.include_router(player_router)
api_router.include_router(game_state_router)
api_router.include_router(npc_router)
api_router.include_router(npc_dialogue_router)
api_router.include_router(deepseek_parameters_router)

# Add a root endpoint
@api_router.get("/")
async def api_root():
    """
    Root endpoint for the API.
    
    Returns:
        Basic API information
    """
    return {
        "name": "Text Adventure API",
        "version": "0.1.0",
        "description": "API for the Text Adventure game"
    } 