"""
Hint Progression Manager for the Companion AI.

This module contains the HintProgressionManager class, which is responsible for
managing the progression of hints provided to the player for different topics.
"""

import logging
import random
from typing import Dict, List, Optional, Any

from backend.ai.companion.core.models import ClassifiedRequest

logger = logging.getLogger(__name__)

# Default hint sequences for common topics
DEFAULT_HINT_SEQUENCES = {
    "buy_ticket": [
        "Look for the ticket machines near the entrance of the station.",
        "On the ticket machine, you can select your destination on the map or use the buttons.",
        "After selecting your destination, the fare will be displayed. Insert money and press the button to get your ticket.",
        "If you're not sure, you can also buy tickets from the station attendant at the ticket counter."
    ],
    "find_platform": [
        "Check the large departure boards in the main concourse for your train and platform number.",
        "Look for signs with your train line's color and name to find the right platform.",
        "If you can't find your platform, look for maps that show the station layout.",
        "Station attendants can help direct you to the right platform if you show them your ticket."
    ],
    "train_schedule": [
        "Train schedules are displayed on electronic boards throughout the station.",
        "Look for your destination to find the next departure times.",
        "The schedule will show the train type, departure time, and platform number.",
        "If your train isn't listed, you might need to check a different board or ask an attendant."
    ],
    "station_facilities": [
        "Most stations have restrooms, vending machines, and convenience stores.",
        "Look for signs with universal symbols to find facilities like restrooms and coin lockers.",
        "Larger stations often have restaurants, shops, and information centers.",
        "If you need assistance, look for the station office or information counter."
    ],
    "transfer_trains": [
        "When transferring, follow the signs for your next train line.",
        "Different train lines often have different colored signs to help you navigate.",
        "You may need to exit through ticket gates and enter a different part of the station.",
        "If your transfer is complex, consider asking a station attendant for directions."
    ]
}

# Generic hints that can be used for any topic
GENERIC_HINTS = [
    "Look for signs in both Japanese and English throughout the station.",
    "Station attendants can usually help if you're having trouble.",
    "Many stations have information counters where you can ask for assistance.",
    "If you're not sure what to do, observe what other passengers are doing.",
    "Most ticket machines have an English language option button."
]


class HintProgressionManager:
    """
    Manages the progression of hints provided to the player.
    
    The HintProgressionManager is responsible for:
    - Storing hint sequences for different topics
    - Tracking which hints have been given to the player
    - Providing the next appropriate hint based on the player's history
    - Customizing hint sequences for specific topics
    
    Hints are provided in a progressive manner, starting with general guidance
    and becoming more specific with each subsequent hint.
    """
    
    def __init__(self):
        """Initialize the HintProgressionManager."""
        # Copy the default hint sequences
        self.hint_sequences = DEFAULT_HINT_SEQUENCES.copy()
        
        # Track hint history for the player
        self.player_hint_history = {}
        
        logger.debug("HintProgressionManager initialized")
    
    def get_next_hint(self, request: ClassifiedRequest, topic: str) -> str:
        """
        Get the next hint for a specific topic.
        
        Args:
            request: The classified request from the player
            topic: The topic to provide a hint for
            
        Returns:
            The next hint in the sequence
        """
        # Initialize history for this topic if it doesn't exist
        if topic not in self.player_hint_history:
            self.player_hint_history[topic] = []
        
        # Get the hint sequence for this topic
        hint_sequence = self.hint_sequences.get(topic)
        
        # If no specific sequence exists, create one from generic hints
        if not hint_sequence:
            # Create a new sequence using generic hints and add it to the sequences
            hint_sequence = GENERIC_HINTS.copy()
            self.hint_sequences[topic] = hint_sequence
            logger.debug(f"Created generic hint sequence for topic: {topic}")
        
        # Determine which hint to provide next
        history = self.player_hint_history[topic]
        hint_index = len(history)
        
        # If we've given all hints, cycle back to the beginning
        if hint_index >= len(hint_sequence):
            hint_index = 0
            logger.debug(f"Cycling back to first hint for topic: {topic}")
        
        # Get the hint
        hint = hint_sequence[hint_index]
        
        # Record that we've given this hint
        self.player_hint_history[topic].append(hint_index)
        
        logger.debug(f"Provided hint {hint_index + 1}/{len(hint_sequence)} for topic: {topic}")
        return hint
    
    def reset_hint_progression(self, topic: str) -> None:
        """
        Reset the hint progression for a specific topic.
        
        Args:
            topic: The topic to reset progression for
        """
        if topic in self.player_hint_history:
            self.player_hint_history[topic] = []
            logger.debug(f"Reset hint progression for topic: {topic}")
    
    def customize_hint_sequence(self, topic: str, hints: List[str]) -> None:
        """
        Customize the hint sequence for a specific topic.
        
        Args:
            topic: The topic to customize hints for
            hints: The list of hints to use for this topic
        """
        if not hints:
            logger.warning(f"Attempted to set empty hint sequence for topic: {topic}")
            return
        
        self.hint_sequences[topic] = hints.copy()
        
        # Reset the hint progression for this topic
        self.reset_hint_progression(topic)
        
        logger.debug(f"Customized hint sequence for topic: {topic} with {len(hints)} hints")
    
    def get_hint_sequence(self, topic: str) -> List[str]:
        """
        Get the full hint sequence for a topic.
        
        Args:
            topic: The topic to get hints for
            
        Returns:
            The list of hints for the topic
        """
        return self.hint_sequences.get(topic, GENERIC_HINTS).copy()
    
    def get_hint_progress(self, topic: str) -> Dict[str, Any]:
        """
        Get the player's progress through the hint sequence for a topic.
        
        Args:
            topic: The topic to get progress for
            
        Returns:
            A dictionary with progress information
        """
        if topic not in self.player_hint_history:
            return {
                "topic": topic,
                "hints_given": 0,
                "total_hints": len(self.hint_sequences.get(topic, GENERIC_HINTS)),
                "completed": False
            }
        
        history = self.player_hint_history[topic]
        total_hints = len(self.hint_sequences.get(topic, GENERIC_HINTS))
        
        return {
            "topic": topic,
            "hints_given": len(history),
            "total_hints": total_hints,
            "completed": len(history) >= total_hints,
            "hint_indices": history
        }
    
    def get_all_topics(self) -> List[str]:
        """
        Get a list of all available hint topics.
        
        Returns:
            A list of topic names
        """
        return list(self.hint_sequences.keys())
    
    def add_hint_to_sequence(self, topic: str, hint: str) -> None:
        """
        Add a new hint to an existing sequence.
        
        Args:
            topic: The topic to add a hint to
            hint: The hint to add
        """
        if topic not in self.hint_sequences:
            self.hint_sequences[topic] = [hint]
            logger.debug(f"Created new hint sequence for topic: {topic}")
        else:
            self.hint_sequences[topic].append(hint)
            logger.debug(f"Added hint to sequence for topic: {topic}")
    
    def clear_player_history(self) -> None:
        """Clear all player hint history."""
        self.player_hint_history = {}
        logger.debug("Cleared all player hint history") 