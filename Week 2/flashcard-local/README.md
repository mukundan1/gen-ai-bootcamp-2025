# Flashcard Generator Local

## Overview
This application is a Japanese language learning tool that generates random Japanese vocabulary flashcards using Ollama's LLaVA model for scene descriptions.

## Features
- Generate random Japanese vocabulary words (JLPT N5 level)
- Generate scene descriptions using Ollama's LLaVA model
- Simple web interface for interaction

## Prerequisites
- Python 3.8+
- Ollama installed and running locally
- Internet Connection

## Installation

### 1. Install Ollama
Follow the instructions at https://ollama.com to install Ollama for your operating system.

### 2. Pull the LLaVA model
```bash
ollama pull llava
```

### 3. Clone the Repository
```bash
git clone https://github.com/yourusername/flashcard-local.git
cd flashcard-local
```

### 4. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

### 6. Running the Application
First, ensure Ollama is running in the background.

Start the FastAPI Backend:
```bash
python run.py
```

Start the Streamlit Frontend in a new terminal:
```bash
streamlit run app.py
```

## Usage
1. Ensure Ollama is running and the LLaVA model is downloaded
2. Start the backend and frontend servers
3. Navigate to the Streamlit URL shown in the terminal
4. Click "Generate Flashcard" to create a new flashcard with a scene description

## Troubleshooting
- Make sure Ollama is running (`ollama serve`)
- Verify that the LLaVA model is downloaded
- Check that all dependencies are correctly installed
- Verify your internet connection

## Technologies Used
- Python
- FastAPI
- Streamlit
- Ollama (LLaVA model)