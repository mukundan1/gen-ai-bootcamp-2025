# Text Adventure - Companion AI Simulator

A simple text-based simulator for testing the companion AI in the Text Adventure game.

## Overview

This simulator provides a Gradio-based web interface for interacting with the companion AI without needing the full game client. It allows you to:

- Send text requests to the companion AI
- Configure game context (location, quest, etc.)
- View the companion's responses
- See debug information about the response

## Prerequisites

- Python 3.8+
- Backend server running locally

## Starting the Backend Server

Before using the simulator, you need to start the backend server:

1. Navigate to the project root directory:

```bash
cd /path/to/text-adventure
```

2. Install the backend dependencies if you haven't already:

```bash
pip install -r backend/requirements.txt
```

3. Start the backend server:

```bash
python backend/run_server.py
```

The server should start and be available at http://localhost:8000. You can verify it's running by accessing http://localhost:8000/api/docs in your browser, which should display the API documentation.

## Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Make sure the backend server is running (typically on http://localhost:8000).

## Usage

1. Start the simulator:

```bash
python app.py
```

2. Open your browser and navigate to http://localhost:7860 (or the URL displayed in the console).

3. Configure the request parameters:
   - **Player Information**: Set player ID and session ID
   - **Game Context**: Select location, quest, and quest step
   - **Request Details**: Choose request type, enter text, and optionally specify target entity/location

4. Click "Submit Request" to send the request to the companion AI.

5. View the companion's response and debug information in the panels below.

## Configuration

You can configure the API URL by setting the `API_URL` environment variable or by creating a `.env` file with the following content:

```
API_URL=http://localhost:8000
```





## Troubleshooting

If you encounter issues:

1. Make sure the backend server is running and accessible.
2. Check the console for error messages.
3. Verify that the API URL is correct.
4. Ensure all required fields in the request are filled out correctly.








## Development

The simulator consists of three main components:

- `app.py`: The Gradio web interface
- `client.py`: API client for communicating with the backend
- `defaults.py`: Default values for testing

To modify the simulator, edit these files as needed. 