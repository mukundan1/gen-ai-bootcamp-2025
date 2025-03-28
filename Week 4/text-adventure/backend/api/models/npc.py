"""
Models for the NPC Information API.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


# NPC Information Models

class VisualAppearance(BaseModel):
    """Visual appearance information for an NPC."""
    spriteKey: str = Field(..., description="Key for the NPC's sprite sheet")
    animations: List[str] = Field(..., description="List of available animations")


class NPCStatus(BaseModel):
    """Current status information for an NPC."""
    active: bool = Field(..., description="Whether the NPC is currently active")
    currentEmotion: str = Field(..., description="Current emotional state")
    currentActivity: str = Field(..., description="Current activity the NPC is engaged in")


class NPCInformationResponse(BaseModel):
    """Response model for NPC information."""
    npcId: str = Field(..., description="Unique identifier for the NPC")
    name: str = Field(..., description="The NPC's display name")
    role: str = Field(..., description="The NPC's role in the railway station")
    location: str = Field(..., description="The NPC's current location")
    availableDialogueTopics: List[str] = Field(..., description="List of topics this NPC can discuss")
    visualAppearance: VisualAppearance = Field(..., description="Visual representation information")
    status: NPCStatus = Field(..., description="Current state information")


# NPC Configuration Models

class NPCProfile(BaseModel):
    """Profile information for an NPC."""
    name: str = Field(..., description="The NPC's display name")
    role: str = Field(..., description="The NPC's role in the railway station")
    location: str = Field(..., description="The NPC's primary location")
    personality: List[str] = Field(..., description="List of personality traits")
    expertise: List[str] = Field(..., description="Topics the NPC is knowledgeable about")
    limitations: List[str] = Field(..., description="Topics the NPC is not knowledgeable about")


class LanguageProfile(BaseModel):
    """Language profile for an NPC."""
    defaultLanguage: str = Field(..., description="Primary language of the NPC")
    japaneseLevel: str = Field(..., description="JLPT level of Japanese used by the NPC")
    speechPatterns: List[str] = Field(..., description="Characteristic speech patterns")
    commonPhrases: List[str] = Field(..., description="Frequently used phrases")
    vocabularyFocus: List[str] = Field(..., description="Vocabulary domains this NPC emphasizes")


class PromptTemplates(BaseModel):
    """Prompt templates for an NPC."""
    initialGreeting: str = Field(..., description="Template for initial greeting")
    responseFormat: str = Field(..., description="Format specification for responses")
    errorHandling: str = Field(..., description="Template for handling errors")
    conversationClose: str = Field(..., description="Template for ending conversations")


class ConversationParameters(BaseModel):
    """Conversation parameters for an NPC."""
    maxTurns: int = Field(..., description="Maximum number of conversation turns")
    temperatureDefault: float = Field(..., description="Default temperature for AI generation")
    contextWindowSize: int = Field(..., description="Size of context window for conversation history")


class NPCConfigurationResponse(BaseModel):
    """Response model for NPC configuration."""
    npcId: str = Field(..., description="Unique identifier for the NPC")
    profile: NPCProfile = Field(..., description="General profile information about the NPC")
    languageProfile: LanguageProfile = Field(..., description="Language-related characteristics")
    promptTemplates: PromptTemplates = Field(..., description="Templates used for AI prompt construction")
    conversationParameters: ConversationParameters = Field(..., description="Parameters controlling conversation behavior")


# NPC Interaction State Models

class RelationshipMetrics(BaseModel):
    """Metrics tracking the player-NPC relationship."""
    familiarityLevel: float = Field(..., description="How familiar the player is with the NPC (0.0-1.0)")
    interactionCount: int = Field(..., description="How many times the player has interacted with this NPC")
    lastInteractionTime: datetime = Field(..., description="Timestamp of the last interaction")


class ConversationState(BaseModel):
    """Current conversation state information."""
    activeConversation: bool = Field(..., description="Whether there is an active conversation")
    conversationId: Optional[str] = Field(None, description="ID of the active conversation, if any")
    turnCount: int = Field(..., description="Number of turns in the current conversation")
    pendingResponse: bool = Field(..., description="Whether the NPC is waiting for a player response")


class GameProgressUnlocks(BaseModel):
    """Progress-related information."""
    unlockedTopics: List[str] = Field(..., description="Dialogue topics unlocked with this NPC")


class NPCInteractionStateResponse(BaseModel):
    """Response model for NPC interaction state."""
    playerId: str = Field(..., description="Unique identifier for the player")
    npcId: str = Field(..., description="Unique identifier for the NPC")
    relationshipMetrics: RelationshipMetrics = Field(..., description="Metrics tracking the player-NPC relationship")
    conversationState: ConversationState = Field(..., description="Current conversation state information")
    gameProgressUnlocks: GameProgressUnlocks = Field(..., description="Progress-related information")


# Error Response Model

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details")


# Update NPC Configuration Models

class UpdateNPCProfileRequest(BaseModel):
    """Profile information for updating an NPC."""
    name: str = Field(..., description="The NPC's display name")
    role: str = Field(..., description="The NPC's role in the railway station")
    location: str = Field(..., description="The NPC's primary location")
    personality: List[str] = Field(..., description="List of personality traits")
    expertise: List[str] = Field(..., description="Topics the NPC is knowledgeable about")
    limitations: List[str] = Field(..., description="Topics the NPC is not knowledgeable about")


class UpdateLanguageProfileRequest(BaseModel):
    """Language profile for updating an NPC."""
    defaultLanguage: str = Field(..., description="Primary language of the NPC")
    japaneseLevel: str = Field(..., description="JLPT level of Japanese used by the NPC")
    speechPatterns: List[str] = Field(..., description="Characteristic speech patterns")
    commonPhrases: List[str] = Field(..., description="Frequently used phrases")
    vocabularyFocus: List[str] = Field(..., description="Vocabulary domains this NPC emphasizes")


class UpdatePromptTemplatesRequest(BaseModel):
    """Prompt templates for updating an NPC."""
    initialGreeting: str = Field(..., description="Template for initial greeting")
    responseFormat: str = Field(..., description="Format specification for responses")
    errorHandling: str = Field(..., description="Template for handling errors")
    conversationClose: str = Field(..., description="Template for ending conversations")


class UpdateConversationParametersRequest(BaseModel):
    """Conversation parameters for updating an NPC."""
    maxTurns: int = Field(..., description="Maximum number of conversation turns")
    temperatureDefault: float = Field(..., description="Default temperature for AI generation")
    contextWindowSize: int = Field(..., description="Size of context window for conversation history")


class UpdateNPCConfigurationRequest(BaseModel):
    """Request model for updating NPC configuration."""
    profile: UpdateNPCProfileRequest = Field(..., description="General profile information about the NPC")
    languageProfile: UpdateLanguageProfileRequest = Field(..., description="Language-related characteristics")
    promptTemplates: UpdatePromptTemplatesRequest = Field(..., description="Templates used for AI prompt construction")
    conversationParameters: UpdateConversationParametersRequest = Field(..., description="Parameters controlling conversation behavior") 