                                   # Generative AI Architecture

Below is an ASCII diagram showing the architecture of our Generative AI system:

    [User/Teacher] -----> [Landing Portal] -----> [Study Activities]
                              |                         |
                              |                         |
                              v                         v
                        [Word Groups] <-------- [Sentence Constructor]
                              |                [Visual Flashcards]
                              |                [Speaking Practice]
                              v                [Reading Immersion]
                     [Core Database]           [Writing Practice]
                              |                         |
                              |                         v
                        [Vector DB] <----- [Retrieval Augmentation] <--> [Prompt Cache]
                              |                         |
                              |                         v
                              +-----------------> [Large Language Model]
                                                        |
                                                [Input GuardRail]
                                                        |
                                                [Output GuardRail]
                                                        |
                                                        v
                                                [Final Response]

## Key Components

### Frontend Layer

- **Landing Portal**: Main entry point
- **Word Groups**: Vocabulary management
- **Study Activities**: Learning modules
  - Sentence Constructor
  - Visual Flashcards
  - Speaking Practice
  - Reading Immersion
  - Writing Practice

### Database Layer

- **Core Database**: 2000+ words
- **Vector Database**: Semantic search
- **Prompt Cache**: Optimization

### AI Processing

- **Retrieval Augmentation**: Context enhancement
- **LLM (7B parameters)**: Text generation
- **GuardRails**: Safety & quality

## Data Flow

1. User accesses portal
2. Selects study activity
3. System retrieves relevant data
4. AI processes request
5. Safety checks applied
6. Response delivered to user
