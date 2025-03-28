"""
Adapters for the DeepSeek engine parameters API.
"""

from typing import Dict, Any
from backend.api.adapters.base import RequestAdapter, ResponseAdapter
from backend.api.models.deepseek_parameters import DeepSeekParametersResponse


class DeepSeekParametersRequestAdapter(RequestAdapter):
    """Adapter for DeepSeek parameters requests."""
    
    def adapt(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt API request to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal request data.
        """
        return self.to_internal(request_data)
    
    def to_internal(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert API request to internal format.
        
        Args:
            request_data: The API request data.
            
        Returns:
            The internal request data.
        """
        # The request format is already compatible with the internal format
        return request_data


class DeepSeekParametersResponseAdapter(ResponseAdapter):
    """Adapter for DeepSeek parameters responses."""
    
    def adapt(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adapt internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        return self.to_api(internal_data)
    
    def to_api(self, internal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert internal data to API format.
        
        Args:
            internal_data: The internal data.
            
        Returns:
            The API response data.
        """
        api_data = DeepSeekParametersResponse(
            success=True,
            parameters=internal_data,
            message="DeepSeek engine parameters updated successfully"
        )
        
        return api_data.model_dump() 