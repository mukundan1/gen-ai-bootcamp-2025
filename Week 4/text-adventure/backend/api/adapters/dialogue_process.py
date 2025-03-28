"""
Adapters for the dialogue process endpoint.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

from backend.api.adapters.base import RequestAdapter, ResponseAdapter
from backend.api.models.dialogue_process import DialogueProcessRequest, DialogueProcessResponse


# Placeholder for internal models
# In a real implementation, these would be imported from the game core
class InternalDialogueRequest:
    """Internal representation of a dialogue request."""
    
    def __init__(
        self,
        request_id: str,
        player_id: str,
        session_id: str,
        speaker_id: str,
        speaker_type: str,
        text: str,
        language: str,
        input_type: str,
        location: str,
        conversation_id: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        quest_info: Optional[Dict[str, Any]] = None,
        player_stats: Optional[Dict[str, Any]] = None,
        inventory: Optional[List[Dict[str, Any]]] = None,
        learned_vocabulary: Optional[List[str]] = None,
        game_progress: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.player_id = player_id
        self.session_id = session_id
        self.speaker_id = speaker_id
        self.speaker_type = speaker_type
        self.text = text
        self.language = language
        self.input_type = input_type
        self.location = location
        self.conversation_id = conversation_id
        self.conversation_history = conversation_history or []
        self.quest_info = quest_info or {}
        self.player_stats = player_stats or {}
        self.inventory = inventory or []
        self.learned_vocabulary = learned_vocabulary or []
        self.game_progress = game_progress or {}


class InternalDialogueResponse:
    """Internal representation of a dialogue response."""
    
    def __init__(
        self,
        request_id: str,
        response_text: str,
        japanese_text: Optional[str] = None,
        transliteration: Optional[str] = None,
        audio_url: Optional[str] = None,
        is_correct: bool = True,
        corrections: Optional[List[Dict[str, Any]]] = None,
        encouragement: Optional[str] = None,
        grammar_tips: Optional[List[str]] = None,
        npc_mood: Optional[str] = None,
        npc_relationship: Optional[int] = None,
        npc_animation: Optional[str] = None,
        companion_mood: Optional[str] = None,
        companion_animation: Optional[str] = None,
        companion_emotional_state: Optional[str] = None,
        dialogue_options: Optional[List[Dict[str, Any]]] = None,
        highlight_elements: Optional[List[str]] = None,
        suggestions: Optional[List[Dict[str, Any]]] = None,
        visual_cues: Optional[List[str]] = None,
        quest_updates: Optional[Dict[str, Any]] = None,
        inventory_updates: Optional[List[Dict[str, Any]]] = None,
        vocabulary_learned: Optional[List[str]] = None,
        achievements_unlocked: Optional[List[str]] = None,
        location_changes: Optional[Dict[str, Any]] = None,
        processing_tier: str = "rule",
        timestamp: Optional[str] = None
    ):
        self.request_id = request_id
        self.response_text = response_text
        self.japanese_text = japanese_text
        self.transliteration = transliteration
        self.audio_url = audio_url
        self.is_correct = is_correct
        self.corrections = corrections or []
        self.encouragement = encouragement
        self.grammar_tips = grammar_tips or []
        self.npc_mood = npc_mood
        self.npc_relationship = npc_relationship
        self.npc_animation = npc_animation
        self.companion_mood = companion_mood
        self.companion_animation = companion_animation
        self.companion_emotional_state = companion_emotional_state
        self.dialogue_options = dialogue_options or []
        self.highlight_elements = highlight_elements or []
        self.suggestions = suggestions or []
        self.visual_cues = visual_cues or []
        self.quest_updates = quest_updates or {}
        self.inventory_updates = inventory_updates or []
        self.vocabulary_learned = vocabulary_learned or []
        self.achievements_unlocked = achievements_unlocked or []
        self.location_changes = location_changes or {}
        self.processing_tier = processing_tier
        self.timestamp = timestamp or datetime.now().isoformat()


class DialogueProcessRequestAdapter(RequestAdapter):
    """Adapter for dialogue process requests."""
    
    def adapt(self, request: DialogueProcessRequest) -> InternalDialogueRequest:
        """
        Transform an API request to the internal format.
        
        Args:
            request: The API request
            
        Returns:
            The internal request
        """
        # Generate a request ID
        request_id = str(uuid.uuid4())
        
        # Extract game context information
        location = request.gameContext.location
        quest_info = request.gameContext.quest_info
        player_stats = request.gameContext.player_stats
        inventory = request.gameContext.inventory
        learned_vocabulary = request.gameContext.learned_vocabulary
        game_progress = request.gameContext.game_progress
        
        # Process conversation history
        conversation_history = []
        if request.conversationHistory:
            for exchange in request.conversationHistory:
                conversation_history.append({
                    "speaker": exchange.speaker,
                    "text": exchange.text,
                    "timestamp": exchange.timestamp
                })
        
        # Create the internal request
        internal_request = InternalDialogueRequest(
            request_id=request_id,
            player_id=request.playerId,
            session_id=request.sessionId,
            speaker_id=request.speakerId,
            speaker_type=request.speakerType.value,
            text=request.dialogueInput.text,
            language=request.dialogueInput.language.value,
            input_type=request.dialogueInput.inputType.value,
            location=location,
            conversation_id=request.conversationId,
            conversation_history=conversation_history,
            quest_info=quest_info,
            player_stats=player_stats,
            inventory=inventory,
            learned_vocabulary=learned_vocabulary,
            game_progress=game_progress
        )
        
        return internal_request


class DialogueProcessResponseAdapter(ResponseAdapter):
    """Adapter for dialogue process responses."""
    
    def adapt(self, response: InternalDialogueResponse) -> DialogueProcessResponse:
        """
        Transform an internal response to the API format.
        
        Args:
            response: The internal response
            
        Returns:
            The API response
        """
        from backend.api.models.dialogue_process import (
            DialogueContent,
            FeedbackContent,
            NPCState,
            CompanionState,
            UIElements,
            GameStateUpdate,
            ResponseMetadata,
            DialogueOption,
            UISuggestion,
            Correction
        )
        
        # Create dialogue content
        dialogue_content = DialogueContent(
            responseText=response.response_text,
            japaneseText=response.japanese_text,
            transliteration=response.transliteration,
            audioUrl=response.audio_url
        )
        
        # Create feedback content if corrections exist
        feedback_content = None
        if response.corrections or response.encouragement or response.grammar_tips:
            corrections = None
            if response.corrections:
                corrections = [
                    Correction(
                        original=correction["original"],
                        corrected=correction["corrected"],
                        explanation=correction["explanation"]
                    ) for correction in response.corrections
                ]
            
            feedback_content = FeedbackContent(
                isCorrect=response.is_correct,
                corrections=corrections,
                encouragement=response.encouragement,
                grammarTips=response.grammar_tips
            )
        
        # Create NPC state if applicable
        npc_state = None
        if response.npc_mood:
            npc_state = NPCState(
                mood=response.npc_mood,
                relationship=response.npc_relationship,
                animation=response.npc_animation
            )
        
        # Create companion state if applicable
        companion_state = None
        if response.companion_mood:
            companion_state = CompanionState(
                mood=response.companion_mood,
                animation=response.companion_animation,
                emotionalState=response.companion_emotional_state
            )
        
        # Create UI elements
        dialogue_options = None
        if response.dialogue_options:
            dialogue_options = [
                DialogueOption(
                    id=option["id"],
                    text=option["text"],
                    japaneseText=option.get("japanese_text"),
                    transliteration=option.get("transliteration")
                ) for option in response.dialogue_options
            ]
        
        suggestions = None
        if response.suggestions:
            suggestions = [
                UISuggestion(
                    text=suggestion["text"],
                    type=suggestion["type"]
                ) for suggestion in response.suggestions
            ]
        
        ui_elements = UIElements(
            dialogueOptions=dialogue_options,
            highlightElements=response.highlight_elements,
            suggestions=suggestions,
            visualCues=response.visual_cues
        )
        
        # Create game state updates
        game_state_update = GameStateUpdate(
            questUpdates=response.quest_updates,
            inventoryUpdates=response.inventory_updates,
            vocabularyLearned=response.vocabulary_learned,
            achievementsUnlocked=response.achievements_unlocked,
            locationChanges=response.location_changes
        )
        
        # Create metadata
        metadata = ResponseMetadata(
            responseId=response.request_id,
            processingTier=response.processing_tier,
            timestamp=response.timestamp
        )
        
        # Create the API response
        api_response = DialogueProcessResponse(
            dialogueContent=dialogue_content,
            feedbackContent=feedback_content,
            npcState=npc_state,
            companionState=companion_state,
            uiElements=ui_elements,
            gameStateUpdates=game_state_update,
            metadata=metadata
        )
        
        return api_response 