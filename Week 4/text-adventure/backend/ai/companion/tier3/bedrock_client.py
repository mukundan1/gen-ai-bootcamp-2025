"""
Text Adventure - Amazon Bedrock Client

This module provides a client for interacting with Amazon Bedrock, a fully managed
service that offers high-performing foundation models from leading AI companies.
"""

import json
import logging
import asyncio
import aiohttp
import boto3
import time
from typing import Dict, List, Any, Optional, Union
from botocore.auth import SigV4Auth
from botocore.awsrequest import AWSRequest
from botocore.credentials import Credentials

from backend.ai.companion.core.models import CompanionRequest
from backend.ai.companion.tier3.prompt_optimizer import create_optimized_prompt
from backend.ai.companion.tier3.usage_tracker import (
    track_request,
    check_quota,
    UsageTracker,
    default_tracker
)
from backend.ai.companion.utils.retry import RetryConfig, retry_async

logger = logging.getLogger(__name__)


class BedrockError(Exception):
    """Error that occurred when calling the Bedrock API."""
    
    # Error types
    API_ERROR = "api_error"
    AUTHENTICATION_ERROR = "authentication_error"
    QUOTA_ERROR = "quota_exceeded"
    TIMEOUT_ERROR = "timeout"
    CONNECTION_ERROR = "connection_error"
    MODEL_ERROR = "model_error"
    UNKNOWN_ERROR = "unknown_error"
    
    def __init__(self, message: str, error_type: str = UNKNOWN_ERROR):
        """Initialize the error."""
        super().__init__(message)
        self.message = message
        self.error_type = error_type


class BedrockClient:
    """
    Client for Amazon Bedrock.
    
    This class provides a simplified interface for generating text with Amazon Bedrock.
    It handles authentication, model selection, and usage tracking.
    """
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        model_id: str = "amazon.nova-micro-v1:0",
        max_tokens: int = 512,
        usage_tracker: Optional[UsageTracker] = None
    ):
        """
        Initialize the Bedrock client.
        
        Args:
            region_name: The AWS region to use
            model_id: The default model ID to use
            max_tokens: The maximum number of tokens to generate
            usage_tracker: The usage tracker to use
        """
        self.logger = logging.getLogger(__name__)
        self.region_name = region_name
        self.default_model = model_id
        self.max_tokens = max_tokens
        self.usage_tracker = usage_tracker or default_tracker
        
        # Create the Bedrock client
        try:
            self.logger.debug(f"Creating Bedrock client in region {region_name}")
            self.client = boto3.client(service_name="bedrock-runtime", region_name=region_name)
            self.logger.debug("Bedrock client created successfully")
        except Exception as e:
            self.logger.error(f"Error creating Bedrock client: {str(e)}")
            raise BedrockError(f"Error creating Bedrock client: {str(e)}", BedrockError.API_ERROR)

    def _redact_sensitive_info(self, data):
        """
        Redact sensitive information from a dictionary or string.
        
        Args:
            data: The data to redact
            
        Returns:
            The redacted data
        """
        if isinstance(data, str):
            try:
                # Try to parse as JSON
                data_dict = json.loads(data)
                return self._redact_sensitive_info(data_dict)
            except:
                # Not JSON, redact known patterns
                return data
        
        if not isinstance(data, dict):
            return data
            
        # Create a copy to avoid modifying the original
        redacted = data.copy()
        
        # Keys to completely redact
        sensitive_keys = [
            "authentication", "credentials", "secret", "token", "signature",
            "access_key", "secret_key", "password", "api_key", "auth"
        ]
        
        # Keys to redact values
        keys_to_check = sensitive_keys + ["inference_config", "parameters"]
        
        for key in list(redacted.keys()):
            # If the key itself is sensitive, replace the entire value
            if any(sensitive_word in key.lower() for sensitive_word in sensitive_keys):
                redacted[key] = "[REDACTED]"
            
            # If the key might contain sensitive nested information
            elif isinstance(redacted[key], dict):
                redacted[key] = self._redact_sensitive_info(redacted[key])
            
            # If this is a list, check each item
            elif isinstance(redacted[key], list):
                redacted[key] = [
                    self._redact_sensitive_info(item) if isinstance(item, (dict, list)) else item
                    for item in redacted[key]
                ]
        
        return redacted

    def _pretty_print_json(self, data):
        """Helper method to pretty-print JSON with Unicode characters, redacting sensitive info."""
        # First redact sensitive information
        redacted_data = self._redact_sensitive_info(data)
        
        if isinstance(redacted_data, str):
            try:
                redacted_data = json.loads(redacted_data)
            except:
                return redacted_data
        
        return json.dumps(redacted_data, ensure_ascii=False, indent=2)
    
    def _call_bedrock_api(self, model_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call the Amazon Bedrock API with the provided model ID and payload.
        
        Args:
            model_id: The model ID to use
            payload: The request payload
            
        Returns:
            The response from the API
        """
        # Log the request payload in detail for debugging, but redact sensitive info
        self.logger.debug(f"Request model_id: {model_id}")
        self.logger.debug(f"Request payload: {self._pretty_print_json(payload)}")
        
        try:
            # Call the API
            self.logger.debug(f"Calling Bedrock API with model {model_id}")
            response = self.client.invoke_model(
                modelId=model_id,
                body=json.dumps(payload),
                contentType="application/json",
                accept="application/json"
            )
            
            # Parse the response
            response_body = response["body"].read().decode("utf-8")
            response_json = json.loads(response_body)
            
            # Log the complete raw response for debugging, but redact sensitive info
            self.logger.debug(f"Raw response: {self._pretty_print_json(response_json)}")
            
            return response_json
        except Exception as e:
            # Log detailed error information, but redact sensitive info
            self.logger.error(f"Error calling Bedrock API: {str(e)}")
            self.logger.error(f"Model ID: {model_id}")
            self.logger.error(f"Request payload: {self._pretty_print_json(payload)}")
            
            # Check for specific error types
            error_type = BedrockError.API_ERROR
            error_msg = str(e)
            
            if "AccessDeniedException" in error_msg:
                error_type = BedrockError.AUTHENTICATION_ERROR
            elif "ValidationException" in error_msg:
                # Log more details about validation errors
                self.logger.error(f"Validation error details: Request format may be incorrect for model {model_id}")
            elif "ThrottlingException" in error_msg or "TooManyRequestsException" in error_msg:
                error_type = BedrockError.QUOTA_ERROR
            elif "Timeout" in error_msg:
                error_type = BedrockError.TIMEOUT_ERROR
                
            raise BedrockError(f"Error calling Bedrock API: {error_msg}", error_type)

    async def generate(
        self, 
        request: CompanionRequest,
        model_id: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        prompt: str = ""
    ) -> str:
        """
        Generate text with Amazon Bedrock.
        
        Args:
            request: The request to generate text for
            model_id: The model ID to use (optional, defaults to the default model)
            temperature: The temperature to use for generation
            max_tokens: The maximum number of tokens to generate
            prompt: The prompt to use
            
        Returns:
            The generated text
        """
        # Use default values if not provided
        model_id = model_id or self.default_model
        max_tokens = max_tokens or self.max_tokens
        
        # Log the generation request
        self.logger.info(f"Generating text for request {request.request_id} with model {model_id}")
        self.logger.debug(f"Prompt: {prompt}")
        self.logger.debug(f"Temperature: {temperature}, max_tokens: {max_tokens}")
        
        # Create the payload based on the model type
        if "claude" in model_id.lower():
            # Claude-specific payload
            payload = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        elif "nova" in model_id.lower():
            # Nova-specific payload using Converse API format
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": [{"text": prompt}]
                    }
                ],
                "inferenceConfig": {
                    "maxTokens": max_tokens,
                    "temperature": temperature,
                    "topP": 0.9
                }
            }
        else:
            # Default payload for other models (text completion format)
            payload = {
                "inputText": prompt,
                "textGenerationConfig": {
                    "maxTokenCount": max_tokens,
                    "temperature": temperature,
                    "topP": 0.9,
                    "stopSequences": []
                }
            }
        
        try:
            # Call the API
            response_json = self._call_bedrock_api(model_id, payload)
            
            # Extract the generated text based on the model type
            if "claude" in model_id.lower():
                # Claude-specific response format
                content = response_json.get("content", [])
                if isinstance(content, list) and len(content) > 0:
                    text = content[0].get("text", "")
                else:
                    text = response_json.get("output", {}).get("message", {}).get("content", "")
            elif "nova" in model_id.lower():
                # Nova-specific response format from Converse API
                output = response_json.get("output", {})
                if "message" in output:
                    message = output["message"]
                    if isinstance(message, dict) and "content" in message:
                        content = message["content"]
                        if isinstance(content, list) and len(content) > 0:
                            # Content is a list of content blocks
                            text_blocks = []
                            for block in content:
                                if isinstance(block, dict) and "text" in block:
                                    text_blocks.append(block["text"])
                            if text_blocks:
                                text = " ".join(text_blocks)
                            else:
                                text = str(content)
                        else:
                            text = str(content)
                    else:
                        text = str(message)
                else:
                    # Fallback for other response formats
                    text = str(output)
            else:
                # Default response format for other models
                text = response_json.get("outputText", response_json.get("results", [{}])[0].get("outputText", ""))
            
            # Log the generated text
            self.logger.debug(f"Generated text: {text}")
            
            # Track usage
            if "usage" in response_json:
                input_tokens = response_json["usage"].get("inputTokens", 0)
                output_tokens = response_json["usage"].get("outputTokens", 0)
                
                # Check if the usage_tracker has the record_usage method
                if hasattr(self.usage_tracker, 'record_usage'):
                    self.usage_tracker.record_usage(
                        model_id=model_id,
                        input_tokens=input_tokens,
                        output_tokens=output_tokens
                    )
                else:
                    # Log usage information without tracking
                    self.logger.info(f"Usage: {input_tokens} input tokens, {output_tokens} output tokens")
            
            return text
        except BedrockError as e:
            # Preserve the original error type
            self.logger.error(f"Error generating text: {str(e)}")
            raise  # Re-raise the original BedrockError with its type intact
        except Exception as e:
            self.logger.error(f"Error generating text: {str(e)}")
            raise BedrockError(f"Error generating text: {str(e)}", BedrockError.API_ERROR)
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """
        Get a list of available models from Amazon Bedrock.
        
        Returns:
            A list of model information dictionaries
            
        Raises:
            BedrockError: If there is an error getting the models
        """
        logger.info("Getting available models from Bedrock")
        
        try:
            # Create a Bedrock client
            bedrock = boto3.client('bedrock', region_name=self.region_name)
            
            # Get the list of foundation models
            response = bedrock.list_foundation_models()
            
            # Extract the model summaries
            if "modelSummaries" in response:
                return response["modelSummaries"]
            else:
                return []
                
        except Exception as e:
            # Wrap exceptions in BedrockError
            logger.error(f"Error getting available models: {e}")
            raise BedrockError(f"Error getting available models: {e}")
