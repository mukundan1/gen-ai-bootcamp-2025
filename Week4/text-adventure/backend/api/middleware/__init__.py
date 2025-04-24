"""
API middleware package.
"""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.api.middleware.cors import setup_cors
from backend.api.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)


def setup_middleware(app: FastAPI):
    """
    Set up middleware for the application.
    
    Args:
        app: The FastAPI application
    """
    # Set up CORS
    setup_cors(app)
    
    # Set up exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler) 