"""
Text Adventure - Vector and Conversation Integration Example

This example demonstrates the integration of the PromptManager with both
ConversationManager and TokyoKnowledgeStore, showing how conversation history
and game world knowledge together enhance the contextual understanding of the
AI companion.
"""

import asyncio
import json
import os
import logging
import tempfile
from pathlib import Path

from backend.ai.companion.core.models import (
    ClassifiedRequest,
    IntentCategory,
    ComplexityLevel,
    GameContext,
    ProcessingTier
)
from backend.ai.companion.core.prompt_manager import PromptManager
from backend.ai.companion.core.conversation_manager import ConversationManager, ConversationState
from backend.ai.companion.core.storage.memory import InMemoryConversationStorage
from backend.ai.companion.core.vector.tokyo_knowledge_store import TokyoKnowledgeStore


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    logger.info("Starting vector and conversation integration example")
    
    # Create a temporary knowledge base file for this example
    knowledge_base = [
        {
            "title": "Ticket Vocabulary",
            "type": "language_learning",
            "content": "Essential ticket vocabulary: 切符 (きっぷ - ticket), 片道 (かたみち - one-way), 往復 (おうふく - round-trip).",
            "importance": "high"
        },
        {
            "title": "Tokyo Station Overview",
            "type": "location",
            "content": "Tokyo Station is one of Japan's busiest railway stations, serving as the main interchange for various JR lines.",
            "importance": "medium"
        },
        {
            "title": "Station Navigation",
            "type": "language_learning",
            "content": "Basic navigation vocabulary: 入口 (いりぐち - entrance), 出口 (でぐち - exit), 階段 (かいだん - stairs), エレベーター (elevator).",
            "importance": "high"
        }
    ]
    
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
        json.dump(knowledge_base, f)
        knowledge_file_path = f.name
        logger.info(f"Created temporary knowledge base file at {knowledge_file_path}")
    
    try:
        # Set up the conversation manager with in-memory storage
        conversation_storage = InMemoryConversationStorage()
        conversation_manager = ConversationManager(storage=conversation_storage)
        
        # Create the prompt manager with both conversation and vector store integration
        prompt_manager = PromptManager(
            conversation_manager=conversation_manager,
            tokyo_knowledge_base_path=knowledge_file_path,
            tier_specific_config={
                "optimize_prompt": True,
                "format_for_model": "ollama"
            }
        )
        
        # Generate some example requests
        conversation_id = "demo-conversation-123"
        
        # First request about tickets (new topic)
        first_request = ClassifiedRequest(
            request_id="req-1",
            player_input="What is the Japanese word for ticket?",
            request_type="vocabulary",
            intent=IntentCategory.VOCABULARY_HELP,
            complexity=ComplexityLevel.SIMPLE,
            processing_tier=ProcessingTier.TIER_2,
            game_context=GameContext(
                player_location="Tokyo Station Entrance",
                current_objective="Purchase ticket to Odawara",
                nearby_npcs=["Information Booth Attendant"]
            )
        )
        
        # Generate a prompt for the first request
        logger.info("\n--- First request (New Topic) ---")
        logger.info(f"Player question: {first_request.player_input}")
        
        first_prompt = await prompt_manager.create_contextual_prompt(
            first_request, 
            conversation_id
        )
        
        logger.info("\nGenerated prompt (truncated):")
        logger.info(first_prompt[:500] + "..." if len(first_prompt) > 500 else first_prompt)
        
        # Simulate AI response
        ai_response = "Ticket is きっぷ (kippu) in Japanese. You can say: きっぷ を ください (kippu wo kudasai) for 'ticket please'."
        
        # Add to conversation history
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "user_message",
                "text": first_request.player_input
            }
        )
        
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "assistant_message",
                "text": ai_response
            }
        )
        
        logger.info(f"\nAI Response: {ai_response}")
        
        # Second request - follow-up about where to buy tickets
        second_request = ClassifiedRequest(
            request_id="req-2",
            player_input="What about where to buy one?",
            request_type="directions",
            intent=IntentCategory.DIRECTION_GUIDANCE,
            complexity=ComplexityLevel.SIMPLE,
            processing_tier=ProcessingTier.TIER_2,
            game_context=GameContext(
                player_location="Tokyo Station Main Hall",
                current_objective="Purchase ticket to Odawara",
                nearby_npcs=["Information Booth Attendant", "Station Staff"]
            )
        )
        
        # Generate a prompt for the second request (should include conversation history)
        logger.info("\n\n--- Second request (Follow-up) ---")
        logger.info(f"Player question: {second_request.player_input}")
        
        # Get the conversation state
        conversation_history = (await conversation_manager.get_or_create_context(conversation_id)).get("entries", [])
        state = conversation_manager.detect_conversation_state(second_request, conversation_history)
        logger.info(f"Detected conversation state: {state}")
        
        # Add message if not a follow-up as expected
        if state != ConversationState.FOLLOW_UP:
            logger.warning(f"Expected FOLLOW_UP but got {state}. This example demonstrates how the pattern matching works.")
            logger.info("The follow-up patterns in ConversationManager include: 'what about', 'how about', 'tell me more about', etc.")
            logger.info("To be detected as a follow-up, the input needs to match one of these patterns.")

        second_prompt = await prompt_manager.create_contextual_prompt(
            second_request, 
            conversation_id
        )
        
        logger.info("\nGenerated prompt (truncated):")
        logger.info(second_prompt[:500] + "..." if len(second_prompt) > 500 else second_prompt)
        
        # Simulate AI response
        ai_response_2 = "You can buy a ticket at きっぷうりば (kippu-uriba), the ticket counter. It's usually near the station entrance. In Japanese: きっぷうりば は いりぐち の ちかく です (kippu-uriba wa iriguchi no chikaku desu)."
        
        # Add to conversation history
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "user_message",
                "text": second_request.player_input
            }
        )
        
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "assistant_message",
                "text": ai_response_2
            }
        )
        
        logger.info(f"\nAI Response: {ai_response_2}")
        
        # Third request - question about a different location
        third_request = ClassifiedRequest(
            request_id="req-3",
            player_input="How do I get to the platform?",
            request_type="directions",
            intent=IntentCategory.DIRECTION_GUIDANCE,
            complexity=ComplexityLevel.SIMPLE,
            processing_tier=ProcessingTier.TIER_2,
            game_context=GameContext(
                player_location="Railway Station Ticket Area",
                current_objective="Find the Shinkansen platform",
                nearby_npcs=["Station Staff"],
                player_inventory=["Ticket to Odawara"]
            )
        )
        
        # Generate a prompt for the third request (should detect new topic despite conversation history)
        logger.info("\n\n--- Third request (New Topic/Context Change) ---")
        logger.info(f"Player question: {third_request.player_input}")
        
        # Get the conversation state
        conversation_history = (await conversation_manager.get_or_create_context(conversation_id)).get("entries", [])
        state = conversation_manager.detect_conversation_state(third_request, conversation_history)
        logger.info(f"Detected conversation state: {state}")
        
        third_prompt = await prompt_manager.create_contextual_prompt(
            third_request, 
            conversation_id
        )
        
        logger.info("\nGenerated prompt (truncated):")
        logger.info(third_prompt[:500] + "..." if len(third_prompt) > 500 else third_prompt)
        
        # Simulate AI response
        ai_response_3 = "To get to the platform, follow the signs that say ホーム (hoomu). Go up the 階段 (kaidan - stairs) or take the エレベーター (erebeetaa - elevator). In Japanese: ホーム へ 行くには、階段 か エレベーター を 使って ください。"
        
        # Add to conversation history
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "user_message",
                "text": third_request.player_input
            }
        )
        
        await conversation_manager.add_entry(
            conversation_id,
            {
                "type": "assistant_message",
                "text": ai_response_3
            }
        )
        
        logger.info(f"\nAI Response: {ai_response_3}")
        
        # Analyze what we've learned
        logger.info("\n\n--- Analysis ---")
        logger.info("This example demonstrates the integration of three key components:")
        logger.info("1. PromptManager - Creates context-aware prompts")
        logger.info("2. ConversationManager - Tracks conversation history and detects states")
        logger.info("3. KnowledgeStore - Provides relevant game world knowledge via vector search")
        
        logger.info("\nKey observations:")
        logger.info("- First prompt included relevant vocabulary but no conversation history")
        logger.info("- Second prompt detected a follow-up question and included previous exchanges")
        logger.info("- Third prompt detected a context change despite being in the same conversation")
        logger.info("- Each prompt included different relevant knowledge from the vector store")
        
    finally:
        # Clean up the temporary file
        if os.path.exists(knowledge_file_path):
            os.remove(knowledge_file_path)
            logger.info(f"Removed temporary knowledge base file {knowledge_file_path}")


if __name__ == "__main__":
    asyncio.run(main()) 