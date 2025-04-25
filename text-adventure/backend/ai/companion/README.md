# Text Adventure - Companion AI

This module implements the companion dog AI that assists the player with Japanese language learning and navigation through the train station.

## Architecture

The companion AI uses a tiered processing approach:

- **Tier 1**: Rule-based processing for simple requests
- **Tier 2**: Local language model (Ollama) for moderate requests
- **Tier 3**: Cloud-based language model (Amazon Bedrock) for complex requests

## Common Components

The system uses shared components for consistent behavior across tiers:

### Prompt Manager

The `PromptManager` in `core/prompt_manager.py` provides a unified prompt creation system that can be used by both tier2 and tier3 processors. It creates prompts based on the tier2 format but allows for tier-specific optimizations.

```python
from backend.ai.companion.core.prompt_manager import PromptManager

# Create a prompt manager with tier-specific configuration
tier_config = {
    'format_for_model': 'bedrock',  # or 'ollama'
    'optimize_prompt': True,        # Whether to optimize the prompt for token efficiency
    'max_prompt_tokens': 1000,      # Maximum tokens for the prompt
    'additional_instructions': ""   # Any additional instructions to add
}
prompt_manager = PromptManager(tier_specific_config=tier_config)

# Create a prompt for a request
prompt = prompt_manager.create_prompt(request)
```

### Conversation Manager

The `ConversationManager` in `core/conversation_manager.py` provides a unified conversation management system that can detect conversation states, generate contextual prompts, and maintain conversation history.

```python
from backend.ai.companion.core.conversation_manager import ConversationManager

# Create a conversation manager with tier-specific configuration
tier_config = {
    'max_history_size': 10  # Maximum number of entries to keep in history
}
conversation_manager = ConversationManager(tier_specific_config=tier_config)

# Detect conversation state
state = conversation_manager.detect_conversation_state(request, conversation_history)

# Generate a contextual prompt
prompt = conversation_manager.generate_contextual_prompt(
    request, 
    conversation_history, 
    state, 
    base_prompt
)

# Add a request-response pair to the history
updated_history = conversation_manager.add_to_history(
    conversation_history,
    request,
    response
)
```

### Context Manager

The `ContextManager` in `core/context_manager.py` provides a unified context management system that can create, retrieve, update, and delete conversation contexts.

```python
from backend.ai.companion.core.context_manager import ContextManager, default_context_manager

# Use the default context manager
context_manager = default_context_manager

# Or create a custom context manager with tier-specific configuration
tier_config = {}
context_manager = ContextManager(tier_specific_config=tier_config)

# Create a new context
context = context_manager.create_context(
    player_id="player123",
    player_language_level="N5",
    current_location="ticket_gate"
)

# Get a context by ID
context = context_manager.get_context(conversation_id)

# Update a context with a new request-response pair
context = context_manager.update_context(
    conversation_id,
    request,
    response
)

# Get or create a context
context = context_manager.get_or_create_context(
    conversation_id="conv123",
    player_id="player123",
    player_language_level="N5",
    current_location="ticket_gate"
)
```

## Tier-Specific Components

### Tier 2 (Local LLM)

- `tier2/ollama_client.py`: Client for the Ollama API
- `tier2/tier2_processor.py`: Processor that uses the Ollama client
- `tier2/response_parser.py`: Parser for Ollama responses

### Tier 3 (Cloud LLM)

- `tier3/bedrock_client.py`: Client for the Amazon Bedrock API
- `tier3/tier3_processor.py`: Processor that uses the Bedrock client
- `tier3/usage_tracker.py`: Tracker for API usage
- `tier3/scenario_detection.py`: Detector for specific scenarios
- `tier3/specialized_handlers.py`: Handlers for specific scenarios

## Usage

The companion AI is used through the `process_companion_request` function in `__init__.py`:

```python
from backend.ai.companion import process_companion_request
from backend.ai.companion.core.models import CompanionRequest

# Create a request
request = CompanionRequest(
    request_id="753689",
    player_input="How do I say 'thank you, pal' in Japanese?",
    request_type="vocabulary"
)

# Process the request
response = await process_companion_request(request)
```

The request will be classified and routed to the appropriate tier based on its complexity. 