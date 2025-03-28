#!/usr/bin/env python
"""
Simple server runner for Tokyo Train Station Adventure.
"""

import os
import sys
import uvicorn
import logging
import logging.config

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Configure logging
logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        },
        "detailed": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(funcName)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",  # Set to DEBUG to see all logs
            "formatter": "detailed",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "backend.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "loggers": {
        "backend": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False
        }
    },
    "root": {
        "level": "DEBUG",  # Set root logger to DEBUG
        "handlers": ["console"]
    }
}

# Apply the logging configuration
logging.config.dictConfig(logging_config)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "backend.api:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=True,
        log_level="debug"  # Set uvicorn log level to debug
    ) 