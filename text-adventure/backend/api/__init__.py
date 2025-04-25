"""
API package for the Text Adventure game.
"""

from fastapi import FastAPI
from backend.api.routers import api_router
from backend.api.middleware import setup_middleware


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        The configured FastAPI application
    """
    # Create the application
    app = FastAPI(
        title="Text Adventure API",
        description="API for the Text Adventure game",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Set up middleware
    setup_middleware(app)
    
    # Include the API router
    app.include_router(api_router)
    
    # Add a health check endpoint
    @app.get("/health")
    async def health_check():
        """
        Health check endpoint.
        
        Returns:
            A simple status message
        """
        return {"status": "ok"}
    
    return app 