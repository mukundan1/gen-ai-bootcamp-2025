"""
Pydantic models for the companion assist endpoint.
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


class GameContext(BaseModel):
    """Game context information."""
    location: str = Field(..., description="Player's current location in the station")
    currentQuest: Optional[str] = Field(None, description="Active quest identifier")
    questStep: Optional[str] = Field(None, description="Current step in the active quest")
    nearbyEntities: Optional[List[str]] = Field(None, description="List of nearby interactive entities")
    lastInteraction: Optional[str] = Field(None, description="ID of the last entity interacted with")


class RequestDetails(BaseModel):
    """Details of the assistance request."""
    type: Literal["assistance", "vocabulary", "grammar", "direction", "translation"] = Field(
        ..., description="Type of assistance requested"
    )
    text: Optional[str] = Field(None, description="Player's question or request text")
    targetEntity: Optional[str] = Field(None, description="Entity the player is asking about")
    targetLocation: Optional[str] = Field(None, description="Location the player is asking about")
    language: Optional[Literal["english", "japanese"]] = Field(None, description="Language of the player's request")


class CompanionAssistRequest(BaseModel):
    """Request model for the companion assist endpoint."""
    playerId: str = Field(..., description="Unique identifier for the player")
    sessionId: str = Field(..., description="Current session identifier")
    gameContext: GameContext = Field(..., description="Current game state information")
    request: RequestDetails = Field(..., description="The assistance request details")
    conversationId: Optional[str] = Field(None, description="Optional conversation ID for tracking specific conversations")


class UIHighlight(BaseModel):
    """UI highlight information."""
    id: str = Field(..., description="ID of the element to highlight")
    effect: Literal["pulse", "glow", "bounce", "arrow"] = Field(..., description="Visual effect to apply")
    duration: int = Field(..., description="Duration of the effect in milliseconds")


class UISuggestion(BaseModel):
    """UI suggestion information."""
    text: str = Field(..., description="Text of the suggestion")
    action: str = Field(..., description="Action to perform when the suggestion is selected")
    params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the action")


class DialogueResponse(BaseModel):
    """Dialogue response information."""
    text: str = Field(..., description="The main dialogue text (in English)")
    japanese: Optional[str] = Field(None, description="Japanese text if relevant")
    pronunciation: Optional[str] = Field(None, description="Romanized pronunciation if relevant")
    characterName: str = Field("Hachi", description="Name of the speaking character")


class CompanionState(BaseModel):
    """Companion state information."""
    animation: Optional[str] = Field(None, description="Animation to play")
    emotionalState: Optional[str] = Field(None, description="Emotional state")
    position: Optional[Dict[str, Optional[float]]] = Field(None, description="Optional positioning information")


class UIElements(BaseModel):
    """UI elements for the response."""
    highlights: List[UIHighlight] = Field(default_factory=list, description="Elements to highlight")
    suggestions: List[UISuggestion] = Field(default_factory=list, description="Suggested follow-up actions")


class GameStateUpdate(BaseModel):
    """Game state updates."""
    learningMoments: List[str] = Field(default_factory=list, description="Language learning opportunities")
    questProgress: Optional[str] = Field(None, description="Quest progress update if relevant")
    vocabularyUnlocked: List[str] = Field(default_factory=list, description="New vocabulary items unlocked")


class ResponseMetadata(BaseModel):
    """Metadata about the response."""
    responseId: str = Field(..., description="Unique identifier for this response")
    processingTier: Literal["rule", "local", "cloud"] = Field(..., description="AI tier that processed the request")


class CompanionAssistResponse(BaseModel):
    """Response model for the companion assist endpoint."""
    dialogue: DialogueResponse = Field(..., description="The companion's response text")
    companion: CompanionState = Field(..., description="Animation and state information")
    ui: UIElements = Field(..., description="UI-related elements")
    gameState: GameStateUpdate = Field(..., description="Game state updates")
    meta: ResponseMetadata = Field(..., description="Metadata about the response") 