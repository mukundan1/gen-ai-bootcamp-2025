"""
Adapters for the NPC Dialogue API.
"""

from typing import Dict, Any, List
from datetime import datetime
import uuid

from backend.api.adapters.base import ResponseAdapter
from backend.api.models.npc_dialogue import (
    NPCDialogueResponse,
    NPCResponse,
    ExpectedInput,
    ExpectedInputOption,
    GameStateChange,
    NPCDialogueResponseMeta
)


class NPCDialogueResponseAdapter(ResponseAdapter):
    """Adapter for NPC dialogue responses."""
    
    def adapt(self, data: Dict[str, Any]) -> NPCDialogueResponse:
        """
        Adapt the internal data format to the API response format.
        
        Args:
            data: The internal data format.
            
        Returns:
            The API response format.
        """
        # Extract NPC response data
        npc_response_data = data.get("npcResponse", {})
        npc_response = NPCResponse(
            text=npc_response_data.get("text", ""),
            japanese=npc_response_data.get("japanese", ""),
            animation=npc_response_data.get("animation", "idle"),
            emotion=npc_response_data.get("emotion", "neutral"),
            feedback=npc_response_data.get("feedback")
        )
        
        # Extract expected input data
        expected_input_data = data.get("expectedInput", {})
        expected_input_options = []
        
        for option_data in expected_input_data.get("options", []) or []:
            option = ExpectedInputOption(
                id=option_data.get("id", str(uuid.uuid4())),
                text=option_data.get("text", ""),
                japanese=option_data.get("japanese", ""),
                hint=option_data.get("hint")
            )
            expected_input_options.append(option)
        
        expected_input = ExpectedInput(
            type=expected_input_data.get("type", "free_text"),
            options=expected_input_options if expected_input_options else None,
            prompt=expected_input_data.get("prompt")
        )
        
        # Extract game state changes
        game_state_changes = []
        for change_data in data.get("gameStateChanges", []):
            change = GameStateChange(
                type=change_data.get("type", ""),
                data=change_data.get("data", {})
            )
            game_state_changes.append(change)
        
        # Extract metadata
        meta_data = data.get("meta", {})
        meta = NPCDialogueResponseMeta(
            processingTime=meta_data.get("processingTime", 0.0),
            aiTier=meta_data.get("aiTier", "rule"),
            confidenceScore=meta_data.get("confidenceScore", 0.0)
        )
        
        # Create the response
        response = NPCDialogueResponse(
            conversationId=data.get("conversationId", str(uuid.uuid4())),
            npcResponse=npc_response,
            expectedInput=expected_input,
            gameStateChanges=game_state_changes,
            meta=meta
        )
        
        return response 