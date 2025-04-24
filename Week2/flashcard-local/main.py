from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import logging
import random
import json

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()

# New health-check route
@app.get("/")
async def health_check():
    return {"status": "success"}


class Vocabulary(BaseModel):
    japanese: str
    english: str

@app.get("/flashcards/")
async def generate_flashcards():
    try:
        logger.debug("Flashcard generation started")
        try:
            # Check if Ollama is running and llava is available
            model_check = requests.get('http://localhost:11434/api/list')
            models = model_check.json()
            logger.debug(f"Available models: {models}")

            if not any(model['name'] == 'llava' for model in models.get('models', [])):
                raise HTTPException(
                    status_code=500,
                    detail="LLaVA model not found. Please run 'ollama pull llava' first"
                )
        except requests.exceptions.ConnectionError:
            raise HTTPException(
                status_code=500,
                detail="Cannot connect to Ollama service. Make sure it's running with 'ollama serve'"
            )

        vocabulary_list = [
            {"japanese": "本", "english": "book"},
            {"japanese": "食べる", "english": "eat"},
            {"japanese": "飲む", "english": "drink"},
            {"japanese": "会う", "english": "meet"},
            {"japanese": "車", "english": "car"}
        ]

        vocab = random.choice(vocabulary_list)
        logger.debug(f"Selected vocabulary: {vocab}")

        try:
            # Make request to Ollama
            payload = {
                "model": "llava",
                "prompt": f"Describe a visual scene that represents the word '{vocab['english']}' in a few sentences.",
                "stream": False
            }
            logger.debug(f"Sending request to Ollama with payload: {payload}")

            response = requests.post(
                'http://localhost:11434/api/generate',
                json=payload,
                timeout=30
            )

            response_text = response.text
            logger.debug(f"Raw response from Ollama: {response_text}")

            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Ollama returned status code: {response.status_code}"
                )

            # Parse the response
            try:
                # Remove any potential leading/trailing whitespace or non-JSON characters
                response_text = response_text.strip()
                if response_text.startswith("data: "):
                    response_text = response_text[5:].strip()

                # Try to load the JSON, if it fails, try to extract the JSON part
                try:
                    response_data = json.loads(response_text)
                except json.JSONDecodeError:
                    # Attempt to extract the JSON object from the string
                    start_index = response_text.find('{')
                    end_index = response_text.rfind('}')
                    if start_index != -1 and end_index != -1:
                        json_string = response_text[start_index:end_index+1]
                        response_data = json.loads(json_string)
                    else:
                        raise

                description = response_data.get('response', '').strip()
                if not description:
                    raise ValueError("Empty response from Ollama")
                logger.debug(f"Parsed description: {description}")
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Failed response content: {response_text}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to parse Ollama response: {str(e)}"
                )

        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Ollama API error: {str(e)}"
            )

        flashcard = {
            "vocabulary": vocab,
            "description": description
        }

        return {"status": "success", "flashcard": flashcard}

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))