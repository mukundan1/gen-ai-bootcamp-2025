# Text Adventure

An immersive pixel art adventure game designed to help English speakers with JLPT N5 level Japanese navigate a railway station. Players interact with a bilingual companion dog while learning practical Japanese skills through the task of purchasing a ticket to Odawara.

## Project Overview

Experience practical Japanese language learning through an engaging gaming environment. 
Navigate a meticulously crafted railway station, where you'll interact with station staff, ticket machines, and fellow travelers. 
Your bilingual dog companion will guide you through authentic Japanese conversations and cultural experiences.

### Key Features

- **Immersive Pixel Art Environment**: Navigate through a detailed railway station
- **Practical Language Learning**: Focus on real-world Japanese usage in railway stations
- **Bilingual Dog Companion**: Get assistance and translations from your companion
- **Tiered AI Approach**: Optimized for performance and cost with local-first processing
- **Progress Tracking**: Monitor your Japanese language acquisition
- **Context-Aware AI Responses**: Vector database for relevant game world knowledge

## Technical Architecture

- **Frontend**: HTML5 Canvas for pixel art rendering
- **Backend**: Python with FastAPI for game logic and AI integration
- **AI Processing**: 
  - Three-tier processing system with full configurability:
    - **Tier 1**: Rule-based systems (Default: handles 70% of interactions)
    - **Tier 2**: Local Ollama with DeepSeek 7B model (Default: handles 20% of interactions)
      - Configurable parameters via API for temperature, top_p, etc.
      - Japanese language correction features
    - **Tier 3**: Amazon Bedrock APIs (Default: handles 10% of complex scenarios)
  - Individual tiers can be enabled/disabled via configuration
  - System can be set to exclusively use a single tier
  - Default behavior uses automatic routing based on request complexity
  - Runtime tier selection API for development and testing purposes
  - Strict topic guardrails to ensure responses stay on-topic:
    - Limited to Japanese language (JLPT N5), station navigation, and game mechanics
    - Automatic redirection of off-topic questions back to game-relevant topics
    - Character-appropriate boundary enforcement that maintains immersion
  - Scenario detection system for specialized handling of common player requests
- **Knowledge Management**:
  - ChromaDB vector database for semantic search of game world knowledge
  - Conversation history tracking for contextual responses
  - Integration of conversation context and world knowledge in AI prompts
- **Data Storage**: 
  - Development: In-memory dictionaries for rapid testing
  - Production: SQLite database with Google/Facebook OAuth integration (planned)
- **Communication**: 
  - Planned: Event-based architecture with domain events
  - Current: Direct function calls between components
- **API**: RESTful API with comprehensive endpoints (mock implementations)

## Repository Structure

Current project structure:

```
text-adventure/
├── frontend/                         # Frontend 
├── backend/                          # Python backend 
│   ├── ai/                           # AI components (fully implemented)
│   │   └── companion/                # Companion dog AI
│   │       └── core/                 # Core AI components
│   │           ├── vector/           # Vector database integration
│   │           ├── storage/          # Conversation storage
│   │           └── models/           # Data models
│   ├── api/                          # API endpoints (mock implementations)
│   │   └── routers/                  # API routes for game functionality
│   ├── data/                         # Data access layer (in-memory implementations)
│   ├── game_core/                    # Game mechanics (planned implementation)
│   └── domain/                       # Domain models and business logic (planned)
└── docs/                             # Project documentation
    ├── design/                       # Design documents
    ├── pm/                           # Project management docs
    └── ui/                           # UI documentation
```

**Implementation Notes:**
- AI components are fully implemented with functioning vector database integration
- API endpoints are defined but currently use mock implementations
- Game logic is currently placeholder with planned future implementation
- Data is stored in-memory with database integration planned for later phases

**Planned Future Components:**
```
text-adventure/
├── shared/                           # Shared code/types
├── assets/                           # Raw game assets
├── tools/                            # Development and build tools
└── infrastructure/                   # Deployment configurations
```

## AI Companion System

The game's companion dog uses a sophisticated AI system to provide context-aware assistance:

1. **Tiered Processing**: Requests are classified by complexity and routed to appropriate AI tiers
2. **Conversation Management**: Tracks conversation history to provide coherent multi-turn responses
3. **Vector Knowledge Store**: Uses ChromaDB to retrieve relevant game world information
4. **Contextual Prompting**: Combines conversation context and knowledge base data for accurate responses, with strict topic guardrails that keep interactions focused on game-relevant topics

The system is designed to be efficient, using local models where possible and only calling cloud APIs for complex interactions. 
Content guardrails ensure all interactions remain focused on language learning, station navigation, and game mechanics, redirecting off-topic questions in a character-appropriate way that enhances rather than breaks immersion.

## API Documentation

The backend provides a comprehensive REST API for game functionality:

### Core Endpoints

- **Companion Assist**: `POST /api/companion/assist` - Get assistance from the companion dog
- **Dialogue Processing**: `POST /api/dialogue/process` - Process dialogue exchanges
- **Game State**: `POST /api/game/state`, `GET /api/game/state/{player_id}` - Save/load game progress
- **NPC Interaction**: Various endpoints for NPC information and dialogue
- **DeepSeek Engine**: `POST /api/npc/engine/parameters` - Configure the AI language model

Full API documentation is available at `/api/docs` when running the server.

## Development Plan

1. **Phase 1**: Japanese language processing prototype with vector database integration
2. **Phase 2**: Core game mechanics and station environment
3. **Phase 3**: Companion assistance features
4. **Phase 4**: Learning progress analytics and achievements
5. **Phase 5**: Vector database integration for context-aware responses

## Getting Started

### Prerequisites

**Required:**

- Python 3.10+
- Sentence Transformers (vector embeddings)
- ChromaDB (vector database)
- FastAPI and Uvicorn (API server)

**Optional:**

- Node.js 16+ (frontend development)
- SQLite (persistent storage)

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/text-adventure.git
   cd text-adventure
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv text-adventure-py
   source text-adventure-py/bin/activate  # On Windows: text-adventure-py\Scripts\activate
   pip install -r requirements.txt
   ```

3. Start the backend server:
   ```bash
   python -m backend.main
   ```

4. Access the API documentation at http://localhost:8000/api/docs

### AI Companion Simulator

To test the AI companion functionality without running the full game, you can use the Gradio-based simulator:

```bash
# Install Gradio if you haven't already
pip install gradio httpx python-dotenv

# Run the companion simulator
cd simulator
python app.py
```

The simulator provides a web interface to interact with the AI companion directly. This allows you to:

- Test various conversation patterns and contextual awareness
- Evaluate the effectiveness of topic guardrails
- Test Japanese language responses
- Debug AI behavior in isolation

The simulator provides options to configure different game contexts such as player location, current quest, and request type, giving you control over the testing environment.

For more information, see the [Simulator README](simulator/README.md).