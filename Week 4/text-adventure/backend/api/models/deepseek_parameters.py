"""
Models for the DeepSeek engine parameters API.
"""

from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, field_validator, model_validator


class DeepSeekParametersRequest(BaseModel):
    """Request model for adjusting DeepSeek engine parameters."""
    temperature: Optional[float] = Field(None, description="Temperature for text generation (0.0-1.0)", ge=0.0, le=1.0)
    top_p: Optional[float] = Field(None, description="Top-p sampling parameter (0.0-1.0)", ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, description="Top-k sampling parameter", ge=1)
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate", ge=1)
    presence_penalty: Optional[float] = Field(None, description="Presence penalty for text generation (-2.0-2.0)", ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty for text generation (-2.0-2.0)", ge=-2.0, le=2.0)
    context_window: Optional[int] = Field(None, description="Size of the context window in tokens", ge=512)
    model_version: Optional[str] = Field(None, description="Version of the DeepSeek model to use")
    enable_japanese_corrections: Optional[bool] = Field(None, description="Whether to enable Japanese language corrections")
    jlpt_level_cap: Optional[Literal["N5", "N4", "N3", "N2", "N1"]] = Field(None, description="Maximum JLPT level for vocabulary")
    
    @field_validator('model_version')
    def validate_model_exists(cls, v):
        """Validate that the model exists."""
        if v is not None and v not in ["deepseek-chat", "deepseek-coder", "deepseek-llm"]:
            raise ValueError(f"Model {v} is not supported")
        return v
    
    @model_validator(mode='after')
    def at_least_one_parameter_required(self):
        """Validate that at least one parameter is provided."""
        if all(v is None for v in self.model_dump().values()):
            raise ValueError("At least one parameter must be provided")
        return self


class DeepSeekParametersResponse(BaseModel):
    """Response model for adjusting DeepSeek engine parameters."""
    success: bool = Field(..., description="Whether the parameters were successfully updated")
    parameters: Dict[str, Any] = Field(..., description="The updated parameters")
    message: str = Field(..., description="A message describing the result of the operation")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Any] = Field(None, description="Additional error details") 