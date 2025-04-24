import streamlit as st
import requests
from requests.exceptions import RequestException
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def check_backend():
    try:
        response = requests.get("http://localhost:8001/")
        return response.status_code == 200
    except:
        return False

def generate_flashcard():
    if not check_backend():
        st.error("Backend is not running. Start it with 'python run.py'")
        return

    try:
        st.info("Requesting flashcard from backend...")
        response = requests.get("http://localhost:8001/flashcards/")
        logger.debug(f"Response received: {response.text}")
        
        if response.status_code != 200:
            st.error(f"Backend error: {response.status_code}")
            st.error(f"Error details: {response.text}")
            return
        
        data = response.json()
        logger.debug(f"Parsed JSON data: {data}")
        
        if "status" not in data or data["status"] != "success":
            st.error(f"Invalid response from backend: {data}")
            st.write(f"Raw response content: {response.text}")
            return
        
        flashcard = data["flashcard"]
        st.success("Flashcard generated successfully!")
        st.write(f"Japanese: {flashcard['vocabulary']['japanese']}")
        st.write(f"English: {flashcard['vocabulary']['english']}")
        st.write("Scene Description:")
        st.write(flashcard['description'])
        
    except requests.ConnectionError as e:
        logger.error(f"Connection error: {str(e)}")
        st.error(f"Could not connect to backend: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        st.error(f"Error: {str(e)}")
        st.error("Check the backend logs for more details")

st.title("Japanese Flashcards")
st.write("Study Japanese vocabulary with flashcards")

if st.button("Generate Flashcard"):
    generate_flashcard()