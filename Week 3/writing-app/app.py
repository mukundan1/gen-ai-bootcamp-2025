import streamlit as st
import requests
import json
import random
import os
import io
from PIL import Image
import base64

# Page title
st.set_page_config(page_title="Japanese Writing Practice", layout="wide")
st.title("Japanese Writing Practice")

# Simplify session state initialization without debug logs
if 'page_state' not in st.session_state:
    st.session_state.page_state = "setup"
    st.session_state.words = []
    st.session_state.current_sentence = ""
    st.session_state.current_word = None
    st.session_state.review_data = {}

# Fetch words from API on initialization
@st.cache_data
def fetch_words(group_id):
    try:
        response = requests.get(f"http://localhost:5000/api/groups/{group_id}/words/raw")
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch words: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"Error fetching words: {e}")
        return []

# Mock Sentence Generator LLM
def generate_sentence(word):
    """
    Mock implementation of an LLM that generates a simple sentence using the provided word.
    In a real application, this would call an actual LLM API.
    """
    # Simple template sentences based on word types
    templates = [
        f"I {word['english']} every day.",
        f"She likes to {word['english']} in the morning.",
        f"The {word['english']} is on the table.",
        f"We will {word['english']} tomorrow.",
        f"Yesterday, I {word['english']} with my friend."
    ]
    return random.choice(templates)

# Mock Grading System
def grade_submission(image, english_sentence):
    """
    Mock implementation of the grading system that would:
    1. Transcribe the image using MangaOCR
    2. Translate the transcription
    3. Grade the submission
    
    In a real application, this would call actual OCR and LLM APIs.
    """
    # Mock transcription (in a real app, this would use MangaOCR)
    mock_transcriptions = ["これは本です。", "明日、友達に会います。", "昨日、ラーメンを食べました。"]
    transcription = random.choice(mock_transcriptions)
    
    # Mock translation
    translations = {
        "これは本です。": "This is a book.",
        "明日、友達に会います。": "I will meet my friend tomorrow.",
        "昨日、ラーメンを食べました。": "Yesterday, I ate ramen."
    }
    translation = translations.get(transcription, "I like to study Japanese.")
    
    # Mock grading
    grades = ["S", "A", "B", "C"]
    grade = random.choice(grades)
    
    feedback_templates = {
        "S": "Excellent! Your handwriting is clear and the sentence is perfectly accurate.",
        "A": "Very good! Your handwriting is readable and the sentence is mostly accurate.",
        "B": "Good effort. Your handwriting needs some work and there are a few grammatical errors.",
        "C": "Keep practicing. Your handwriting is difficult to read and there are several errors."
    }
    
    feedback = feedback_templates[grade]
    
    return {
        "transcription": transcription,
        "translation": translation,
        "grade": grade,
        "feedback": feedback
    }

# Initialize app by fetching words (using group_id=1 as an example)
if len(st.session_state.words) == 0:
    st.session_state.words = fetch_words(1)
    if st.session_state.words:
        st.success("Successfully loaded words!")
    else:
        st.warning("No words loaded. Using mock data instead.")
        # Add mock data if API fails
        st.session_state.words = [
            {"japanese": "本", "english": "book"},
            {"japanese": "食べる", "english": "eat"},
            {"japanese": "飲む", "english": "drink"},
            {"japanese": "会う", "english": "meet"},
            {"japanese": "車", "english": "car"}
        ]

# Function to handle state transitions
def move_to_practice():
    # Select a random word from our collection
    st.session_state.current_word = random.choice(st.session_state.words)
    # Generate a sentence based on the word
    st.session_state.current_sentence = generate_sentence(st.session_state.current_word)
    # Update state
    st.session_state.page_state = "practice"

def move_to_review(image):
    # Get review data from grading system
    st.session_state.review_data = grade_submission(image, st.session_state.current_sentence)
    # Update state
    st.session_state.page_state = "review"

def move_to_next_question():
    # Move back to practice state with a new question
    move_to_practice()

# Render appropriate content based on page state
if st.session_state.page_state == "setup":
    st.write("Welcome to the Japanese Writing Practice App!")
    st.write("Press the button below to generate a sentence to practice writing in Japanese.")
    
    if st.button("Generate Sentence"):
        move_to_practice()

elif st.session_state.page_state == "practice":
    st.header("Practice Writing")
    st.subheader("Translate and write the following sentence in Japanese:")
    st.write(st.session_state.current_sentence)
    st.write("Hint: Use the word: " + st.session_state.current_word["japanese"] + 
             " (" + st.session_state.current_word["english"] + ")")
    
    # File uploader for image submission
    uploaded_file = st.file_uploader("Upload your handwritten Japanese", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Display the uploaded image
        image = Image.open(uploaded_file)
        st.image(image, caption="Your submission", width=400)
        
        if st.button("Submit for Review"):
            move_to_review(uploaded_file)

elif st.session_state.page_state == "review":
    st.header("Review")
    st.subheader("Original Sentence:")
    st.write(st.session_state.current_sentence)
    
    st.subheader("Your Submission Results:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Transcription:**")
        st.write(st.session_state.review_data["transcription"])
        
        st.markdown("**Translation:**")
        st.write(st.session_state.review_data["translation"])
    
    with col2:
        st.markdown("**Grade:**")
        grade = st.session_state.review_data["grade"]
        
        # Display grade with appropriate color
        grade_colors = {"S": "green", "A": "blue", "B": "orange", "C": "red"}
        st.markdown(f"<h1 style='color: {grade_colors[grade]};'>{grade}</h1>", unsafe_allow_html=True)
        
    st.markdown("**Feedback:**")
    st.write(st.session_state.review_data["feedback"])
    
    if st.button("Next Question"):
        move_to_next_question()

# Add some styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    h1, h2, h3 {
        color: #1E3A8A;
    }
</style>
""", unsafe_allow_html=True)