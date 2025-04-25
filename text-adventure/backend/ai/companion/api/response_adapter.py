"""
Response adapter module for the Companion AI system.

This module contains the ResponseAdapter class, which is responsible for
transforming internal response objects into the format expected by the API.
"""
import logging

class ResponseAdapter:
    """
    Adapter class that converts internal CompanionResponse objects to the format
    expected by external APIs or clients.
    """
    
    def __init__(self):
        """Initialize the ResponseAdapter."""
        self.logger = logging.getLogger(__name__)
    
    def format_response(self, response_data):
        """
        Format a response for the API.
        
        Args:
            response_data: A dictionary containing response information
            
        Returns:
            A formatted response dictionary ready for API output
        """
        # Extract the response text
        response_text = response_data.get('response_text', '')
        
        # Get the processing tier from the response data, ensuring it's passed through correctly
        processing_tier = response_data.get('processing_tier', 'unknown')
        
        # Convert from enum to string if needed
        if hasattr(processing_tier, 'name'):
            processing_tier = processing_tier.name
        elif isinstance(processing_tier, str) and processing_tier in ["tier_1", "tier_2", "tier_3", "rule"]:
            # Convert from tier value to enum name format
            if processing_tier == "tier_1":
                processing_tier = "TIER_1"
            elif processing_tier == "tier_2":
                processing_tier = "TIER_2"
            elif processing_tier == "tier_3":
                processing_tier = "TIER_3"
            elif processing_tier == "rule":
                processing_tier = "RULE"
        
        # Create the final response dictionary
        formatted_response = {
            'text': response_text,
            'metadata': {
                'processing_tier': processing_tier,
                'response_length': len(response_text)
            }
        }
        
        self.logger.info(f"Response details - dialogue length: {len(response_text)}, processing tier: {processing_tier}")
        
        return formatted_response 