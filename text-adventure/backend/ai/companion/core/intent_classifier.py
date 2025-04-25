"""
Text Adventure - Intent Classifier

This module implements the intent classifier for the companion AI system.
It determines the intent, complexity, and processing tier for player requests.
"""

import re
import logging
from typing import Tuple, Dict, Any, List, Optional

from backend.ai.companion.core.models import (
    CompanionRequest,
    IntentCategory,
    ComplexityLevel,
    ProcessingTier
)
from backend.ai.companion.config import TIER_CONFIG


class IntentClassifier:
    """
    Classifies the intent and complexity of player requests.
    
    This class is responsible for:
    1. Determining the intent category of a request
    2. Assessing the complexity of the request
    3. Selecting the appropriate processing tier
    4. Extracting relevant entities from the request
    """
    
    def __init__(self):
        """Initialize the intent classifier."""
        self.logger = logging.getLogger(__name__)
        
        # Intent patterns for basic pattern matching
        self.intent_patterns = {
            IntentCategory.VOCABULARY_HELP: [
                r"what does ['\"](.*?)['\"] mean",
                r"what is the meaning of ['\"](.*?)['\"]",
                r"how do you say (.*?) in japanese",
                r"translate (.*?) to japanese",
                r"what is ['\"](.*?)['\"] in japanese"
            ],
            IntentCategory.GRAMMAR_EXPLANATION: [
                r"how do i use ['\"](.*?)['\"]",
                r"explain (.*?) grammar",
                r"what is the difference between (.*?)\?",
                r"when should i use (.*?)\?",
                r"grammar (.*?)"
            ],
            IntentCategory.DIRECTION_GUIDANCE: [
                r"how do i get to (.*?)\?",
                r"where is (.*?)\?",
                r"which way to (.*?)\?",
                r"find (.*?)",
                r"locate (.*?)"
            ],
            IntentCategory.TRANSLATION_CONFIRMATION: [
                r"translate (.*?)",
                r"what does this (.*?) say",
                r"read this (.*?)",
                r"what is written (.*?)"
            ],
            IntentCategory.GENERAL_HINT: [
                r"what should i do",
                r"what now",
                r"help",
                r"hint",
                r"stuck",
                r"next step"
            ]
        }
        
        # Complexity indicators
        self.complexity_indicators = {
            ComplexityLevel.SIMPLE: [
                # Short queries
                lambda text: len(text.split()) < 8,
                # Basic vocabulary questions
                lambda text: "what does" in text.lower() and "mean" in text.lower(),
                # Simple location questions
                lambda text: "where is" in text.lower(),
                # Basic help requests
                lambda text: text.lower() in ["help", "hint", "what now", "what next"]
            ],
            ComplexityLevel.MODERATE: [
                # Medium length queries
                lambda text: 8 <= len(text.split()) < 15,
                # Comparison questions
                lambda text: "difference between" in text.lower(),
                # Explanations
                lambda text: "explain" in text.lower() or "how does" in text.lower(),
                # Context-dependent questions
                lambda text: "in this context" in text.lower()
            ],
            ComplexityLevel.COMPLEX: [
                # Long queries
                lambda text: len(text.split()) >= 15,
                # Hypothetical scenarios
                lambda text: "if" in text.lower() and "would" in text.lower(),
                # Multiple conditions
                lambda text: text.lower().count("and") + text.lower().count("or") > 2,
                # Advanced grammar
                lambda text: "conditional" in text.lower() or "passive" in text.lower() or "causative" in text.lower()
            ]
        }
    
    def classify(self, request: CompanionRequest) -> Tuple[IntentCategory, ComplexityLevel, ProcessingTier, float, Dict[str, Any]]:
        """
        Classify a player request.
        
        Args:
            request: The request to classify
            
        Returns:
            A tuple containing:
            - The intent category
            - The complexity level
            - The processing tier
            - The confidence score (0-1)
            - Extracted entities
        """
        self.logger.info(f"Classifying request: {request.request_id}")
        
        # Extract the player input
        text = request.player_input.lower()
        
        # Determine the intent
        intent, confidence, entities = self._determine_intent(text, request)
        
        # Determine the complexity
        complexity = self._determine_complexity(text, intent, request)
        
        # Select the processing tier
        tier = self._select_tier(complexity)
        
        self.logger.info(f"Classified as: {intent.value}, {complexity.value}, {tier.value}, {confidence}")
        
        return intent, complexity, tier, confidence, entities
    
    def _determine_intent(self, text: str, request: CompanionRequest) -> Tuple[IntentCategory, float, Dict[str, Any]]:
        """
        Determine the intent of the request.
        
        Args:
            text: The lowercase text of the request
            request: The original request object
            
        Returns:
            A tuple containing:
            - The intent category
            - The confidence score (0-1)
            - Extracted entities
        """
        best_intent = None
        best_confidence = 0.0
        best_entities = {}
        
        # Check request_type for direct mapping
        request_type_mapping = {
            "vocabulary": IntentCategory.VOCABULARY_HELP,
            "grammar": IntentCategory.GRAMMAR_EXPLANATION,
            "direction": IntentCategory.DIRECTION_GUIDANCE,
            "translation": IntentCategory.TRANSLATION_CONFIRMATION,
            "hint": IntentCategory.GENERAL_HINT
        }
        
        if request.request_type in request_type_mapping:
            best_intent = request_type_mapping[request.request_type]
            best_confidence = 0.8  # High confidence for direct mapping
        
        # Pattern matching for more specific intent and entity extraction
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    confidence = 0.9  # High confidence for pattern match
                    
                    # Extract entities
                    entities = {}
                    if match.groups():
                        if intent == IntentCategory.VOCABULARY_HELP:
                            entities["word"] = match.group(1).strip().strip("'\"")
                        elif intent == IntentCategory.GRAMMAR_EXPLANATION:
                            entities["grammar_point"] = match.group(1).strip().strip("'\"")
                        elif intent == IntentCategory.DIRECTION_GUIDANCE:
                            entities["location"] = match.group(1).strip().strip("'\"")
                        elif intent == IntentCategory.TRANSLATION_CONFIRMATION:
                            entities["text"] = match.group(1).strip().strip("'\"")
                    
                    if confidence > best_confidence:
                        best_intent = intent
                        best_confidence = confidence
                        best_entities = entities
        
        # If no intent was determined, use a fallback
        if best_intent is None:
            best_intent = IntentCategory.GENERAL_HINT
            best_confidence = 0.5  # Lower confidence for fallback
        
        # Additional entity extraction for specific intents
        if best_intent == IntentCategory.VOCABULARY_HELP and "word" not in best_entities:
            # Try to extract a word in quotes
            match = re.search(r"['\"]([^'\"]+)['\"]", text)
            if match:
                best_entities["word"] = match.group(1).strip().strip("'\"")
        
        # Additional entity extraction for grammar requests
        if best_intent == IntentCategory.GRAMMAR_EXPLANATION and "grammar_point" not in best_entities:
            # Try to extract a grammar point in quotes
            match = re.search(r"['\"]([^'\"]+)['\"]", text)
            if match:
                best_entities["grammar_point"] = match.group(1).strip().strip("'\"")
            # Try to extract "particle X" pattern
            match = re.search(r"particle ['\"]([^'\"]+)['\"]", text)
            if match:
                best_entities["grammar_point"] = match.group(1).strip().strip("'\"")
        
        # Additional entity extraction for direction requests
        if best_intent == IntentCategory.DIRECTION_GUIDANCE and "location" not in best_entities:
            # Try to extract common location patterns
            match = re.search(r"(platform \d+|ticket (office|counter|machine)|exit|entrance|gate \w+)", text, re.IGNORECASE)
            if match:
                best_entities["location"] = match.group(1).strip().strip("'\"")
        
        return best_intent, best_confidence, best_entities
    
    def _determine_complexity(self, text: str, intent: IntentCategory, request: CompanionRequest) -> ComplexityLevel:
        """
        Determine the complexity of the request.
        
        Args:
            text: The lowercase text of the request
            intent: The determined intent
            request: The original request object
            
        Returns:
            The complexity level
        """
        # Count matches for each complexity level
        complexity_scores = {
            ComplexityLevel.SIMPLE: 0,
            ComplexityLevel.MODERATE: 0,
            ComplexityLevel.COMPLEX: 0
        }
        
        # Check each indicator
        for complexity, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator(text):
                    complexity_scores[complexity] += 1
        
        # Adjust based on intent
        if intent == IntentCategory.VOCABULARY_HELP:
            complexity_scores[ComplexityLevel.SIMPLE] += 1
        elif intent == IntentCategory.GRAMMAR_EXPLANATION:
            complexity_scores[ComplexityLevel.MODERATE] += 1
        
        # Consider game context if available
        if request.game_context:
            # If player is in a complex area, slightly increase complexity
            if request.game_context.player_location in ["platform_transfer", "ticket_office"]:
                complexity_scores[ComplexityLevel.MODERATE] += 0.5
            
            # If player has low language proficiency, decrease complexity
            if request.game_context.language_proficiency.get("vocabulary", 0.5) < 0.3:
                complexity_scores[ComplexityLevel.SIMPLE] += 0.5
        
        # Determine the highest scoring complexity
        max_score = 0
        best_complexity = ComplexityLevel.SIMPLE  # Default to simple
        
        for complexity, score in complexity_scores.items():
            if score > max_score:
                max_score = score
                best_complexity = complexity
        
        return best_complexity
    
    def _select_tier(self, complexity: ComplexityLevel) -> ProcessingTier:
        """
        Select the processing tier based on complexity.
        
        Args:
            complexity: The determined complexity level
            
        Returns:
            The processing tier
        """
        # Direct mapping from complexity to tier
        if complexity == ComplexityLevel.SIMPLE:
            return ProcessingTier.TIER_1
        elif complexity == ComplexityLevel.MODERATE:
            return ProcessingTier.TIER_2
        else:  # ComplexityLevel.COMPLEX
            return ProcessingTier.TIER_3 