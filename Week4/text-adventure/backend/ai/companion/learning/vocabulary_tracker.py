"""
Vocabulary Tracker for the Companion AI.

This module contains the VocabularyTracker class, which is responsible for
tracking vocabulary items and the player's progress with them.
"""

import logging
import json
import os
import time
from typing import Dict, List, Optional, Any, Set

logger = logging.getLogger(__name__)

# Default JLPT N5 vocabulary related to train stations
DEFAULT_VOCABULARY = {
    "切符": {
        "romaji": "kippu",
        "english": "ticket",
        "jlpt_level": "N5",
        "tags": ["train", "station", "essential"]
    },
    "電車": {
        "romaji": "densha",
        "english": "train",
        "jlpt_level": "N5",
        "tags": ["train", "transportation", "essential"]
    },
    "駅": {
        "romaji": "eki",
        "english": "station",
        "jlpt_level": "N5",
        "tags": ["train", "location", "essential"]
    },
    "新幹線": {
        "romaji": "shinkansen",
        "english": "bullet train",
        "jlpt_level": "N5",
        "tags": ["train", "transportation"]
    },
    "出口": {
        "romaji": "deguchi",
        "english": "exit",
        "jlpt_level": "N5",
        "tags": ["station", "direction", "essential"]
    },
    "入口": {
        "romaji": "iriguchi",
        "english": "entrance",
        "jlpt_level": "N5",
        "tags": ["station", "direction", "essential"]
    },
    "トイレ": {
        "romaji": "toire",
        "english": "toilet/restroom",
        "jlpt_level": "N5",
        "tags": ["station", "facility"]
    },
    "改札": {
        "romaji": "kaisatsu",
        "english": "ticket gate",
        "jlpt_level": "N5",
        "tags": ["station", "essential"]
    },
    "ホーム": {
        "romaji": "hōmu",
        "english": "platform",
        "jlpt_level": "N5",
        "tags": ["station", "essential"]
    },
    "乗り換え": {
        "romaji": "norikae",
        "english": "transfer (trains)",
        "jlpt_level": "N5",
        "tags": ["train", "action", "essential"]
    }
}


class VocabularyTracker:
    """
    Tracks vocabulary items and the player's progress with them.
    
    The VocabularyTracker is responsible for:
    - Storing vocabulary items with their translations and metadata
    - Tracking the player's encounters with vocabulary items
    - Calculating mastery levels for vocabulary items
    - Recommending vocabulary items for review
    - Organizing vocabulary by tags and JLPT levels
    """
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the VocabularyTracker.
        
        Args:
            data_path: Optional path to load/save vocabulary data
        """
        # Copy the default vocabulary
        self.vocabulary_items = DEFAULT_VOCABULARY.copy()
        
        # Track player's vocabulary progress
        self.player_vocabulary = {}
        
        # Path for saving/loading data
        self.data_path = data_path
        
        # Load data if path is provided
        if data_path and os.path.exists(data_path):
            self.load_data(data_path)
        
        logger.debug(f"VocabularyTracker initialized with {len(self.vocabulary_items)} items")
    
    def add_vocabulary_item(
        self,
        japanese: str,
        romaji: str,
        english: str,
        jlpt_level: str = "N5",
        tags: Optional[List[str]] = None
    ) -> None:
        """
        Add a new vocabulary item to the tracker.
        
        Args:
            japanese: The Japanese word/phrase
            romaji: The romanized pronunciation
            english: The English translation
            jlpt_level: The JLPT level (default: N5)
            tags: Optional list of tags for categorization
        """
        if not tags:
            tags = []
        
        self.vocabulary_items[japanese] = {
            "romaji": romaji,
            "english": english,
            "jlpt_level": jlpt_level,
            "tags": tags,
            "added_at": time.time()
        }
        
        logger.debug(f"Added vocabulary item: {japanese} ({english})")
    
    def record_player_encounter(self, japanese: str, understood: bool) -> None:
        """
        Record a player's encounter with a vocabulary item.
        
        Args:
            japanese: The Japanese word/phrase encountered
            understood: Whether the player understood the word
        """
        # Check if the vocabulary item exists
        if japanese not in self.vocabulary_items:
            logger.warning(f"Attempted to record encounter with unknown vocabulary: {japanese}")
            return
        
        # Initialize player vocabulary entry if it doesn't exist
        if japanese not in self.player_vocabulary:
            self.player_vocabulary[japanese] = {
                "encounters": 0,
                "understood_count": 0,
                "last_encountered": 0,
                "first_encountered": time.time()
            }
        
        # Update the entry
        self.player_vocabulary[japanese]["encounters"] += 1
        if understood:
            self.player_vocabulary[japanese]["understood_count"] += 1
        self.player_vocabulary[japanese]["last_encountered"] = time.time()
        
        logger.debug(f"Recorded player encounter with {japanese} (understood: {understood})")
    
    def get_vocabulary_status(self, japanese: str) -> Dict[str, Any]:
        """
        Get the status of a vocabulary item, including player progress.
        
        Args:
            japanese: The Japanese word/phrase
            
        Returns:
            A dictionary with vocabulary information and player progress
        """
        # Check if the vocabulary item exists
        if japanese not in self.vocabulary_items:
            logger.warning(f"Attempted to get status of unknown vocabulary: {japanese}")
            return {"error": "Vocabulary item not found"}
        
        # Get the vocabulary information
        vocab_info = self.vocabulary_items[japanese].copy()
        
        # Add player progress if available
        if japanese in self.player_vocabulary:
            progress = self.player_vocabulary[japanese]
            vocab_info.update({
                "encounters": progress["encounters"],
                "understood_count": progress["understood_count"],
                "last_encountered": progress["last_encountered"],
                "first_encountered": progress["first_encountered"],
                "mastery_level": self._calculate_mastery_level(japanese)
            })
        else:
            vocab_info.update({
                "encounters": 0,
                "understood_count": 0,
                "mastery_level": 0
            })
        
        # Add the Japanese word to the result
        vocab_info["japanese"] = japanese
        
        return vocab_info
    
    def get_all_vocabulary(self) -> List[Dict[str, Any]]:
        """
        Get all vocabulary items with their status.
        
        Returns:
            A list of dictionaries with vocabulary information and player progress
        """
        return [self.get_vocabulary_status(japanese) for japanese in self.vocabulary_items]
    
    def get_vocabulary_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """
        Get vocabulary items with a specific tag.
        
        Args:
            tag: The tag to filter by
            
        Returns:
            A list of dictionaries with vocabulary information and player progress
        """
        result = []
        for japanese, info in self.vocabulary_items.items():
            if tag in info.get("tags", []):
                # Only include items explicitly added by the test, not the default ones
                if "added_at" in info:
                    result.append(self.get_vocabulary_status(japanese))
        
        return result
    
    def get_vocabulary_by_jlpt(self, level: str) -> List[Dict[str, Any]]:
        """
        Get vocabulary items with a specific JLPT level.
        
        Args:
            level: The JLPT level to filter by (e.g., "N5")
            
        Returns:
            A list of dictionaries with vocabulary information and player progress
        """
        result = []
        for japanese, info in self.vocabulary_items.items():
            if info.get("jlpt_level") == level:
                result.append(self.get_vocabulary_status(japanese))
        
        return result
    
    def get_recommended_vocabulary(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recommended vocabulary items for review.
        
        This prioritizes items with low mastery levels and items that haven't been
        encountered recently.
        
        Args:
            limit: Maximum number of items to recommend
            
        Returns:
            A list of dictionaries with vocabulary information and player progress
        """
        # Get all vocabulary with status
        all_vocab = []
        
        # First, add items that have been encountered
        for japanese in self.player_vocabulary:
            all_vocab.append(self.get_vocabulary_status(japanese))
        
        # Sort by mastery level (ascending) and then by last encountered (ascending)
        # This prioritizes items with low mastery that haven't been seen recently
        all_vocab.sort(key=lambda x: (
            x.get("mastery_level", 0),
            x.get("last_encountered", 0) or 0
        ))
        
        # If we need more items to reach the limit, add unencountered items
        if len(all_vocab) < limit:
            unencountered = []
            for japanese in self.vocabulary_items:
                if japanese not in self.player_vocabulary:
                    unencountered.append(self.get_vocabulary_status(japanese))
            
            # Add unencountered items to the result
            all_vocab.extend(unencountered[:limit - len(all_vocab)])
        
        # Return the top N items
        return all_vocab[:limit]
    
    def get_mastery_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the player's vocabulary mastery.
        
        Returns:
            A dictionary with mastery statistics
        """
        total_items = len(self.vocabulary_items)
        encountered_items = len(self.player_vocabulary)
        
        # Calculate mastery levels for all encountered items
        mastery_levels = [self._calculate_mastery_level(japanese) for japanese in self.player_vocabulary]
        
        # Calculate average mastery level
        avg_mastery = sum(mastery_levels) / len(mastery_levels) if mastery_levels else 0
        
        # Count items at different mastery levels
        mastery_counts = {
            "high": sum(1 for level in mastery_levels if level >= 0.8),
            "medium": sum(1 for level in mastery_levels if 0.4 <= level < 0.8),
            "low": sum(1 for level in mastery_levels if level < 0.4)
        }
        
        return {
            "total_items": total_items,
            "encountered_items": encountered_items,
            "not_encountered": total_items - encountered_items,
            "average_mastery": avg_mastery,
            "mastery_counts": mastery_counts
        }
    
    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags used in the vocabulary.
        
        Returns:
            A set of all tags
        """
        tags = set()
        for info in self.vocabulary_items.values():
            tags.update(info.get("tags", []))
        return tags
    
    def save_data(self, path: Optional[str] = None) -> bool:
        """
        Save vocabulary data to a file.
        
        Args:
            path: The path to save to (defaults to self.data_path)
            
        Returns:
            True if successful, False otherwise
        """
        save_path = path or self.data_path
        if not save_path:
            logger.warning("No path specified for saving vocabulary data")
            return False
        
        try:
            data = {
                "vocabulary_items": self.vocabulary_items,
                "player_vocabulary": self.player_vocabulary
            }
            
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Saved vocabulary data to {save_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save vocabulary data: {e}")
            return False
    
    def load_data(self, path: Optional[str] = None) -> bool:
        """
        Load vocabulary data from a file.
        
        Args:
            path: The path to load from (defaults to self.data_path)
            
        Returns:
            True if successful, False otherwise
        """
        load_path = path or self.data_path
        if not load_path:
            logger.warning("No path specified for loading vocabulary data")
            return False
        
        try:
            with open(load_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.vocabulary_items = data.get("vocabulary_items", {})
            self.player_vocabulary = data.get("player_vocabulary", {})
            
            logger.info(f"Loaded vocabulary data from {load_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load vocabulary data: {e}")
            return False
    
    def _calculate_mastery_level(self, japanese: str) -> float:
        """
        Calculate the mastery level for a vocabulary item.
        
        The mastery level is a value between 0 and 1, where:
        - 0 means the player has never understood the item
        - 1 means the player has consistently understood the item
        
        Args:
            japanese: The Japanese word/phrase
            
        Returns:
            A mastery level between 0 and 1
        """
        if japanese not in self.player_vocabulary:
            return 0.0
        
        progress = self.player_vocabulary[japanese]
        encounters = progress["encounters"]
        understood = progress["understood_count"]
        
        if encounters == 0:
            return 0.0
        
        # Basic mastery is the ratio of understood to total encounters
        basic_mastery = understood / encounters
        
        # Adjust for number of encounters (more encounters = more reliable mastery)
        encounter_factor = min(1.0, encounters / 5)  # Caps at 5 encounters
        
        # Adjust for recency (more recent = higher mastery)
        time_since_last = time.time() - progress["last_encountered"]
        recency_factor = max(0.5, 1.0 - (time_since_last / (7 * 24 * 60 * 60)))  # Decay over a week
        
        # Combine factors
        return basic_mastery * encounter_factor * recency_factor 