import gradio as gr
import requests
import random
from PIL import Image
import json
from manga_ocr import MangaOcr
import difflib

class JapaneseWritingPractice:
    def __init__(self):
        self.current_word = None
        self.current_sentence = ""
        self.words = self.initialize_words()
        self.mocr = MangaOcr()

    def initialize_words(self):
        try:
            response = requests.get("http://localhost:5000/api/groups/1/words/raw")
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        
        # Fallback mock data
        return [
            {"japanese": "本", "english": "book"},
            {"japanese": "食べる", "english": "eat"},
            {"japanese": "飲む", "english": "drink"},
            {"japanese": "会う", "english": "meet"},
            {"japanese": "車", "english": "car"}
        ]

    def generate_sentence(self, word):
        templates = [
            f"I {word['english']} every day.",
            f"She likes to {word['english']} in the morning.",
            f"The {word['english']} is on the table.",
            f"We will {word['english']} tomorrow.",
            f"Yesterday, I {word['english']} with my friend."
        ]
        return random.choice(templates)

    def generate_new_practice(self):
        self.current_word = random.choice(self.words)
        self.current_sentence = self.generate_sentence(self.current_word)
        return (
            self.current_sentence,
            f"Hint: Use the word: {self.current_word['japanese']} ({self.current_word['english']})"
        )

    def calculate_similarity(self, str1, str2):
        """Calculate string similarity ratio."""
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def determine_grade(self, similarity):
        """Determine grade based on similarity score."""
        if similarity >= 0.9:
            return "S", "Excellent! Your handwriting is very clear and accurate."
        elif similarity >= 0.8:
            return "A", "Very good! Your writing is clear with minor imperfections."
        elif similarity >= 0.6:
            return "B", "Good effort. Keep practicing to improve accuracy."
        else:
            return "C", "Keep practicing. Focus on character formation and stroke order."

    def grade_submission(self, image):
        if image is None:
            return "Please upload an image first.", "", "", "No Grade", "No feedback available."

        try:
            # Perform OCR on the uploaded image
            transcription = self.mocr(image)
            
            # Calculate similarity with current practice sentence
            similarity = self.calculate_similarity(transcription, self.current_word['japanese'])
            
            # Determine grade and feedback
            grade, feedback = self.determine_grade(similarity)
            
            # Prepare translation (using the current word's English meaning for simplicity)
            translation = self.current_word['english']
            
            return (
                self.current_sentence,
                transcription,
                translation,
                f"Grade: {grade} (Similarity: {similarity:.2%})",
                feedback
            )
            
        except Exception as e:
            return (
                self.current_sentence,
                "Error processing image",
                "",
                "No Grade",
                f"Error: {str(e)}"
            )

def create_app():
    app = JapaneseWritingPractice()
    
    with gr.Blocks(title="Japanese Writing Practice") as interface:
        gr.Markdown("# Japanese Writing Practice")
        
        with gr.Row():
            with gr.Column():
                sentence_text = gr.Textbox(label="Sentence to Practice", interactive=False)
                hint_text = gr.Textbox(label="Hint", interactive=False)
                generate_btn = gr.Button("Generate New Sentence")
                
                image_input = gr.Image(label="Upload your handwritten Japanese", type="pil")
                submit_btn = gr.Button("Submit for Review")

            with gr.Column():
                original_sentence = gr.Textbox(label="Original Sentence", interactive=False)
                transcription = gr.Textbox(label="Transcription", interactive=False)
                translation = gr.Textbox(label="Translation", interactive=False)
                grade = gr.Textbox(label="Grade", interactive=False)
                feedback = gr.Textbox(label="Feedback", interactive=False)

        # Event handlers
        generate_btn.click(
            fn=app.generate_new_practice,
            outputs=[sentence_text, hint_text]
        )
        
        submit_btn.click(
            fn=app.grade_submission,
            inputs=[image_input],
            outputs=[original_sentence, transcription, translation, grade, feedback]
        )

        # Generate initial sentence on load
        initial_sentence, initial_hint = app.generate_new_practice()
        sentence_text.value = initial_sentence
        hint_text.value = initial_hint

    return interface

if __name__ == "__main__":
    demo = create_app()
    demo.launch()
