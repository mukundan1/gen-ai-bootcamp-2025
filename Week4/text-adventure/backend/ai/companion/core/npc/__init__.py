"""
NPC module for the Text Adventure.

This module provides classes for NPC profiles and interactions.
"""

from backend.ai.companion.core.npc.profile import NPCProfile, NPCProfileRegistry
from backend.ai.companion.core.npc.profile_loader import ProfileLoader

__all__ = ["NPCProfile", "NPCProfileRegistry", "ProfileLoader"] 