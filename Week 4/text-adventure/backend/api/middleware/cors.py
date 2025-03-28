"""
CORS middleware for the API.
"""

from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app):
    """
    Set up CORS middleware for the application.
    
    Args:
        app: The FastAPI application
    """
    # Set up CORS with permissive settings for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins in development
        allow_credentials=True,
        allow_methods=["*"],  # Allow all methods
        allow_headers=["*"],  # Allow all headers
    ) 