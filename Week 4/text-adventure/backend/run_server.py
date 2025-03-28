"""
Script to run the FastAPI server.
"""

import uvicorn

if __name__ == "__main__":
    # Run the application with uvicorn
    uvicorn.run(
        "backend.main:app",  # Use the full module path
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 