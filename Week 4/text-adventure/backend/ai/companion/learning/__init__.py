"""
Learning Assistance module for the Companion AI.

This module contains classes and functions for managing the learning assistance
features of the companion AI, including hint progression, vocabulary tracking,
grammar explanation templates, and learning pace adaptation.
"""

from backend.ai.companion.learning.hint_progression import HintProgressionManager
from backend.ai.companion.learning.vocabulary_tracker import VocabularyTracker
from backend.ai.companion.learning.grammar_templates import GrammarTemplateManager
from backend.ai.companion.learning.learning_pace import LearningPaceAdapter

__all__ = [
    'HintProgressionManager',
    'VocabularyTracker',
    'GrammarTemplateManager',
    'LearningPaceAdapter'
] 