"""
Personality Engine for the Companion AI.

This module contains the PersonalityEngine class, which is responsible for
managing the companion's personality, including adaptation to the player's
behavior and preferences.
"""

import logging
import os
import random
from typing import Dict, Any, Optional, List, Tuple

from backend.ai.companion.core.models import ClassifiedRequest, CompanionResponse
from backend.ai.companion.personality.config import PersonalityConfig, PersonalityProfile

logger = logging.getLogger(__name__)


class PersonalityEngine:
    """
    Manages the companion's personality and adaptation.
    
    The PersonalityEngine is responsible for:
    - Loading and managing personality profiles
    - Adapting the companion's personality based on player interactions
    - Providing personality information to the response formatter
    - Tracking player preferences and adjusting accordingly
    
    It uses the PersonalityConfig to store and retrieve personality profiles.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the PersonalityEngine.
        
        Args:
            config_path: Optional path to a personality configuration file
        """
        self.config = PersonalityConfig()
        
        # Load configuration from file if provided
        if config_path and os.path.exists(config_path):
            self.config.load_from_file(config_path)
            logger.info(f"Loaded personality configuration from {config_path}")
        else:
            logger.info("Using default personality configuration")
        
        # Track player preferences and interaction history
        self.player_preferences = {
            "formality_preference": 0.5,  # 0.0 = casual, 1.0 = formal
            "detail_preference": 0.5,     # 0.0 = concise, 1.0 = detailed
            "humor_preference": 0.5,      # 0.0 = serious, 1.0 = humorous
            "learning_style": "balanced"  # visual, auditory, kinesthetic, balanced
        }
        
        # Interaction tracking
        self.interaction_count = 0
        self.positive_interactions = 0
        self.negative_interactions = 0
        self.topic_interests = {}  # Track topics the player seems interested in
        
        logger.debug("PersonalityEngine initialized")
    
    def get_active_profile(self) -> PersonalityProfile:
        """
        Get the currently active personality profile.
        
        Returns:
            The active personality profile
        """
        return self.config.get_active_profile()
    
    def set_active_profile(self, profile_name: str) -> bool:
        """
        Set the active personality profile.
        
        Args:
            profile_name: The name of the profile to activate
            
        Returns:
            True if the profile was activated, False otherwise
        """
        success = self.config.set_active_profile(profile_name)
        if success:
            logger.info(f"Activated personality profile: {profile_name}")
        else:
            logger.warning(f"Failed to activate personality profile: {profile_name}")
        return success
    
    def get_available_profiles(self) -> List[str]:
        """
        Get a list of available personality profiles.
        
        Returns:
            A list of profile names
        """
        return list(self.config.get_available_profiles())
    
    def create_profile(self, profile_name: str, traits: Dict[str, float]) -> bool:
        """
        Create a new personality profile.
        
        Args:
            profile_name: The name for the new profile
            traits: A dictionary of personality traits and their values
            
        Returns:
            True if the profile was created, False otherwise
        """
        if profile_name in self.config.get_available_profiles():
            logger.warning(f"Profile {profile_name} already exists")
            return False
        
        profile_data = {
            "name": profile_name,
            "description": f"Custom profile: {profile_name}",
            "traits": traits
        }
        
        self.config.add_profile(profile_name, profile_data)
        logger.info(f"Created new personality profile: {profile_name}")
        return True
    
    def save_configuration(self, config_path: str) -> bool:
        """
        Save the current personality configuration to a file.
        
        Args:
            config_path: The path to save the configuration to
            
        Returns:
            True if the configuration was saved, False otherwise
        """
        try:
            self.config.save_to_file(config_path)
            logger.info(f"Saved personality configuration to {config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save personality configuration: {e}")
            return False
    
    def process_player_feedback(self, request_id: str, feedback: str, rating: int) -> None:
        """
        Process feedback from the player about a response.
        
        Args:
            request_id: The ID of the request that generated the response
            feedback: The feedback text from the player
            rating: A rating from 1-5 (1=negative, 5=positive)
        """
        self.interaction_count += 1
        
        # Track positive/negative interactions
        if rating >= 4:
            self.positive_interactions += 1
        elif rating <= 2:
            self.negative_interactions += 1
        
        # Analyze feedback for preferences
        feedback_lower = feedback.lower()
        
        # Check for formality preferences
        if any(word in feedback_lower for word in ["formal", "professional", "serious"]):
            self._adjust_preference("formality_preference", 0.1)
        elif any(word in feedback_lower for word in ["casual", "friendly", "relaxed"]):
            self._adjust_preference("formality_preference", -0.1)
        
        # Check for detail preferences
        if any(word in feedback_lower for word in ["detail", "thorough", "comprehensive"]):
            self._adjust_preference("detail_preference", 0.1)
        elif any(word in feedback_lower for word in ["brief", "concise", "short"]):
            self._adjust_preference("detail_preference", -0.1)
        
        # Check for humor preferences
        if any(word in feedback_lower for word in ["funny", "humor", "joke"]):
            self._adjust_preference("humor_preference", 0.1)
        elif any(word in feedback_lower for word in ["serious", "straightforward"]):
            self._adjust_preference("humor_preference", -0.1)
        
        logger.debug(f"Processed player feedback for request {request_id}: rating={rating}")
    
    def adapt_to_player(self, frequency: int = 10) -> bool:
        """
        Adapt the companion's personality based on player interactions.
        
        This method is called periodically to adjust the personality traits
        based on the player's preferences and interaction history.
        
        Args:
            frequency: How often to adapt (every N interactions)
            
        Returns:
            True if adaptation occurred, False otherwise
        """
        # Only adapt every N interactions
        if self.interaction_count % frequency != 0 or self.interaction_count == 0:
            return False
        
        active_profile = self.get_active_profile()
        
        # Calculate adaptation strength based on interaction count
        # (stronger adaptation early on, then more stable)
        adaptation_strength = min(0.1, 1.0 / (self.interaction_count / 10 + 1))
        
        # Adapt formality based on player preference
        formality_target = self.player_preferences["formality_preference"]
        current_formality = active_profile.get_trait_value("formality")
        new_formality = self._adapt_trait_value(current_formality, formality_target, adaptation_strength)
        active_profile.set_trait_value("formality", new_formality)
        
        # Adapt enthusiasm based on positive/negative interactions
        if self.interaction_count > 0:
            positivity_ratio = self.positive_interactions / self.interaction_count
            enthusiasm_target = 0.5 + (positivity_ratio - 0.5) * 0.5  # Map to 0.25-0.75 range
            current_enthusiasm = active_profile.get_trait_value("enthusiasm")
            new_enthusiasm = self._adapt_trait_value(current_enthusiasm, enthusiasm_target, adaptation_strength)
            active_profile.set_trait_value("enthusiasm", new_enthusiasm)
        
        # Adapt playfulness based on humor preference
        playfulness_target = self.player_preferences["humor_preference"]
        current_playfulness = active_profile.get_trait_value("playfulness")
        new_playfulness = self._adapt_trait_value(current_playfulness, playfulness_target, adaptation_strength)
        active_profile.set_trait_value("playfulness", new_playfulness)
        
        logger.info(f"Adapted personality after {self.interaction_count} interactions")
        return True
    
    def analyze_request(self, request: ClassifiedRequest) -> Dict[str, Any]:
        """
        Analyze a player request to extract personality-relevant information.
        
        Args:
            request: The classified request from the player
            
        Returns:
            A dictionary of personality-relevant information
        """
        # Extract the intent and entities
        intent = getattr(request, 'intent', None)
        entities = getattr(request, 'extracted_entities', {}) or {}
        
        # Track topic interests
        if intent:
            self.topic_interests[intent] = self.topic_interests.get(intent, 0) + 1
        
        # Analyze the request text for personality cues
        request_text = request.player_input.lower()
        
        # Check for formality cues
        formality_cues = {
            "formal": ["please", "could you", "would you", "formal", "proper"],
            "casual": ["hey", "yo", "sup", "casual", "chill"]
        }
        
        formality_score = 0.5  # Default neutral
        formal_matches = sum(1 for cue in formality_cues["formal"] if cue in request_text)
        casual_matches = sum(1 for cue in formality_cues["casual"] if cue in request_text)
        
        if formal_matches > casual_matches:
            formality_score = 0.7
        elif casual_matches > formal_matches:
            formality_score = 0.3
        
        # Check for detail preference cues
        detail_cues = {
            "detailed": ["detail", "explain", "thorough", "comprehensive"],
            "concise": ["brief", "quick", "short", "simple"]
        }
        
        detail_score = 0.5  # Default neutral
        detailed_matches = sum(1 for cue in detail_cues["detailed"] if cue in request_text)
        concise_matches = sum(1 for cue in detail_cues["concise"] if cue in request_text)
        
        if detailed_matches > concise_matches:
            detail_score = 0.7
        elif concise_matches > detailed_matches:
            detail_score = 0.3
        
        return {
            "formality_cue": formality_score,
            "detail_preference": detail_score,
            "topic": intent,
            "entities": entities
        }
    
    def enhance_response(self, response: CompanionResponse, analysis: Dict[str, Any]) -> CompanionResponse:
        """
        Enhance a response with personality-based modifications.
        
        Args:
            response: The response to enhance
            analysis: The analysis of the request
            
        Returns:
            The enhanced response
        """
        # Get the active personality profile
        profile = self.get_active_profile()
        
        # Adjust response based on formality cue
        formality_cue = analysis.get("formality_cue", 0.5)
        formality_trait = profile.get_trait_value("formality")
        
        # Blend the profile's formality with the detected cue
        effective_formality = (formality_trait * 0.7) + (formality_cue * 0.3)
        
        # Modify the response based on effective formality
        if effective_formality > 0.7:
            # More formal response
            response.suggested_emotion = "neutral"
        elif effective_formality < 0.3:
            # More casual response
            response.suggested_emotion = random.choice(["happy", "excited"])
        else:
            # Neutral formality
            response.suggested_emotion = random.choice(["neutral", "happy"])
        
        # Adjust response based on detail preference
        detail_preference = analysis.get("detail_preference", 0.5)
        
        # Add learning cues based on detail preference
        response.add_learning_cues = detail_preference > 0.5
        
        # Add suggested actions based on helpfulness trait
        helpfulness = profile.get_trait_value("helpfulness")
        if helpfulness > 0.6 and not response.suggested_actions:
            # Generate some generic suggested actions based on the topic
            topic = analysis.get("topic")
            if topic:
                response.suggested_actions = self._generate_suggested_actions(topic)
        
        return response
    
    def _adjust_preference(self, preference: str, adjustment: float) -> None:
        """
        Adjust a player preference value, keeping it within 0-1 range.
        
        Args:
            preference: The preference to adjust
            adjustment: The amount to adjust by (positive or negative)
        """
        if preference in self.player_preferences:
            current = self.player_preferences[preference]
            self.player_preferences[preference] = max(0.0, min(1.0, current + adjustment))
            logger.debug(f"Adjusted {preference} from {current} to {self.player_preferences[preference]}")
    
    def _adapt_trait_value(self, current: float, target: float, strength: float) -> float:
        """
        Adapt a trait value towards a target value with a given strength.
        
        Args:
            current: The current trait value
            target: The target trait value
            strength: The adaptation strength (0-1)
            
        Returns:
            The new trait value
        """
        # Move the current value towards the target by the strength amount
        return current + (target - current) * strength
    
    def _generate_suggested_actions(self, topic: Any) -> List[str]:
        """
        Generate suggested actions based on a topic.
        
        Args:
            topic: The topic to generate actions for
            
        Returns:
            A list of suggested actions
        """
        # Generic suggested actions based on intent category
        if topic == "VOCABULARY_HELP":
            return [
                "Try using this word in a sentence.",
                "Look for this word on signs at the station.",
                "Practice saying this word out loud."
            ]
        elif topic == "GRAMMAR_EXPLANATION":
            return [
                "Try making your own sentence with this grammar pattern.",
                "Listen for this pattern in station announcements.",
                "Practice this pattern with different vocabulary."
            ]
        elif topic == "DIRECTION_GUIDANCE":
            return [
                "Look for the station map near the ticket gates.",
                "Check the color-coded signs for your train line.",
                "Ask a station attendant if you're still unsure."
            ]
        elif topic == "TRANSLATION_CONFIRMATION":
            return [
                "Practice saying the Japanese phrase out loud.",
                "Try using this phrase when speaking with station staff.",
                "Write down this phrase for future reference."
            ]
        else:
            return [
                "Try practicing what you've learned in a real conversation.",
                "Look for examples of this in the train station.",
                "Take notes to help remember this information."
            ] 