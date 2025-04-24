"""
Example script demonstrating the PromptManager with ConversationManager integration.
"""

import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add parent directory to path so we can import project modules
parent_dir = Path(__file__).parent.parent
sys.path.append(str(parent_dir))

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    IntentCategory,
    ComplexityLevel,
    ProcessingTier
)
from backend.ai.companion.core.prompt_manager import PromptManager
from backend.ai.companion.core.conversation_manager import ConversationManager, ConversationState
from backend.ai.companion.core.storage.memory import InMemoryConversationStorage


async def main():
    # Create a storage instance and a conversation manager
    storage = InMemoryConversationStorage()
    conversation_manager = ConversationManager(storage=storage)
    
    # Create a prompt manager with the conversation manager
    prompt_manager = PromptManager(conversation_manager=conversation_manager)
    
    # Create a sample conversation ID
    conversation_id = "example-conversation-1"
    
    # Create a first request
    first_request = ClassifiedRequest(
        request_id="request-1",
        player_input="What does 'kippu' mean?",
        request_type="vocabulary",
        intent=IntentCategory.VOCABULARY_HELP,
        complexity=ComplexityLevel.SIMPLE,
        processing_tier=ProcessingTier.TIER_1,
        confidence=0.9,
        extracted_entities={"word": "kippu"},
        timestamp=datetime.now()
    )
    
    # Generate a contextual prompt for the first request
    first_prompt = await prompt_manager.create_contextual_prompt(first_request, conversation_id)
    
    print("First prompt (should not include conversation history):")
    print("-" * 80)
    print(first_prompt)
    print("-" * 80)
    
    # Simulate adding an entry to the conversation history
    await conversation_manager.add_to_history(
        conversation_id=conversation_id,
        request=first_request,
        response="'Kippu' (切符) means 'ticket' in Japanese. It's an important word to know when traveling by train."
    )
    
    # Get and print the conversation history
    context = await conversation_manager.get_or_create_context(conversation_id)
    print("\nCurrent conversation context:")
    print(context)
    
    # Create a second request with a more obvious follow-up phrasing
    second_request = ClassifiedRequest(
        request_id="request-2",
        player_input="What about asking for a ticket to Odawara?",  # Using "what about" pattern to trigger follow-up detection
        request_type="translation",
        intent=IntentCategory.TRANSLATION_CONFIRMATION,
        complexity=ComplexityLevel.SIMPLE,
        processing_tier=ProcessingTier.TIER_1,
        confidence=0.9,
        extracted_entities={"destination": "Odawara", "word": "kippu"},
        timestamp=datetime.now()
    )
    
    # Manually detect the conversation state for debugging
    entries = await conversation_manager.get_entries(conversation_id)
    state = conversation_manager.detect_conversation_state(second_request, entries)
    print(f"\nDetected conversation state: {state}")
    
    # Generate a contextual prompt for the second request
    second_prompt = await prompt_manager.create_contextual_prompt(second_request, conversation_id)
    
    print("\nSecond prompt (should include conversation history):")
    print("-" * 80)
    print(second_prompt)
    print("-" * 80)


if __name__ == "__main__":
    asyncio.run(main()) 