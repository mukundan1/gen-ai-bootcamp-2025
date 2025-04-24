"""
Text Adventure - Companion AI Configuration

This module contains configuration settings for the companion AI system.
"""

import os
import yaml
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants for the different processing tiers
TIER_CONFIG = {
    "TIER_1_THRESHOLD": 0.3,  # Threshold for Tier 1 processing
    "TIER_2_THRESHOLD": 0.7,  # Threshold for Tier 2 processing
    "TIER_3_THRESHOLD": 1.0,  # Threshold for Tier 3 processing
}

# Intent categories
INTENT_CATEGORIES = {
    "VOCABULARY_HELP": "vocabulary_help",
    "NAVIGATION_HELP": "navigation_help",
    "CULTURAL_INFO": "cultural_info",
    "TRANSLATION_REQUEST": "translation_request",
    "TICKET_INFO": "ticket_info",
    "CASUAL_CHAT": "casual_chat",
    "SAFETY_INFO": "safety_info",
    "FOOD_RECOMMENDATION": "food_recommendation",
    "EMERGENCY_HELP": "emergency_help",
    "ATTRACTION_INFO": "attraction_info",
}

# Complexity levels
COMPLEXITY_LEVELS = {
    "SIMPLE": 0.3,
    "MODERATE": 0.7,
    "COMPLEX": 1.0,
}

# Personality traits
PERSONALITY_TRAITS = {
    "FRIENDLY": 0.8,
    "HELPFUL": 0.9,
    "KNOWLEDGEABLE": 0.7,
    "PATIENT": 0.9,
    "ENTHUSIASTIC": 0.6,
}

# Local model configuration
LOCAL_MODEL_CONFIG = {
    "model_name": "deepseek-coder:7b",
    "max_tokens": 256,
    "temperature": 0.7,
    "top_p": 0.9,
    "cache_size": 100,  # Number of responses to cache
}

# Cloud API configuration
CLOUD_API_CONFIG = {
    "region_name": "ap-south-1",
    "model_id": "amazon.claude-3-sonnet-20240229-v1:0",
    "max_tokens": 1024,
    "temperature": 0.7,
    "top_p": 0.95,
    "daily_quota": 10000  # Maximum tokens per day
}

# Logging configuration
LOGGING_CONFIG = {
    "log_level": "INFO",
    "log_file": "companion_ai.log",
    "enable_request_logging": True,
    "enable_response_logging": True,
}

# Path to the companion.yaml configuration file
CONFIG_FILE_PATH = os.environ.get('COMPANION_CONFIG', 'config/companion.yaml')

def get_config(section: str, default: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
    """
    Get configuration for the specified section from companion.yaml.
    
    Args:
        section: The section name to retrieve
        default: Default values to return if section is not found
        
    Returns:
        Configuration dictionary or default if not found
    """
    try:
        config_path = os.environ.get('COMPANION_CONFIG', 'config/companion.yaml')
        
        if not os.path.exists(config_path):
            logger.warning(f"Configuration file {config_path} not found, using defaults")
            return default
            
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            
        if config is None:
            logger.warning(f"Configuration file {config_path} is empty, using defaults")
            return default
        
        # Only log at INFO level for production config, DEBUG for test config
        is_test_config = 'test' in config_path
        log_level = logging.DEBUG if is_test_config else logging.INFO
        logger.log(log_level, f"Loaded configuration from {config_path}")
        
        # Return the specified section or default if not found
        if section in config:
            logger.debug(f"Found configuration for section '{section}'")
            return config[section]
        else:
            logger.debug(f"Section '{section}' not found in configuration, using defaults")
            return default
            
    except Exception as e:
        logger.error(f"Error loading configuration: {str(e)}")
        return default 