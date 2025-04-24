"""
Dialogue router for the API.
"""

import logging
import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from backend.api.models.dialogue_process import (
    DialogueProcessRequest,
    DialogueProcessResponse,
    DialogueContent,
    FeedbackContent,
    NPCState,
    CompanionState,
    UIElements,
    GameStateUpdate,
    ResponseMetadata,
    DialogueOption,
    UISuggestion
)
from backend.api.adapters.base import AdapterFactory

# Set up logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter(
    prefix="/dialogue",
    tags=["dialogue"],
    responses={
        404: {"description": "Not found"},
        422: {"description": "Validation Error"},
        500: {"description": "Internal server error"}
    }
)

# Create adapter factory
adapter_factory = AdapterFactory()


@router.post("/process", response_model=DialogueProcessResponse)
async def process_dialogue(request: Request, dialogue_request: DialogueProcessRequest):
    """
    Process a dialogue exchange between a player and an NPC or companion.
    
    Args:
        request: The FastAPI request object
        dialogue_request: The dialogue process request
        
    Returns:
        A dialogue process response
    """
    try:
        logger.info(f"Processing dialogue for player {dialogue_request.playerId} with {dialogue_request.speakerId}")
        
        # Get the request adapter
        request_adapter = adapter_factory.get_request_adapter("dialogue_process")
        
        # Transform the API request to internal format
        # In a real implementation, this would be passed to a dialogue processing service
        internal_request = request_adapter.adapt(dialogue_request)
        
        # For now, we'll create a mock response
        # In a real implementation, this would come from a dialogue processing service
        mock_internal_response = {
            "request_id": str(uuid.uuid4()),
            "response_text": "To buy a ticket, you need to use the ticket machine. In Japanese, a ticket is called 'kippu' (切符).",
            "japanese_text": "切符を買うには、券売機を使う必要があります。",
            "transliteration": "Kippu o kau ni wa, kenbaiki o tsukau hitsuyō ga arimasu.",
            "is_correct": True,
            "mood": "helpful",
            "animation": "pointing",
            "dialogue_options": [
                {
                    "id": "option1",
                    "text": "How much is a ticket to Tokyo?",
                    "japanese_text": "東京までの切符はいくらですか？",
                    "transliteration": "Tōkyō made no kippu wa ikura desu ka?"
                },
                {
                    "id": "option2",
                    "text": "Where is the ticket machine?",
                    "japanese_text": "券売機はどこですか？",
                    "transliteration": "Kenbaiki wa doko desu ka?"
                }
            ],
            "highlight_elements": ["ticket_machine"],
            "suggestions": [
                {
                    "text": "Ask about train times",
                    "type": "question"
                },
                {
                    "text": "Learn how to say 'platform' in Japanese",
                    "type": "vocabulary"
                }
            ],
            "vocabulary_learned": ["切符 (kippu) - ticket", "券売機 (kenbaiki) - ticket machine"],
            "processing_tier": "rule"
        }
        
        # Get the response adapter
        response_adapter = adapter_factory.get_response_adapter("dialogue_process")
        
        # Transform the internal response to API format
        # In a real implementation, this would come from the dialogue processing service
        api_response = DialogueProcessResponse(
            dialogueContent=DialogueContent(
                responseText=mock_internal_response["response_text"],
                japaneseText=mock_internal_response["japanese_text"],
                transliteration=mock_internal_response["transliteration"]
            ),
            feedbackContent=FeedbackContent(
                isCorrect=mock_internal_response["is_correct"],
                corrections=None,
                encouragement="Good question! Let me help you with that."
            ),
            npcState=NPCState(
                mood=mock_internal_response["mood"],
                animation=mock_internal_response["animation"]
            ) if dialogue_request.speakerType.value == "npc" else None,
            companionState=CompanionState(
                mood=mock_internal_response["mood"],
                animation=mock_internal_response["animation"]
            ) if dialogue_request.speakerType.value == "companion" else None,
            uiElements=UIElements(
                dialogueOptions=[
                    DialogueOption(
                        id=option["id"],
                        text=option["text"],
                        japaneseText=option.get("japanese_text"),
                        transliteration=option.get("transliteration")
                    ) for option in mock_internal_response["dialogue_options"]
                ],
                highlightElements=mock_internal_response["highlight_elements"],
                suggestions=[
                    UISuggestion(
                        text=suggestion["text"],
                        type=suggestion["type"]
                    ) for suggestion in mock_internal_response["suggestions"]
                ]
            ),
            gameStateUpdates=GameStateUpdate(
                vocabularyLearned=mock_internal_response["vocabulary_learned"]
            ),
            metadata=ResponseMetadata(
                responseId=mock_internal_response["request_id"],
                processingTier=mock_internal_response["processing_tier"],
                timestamp=datetime.now().isoformat()
            )
        )
        
        return api_response
        
    except Exception as e:
        logger.error(f"Error processing dialogue: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Internal Server Error",
                "message": "An error occurred while processing the dialogue",
                "details": str(e)
            }
        ) 