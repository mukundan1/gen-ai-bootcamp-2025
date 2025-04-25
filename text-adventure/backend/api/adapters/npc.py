"""
Adapters for NPC Information API.
"""

from typing import Dict, Any, List
from datetime import datetime, UTC

from backend.api.adapters.base import ResponseAdapter, RequestAdapter
from backend.api.models.npc import (
    NPCInformationResponse,
    NPCConfigurationResponse,
    NPCInteractionStateResponse,
    UpdateNPCConfigurationRequest,
    VisualAppearance,
    NPCStatus,
    NPCProfile,
    LanguageProfile,
    PromptTemplates,
    ConversationParameters,
    RelationshipMetrics,
    ConversationState,
    GameProgressUnlocks
)


class NPCInformationResponseAdapter(ResponseAdapter):
    """Adapter for NPC information responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        return self.to_api(internal_data)
    
    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        visual_appearance = VisualAppearance(
            spriteKey=internal_data.get("visual_appearance", {}).get("sprite_key", ""),
            animations=internal_data.get("visual_appearance", {}).get("animations", [])
        )
        
        status = NPCStatus(
            active=internal_data.get("status", {}).get("active", False),
            currentEmotion=internal_data.get("status", {}).get("current_emotion", ""),
            currentActivity=internal_data.get("status", {}).get("current_activity", "")
        )
        
        api_data = NPCInformationResponse(
            npcId=internal_data.get("npc_id", ""),
            name=internal_data.get("name", ""),
            role=internal_data.get("role", ""),
            location=internal_data.get("location", ""),
            availableDialogueTopics=internal_data.get("available_dialogue_topics", []),
            visualAppearance=visual_appearance,
            status=status
        )
        
        return api_data.model_dump()


class NPCConfigurationResponseAdapter(ResponseAdapter):
    """Adapter for NPC configuration responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        return self.to_api(internal_data)
    
    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        profile = NPCProfile(
            name=internal_data.get("profile", {}).get("name", ""),
            role=internal_data.get("profile", {}).get("role", ""),
            location=internal_data.get("profile", {}).get("location", ""),
            personality=internal_data.get("profile", {}).get("personality", []),
            expertise=internal_data.get("profile", {}).get("expertise", []),
            limitations=internal_data.get("profile", {}).get("limitations", [])
        )
        
        # Check for both camelCase and snake_case keys for backward compatibility
        language_profile_data = internal_data.get("languageProfile", internal_data.get("language_profile", {}))
        language_profile = LanguageProfile(
            defaultLanguage=language_profile_data.get("defaultLanguage", language_profile_data.get("default_language", "")),
            japaneseLevel=language_profile_data.get("japaneseLevel", language_profile_data.get("japanese_level", "")),
            speechPatterns=language_profile_data.get("speechPatterns", language_profile_data.get("speech_patterns", [])),
            commonPhrases=language_profile_data.get("commonPhrases", language_profile_data.get("common_phrases", [])),
            vocabularyFocus=language_profile_data.get("vocabularyFocus", language_profile_data.get("vocabulary_focus", []))
        )
        
        # Check for both camelCase and snake_case keys for backward compatibility
        prompt_templates_data = internal_data.get("promptTemplates", internal_data.get("prompt_templates", {}))
        prompt_templates = PromptTemplates(
            initialGreeting=prompt_templates_data.get("initialGreeting", prompt_templates_data.get("initial_greeting", "")),
            responseFormat=prompt_templates_data.get("responseFormat", prompt_templates_data.get("response_format", "")),
            errorHandling=prompt_templates_data.get("errorHandling", prompt_templates_data.get("error_handling", "")),
            conversationClose=prompt_templates_data.get("conversationClose", prompt_templates_data.get("conversation_close", ""))
        )
        
        # Check for both camelCase and snake_case keys for backward compatibility
        conversation_params_data = internal_data.get("conversationParameters", internal_data.get("conversation_parameters", {}))
        conversation_parameters = ConversationParameters(
            maxTurns=conversation_params_data.get("maxTurns", conversation_params_data.get("max_turns", 0)),
            temperatureDefault=conversation_params_data.get("temperatureDefault", conversation_params_data.get("temperature_default", 0.0)),
            contextWindowSize=conversation_params_data.get("contextWindowSize", conversation_params_data.get("context_window_size", 0))
        )
        
        api_data = NPCConfigurationResponse(
            npcId=internal_data.get("npc_id", ""),
            profile=profile,
            languageProfile=language_profile,
            promptTemplates=prompt_templates,
            conversationParameters=conversation_parameters
        )
        
        return api_data.model_dump()


class NPCInteractionStateResponseAdapter(ResponseAdapter):
    """Adapter for NPC interaction state responses."""

    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        return self.to_api(internal_data)
    
    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        # Convert internal data to API format
        # Check for both camelCase and snake_case keys for backward compatibility
        relationship_data = internal_data.get("relationship", internal_data.get("relationship_metrics", {}))
        relationship = RelationshipMetrics(
            familiarityLevel=relationship_data.get("familiarityLevel", relationship_data.get("familiarity_level", 0.0)),
            interactionCount=relationship_data.get("interactionCount", relationship_data.get("interaction_count", 0)),
            lastInteractionTime=relationship_data.get("lastInteractionTime", relationship_data.get("last_interaction_time", datetime.now(UTC)))
        )
        
        # Check for both camelCase and snake_case keys for backward compatibility
        conversation_state_data = internal_data.get("conversationState", internal_data.get("conversation_state", {}))
        conversation_state = ConversationState(
            activeConversation=conversation_state_data.get("activeConversation", conversation_state_data.get("active_conversation", False)),
            conversationId=conversation_state_data.get("conversationId", conversation_state_data.get("conversation_id")),
            turnCount=conversation_state_data.get("turnCount", conversation_state_data.get("turn_count", 0)),
            pendingResponse=conversation_state_data.get("pendingResponse", conversation_state_data.get("pending_response", False))
        )
        
        # Check for both camelCase and snake_case keys for backward compatibility
        game_progress_data = internal_data.get("gameProgress", internal_data.get("game_progress", {}))
        game_progress = GameProgressUnlocks(
            unlockedTopics=game_progress_data.get("unlockedTopics", game_progress_data.get("unlocked_topics", []))
        )
        
        api_data = NPCInteractionStateResponse(
            playerId=internal_data.get("playerId", internal_data.get("player_id", "")),
            npcId=internal_data.get("npcId", internal_data.get("npc_id", "")),
            relationshipMetrics=relationship,
            conversationState=conversation_state,
            gameProgressUnlocks=game_progress
        )
        
        return api_data.model_dump()


class NPCConfigurationUpdateRequestAdapter(RequestAdapter):
    """Adapter for NPC configuration update requests."""
    
    def adapt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt API request to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal request data.
        """
        return self.to_internal(request_data)
    
    def to_internal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal request data.
        """
        # Convert API request to internal format
        return {
            "profile": {
                "name": request_data["profile"]["name"],
                "role": request_data["profile"]["role"],
                "location": request_data["profile"]["location"],
                "personality": request_data["profile"]["personality"],
                "expertise": request_data["profile"]["expertise"],
                "limitations": request_data["profile"]["limitations"]
            },
            "languageProfile": {
                "defaultLanguage": request_data["languageProfile"]["defaultLanguage"],
                "japaneseLevel": request_data["languageProfile"]["japaneseLevel"],
                "speechPatterns": request_data["languageProfile"]["speechPatterns"],
                "commonPhrases": request_data["languageProfile"]["commonPhrases"],
                "vocabularyFocus": request_data["languageProfile"]["vocabularyFocus"]
            },
            "promptTemplates": {
                "initialGreeting": request_data["promptTemplates"]["initialGreeting"],
                "responseFormat": request_data["promptTemplates"]["responseFormat"],
                "errorHandling": request_data["promptTemplates"]["errorHandling"],
                "conversationClose": request_data["promptTemplates"]["conversationClose"]
            },
            "conversationParameters": {
                "maxTurns": request_data["conversationParameters"]["maxTurns"],
                "temperatureDefault": request_data["conversationParameters"]["temperatureDefault"],
                "contextWindowSize": request_data["conversationParameters"]["contextWindowSize"]
            }
        } 