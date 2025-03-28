"""
Text Adventure - Tier 1 Processor

This module implements the Tier 1 processor for the companion AI system,
which uses rule-based techniques to generate responses to simple requests.
"""

import logging
import os
import json
import re
from typing import Dict, Any, Optional, List, Match

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    CompanionRequest,
    IntentCategory
)
from backend.ai.companion.core.processor_framework import Processor
from backend.ai.companion.config import get_config

logger = logging.getLogger(__name__)

class Tier1Processor(Processor):
    """
    Tier 1 processor for the companion AI system.
    
    This processor uses rule-based techniques to generate responses to simple
    requests. It is the most limited but also the most reliable and fastest
    processor in the tiered processing framework.
    """
    
    def __init__(self):
        """
        Initialize the Tier 1 processor.
        """
        self.logger = logging.getLogger(__name__)
        self.decision_trees = {}
        
        # Load the configuration - try both with and without underscore
        config = get_config('tier1', {})
        
        # Store the enabled state from the config, with a safe default if config is None
        self.enabled = True if config is None else config.get('enabled', True)
        
        logger.debug(f"Initialized Tier1Processor (enabled: {self.enabled})")
        
        # Handle None config safely
        self.default_model = "rule-based" if config is None else config.get('default_model', "rule-based")
        
        self._load_default_trees()
    
    async def process(self, request: ClassifiedRequest) -> str:
        """
        Process a request using the Tier 1 processor.
        
        Args:
            request: The classified request to process
            
        Returns:
            The generated response
        """
        logger.info(f"Processing request {request.request_id} with Tier 1 processor")
        
        # Check if processor is enabled
        if not self.enabled:
            logger.warning("Tier 1 processor is disabled in configuration")
            return "Tier 1 processor is disabled in configuration"
        
        # Create a companion request from the classified request
        companion_request = self._create_companion_request(request)
        
        # Determine which decision tree to use based on the intent
        tree_name = self._get_tree_name_for_intent(request.intent)
        
        # Load the decision tree
        tree = self._load_decision_tree(tree_name)
        
        if not tree:
            self.logger.warning(f"No decision tree found for intent {request.intent.value}")
            return "I'm sorry, I don't know how to help with that."
        
        # Check if the tree has patterns
        if "patterns" in tree:
            response = self._process_with_patterns(tree, companion_request)
            return str(response)
        
        # Otherwise, use the decision tree nodes
        if "nodes" in tree:
            response = self._process_with_decision_tree(tree, companion_request)
            return str(response)
        
        # If no patterns or nodes, use the default response
        self.logger.warning(f"Decision tree {tree_name} has no patterns or nodes")
        return str(tree.get("default_response", "I'm sorry, I don't know how to help with that."))
    
    def _get_tree_name_for_intent(self, intent: IntentCategory) -> str:
        """
        Get the name of the decision tree to use for a given intent.
        
        Args:
            intent: The intent of the request
            
        Returns:
            The name of the decision tree to use
        """
        # Map intents to decision tree names
        intent_to_tree = {
            IntentCategory.VOCABULARY_HELP: "vocabulary",
            IntentCategory.GRAMMAR_EXPLANATION: "grammar",
            IntentCategory.DIRECTION_GUIDANCE: "directions",
            IntentCategory.TRANSLATION_CONFIRMATION: "translation",
            IntentCategory.GENERAL_HINT: "general"
        }
        
        return intent_to_tree.get(intent, "general")
    
    def _load_decision_tree(self, tree_name: str) -> Dict[str, Any]:
        """
        Load a decision tree from the trees directory.
        
        Args:
            tree_name: The name of the decision tree to load
            
        Returns:
            The loaded decision tree
        """
        # Check if the tree is already loaded
        if tree_name in self.decision_trees:
            return self.decision_trees[tree_name]
        
        # Try to load the tree from the trees directory
        try:
            tree_path = os.path.join(
                os.path.dirname(__file__),
                "trees",
                f"{tree_name}.json"
            )
            
            if os.path.exists(tree_path):
                with open(tree_path, "r") as f:
                    tree = json.load(f)
                
                # Cache the tree
                self.decision_trees[tree_name] = tree
                
                return tree
        except Exception as e:
            self.logger.error(f"Error loading decision tree {tree_name}: {e}")
        
        # If the tree couldn't be loaded, return a default tree
        return self.decision_trees.get(tree_name, {
            "default_response": "I'm sorry, I don't know how to help with that."
        })
    
    def _process_with_patterns(self, tree: Dict[str, Any], request: Dict[str, Any]) -> str:
        """
        Process a request using pattern matching.
        
        Args:
            tree: The decision tree with patterns
            request: The companion request
            
        Returns:
            The generated response
        """
        player_input = request["player_input"].lower()
        
        for pattern_info in tree.get("patterns", []):
            pattern = pattern_info.get("pattern", "")
            
            if not pattern:
                continue
            
            match = re.search(pattern, player_input, re.IGNORECASE)
            
            if match:
                return self._generate_response_from_pattern(pattern_info, match, request)
        
        # If no pattern matched, return the default response
        return tree.get("default_response", "I'm sorry, I don't know how to help with that.")
    
    def _generate_response_from_pattern(
        self,
        pattern_info: Dict[str, Any],
        match: Match,
        request: Dict[str, Any]
    ) -> str:
        """
        Generate a response from a matched pattern.
        
        Args:
            pattern_info: The pattern information
            match: The regex match object
            request: The companion request
            
        Returns:
            The generated response
        """
        response_template = pattern_info.get("response", "")
        
        if not response_template:
            return "I'm sorry, I don't know how to help with that."
        
        # Get the values for the matched groups
        values = pattern_info.get("values", {})
        
        # Get the first matched group (if any)
        matched_value = match.group(1) if match.groups() else ""
        
        # Get the value for the matched group
        value = values.get(matched_value.lower(), "")
        
        # Format the response
        return response_template.format(matched_value, value)
    
    def _process_with_decision_tree(self, tree: Dict[str, Any], request: Dict[str, Any]) -> str:
        """
        Process a request using a decision tree.
        
        Args:
            tree: The decision tree with nodes
            request: The companion request
            
        Returns:
            The generated response
        """
        # Start at the root node
        current_node = "root"
        
        # Get the nodes
        nodes = tree.get("nodes", {})
        
        # Traverse the tree
        while current_node in nodes:
            node = nodes[current_node]
            
            # If the node has a response, return it
            if "response" in node:
                return node["response"]
            
            # If the node has a condition, evaluate it
            if "condition" in node and "branches" in node:
                condition = node["condition"]
                branches = node["branches"]
                
                # Get the value of the condition
                value = self._evaluate_condition(condition, request)
                
                # Get the next node
                current_node = branches.get(value, branches.get("default", ""))
            else:
                # If the node has no condition or branches, break the loop
                break
        
        # If we couldn't find a response, return the default response
        return tree.get("default_response", "I'm sorry, I don't know how to help with that.")
    
    def _evaluate_condition(self, condition: str, request: Dict[str, Any]) -> str:
        """
        Evaluate a condition in a decision tree.
        
        Args:
            condition: The condition to evaluate
            request: The companion request
            
        Returns:
            The value of the condition
        """
        # Split the condition into parts
        parts = condition.split(".")
        
        # Start with the request
        value = request
        
        # Traverse the request to get the value
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return ""
        
        # Return the value as a string
        return str(value).lower()
    
    def _create_companion_request(self, request: ClassifiedRequest) -> Dict[str, Any]:
        """
        Create a companion request from a classified request.
        
        Args:
            request: The classified request
            
        Returns:
            A companion request
        """
        return {
            "request_id": request.request_id,
            "player_input": request.player_input,
            "request_type": request.request_type,
            "intent": request.intent.value,
            "complexity": request.complexity.value,
            "extracted_entities": request.extracted_entities
        }
    
    def _load_default_trees(self):
        """Load the default decision trees."""
        # This is a simplified implementation
        # In a real system, this would load decision trees from files
        self.decision_trees = {
            "vocabulary": {
                "patterns": [
                    {
                        "pattern": r"what does '(\w+)' mean",
                        "response": "'{0}' means '{1}' in Japanese.",
                        "values": {
                            "kippu": "ticket",
                            "eki": "station",
                            "densha": "train"
                        }
                    }
                ],
                "nodes": {
                    "root": {
                        "condition": "extracted_entities.word",
                        "branches": {
                            "kippu": "node_kippu",
                            "eki": "node_eki",
                            "default": "node_unknown"
                        }
                    },
                    "node_kippu": {
                        "response": "'Kippu' means 'ticket' in Japanese."
                    },
                    "node_eki": {
                        "response": "'Eki' means 'station' in Japanese."
                    },
                    "node_unknown": {
                        "response": "I'm not familiar with that word."
                    }
                },
                "default_response": "That word means 'hello' in Japanese. In Japanese: こんにちは (konnichiwa)."
            },
            "grammar": {
                "default_response": "This grammar point is used to express a desire to do something. For example: 食べたい (tabetai) means 'I want to eat'."
            },
            "directions": {
                "default_response": "The ticket gate is straight ahead. In Japanese: きっぷうりば は まっすぐ です (kippu-uriba wa massugu desu)."
            },
            "translation": {
                "default_response": "Yes, that's correct! 'Thank you' in Japanese is ありがとう (arigatou)."
            },
            "general": {
                "default_response": "I'm Hachiko, your companion in Railway Station. How can I help you learn Japanese today?"
            }
        } 