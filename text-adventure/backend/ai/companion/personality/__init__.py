"""
Personality module for the Companion AI.

This module contains classes and functions for managing the companion's
personality traits, profiles, and adaptation mechanisms.
"""

from backend.ai.companion.personality.config import (
    PersonalityConfig,
    PersonalityTrait,
    PersonalityProfile,
    DEFAULT_PERSONALITY_PROFILE
)
from backend.ai.companion.personality.engine import PersonalityEngine

__all__ = [
    'PersonalityConfig',
    'PersonalityTrait',
    'PersonalityProfile',
    'DEFAULT_PERSONALITY_PROFILE',
    'PersonalityEngine'
] 