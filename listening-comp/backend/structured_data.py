"""
This module handles the parsing of listening comprehension transcripts.
It extracts structured question data using Amazon Bedrock and manages the storage
of parsed questions.
"""

import boto3
from typing import List, Optional, Dict, Any
from .vector_store import Question, QuestionStore
import json
import os
from pathlib import Path

MODEL_ID = "amazon.nova-lite-v1:0"
BEDROCK_REGION = "ap-south-1"

class TranscriptParser:
    """
    Parses transcripts into structured question formats using AI.
    Features:
    - Extracts introduction, conversation, and question components
    - Saves parsed questions to JSON files
    - Integrates with vector store for similarity search
    - Handles batch processing of multiple questions
    """

    def __init__(self, model_id: str = MODEL_ID, question_store: Optional[QuestionStore] = None, output_dir: str = "parsed_questions"):
        """
        Initialize the transcript parser with:
        - Bedrock client for AI processing
        - Question store for vector search
        - Output directory for saving results
        """
        self.bedrock_client = boto3.client('bedrock-runtime', region_name=BEDROCK_REGION)
        self.model_id = model_id
        self.question_store = question_store or QuestionStore()
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def extract_question_structure(self, text: str, inference_config: Optional[Dict[str, Any]] = None) -> Optional[Question]:
        """
        Use AI to extract structured components from text.
        
        Process:
        1. Validates input text
        2. Constructs prompt for AI model
        3. Calls Bedrock for analysis
        4. Parses response into structured format
        5. Stores result in vector database
        
        Args:
            text: Raw text to analyze
            inference_config: Model configuration parameters
            
        Returns:
            Structured Question object or None if parsing fails
        """
        if not text:
            print("Error: Text cannot be empty.")
            return None

        if inference_config is None:
            inference_config = {"temperature": 0.7}

        prompt = f"""Analyze this text and extract these components:
        - Introduction/context
        - The conversation
        - The actual question being asked

        Format your response exactly like this:
        INTRODUCTION:
        <the introduction text>
        CONVERSATION:
        <the conversation text>
        QUESTION:
        <the question text>

        Text to analyze:
        {text}"""

        try:
            print(f"Sending request to Bedrock with model ID: {self.model_id}")
            response = self.bedrock_client.converse(
                modelId=self.model_id,
                messages=[{
                    "role": "user",
                    "content": [{"text": prompt}]
                }],
                inferenceConfig=inference_config
            )
            print(f"Received response from Bedrock: {response}")

            # Parse the response
            response_text = response['output']['message']['content'][0]['text']
            parts = {"introduction": "", "conversation": "", "question": ""}
            current_section = None
            
            for line in response_text.split('\n'):
                line = line.strip()
                if line.startswith('INTRODUCTION:'):
                    current_section = "introduction"
                elif line.startswith('CONVERSATION:'):
                    current_section = "conversation"
                elif line.startswith('QUESTION:'):
                    current_section = "question"
                elif current_section and line:
                    parts[current_section] = parts[current_section] + line + '\n'
            
            # Clean up the extracted text
            for key in parts:
                parts[key] = parts[key].strip()
            
            question = Question(**parts)
            if question:
                # Store the question in vector store
                self.question_store.add_question(question)
            return question
            
        except Exception as e:
            print(f"Error generating response: {str(e)}, type: {type(e)}")
            return None

    def parse_transcript(self, transcript: str) -> List[Question]:
        """Parse full transcript into list of structured questions"""
        # Split transcript into individual questions (implementation depends on transcript format)
        question_segments = self._split_into_questions(transcript)
        
        # Process each question segment
        questions = []
        for segment in question_segments:
            question = self.extract_question_structure(segment)
            if question:
                questions.append(question)
            
        return questions
    
    def _split_into_questions(self, transcript: str) -> List[str]:
        # This method should be implemented based on the actual format of your transcript
        # For now, returning a simple split (you'll need to adjust this)
        return transcript.split("\n\n")
    
    def find_similar_questions(self, text: str, n_results: int = 5) -> List[Question]:
        """Find similar questions from the vector store"""
        return self.question_store.find_similar_questions(text, n_results)

    def save_questions(self, questions: List[Question], filename: str):
        """
        Save parsed questions to JSON file for persistence.
        
        Args:
            questions: List of parsed Question objects
            filename: Output JSON filename
        """
        output_path = self.output_dir / filename
        questions_data = [q.to_dict() for q in questions]
        with open(output_path, 'w') as f:
            json.dump(questions_data, f, indent=2)
        print(f"Saved {len(questions)} questions to {output_path}")

def test_transcript_parser():
    """
    Demonstrates the transcript parser functionality:
    1. Processes sample transcript
    2. Extracts structured questions
    3. Saves to JSON file
    4. Tests similarity search
    5. Displays results
    """
    # Sample transcript text
    sample_transcript = """
    You hear a conversation between two students discussing a project.
    
    Male: Hey Sarah, have you started working on the history project yet?
    Female: Not really, I've been quite busy with other assignments.
    Male: Well, we should probably get started soon. It's due next week.
    Female: You're right. What topic did you have in mind?
    
    What are the students mainly discussing?
    
    ---
    
    You hear an announcement at a train station.
    
    Announcer: Attention passengers. The 3:15 express train to London will be delayed by approximately 20 minutes due to signal problems. We apologize for any inconvenience caused. Passengers can wait in the main hall where refreshments are available.
    
    What is the main purpose of this announcement?
    """

    # Initialize parser with output directory
    parser = TranscriptParser(output_dir="parsed_questions")
    
    # Parse the transcript and save to file
    questions = parser.parse_transcript(sample_transcript)
    parser.save_questions(questions, "sample_questions.json")
    
    # Print results
    print("\n=== Parsed Questions ===\n")
    for i, question in enumerate(questions, 1):
        print(f"\nQuestion {i}:")
        print("-" * 50)
        print(f"Introduction:\n{question.introduction}\n")
        print(f"Conversation:\n{question.conversation}\n")
        print(f"Question:\n{question.question}\n")
        print("-" * 50)
    
    # Add similarity search test
    print("\n=== Testing Similar Questions ===\n")
    search_text = "conversation about school project"
    similar_questions = parser.find_similar_questions(search_text)
    print(f"\nFound {len(similar_questions)} similar questions for: '{search_text}'")
    for i, question in enumerate(similar_questions, 1):
        print(f"\nSimilar Question {i}:")
        print("-" * 50)
        print(f"Question:\n{question.question}\n")

if __name__ == "__main__":
    test_transcript_parser()