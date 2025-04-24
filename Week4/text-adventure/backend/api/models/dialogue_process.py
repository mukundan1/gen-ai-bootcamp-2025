"""
Models for the dialogue process endpoint.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator


class Language(str, Enum):
    """Language options for dialogue input."""
    ENGLISH = "english"
    JAPANESE = "japanese"


class SpeakerType(str, Enum):
    """Types of speakers in the game."""
    NPC = "npc"
    COMPANION = "companion"


class InputType(str, Enum):
    """Types of dialogue input."""
    TEXT = "text"
    VOICE = "voice"
    SELECTION = "selection"


class GameContext(BaseModel):
    """Context information about the game state."""
    location: str = Field(..., description="Current location in the game")
    quest_info: Optional[Dict[str, Any]] = Field(default=None, description="Information about active quests")
    player_stats: Optional[Dict[str, Any]] = Field(default=None, description="Player statistics")
    inventory: Optional[List[Dict[str, Any]]] = Field(default=None, description="Player inventory items")
    learned_vocabulary: Optional[List[str]] = Field(default=None, description="Japanese vocabulary the player has learned")
    game_progress: Optional[Dict[str, Any]] = Field(default=None, description="Overall game progress information")


class DialogueInput(BaseModel):
    """Input from the player for dialogue processing."""
    text: str = Field(..., min_length=1, description="The text input from the player")
    language: Language = Field(..., description="The language of the input (english or japanese)")
    inputType: InputType = Field(..., description="The type of input (text, voice, or selection)")
    context: Optional[str] = Field(default=None, description="Additional context for the input")


class DialogueExchange(BaseModel):
    """A single exchange in a dialogue conversation."""
    speaker: str = Field(..., description="The ID of the speaker")
    text: str = Field(..., description="The text spoken")
    timestamp: str = Field(..., description="The timestamp of the exchange")


class DialogueProcessRequest(BaseModel):
    """Request model for the dialogue process endpoint."""
    playerId: str = Field(..., min_length=1, description="The ID of the player")
    sessionId: str = Field(..., min_length=1, description="The ID of the session")
    speakerId: str = Field(..., min_length=1, description="The ID of the speaker (NPC or companion)")
    speakerType: SpeakerType = Field(..., description="The type of speaker (NPC or companion)")
    dialogueInput: DialogueInput = Field(..., description="The input from the player")
    conversationId: Optional[str] = Field(default=None, description="The ID of the conversation if continuing")
    gameContext: GameContext = Field(..., description="Context information about the game state")
    conversationHistory: Optional[List[DialogueExchange]] = Field(default=None, description="Previous exchanges in the conversation")


class DialogueContent(BaseModel):
    """Content of the dialogue response."""
    responseText: str = Field(..., description="The text response in the player's language")
    japaneseText: Optional[str] = Field(default=None, description="The Japanese version of the response")
    transliteration: Optional[str] = Field(default=None, description="Transliteration of Japanese text")
    audioUrl: Optional[str] = Field(default=None, description="URL to audio file of the response")


class Correction(BaseModel):
    """Correction for player's Japanese input."""
    original: str = Field(..., description="The original text from the player")
    corrected: str = Field(..., description="The corrected text")
    explanation: str = Field(..., description="Explanation of the correction")


class FeedbackContent(BaseModel):
    """Feedback on the player's input."""
    isCorrect: bool = Field(..., description="Whether the player's input was correct")
    corrections: Optional[List[Correction]] = Field(default=None, description="Corrections for the player's input")
    encouragement: Optional[str] = Field(default=None, description="Encouraging message for the player")
    grammarTips: Optional[List[str]] = Field(default=None, description="Grammar tips for the player")


class NPCState(BaseModel):
    """State of the NPC after the dialogue."""
    mood: str = Field(..., description="The mood of the NPC")
    relationship: Optional[int] = Field(default=None, description="Relationship level with the player")
    animation: Optional[str] = Field(default=None, description="Animation to play for the NPC")


class CompanionState(BaseModel):
    """State of the companion after the dialogue."""
    mood: str = Field(..., description="The mood of the companion")
    animation: Optional[str] = Field(default=None, description="Animation to play for the companion")
    emotionalState: Optional[str] = Field(default=None, description="Emotional state of the companion")


class DialogueOption(BaseModel):
    """A dialogue option for the player to select."""
    id: str = Field(..., description="The ID of the option")
    text: str = Field(..., description="The text of the option")
    japaneseText: Optional[str] = Field(default=None, description="The Japanese version of the option")
    transliteration: Optional[str] = Field(default=None, description="Transliteration of Japanese text")


class UISuggestion(BaseModel):
    """A suggestion for the UI to display."""
    text: str = Field(..., description="The text of the suggestion")
    type: str = Field(..., description="The type of suggestion")


class UIElements(BaseModel):
    """UI elements to display in the game."""
    dialogueOptions: Optional[List[DialogueOption]] = Field(default=None, description="Options for the player to select")
    highlightElements: Optional[List[str]] = Field(default=None, description="Elements to highlight in the UI")
    suggestions: Optional[List[UISuggestion]] = Field(default=None, description="Suggestions for the player")
    visualCues: Optional[List[str]] = Field(default=None, description="Visual cues to display")


class GameStateUpdate(BaseModel):
    """Updates to the game state."""
    questUpdates: Optional[Dict[str, Any]] = Field(default=None, description="Updates to quests")
    inventoryUpdates: Optional[List[Dict[str, Any]]] = Field(default=None, description="Updates to inventory")
    vocabularyLearned: Optional[List[str]] = Field(default=None, description="New vocabulary learned")
    achievementsUnlocked: Optional[List[str]] = Field(default=None, description="Achievements unlocked")
    locationChanges: Optional[Dict[str, Any]] = Field(default=None, description="Changes to the location")


class ResponseMetadata(BaseModel):
    """Metadata about the response."""
    responseId: str = Field(..., description="The ID of the response")
    processingTier: str = Field(..., description="The processing tier used")
    timestamp: str = Field(..., description="The timestamp of the response")


class DialogueProcessResponse(BaseModel):
    """Response model for the dialogue process endpoint."""
    dialogueContent: DialogueContent = Field(..., description="Content of the dialogue response")
    feedbackContent: Optional[FeedbackContent] = Field(default=None, description="Feedback on the player's input")
    npcState: Optional[NPCState] = Field(default=None, description="State of the NPC after the dialogue")
    companionState: Optional[CompanionState] = Field(default=None, description="State of the companion after the dialogue")
    uiElements: UIElements = Field(..., description="UI elements to display in the game")
    gameStateUpdates: GameStateUpdate = Field(..., description="Updates to the game state")
    metadata: ResponseMetadata = Field(..., description="Metadata about the response") 