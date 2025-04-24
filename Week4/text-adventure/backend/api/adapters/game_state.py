from datetime import datetime, UTC
import uuid
from typing import Dict, Any

from backend.api.adapters.base import RequestAdapter, ResponseAdapter
from backend.api.models.game_state import (
    SaveGameStateRequest,
    SaveGameStateResponse,
    LoadGameStateResponse,
    ListSavedGamesResponse,
    SaveMetadata
)


class GameStateSaveRequestAdapter(RequestAdapter):
    """Adapter for save game state requests."""

    def adapt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an external request to the internal format.
        
        Args:
            request_data: The external request to transform
            
        Returns:
            The transformed external response
        """
        return self.to_internal(request_data)

    def to_internal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request data to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal format data.
        """
        # Validate request data using Pydantic model
        validated_data = SaveGameStateRequest(**request_data)
        
        # Convert to internal format
        internal_data = {
            "player_id": validated_data.playerId,
            "session_id": validated_data.sessionId,
            "timestamp": validated_data.timestamp,
            "location": {
                "area": validated_data.location.area,
                "position": {
                    "x": validated_data.location.position.x,
                    "y": validated_data.location.position.y
                }
            },
            "quest_state": {
                "active_quest": validated_data.questState.activeQuest,
                "quest_step": validated_data.questState.questStep,
                "objectives": [
                    {
                        "id": obj.id,
                        "completed": obj.completed,
                        "description": obj.description
                    }
                    for obj in validated_data.questState.objectives
                ]
            },
            "inventory": validated_data.inventory,
            "game_flags": validated_data.gameFlags,
            "companions": {
                companion_id: {
                    "relationship": state.relationship,
                    "assistance_used": state.assistanceUsed
                }
                for companion_id, state in validated_data.companions.items()
            }
        }
        
        return internal_data


class GameStateLoadRequestAdapter(RequestAdapter):
    """Adapter for load game state requests."""

    def adapt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an external request to the internal format.
        
        Args:
            request_data: The external request to transform
            
        Returns:
            The transformed internal request
        """
        return self.to_internal(request_data)

    def to_internal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request data to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal format data.
        """
        # For load requests, we typically just need the player ID and save ID
        internal_data = {
            "player_id": request_data.get("playerId"),
            "save_id": request_data.get("saveId")
        }
        
        return internal_data


class GameStateListRequestAdapter(RequestAdapter):
    """Adapter for list saved games requests."""

    def adapt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an external request to the internal format.
        
        Args:
            request_data: The external request to transform
            
        Returns:
            The transformed internal request
        """
        return self.to_internal(request_data)

    def to_internal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request data to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal format data.
        """
        # For list requests, we typically just need the player ID
        internal_data = {
            "player_id": request_data.get("playerId")
        }
        
        return internal_data


class GameStateSaveResponseAdapter(ResponseAdapter):
    """Adapter for save game state responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an internal response to the external format.
        
        Args:
            internal_data: The internal response to transform
            
        Returns:
            The transformed external response
        """
        return self.to_api(internal_data)

    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API response format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        api_data = SaveGameStateResponse(
            success=internal_data.get("success", True),
            saveId=internal_data.get("save_id", str(uuid.uuid4())),
            timestamp=internal_data.get("timestamp", datetime.now(UTC))
        )
        
        return api_data.model_dump()


class GameStateLoadResponseAdapter(ResponseAdapter):
    """Adapter for load game state responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an internal response to the external format.
        
        Args:
            internal_data: The internal response to transform
            
        Returns:
            The transformed external response
        """
        return self.to_api(internal_data)

    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API response format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        api_data = LoadGameStateResponse(
            playerId=internal_data["player_id"],
            saveId=internal_data["save_id"],
            sessionId=internal_data["session_id"],
            timestamp=internal_data["timestamp"],
            lastPlayed=internal_data["last_played"],
            location={
                "area": internal_data["location"]["area"],
                "position": {
                    "x": internal_data["location"]["position"]["x"],
                    "y": internal_data["location"]["position"]["y"]
                }
            },
            questState={
                "activeQuest": internal_data["quest_state"]["active_quest"],
                "questStep": internal_data["quest_state"]["quest_step"],
                "objectives": [
                    {
                        "id": obj["id"],
                        "completed": obj["completed"],
                        "description": obj["description"]
                    }
                    for obj in internal_data["quest_state"]["objectives"]
                ]
            },
            inventory=internal_data["inventory"],
            gameFlags=internal_data["game_flags"],
            companions={
                companion_id: {
                    "relationship": state["relationship"],
                    "assistanceUsed": state["assistance_used"]
                }
                for companion_id, state in internal_data["companions"].items()
            }
        )
        
        return api_data.model_dump()


class GameStateListResponseAdapter(ResponseAdapter):
    """Adapter for list saved games responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform an internal response to the external format.
        
        Args:
            internal_data: The internal response to transform
            
        Returns:
            The transformed external response
        """
        return self.to_api(internal_data)

    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API response format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        saves = [
            SaveMetadata(
                saveId=save["save_id"],
                timestamp=save["timestamp"],
                location=save["location_name"],
                questName=save["quest_name"],
                level=save.get("level")
            )
            for save in internal_data["saves"]
        ]
        
        api_data = ListSavedGamesResponse(
            playerId=internal_data["player_id"],
            saves=saves
        )
        
        return api_data.model_dump() 