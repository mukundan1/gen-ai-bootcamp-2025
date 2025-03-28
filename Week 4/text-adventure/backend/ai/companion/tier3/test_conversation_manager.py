"""
Text Adventure - Tests for ConversationManager

This module tests the conversation manager, which is responsible for managing
conversation history, detecting conversation state, and generating contextual prompts.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime

from backend.ai.companion.core.models import ClassifiedRequest, ProcessingTier, IntentCategory, ComplexityLevel
from backend.ai.companion.core.conversation_manager import ConversationManager, ConversationState
from backend.ai.companion.core.storage.memory import InMemoryConversationStorage
from backend.ai.companion.tier3.tier3_processor import Tier3Processor

@pytest.fixture
def sample_conversation_history():
    """Sample conversation history for testing."""
    return [
        {
            "type": "user_message",
            "text": "What does 'kippu' mean?",
            "timestamp": "2023-05-01T12:00:00",
            "intent": "vocabulary_help",
            "entities": {"word": "kippu"}
        },
        {
            "type": "assistant_message",
            "text": "'Kippu' (切符) means 'ticket' in Japanese. It's an important word to know when traveling by train.",
            "timestamp": "2023-05-01T12:00:30"
        },
        {
            "type": "user_message",
            "text": "How do I ask for a ticket to Odawara?",
            "timestamp": "2023-05-01T12:01:00",
            "intent": "translation_request",
            "entities": {"destination": "Odawara", "word": "kippu"}
        },
        {
            "type": "assistant_message",
            "text": "You can say 'Odawara made no kippu o kudasai'.",
            "timestamp": "2023-05-01T12:01:30"
        }
    ]


@pytest.fixture
def sample_classified_request():
    """Sample classified request for testing."""
    return ClassifiedRequest(
        request_id="test-123",
        player_input="tell me more about train tickets",
        request_type="general",
        intent=IntentCategory.GENERAL_QUESTION,
        complexity=ComplexityLevel.SIMPLE,
        processing_tier=ProcessingTier.TIER_3,
        confidence=0.9,
        extracted_entities={"topic": "train tickets"},
        timestamp=datetime.now(),
        additional_params={"processing_tier": "tier_3"}
    )


@pytest.fixture
def conversation_id():
    """Sample conversation ID for testing."""
    return "test-conversation-123"


class TestConversationManager:
    
    def test_conversation_manager_creation(self):
        """Test creating a conversation manager."""
        manager = ConversationManager()
        assert manager is not None
        assert manager.storage is not None
    
    def test_detect_conversation_state(self, sample_conversation_history, sample_classified_request):
        """Test detecting conversation state."""
        manager = ConversationManager()
        
        # Test with a follow-up question
        sample_classified_request.player_input = "tell me more about train tickets"
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        
        assert state == ConversationState.FOLLOW_UP
        
        # Test with a clarification request
        sample_classified_request.player_input = "I don't understand what you mean"
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        
        assert state == ConversationState.CLARIFICATION
        
        # Test with a new topic
        sample_classified_request.player_input = "What time does the train to Tokyo leave?"
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        
        assert state == ConversationState.NEW_TOPIC
        
        # Test with a reference to a previous entity
        sample_classified_request.player_input = "How much does a kippu cost?"
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        
        assert state == ConversationState.FOLLOW_UP
    
    @pytest.mark.asyncio
    async def test_generate_contextual_prompt_async(self, sample_conversation_history, sample_classified_request):
        """Test generating a contextual prompt using the async method."""
        manager = ConversationManager()
        
        # Test with a follow-up question
        sample_classified_request.player_input = "tell me more about train tickets"
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        base_prompt = "You are Hachiko, a helpful companion dog."
        
        prompt = await manager.generate_contextual_prompt(
            sample_classified_request,
            sample_conversation_history,
            state,
            base_prompt
        )
        
        # Check that the prompt contains instructions for handling follow-up questions
        assert "follow-up question" in prompt
        assert "conversation history" in prompt
        assert sample_classified_request.player_input in prompt
    
    @pytest.mark.asyncio
    async def test_handle_follow_up_question_async(self, sample_conversation_history, sample_classified_request):
        """Test handling a follow-up question using the async method."""
        manager = ConversationManager()
        
        # Set up a follow-up question
        sample_classified_request.player_input = "tell me more about train tickets"
        
        # Generate a prompt for the follow-up question
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        base_prompt = "You are Hachiko, a helpful companion dog."
        
        prompt = await manager.generate_contextual_prompt(
            sample_classified_request,
            sample_conversation_history,
            state,
            base_prompt
        )
        
        # Check that the prompt contains instructions for handling follow-up questions
        assert "follow-up" in prompt.lower()
        assert "conversation history" in prompt.lower()
        assert sample_classified_request.player_input in prompt
    
    @pytest.mark.asyncio
    async def test_handle_clarification_async(self, sample_conversation_history, sample_classified_request):
        """Test handling a clarification request using the async method."""
        manager = ConversationManager()
        
        # Set up a clarification request
        sample_classified_request.player_input = "I don't understand what you mean"
        
        # Generate a prompt for the clarification request
        state = manager.detect_conversation_state(sample_classified_request, sample_conversation_history)
        base_prompt = "You are Hachiko, a helpful companion dog."
        
        prompt = await manager.generate_contextual_prompt(
            sample_classified_request,
            sample_conversation_history,
            state,
            base_prompt
        )
        
        # Check that the prompt contains instructions for handling clarification requests
        assert "clarification" in prompt.lower()
        assert "detailed explanation" in prompt.lower()
        assert sample_classified_request.player_input in prompt
    
    @pytest.mark.asyncio
    async def test_add_to_history(self, sample_classified_request, conversation_id):
        """Test adding to the conversation history."""
        # Create a ConversationManager with an in-memory storage
        storage = InMemoryConversationStorage()
        manager = ConversationManager(storage=storage)
        
        # Add a new entry to the history
        response = "Train tickets in Japan are called 'kippu' and can be purchased at ticket machines or counters."
        updated_history = await manager.add_to_history(
            conversation_id,
            sample_classified_request,
            response
        )
        
        # Check that the history was updated
        assert len(updated_history) == 2
        
        # Check the user entry
        assert updated_history[0]["type"] == "user_message"
        assert updated_history[0]["text"] == sample_classified_request.player_input
        assert updated_history[0]["intent"] == sample_classified_request.intent.value
        
        # Check the assistant entry
        assert updated_history[1]["type"] == "assistant_message"
        assert updated_history[1]["text"] == response
    
    @pytest.mark.asyncio
    async def test_integration_with_tier3_processor(self, sample_classified_request, conversation_id):
        """Test integration with Tier3Processor."""
        # Create a mock processor
        processor = MagicMock(spec=Tier3Processor)
        
        # Mock generate_response to return a simple response
        async def mock_generate_response(prompt):
            return "This is a mock response."
            
        processor.generate_response = AsyncMock(side_effect=mock_generate_response)
        
        # Create a ConversationManager with an in-memory storage
        storage = InMemoryConversationStorage()
        manager = ConversationManager(storage=storage)
        
        # Process a request with conversation history
        response, history = await manager.process_with_history(
            sample_classified_request,
            conversation_id,
            "Base prompt",
            mock_generate_response
        )
        
        # Check the response
        assert response == "This is a mock response."
        
        # Check that the history was updated
        assert len(history) == 2
        assert history[0]["type"] == "user_message"
        assert history[1]["type"] == "assistant_message"
 