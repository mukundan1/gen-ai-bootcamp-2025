"""
Adapters for the companion assist endpoint.
"""

import uuid
from typing import Dict, Any

from backend.api.adapters.base import RequestAdapter, ResponseAdapter
from backend.api.models.companion_assist import (
    CompanionAssistRequest,
    CompanionAssistResponse,
    DialogueResponse,
    CompanionState,
    UIElements,
    GameStateUpdate,
    ResponseMetadata,
    UIHighlight,
    UISuggestion
)
from backend.ai.companion.core.models import (
    CompanionRequest,
    CompanionResponse,
    GameContext,
    IntentCategory
)


class CompanionAssistRequestAdapter(RequestAdapter[CompanionAssistRequest, CompanionRequest]):
    """
    Adapter for transforming companion assist API requests to internal format.
    """
    
    def adapt(self, request: CompanionAssistRequest) -> CompanionRequest:
        """
        Transform an API request to the internal CompanionRequest format.
        
        Args:
            request: The API request to transform
            
        Returns:
            The transformed internal request
        """
        # Create a game context object
        game_context = GameContext(
            player_location=request.gameContext.location,
            current_objective=request.gameContext.currentQuest or "",
            nearby_npcs=request.gameContext.nearbyEntities or [],
            nearby_objects=[],  # Not provided in the API request
            player_inventory=[],  # Not provided in the API request
            language_proficiency={},  # Not provided in the API request
            game_progress={}  # Not provided in the API request
        )
        
        # Map request type to additional params
        additional_params = {
            "target_entity": request.request.targetEntity,
            "target_location": request.request.targetLocation,
            "language": request.request.language,
            "session_id": request.sessionId,
            "player_id": request.playerId  # Add player_id for player history lookup
        }
        
        # Add conversation_id if provided
        if hasattr(request, 'conversationId') and request.conversationId:
            additional_params["conversation_id"] = request.conversationId
        
        # Create the companion request
        companion_request = CompanionRequest(
            request_id=str(uuid.uuid4()),
            player_input=request.request.text or "",
            request_type=request.request.type,
            game_context=game_context,
            additional_params=additional_params
        )
        
        return companion_request


class CompanionAssistResponseAdapter(ResponseAdapter[CompanionResponse, CompanionAssistResponse]):
    """
    Adapter for transforming internal companion responses to API format.
    """
    
    def adapt(self, response: CompanionResponse) -> CompanionAssistResponse:
        """
        Transform an internal response to the API response format.
        
        Args:
            response: The internal response to transform
            
        Returns:
            The transformed API response
        """
        # Extract Japanese text and pronunciation if available
        japanese_text = None
        pronunciation = None
        
        if response.learning_cues and "japanese_text" in response.learning_cues:
            japanese_text = response.learning_cues["japanese_text"]
            
        if response.learning_cues and "pronunciation" in response.learning_cues:
            pronunciation = response.learning_cues["pronunciation"]
        
        # Create the dialogue response
        dialogue = DialogueResponse(
            text=response.response_text,
            japanese=japanese_text,
            pronunciation=pronunciation,
            characterName="Hachi"
        )
        
        # Create the companion state
        companion = CompanionState(
            animation=response.debug_info.get("animation", "idle"),
            emotionalState=response.emotion,
            position=None  # Position is not provided in the internal response
        )
        
        # Create UI elements
        highlights = []
        if response.debug_info and "highlights" in response.debug_info:
            for highlight in response.debug_info["highlights"]:
                highlights.append(UIHighlight(
                    id=highlight["id"],
                    effect=highlight["effect"],
                    duration=highlight["duration"]
                ))
        
        suggestions = []
        for action in response.suggested_actions:
            suggestions.append(UISuggestion(
                text=action,
                action="ASK_QUESTION",
                params={"topic": action.lower().replace(" ", "_")}
            ))
        
        ui = UIElements(
            highlights=highlights,
            suggestions=suggestions
        )
        
        # Create game state update
        learning_moments = []
        vocabulary_unlocked = []
        
        if response.learning_cues:
            if "learning_moments" in response.learning_cues:
                learning_moments = response.learning_cues["learning_moments"]
            if "vocabulary_unlocked" in response.learning_cues:
                vocabulary_unlocked = response.learning_cues["vocabulary_unlocked"]
        
        game_state = GameStateUpdate(
            learningMoments=learning_moments,
            questProgress=None,  # Not provided in the internal response
            vocabularyUnlocked=vocabulary_unlocked
        )
        
        # Create metadata
        meta = ResponseMetadata(
            responseId=response.request_id,
            processingTier=self._map_processing_tier(response.processing_tier)
        )
        
        # Create the API response
        api_response = CompanionAssistResponse(
            dialogue=dialogue,
            companion=companion,
            ui=ui,
            gameState=game_state,
            meta=meta
        )
        
        return api_response
    
    def _map_processing_tier(self, tier: str) -> str:
        """
        Map internal processing tier to API format.
        
        Args:
            tier: The internal processing tier
            
        Returns:
            The API processing tier
        """
        # First check if tier is a ProcessingTier enum
        if hasattr(tier, 'value'):
            tier = tier.value  # Convert enum to its string value
        
        # Now tier should be a string value like 'tier_1', 'tier_2', etc.
        tier_mapping = {
            # Enum names
            "TIER_1": "rule",
            "TIER_2": "local",
            "TIER_3": "cloud",
            # Enum values
            "tier_1": "rule",
            "tier_2": "local",
            "tier_3": "cloud"
        }
        
        return tier_mapping.get(tier, "rule") 