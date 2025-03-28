"""
Personality configuration for the Companion AI.

This module contains classes for defining and managing the companion's personality,
including traits, profiles, and configuration settings.
"""

import json
import os
import logging
from typing import Dict, Any, List, Optional, Union, Set

logger = logging.getLogger(__name__)

# Default personality profile
DEFAULT_PERSONALITY_PROFILE = {
    "name": "Hachiko",
    "description": "A friendly, helpful, and patient companion focused on assisting with Japanese language learning.",
    "traits": {
        "friendliness": 0.8,  # 0.0 = cold, 1.0 = very friendly
        "enthusiasm": 0.7,    # 0.0 = subdued, 1.0 = very enthusiastic
        "helpfulness": 0.9,   # 0.0 = minimal help, 1.0 = very helpful
        "playfulness": 0.6,   # 0.0 = serious, 1.0 = very playful
        "formality": 0.3,     # 0.0 = casual, 1.0 = very formal
        "patience": 0.8,      # 0.0 = impatient, 1.0 = very patient
        "curiosity": 0.6      # 0.0 = incurious, 1.0 = very curious
    },
    "voice_style": "warm and encouraging",
    "language_style": {
        "greeting_style": "warm",
        "explanation_style": "clear and simple",
        "encouragement_style": "supportive"
    },
    "behavioral_tendencies": {
        "asks_follow_up_questions": 0.7,
        "provides_examples": 0.8,
        "uses_humor": 0.6,
        "shows_empathy": 0.8
    },
    "adaptation_settings": {
        "adapt_to_player_language_level": True,
        "adapt_to_player_progress": True,
        "adapt_to_player_mood": True,
        "adaptation_rate": 0.3
    }
}


class PersonalityTrait:
    """
    Represents a single personality trait with a value and valid range.
    
    Attributes:
        name: The name of the trait
        value: The current value of the trait
        min_value: The minimum allowed value
        max_value: The maximum allowed value
    """
    
    def __init__(self, name: str, value: float, min_value: float = 0.0, max_value: float = 1.0):
        """
        Initialize a personality trait.
        
        Args:
            name: The name of the trait
            value: The initial value of the trait
            min_value: The minimum allowed value (default: 0.0)
            max_value: The maximum allowed value (default: 1.0)
        """
        self.name = name
        self.min_value = min_value
        self.max_value = max_value
        self._value = 0.0  # Initial value before clamping
        self.value = value  # This will use the setter which clamps the value
    
    @property
    def value(self) -> float:
        """Get the current trait value."""
        return self._value
    
    @value.setter
    def value(self, new_value: float):
        """
        Set the trait value, clamping it to the valid range.
        
        Args:
            new_value: The new value to set
        """
        self._value = max(self.min_value, min(self.max_value, new_value))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the trait to a dictionary representation.
        
        Returns:
            A dictionary containing the trait's properties
        """
        return {
            "name": self.name,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityTrait':
        """
        Create a trait from a dictionary representation.
        
        Args:
            data: A dictionary containing the trait's properties
            
        Returns:
            A new PersonalityTrait instance
        """
        return cls(
            name=data["name"],
            value=data["value"],
            min_value=data.get("min_value", 0.0),
            max_value=data.get("max_value", 1.0)
        )


class PersonalityProfile:
    """
    Represents a complete personality profile with multiple traits and settings.
    
    Attributes:
        name: The name of the profile
        description: A description of the profile
        traits: A dictionary of personality traits
        voice_style: The style of voice for the companion
        language_style: Settings for language style
        behavioral_tendencies: Settings for behavioral tendencies
        adaptation_settings: Settings for adaptation to player
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        traits: Optional[Dict[str, PersonalityTrait]] = None,
        voice_style: str = "",
        language_style: Optional[Dict[str, str]] = None,
        behavioral_tendencies: Optional[Dict[str, float]] = None,
        adaptation_settings: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a personality profile.
        
        Args:
            name: The name of the profile
            description: A description of the profile
            traits: A dictionary of personality traits
            voice_style: The style of voice for the companion
            language_style: Settings for language style
            behavioral_tendencies: Settings for behavioral tendencies
            adaptation_settings: Settings for adaptation to player
        """
        self.name = name
        self.description = description
        self.traits = traits or {}
        self.voice_style = voice_style
        self.language_style = language_style or {}
        self.behavioral_tendencies = behavioral_tendencies or {}
        self.adaptation_settings = adaptation_settings or {}
    
    def get_trait_value(self, trait_name: str) -> float:
        """
        Get the value of a specific trait.
        
        Args:
            trait_name: The name of the trait
            
        Returns:
            The trait value, or 0.5 if the trait doesn't exist
        """
        if trait_name in self.traits:
            return self.traits[trait_name].value
        return 0.5  # Default middle value
    
    def set_trait_value(self, trait_name: str, value: float):
        """
        Set the value of a specific trait.
        
        Args:
            trait_name: The name of the trait
            value: The new value to set
        """
        if trait_name in self.traits:
            self.traits[trait_name].value = value
        else:
            # Create a new trait if it doesn't exist
            self.traits[trait_name] = PersonalityTrait(trait_name, value)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the profile to a dictionary representation.
        
        Returns:
            A dictionary containing the profile's properties
        """
        # Convert traits to a simple dictionary of name -> value
        traits_dict = {name: trait.value for name, trait in self.traits.items()}
        
        return {
            "name": self.name,
            "description": self.description,
            "traits": traits_dict,
            "voice_style": self.voice_style,
            "language_style": self.language_style,
            "behavioral_tendencies": self.behavioral_tendencies,
            "adaptation_settings": self.adaptation_settings
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonalityProfile':
        """
        Create a profile from a dictionary representation.
        
        Args:
            data: A dictionary containing the profile's properties
            
        Returns:
            A new PersonalityProfile instance
        """
        # Convert simple trait values to PersonalityTrait objects
        traits = {}
        if "traits" in data:
            for name, value in data["traits"].items():
                traits[name] = PersonalityTrait(name, value)
        
        return cls(
            name=data.get("name", "Unnamed Profile"),
            description=data.get("description", ""),
            traits=traits,
            voice_style=data.get("voice_style", ""),
            language_style=data.get("language_style", {}),
            behavioral_tendencies=data.get("behavioral_tendencies", {}),
            adaptation_settings=data.get("adaptation_settings", {})
        )


class PersonalityConfig:
    """
    Manages personality profiles and configuration.
    
    This class is responsible for loading, saving, and managing personality profiles,
    as well as providing access to the active profile.
    """
    
    def __init__(self):
        """Initialize the personality configuration with default settings."""
        self._profiles = {}
        self._active_profile_name = "default"
        
        # Create the default profile
        self.add_profile("default", DEFAULT_PERSONALITY_PROFILE)
    
    def add_profile(self, profile_name: str, profile_data: Union[Dict[str, Any], PersonalityProfile]):
        """
        Add a new personality profile.
        
        Args:
            profile_name: The name to use for the profile
            profile_data: The profile data, either as a dictionary or PersonalityProfile
        """
        if isinstance(profile_data, dict):
            profile = PersonalityProfile.from_dict(profile_data)
        else:
            profile = profile_data
        
        self._profiles[profile_name] = profile
        logger.debug(f"Added personality profile: {profile_name}")
    
    def get_profile(self, profile_name: str) -> Optional[PersonalityProfile]:
        """
        Get a specific personality profile.
        
        Args:
            profile_name: The name of the profile to get
            
        Returns:
            The requested profile, or None if it doesn't exist
        """
        return self._profiles.get(profile_name)
    
    def get_available_profiles(self) -> Set[str]:
        """
        Get the names of all available profiles.
        
        Returns:
            A set of profile names
        """
        return set(self._profiles.keys())
    
    def set_active_profile(self, profile_name: str) -> bool:
        """
        Set the active personality profile.
        
        Args:
            profile_name: The name of the profile to set as active
            
        Returns:
            True if successful, False if the profile doesn't exist
        """
        if profile_name in self._profiles:
            self._active_profile_name = profile_name
            logger.info(f"Set active personality profile to: {profile_name}")
            return True
        return False
    
    def get_active_profile_name(self) -> str:
        """
        Get the name of the active profile.
        
        Returns:
            The name of the active profile
        """
        return self._active_profile_name
    
    def get_active_profile(self) -> PersonalityProfile:
        """
        Get the active personality profile.
        
        Returns:
            The active profile
        """
        return self._profiles[self._active_profile_name]
    
    def get_trait_value(self, trait_name: str) -> float:
        """
        Get a trait value from the active profile.
        
        Args:
            trait_name: The name of the trait
            
        Returns:
            The trait value
        """
        return self.get_active_profile().get_trait_value(trait_name)
    
    def set_trait_value(self, trait_name: str, value: float):
        """
        Set a trait value in the active profile.
        
        Args:
            trait_name: The name of the trait
            value: The new value to set
        """
        self.get_active_profile().set_trait_value(trait_name, value)
    
    def save_to_file(self, file_path: str):
        """
        Save all profiles to a JSON file.
        
        Args:
            file_path: The path to save the file to
        """
        data = {
            "active_profile": self._active_profile_name,
            "profiles": {name: profile.to_dict() for name, profile in self._profiles.items()}
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved personality configuration to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save personality configuration: {e}")
    
    def load_from_file(self, file_path: str) -> bool:
        """
        Load profiles from a JSON file.
        
        Args:
            file_path: The path to load the file from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Clear existing profiles (except default)
            default_profile = self._profiles.get("default")
            self._profiles = {}
            if default_profile:
                self._profiles["default"] = default_profile
            
            # Load profiles from file
            for name, profile_data in data.get("profiles", {}).items():
                self.add_profile(name, profile_data)
            
            # Set active profile
            active_profile = data.get("active_profile")
            if active_profile and active_profile in self._profiles:
                self._active_profile_name = active_profile
            
            logger.info(f"Loaded personality configuration from: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load personality configuration: {e}")
            return False 