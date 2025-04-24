"""
This module implements a vector-based storage and retrieval system for questions
using ChromaDB. It enables semantic similarity search and persistent storage
of question embeddings.
"""

import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Any
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class Question:
    """
    Data structure for listening comprehension questions.
    
    Features:
    - Stores question components (introduction, conversation, question)
    - Provides serialization to/from dict
    - Generates unique IDs for storage
    - Creates combined text for embedding
    """
    introduction: str
    conversation: str
    question: str

    def to_dict(self):
        return {
            "introduction": self.introduction,
            "conversation": self.conversation,
            "question": self.question
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            introduction=data.get("introduction", ""),
            conversation=data.get("conversation", ""),
            question=data.get("question", "")
        )
    
    def get_embedding_text(self) -> str:
        """Combines all components into a single text for embedding"""
        return f"{self.introduction}\n{self.conversation}\n{self.question}"
    
    def generate_id(self) -> str:
        """Creates a unique identifier based on the question content"""
        import hashlib
        text = self.get_embedding_text()
        return hashlib.md5(text.encode()).hexdigest()

class QuestionStore:
    """
    Vector database implementation using ChromaDB.
    
    Features:
    - Stores question embeddings for similarity search
    - Loads questions from JSON files
    - Performs semantic similarity search
    - Maintains persistent storage
    
    The store uses sentence transformers for embedding generation
    and ChromaDB for efficient similarity search.
    """
    
    def __init__(self, collection_name: str = "listening_questions"):
        """
        Initialize vector store with:
        - ChromaDB client
        - Embedding function
        - Named collection for questions
        """
        self.client = chromadb.Client()
        self.embedding_func = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.create_collection(
            name=collection_name,
            embedding_function=self.embedding_func
        )
    
    def add_question(self, question: Question):
        """
        Add a question to the vector store.
        
        Args:
            question (Question): Question object to store
        """
        q_id = question.generate_id()
        self.collection.add(
            documents=[question.get_embedding_text()],
            metadatas=[question.to_dict()],
            ids=[q_id]
        )
    
    def find_similar_questions(self, query: str, n_results: int = 5) -> List[Question]:
        """
        Find questions similar to the query text.
        
        Args:
            query (str): Text to search for
            n_results (int): Number of similar questions to return
            
        Returns:
            List[Question]: List of similar questions found
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        questions = []
        if results and results['metadatas']:
            for metadata in results['metadatas'][0]:
                questions.append(Question.from_dict(metadata))
        return questions

    def load_questions_from_file(self, filepath: str) -> List[Question]:
        """Load questions from a JSON file and add them to the vector store"""
        filepath = Path(filepath)
        if not filepath.exists():
            raise FileNotFoundError(f"Question file not found: {filepath}")
            
        with open(filepath) as f:
            questions_data = json.load(f)
            
        questions = []
        for data in questions_data:
            question = Question.from_dict(data)
            self.add_question(question)
            questions.append(question)
            
        print(f"Loaded {len(questions)} questions from {filepath}")
        return questions

def example_usage():
    """
    Demonstrates the QuestionStore functionality:
    1. Initializes vector store
    2. Loads questions from JSON file
    3. Performs similarity search
    4. Displays search results
    
    This example shows how to:
    - Handle file loading errors
    - Process multiple questions
    - Perform semantic search
    - Display results
    """
    # Initialize the question store
    store = QuestionStore(collection_name="example_questions")
    
    # Load questions from the parser output
    try:
        questions = store.load_questions_from_file("parsed_questions/sample_questions.json")
        print(f"\nLoaded {len(questions)} questions into vector store")
        
        # Search for similar questions
        search_query = "conversation about school assignment"
        similar_questions = store.find_similar_questions(search_query, n_results=2)
        
        # Print results
        print("\n=== Search Results ===")
        print(f"Query: {search_query}")
        for i, question in enumerate(similar_questions, 1):
            print(f"\nResult {i}:")
            print(f"Introduction: {question.introduction}")
            print(f"Question: {question.question}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please run structured_data.py first to generate the question file.")

if __name__ == "__main__":
    example_usage()