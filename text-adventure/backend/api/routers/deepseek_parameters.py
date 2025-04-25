"""
Router for DeepSeek engine parameters.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from backend.api.adapters.base import AdapterFactory
from backend.api.models.deepseek_parameters import (
    DeepSeekParametersRequest,
    DeepSeekParametersResponse,
    ErrorResponse
)
from backend.data.deepseek_parameters import (
    update_deepseek_parameters,
    get_deepseek_parameters,
    InvalidParameterError
)

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/npc/engine",
    tags=["npc-engine"],
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        404: {"model": ErrorResponse, "description": "Not Found"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)


@router.post(
    "/parameters",
    response_model=DeepSeekParametersResponse,
    summary="Update DeepSeek engine parameters",
    description="Adjust parameters for the DeepSeek engine (admin endpoint)",
    responses={
        200: {"description": "Parameters updated successfully"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        422: {"description": "Validation Error"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"}
    }
)
async def update_parameters(
    parameters: DeepSeekParametersRequest
) -> DeepSeekParametersResponse:
    """
    Update DeepSeek engine parameters.
    
    Args:
        parameters: The parameters to update.
        
    Returns:
        The updated parameters.
        
    Raises:
        HTTPException: If an error occurs while updating parameters.
    """
    try:
        logger.info("Updating DeepSeek engine parameters")
        
        # Get the request adapter
        request_adapter = AdapterFactory.get_request_adapter("deepseek_parameters")
        
        # Transform request to internal format
        internal_request = request_adapter.adapt(parameters.model_dump(exclude_none=True))
        
        # Update parameters
        result = update_deepseek_parameters(internal_request)
        
        # Get the response adapter
        response_adapter = AdapterFactory.get_response_adapter("deepseek_parameters")
        
        # Transform result to API format
        response_data = response_adapter.adapt(result)
        
        logger.info("DeepSeek engine parameters updated successfully")
        
        return DeepSeekParametersResponse(**response_data)
        
    except InvalidParameterError as e:
        logger.error(f"Invalid parameter: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error updating DeepSeek engine parameters: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred while updating DeepSeek engine parameters: {str(e)}"
        ) 