from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, field_validator


class Position(BaseModel):
    """Position in the game world."""
    x: float
    y: float


class Location(BaseModel):
    """Location in the game world."""
    area: str
    position: Position


class Objective(BaseModel):
    """Quest objective."""
    id: str
    completed: bool
    description: str


class QuestState(BaseModel):
    """State of the current quest."""
    activeQuest: str
    questStep: str
    objectives: List[Objective]


class CompanionState(BaseModel):
    """State of a companion."""
    relationship: float
    assistanceUsed: int


class SaveGameStateRequest(BaseModel):
    """Request model for saving game state."""
    playerId: str = Field(..., description="Unique identifier for the player")
    sessionId: str = Field(..., description="Current game session identifier")
    timestamp: datetime = Field(..., description="Time when the save was created")
    location: Location = Field(..., description="Player's current location")
    questState: QuestState = Field(..., description="Current quest state")
    inventory: Optional[List[str]] = Field(default=[], description="Items in player's inventory")
    gameFlags: Optional[Dict[str, Any]] = Field(default={}, description="Game state flags")
    companions: Optional[Dict[str, CompanionState]] = Field(default={}, description="Companion states")

    @field_validator('playerId')
    def validate_player_id(cls, v):
        if len(v) < 3:
            raise ValueError("Player ID must be at least 3 characters long")
        return v


class SaveGameStateResponse(BaseModel):
    """Response model for saving game state."""
    success: bool = Field(..., description="Whether the save was successful")
    saveId: str = Field(..., description="Unique identifier for the save")
    timestamp: datetime = Field(..., description="Time when the save was created")


class SaveMetadata(BaseModel):
    """Metadata for a saved game."""
    saveId: str
    timestamp: datetime
    location: str
    questName: str
    level: Optional[str] = None


class ListSavedGamesResponse(BaseModel):
    """Response model for listing saved games."""
    playerId: str
    saves: List[SaveMetadata]


class LoadGameStateResponse(BaseModel):
    """Response model for loading game state."""
    playerId: str
    saveId: str
    sessionId: str
    timestamp: datetime
    lastPlayed: datetime
    location: Location
    questState: QuestState
    inventory: List[str]
    gameFlags: Dict[str, Any]
    companions: Dict[str, CompanionState]


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    message: str
    details: Optional[Any] = None 