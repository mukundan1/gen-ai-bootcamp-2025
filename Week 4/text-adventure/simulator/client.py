"""
Client for communicating with the backend API.
"""

import os
import json
import httpx
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default API URL
DEFAULT_API_URL = "http://localhost:8000"


class CompanionAPIClient:
    """
    Client for communicating with the companion assist API.
    """
    
    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the client.
        
        Args:
            base_url: The base URL for the API. If not provided, uses the
                      API_URL environment variable or the default.
        """
        self.base_url = base_url or os.getenv("API_URL", DEFAULT_API_URL)
        self.client = httpx.AsyncClient(timeout=30.0)  # 30 second timeout
        
    async def __aenter__(self):
        """
        Async context manager entry.
        """
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        Async context manager exit.
        """
        await self.close()
        
    async def close(self):
        """
        Close the client.
        """
        await self.client.aclose()
        
    async def companion_assist(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a request to the companion assist endpoint.
        
        Args:
            payload: The request payload
            
        Returns:
            The response from the API
            
        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        url = f"{self.base_url}/api/companion/assist"
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            # Try to get error details if available
            error_detail = "Unknown error"
            try:
                error_json = e.response.json()
                error_detail = json.dumps(error_json, indent=2)
            except Exception:
                error_detail = e.response.text or str(e)
                
            raise Exception(f"API request failed: {e.response.status_code} - {error_detail}")
        except Exception as e:
            raise Exception(f"API request failed: {str(e)}")


# Simplified function for use in the Gradio app
async def send_companion_request(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Send a request to the companion assist endpoint.
    
    Args:
        payload: The request payload
        
    Returns:
        The response from the API
    """
    async with CompanionAPIClient() as client:
        return await client.companion_assist(payload) 