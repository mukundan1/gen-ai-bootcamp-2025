"""
Pydantic models for the NPC Dialogue API.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime


class LearningProgress(BaseModel):
    """Player's learning progress."""
    vocabularyMastered: int = Field(..., description="Number of vocabulary words mastered")
    grammarPoints: int = Field(..., description="Number of grammar points learned")
    conversationSuccess: float = Field(..., description="Success rate in conversations (0.0-1.0)")


class PlayerContext(BaseModel):
    """Context information about the player."""
    playerId: str = Field(..., description="Unique identifier for the player")
    sessionId: str = Field(..., description="Current session identifier")
    languageLevel: str = Field(..., description="JLPT level of the player (N1-N5)")
    learningProgress: LearningProgress = Field(..., description="Player's learning progress")


class InteractionHistoryItem(BaseModel):
    """Record of an interaction with an NPC."""
    npcId: str = Field(..., description="Identifier of the NPC")
    completed: bool = Field(..., description="Whether the interaction was completed")


class GameContext(BaseModel):
    """Context information about the current game state."""
    location: str = Field(..., description="Current location in the game")
    currentQuest: str = Field(..., description="Current active quest")
    questStep: str = Field(..., description="Current step in the active quest")
    interactionHistory: List[InteractionHistoryItem] = Field(..., description="History of NPC interactions")
    timeOfDay: str = Field(..., description="Time of day in the game world")
    gameFlags: Dict[str, bool] = Field(..., description="Various game state flags")


class PlayerInput(BaseModel):
    """Input provided by the player."""
    text: str = Field(..., description="Text input from the player")
    inputType: str = Field(..., description="Type of input (keyboard, voice, selection)")
    language: str = Field(..., description="Language of the input (japanese, english)")
    selectedOptionId: Optional[str] = Field(None, description="ID of the selected option if inputType is selection")


class ConversationExchange(BaseModel):
    """A single exchange in a conversation."""
    speaker: str = Field(..., description="Who is speaking (player or npc)")
    text: str = Field(..., description="The text that was spoken")
    timestamp: str = Field(..., description="When the exchange occurred")


class ConversationContext(BaseModel):
    """Context of the current conversation."""
    conversationId: Optional[str] = Field(None, description="Identifier for the conversation")
    previousExchanges: List[ConversationExchange] = Field(default_factory=list, description="Previous exchanges in this conversation")


class NPCDialogueRequest(BaseModel):
    """Request body for the NPC dialogue API."""
    playerContext: PlayerContext = Field(..., description="Context information about the player")
    gameContext: GameContext = Field(..., description="Context information about the current game state")
    npcId: str = Field(..., description="Identifier of the NPC to interact with")
    playerInput: PlayerInput = Field(..., description="Input provided by the player")
    conversationContext: ConversationContext = Field(..., description="Context of the current conversation")


class NPCResponse(BaseModel):
    """Response from an NPC."""
    text: str = Field(..., description="English translation of the NPC's response")
    japanese: str = Field(..., description="Japanese text of the NPC's response")
    animation: str = Field(..., description="Animation to play for the NPC")
    emotion: str = Field(..., description="Emotion to display for the NPC")
    feedback: Optional[Dict[str, Any]] = Field(None, description="Language learning feedback")


class ExpectedInputOption(BaseModel):
    """An option that the player can select."""
    id: str = Field(..., description="Unique identifier for this option")
    text: str = Field(..., description="Text to display for this option")
    japanese: str = Field(..., description="Japanese text for this option")
    hint: Optional[str] = Field(None, description="Hint to help the player understand this option")


class ExpectedInput(BaseModel):
    """Expected input from the player."""
    type: str = Field(..., description="Type of input expected (free_text, selection)")
    options: Optional[List[ExpectedInputOption]] = Field(None, description="Options for selection input type")
    prompt: Optional[str] = Field(None, description="Prompt to guide the player's input")


class GameStateChange(BaseModel):
    """A change to the game state."""
    type: str = Field(..., description="Type of change (quest_progress, item_acquired, etc.)")
    data: Dict[str, Any] = Field(..., description="Data associated with the change")


class NPCDialogueResponseMeta(BaseModel):
    """Metadata about the NPC dialogue response."""
    processingTime: float = Field(..., description="Time taken to process the dialogue in milliseconds")
    aiTier: str = Field(..., description="AI tier used for this response (rule, local, cloud)")
    confidenceScore: float = Field(..., description="Confidence score for the response (0.0-1.0)")


class NPCDialogueResponse(BaseModel):
    """Response body for the NPC dialogue API."""
    conversationId: str = Field(..., description="Identifier for the conversation")
    npcResponse: NPCResponse = Field(..., description="Response from the NPC")
    expectedInput: ExpectedInput = Field(..., description="Expected input from the player")
    gameStateChanges: List[GameStateChange] = Field(default_factory=list, description="Changes to apply to the game state")
    meta: NPCDialogueResponseMeta = Field(..., description="Metadata about the response")


class ErrorResponse(BaseModel):
    """Error response for the API."""
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message") 