"""
Text Adventure - Tier 1 Processor Module

This module contains the rule-based processing components for the companion AI system.
It includes the template system, pattern matching, and decision trees for handling
simple requests.
"""

from backend.ai.companion.tier1.template_system import TemplateSystem
from backend.ai.companion.tier1.pattern_matching import PatternMatcher
from backend.ai.companion.tier1.decision_trees import (
    DecisionTree,
    DecisionTreeNavigator,
    DecisionTreeManager,
    DecisionTreeProcessor
)

__all__ = [
    'TemplateSystem',
    'PatternMatcher',
    'DecisionTree',
    'DecisionTreeNavigator',
    'DecisionTreeManager',
    'DecisionTreeProcessor'
] 