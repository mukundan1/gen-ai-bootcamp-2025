"""
Text Adventure - Companion AI Data Models

This module defines the data models used by the companion AI system.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import datetime


class IntentCategory(str, Enum):
    """Intent categories for player requests."""
    VOCABULARY_HELP = "vocabulary_help"
    GRAMMAR_EXPLANATION = "grammar_explanation"
    DIRECTION_GUIDANCE = "direction_guidance"
    TRANSLATION_CONFIRMATION = "translation_confirmation"
    GENERAL_HINT = "general_hint"


@dataclass
class Intent:
    """Intent class to represent the intent of a user request."""
    category: IntentCategory
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ComplexityLevel(str, Enum):
    """Complexity levels for processing requests."""
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ProcessingTier(str, Enum):
    """Processing tiers for handling requests."""
    TIER_1 = "tier_1"  # Rule-based
    TIER_2 = "tier_2"  # Local LLM
    TIER_3 = "tier_3"  # Cloud API
    RULE = "rule"      # Fallback rule-based


@dataclass
class GameContext:
    """Current game context information."""
    player_location: str
    current_objective: str
    nearby_npcs: List[str] = field(default_factory=list)
    nearby_objects: List[str] = field(default_factory=list)
    player_inventory: List[str] = field(default_factory=list)
    language_proficiency: Dict[str, float] = field(default_factory=dict)
    game_progress: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompanionRequest:
    """A request to the companion AI."""
    request_id: str
    player_input: str
    request_type: str
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    game_context: Optional[GameContext] = None
    additional_params: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassifiedRequest:
    """
    A request that has been classified with complexity and intent.
    """
    request_id: str
    player_input: str
    request_type: str
    intent: Optional[IntentCategory] = None
    complexity: ComplexityLevel = ComplexityLevel.SIMPLE
    confidence: float = 0.0
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    extracted_entities: Dict[str, Any] = field(default_factory=dict)
    keywords: List[str] = field(default_factory=list)
    related_intents: List[IntentCategory] = field(default_factory=list)
    additional_params: Dict[str, Any] = field(default_factory=dict)
    game_context: Optional[GameContext] = None
    _processing_tier: Optional[ProcessingTier] = field(default=None, repr=False, init=False)
    profile_id: Optional[str] = None
    processing_tier: Optional[ProcessingTier] = field(default=None)
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Store the processing_tier value in the internal field
        self._processing_tier = self.processing_tier
        
    @property
    def processing_tier(self) -> Optional[ProcessingTier]:
        """Get the processing tier from either the stored value or additional_params."""
        if self._processing_tier is not None:
            return self._processing_tier
        
        # Try to get from additional_params
        tier_value = self.additional_params.get("processing_tier")
        if tier_value is not None:
            # Convert from string value to enum if needed
            if isinstance(tier_value, str):
                try:
                    return ProcessingTier[tier_value]
                except KeyError:
                    # Try to match by value instead of name
                    for tier in ProcessingTier:
                        if tier.value == tier_value:
                            return tier
            return tier_value
        
        return None
        
    @processing_tier.setter
    def processing_tier(self, value: ProcessingTier):
        """Set the processing tier and also update additional_params."""
        self._processing_tier = value
        
        # Also update the value in additional_params for consistency
        if value is not None:
            if hasattr(value, 'value'):
                self.additional_params["processing_tier"] = value.value
            else:
                self.additional_params["processing_tier"] = value
    
    @classmethod
    def from_companion_request(cls, request: CompanionRequest, intent: IntentCategory, 
                              complexity: ComplexityLevel, processing_tier: ProcessingTier,
                              confidence: float = 0.0, extracted_entities: Dict[str, Any] = None,
                              keywords: List[str] = None, related_intents: List[IntentCategory] = None):
        """
        Create a ClassifiedRequest from a CompanionRequest.
        
        Args:
            request: The CompanionRequest to convert
            intent: The detected intent
            complexity: The complexity level
            processing_tier: The processing tier to use
            confidence: The confidence score for the classification
            extracted_entities: Entities extracted from the request
            keywords: Keywords extracted from the request
            related_intents: Related or secondary intents
            
        Returns:
            A new ClassifiedRequest instance
        """
        # Get profile_id from additional_params if it exists
        profile_id = request.additional_params.get("profile_id")
        
        return cls(
            request_id=request.request_id,
            player_input=request.player_input,
            request_type=request.request_type,
            intent=intent,
            complexity=complexity,
            processing_tier=processing_tier,
            confidence=confidence or 0.0,
            timestamp=request.timestamp,
            extracted_entities=extracted_entities or {},
            keywords=keywords or [],
            related_intents=related_intents or [],
            additional_params=request.additional_params.copy(),
            profile_id=profile_id,
            game_context=request.game_context
        )


@dataclass
class CompanionResponse:
    """A response from the companion AI."""
    request_id: str
    response_text: str
    intent: IntentCategory
    processing_tier: ProcessingTier
    timestamp: datetime.datetime = field(default_factory=datetime.datetime.now)
    suggested_actions: List[str] = field(default_factory=list)
    learning_cues: Dict[str, Any] = field(default_factory=dict)
    emotion: str = "neutral"
    confidence: float = 1.0
    debug_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationContext:
    """Context for a conversation with the companion."""
    conversation_id: str
    request_history: List[CompanionRequest] = field(default_factory=list)
    response_history: List[CompanionResponse] = field(default_factory=list)
    session_start: datetime.datetime = field(default_factory=datetime.datetime.now)
    last_updated: datetime.datetime = field(default_factory=datetime.datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_interaction(self, request: CompanionRequest, response: CompanionResponse):
        """Add a request-response interaction to the history."""
        self.request_history.append(request)
        self.response_history.append(response)
        self.last_updated = datetime.datetime.now() 