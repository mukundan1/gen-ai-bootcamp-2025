"""
Text Adventure - Template System

This module implements the template system for the Tier 1 processor.
It provides functionality for loading, managing, and rendering templates
with variable substitution.
"""

import os
import json
import random
import logging
import re
from typing import Dict, List, Optional, Any, Union
from string import Formatter

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    IntentCategory
)

logger = logging.getLogger(__name__)


class TemplateSystem:
    """
    Template system for generating responses based on templates with variable substitution.
    
    The TemplateSystem is responsible for:
    - Loading templates from files or dictionaries
    - Selecting appropriate templates based on intent and context
    - Rendering templates with variable substitution
    - Managing templates (adding, removing, saving)
    
    Templates are organized by intent category and can include variables
    that are substituted with values from the request or context.
    """
    
    # Default templates to use if no templates are provided
    DEFAULT_TEMPLATES = {
        "vocabulary_help": [
            "{word} means {meaning} in Japanese.",
            "The Japanese word '{word}' translates to '{meaning}' in English.",
            "'{word}' is the Japanese word for '{meaning}'."
        ],
        "grammar_explanation": [
            "The pattern {pattern} is used to {usage}.",
            "When you want to {usage}, you can use the pattern {pattern}.",
            "In Japanese, {pattern} is a grammar pattern for {usage}."
        ],
        "direction_guidance": [
            "To get to {destination}, you need to {directions}.",
            "Follow these directions to {destination}: {directions}",
            "Here's how to reach {destination}: {directions}"
        ],
        "translation_confirmation": [
            "'{original}' in Japanese is '{translation}'.",
            "The phrase '{original}' translates to '{translation}' in Japanese.",
            "'{translation}' is how you say '{original}' in Japanese."
        ],
        "general_hint": [
            "Here's a hint: {hint}",
            "Let me give you a tip: {hint}",
            "This might help: {hint}"
        ],
        "fallback": [
            "I'm not sure I understand. Could you rephrase that?",
            "I don't have information about that. Can I help with something else?",
            "I'm still learning and don't know about that yet."
        ]
    }
    
    def __init__(self, template_file: Optional[str] = None, templates: Optional[Dict[str, List[str]]] = None):
        """
        Initialize the TemplateSystem.
        
        Args:
            template_file: Optional path to a JSON file containing templates
            templates: Optional dictionary of templates to use instead of loading from file
        """
        self.templates = self.DEFAULT_TEMPLATES.copy()
        
        if templates:
            # Use provided templates
            self.templates.update(templates)
        elif template_file:
            # Load templates from file
            self._load_templates_from_file(template_file)
        
        logger.debug(f"Initialized TemplateSystem with {sum(len(v) for v in self.templates.values())} templates")
    
    def _load_templates_from_file(self, file_path: str) -> None:
        """
        Load templates from a JSON file.
        
        Args:
            file_path: Path to the JSON file containing templates
        """
        try:
            with open(file_path, 'r') as f:
                loaded_templates = json.load(f)
                self.templates.update(loaded_templates)
                logger.info(f"Loaded templates from {file_path}")
        except FileNotFoundError:
            logger.warning(f"Template file not found: {file_path}")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in template file: {file_path}")
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
    
    def get_template(self, intent: Union[IntentCategory, str], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Get a template for the given intent, considering context if provided.
        
        Args:
            intent: The intent category or string key
            context: Optional context information that may influence template selection
            
        Returns:
            A template string
        """
        # Convert intent to string if it's an enum
        intent_key = intent.value if hasattr(intent, 'value') else str(intent)
        
        # Try to get context-specific templates first
        if context:
            # Check for location-specific templates
            if 'location' in context:
                location = context['location']
                location_key = f"{intent_key}_in_{location}"
                if location_key in self.templates:
                    return random.choice(self.templates[location_key])
            
            # Check for formality-specific templates
            if 'formality' in context:
                formality = context['formality']
                formality_key = f"{intent_key}_{formality}"
                if formality_key in self.templates:
                    return random.choice(self.templates[formality_key])
            
            # Check for proficiency-specific templates
            if 'player_proficiency' in context:
                proficiency = context['player_proficiency']
                proficiency_key = f"{intent_key}_{proficiency}"
                if proficiency_key in self.templates:
                    return random.choice(self.templates[proficiency_key])
        
        # Fall back to standard templates for the intent
        if intent_key in self.templates:
            return random.choice(self.templates[intent_key])
        
        # If no templates found for the intent, use fallback templates
        logger.warning(f"No templates found for intent: {intent_key}")
        return random.choice(self.templates["fallback"])
    
    def render_template(self, template: str, variables: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template by substituting variables.
        
        Args:
            template: The template string to render
            variables: Dictionary of variables to substitute
            context: Optional context variables to use if not in variables
            
        Returns:
            The rendered template string
        """
        # Combine variables and context
        all_vars = {}
        if context:
            all_vars.update(context)
        all_vars.update(variables)
        
        # Find all variables in the template
        formatter = Formatter()
        template_vars = [field_name for _, field_name, _, _ in formatter.parse(template) if field_name]
        
        # Create a dictionary with only the variables needed for this template
        template_values = {}
        for var in template_vars:
            if var in all_vars:
                template_values[var] = all_vars[var]
        
        # Render the template
        try:
            # Use format_map to handle missing keys
            rendered = template.format_map(SafeDict(template_values))
            return rendered
        except Exception as e:
            logger.error(f"Error rendering template: {str(e)}")
            return template
    
    def process_request(self, request: ClassifiedRequest, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process a request using the template system.
        
        Args:
            request: The classified request to process
            context: Optional context information
            
        Returns:
            A response string
        """
        # Get a template for the request intent
        template = self.get_template(request.intent, context)
        
        # Render the template with the request's extracted entities
        response = self.render_template(template, request.extracted_entities, context)
        
        logger.debug(f"Processed request {request.request_id} with template")
        return response
    
    def add_template(self, intent: Union[IntentCategory, str], template: str) -> None:
        """
        Add a new template for the given intent.
        
        Args:
            intent: The intent category or string key
            template: The template string to add
        """
        # Convert intent to string if it's an enum
        intent_key = intent.value if hasattr(intent, 'value') else str(intent)
        
        # Create the intent category if it doesn't exist
        if intent_key not in self.templates:
            self.templates[intent_key] = []
        
        # Add the template
        self.templates[intent_key].append(template)
        logger.debug(f"Added template for intent: {intent_key}")
    
    def remove_template(self, intent: Union[IntentCategory, str], template: str) -> bool:
        """
        Remove a template for the given intent.
        
        Args:
            intent: The intent category or string key
            template: The template string to remove
            
        Returns:
            True if the template was removed, False otherwise
        """
        # Convert intent to string if it's an enum
        intent_key = intent.value if hasattr(intent, 'value') else str(intent)
        
        # Check if the intent category exists
        if intent_key not in self.templates:
            logger.warning(f"Intent category not found: {intent_key}")
            return False
        
        # Try to remove the template
        try:
            self.templates[intent_key].remove(template)
            logger.debug(f"Removed template for intent: {intent_key}")
            return True
        except ValueError:
            logger.warning(f"Template not found for intent: {intent_key}")
            return False
    
    def save_templates(self, file_path: str) -> bool:
        """
        Save templates to a JSON file.
        
        Args:
            file_path: Path to save the templates to
            
        Returns:
            True if the templates were saved successfully, False otherwise
        """
        try:
            with open(file_path, 'w') as f:
                json.dump(self.templates, f, indent=2)
            logger.info(f"Saved templates to {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving templates: {str(e)}")
            return False


class SafeDict(dict):
    """
    A dictionary subclass that returns the key in braces if the key is not found.
    This is used to handle missing variables in templates.
    """
    def __missing__(self, key):
        return '{' + key + '}' 