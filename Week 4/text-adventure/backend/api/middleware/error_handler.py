"""
Error handling middleware for the API.
"""

import logging
import traceback
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Create a logger
logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handle HTTP exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception
        
    Returns:
        A JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": str(exc.detail),
            "details": None
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle validation exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception
        
    Returns:
        A JSON response with error details
    """
    # Extract field errors
    field_errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        field_errors.append({
            "field": field_path,
            "message": error["msg"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request format or missing required fields",
            "details": {
                "fieldErrors": field_errors
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handle general exceptions.
    
    Args:
        request: The request that caused the exception
        exc: The exception
        
    Returns:
        A JSON response with error details
    """
    # Log the error
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.debug(traceback.format_exc())
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": {
                "type": type(exc).__name__,
                "message": str(exc)
            }
        }
    ) 