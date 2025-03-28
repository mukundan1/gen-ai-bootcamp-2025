import gradio as gr
import requests
import random
from PIL import Image, ImageOps
from manga_ocr import MangaOcr
import difflib

class JapaneseWordPractice:
    def __init__(self):
        self.current_word = None
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

    def generate_new_word(self):
        self.current_word = random.choice(self.words)
        return (
            f"Write this word: {self.current_word['japanese']}",
            f"Meaning: {self.current_word['english']}"
        )

    def calculate_similarity(self, str1, str2):
        return difflib.SequenceMatcher(None, str1, str2).ratio()

    def determine_grade(self, similarity):
        if similarity >= 0.9:
            return "S", "Perfect! Your handwriting is excellent and matches the word exactly."
        elif similarity >= 0.8:
            return "A", "Very good! The characters are well-formed and clearly legible."
        elif similarity >= 0.6:
            return "B", "Good effort. Some characters could be improved for better clarity."
        else:
            return "C", "Keep practicing. Focus on the correct stroke order and character shape."

    def grade_submission(self, image):
        if image is None:
            return "", "", "", "No Grade", "Please upload an image first."

        try:
            transcription = self.mocr(image)
            similarity = self.calculate_similarity(transcription, self.current_word['japanese'])
            grade, feedback = self.determine_grade(similarity)
            
            return (
                f"Target word: {self.current_word['japanese']}",
                f"Your writing was read as: {transcription}",
                f"Meaning: {self.current_word['english']}",
                f"Grade: {grade} (Similarity: {similarity:.2%})",
                feedback
            )
            
        except Exception as e:
            return (
                self.current_word['japanese'],
                "Error processing image",
                "",
                "No Grade",
                f"Error: {str(e)}"
            )

    def process_input(self, image=None, sketch=None):
        """Handle input from either image upload or sketch pad"""
        if sketch is not None:
            # Convert sketch to PIL Image if it's not None
            return self.grade_submission(sketch)
        elif image is not None:
            return self.grade_submission(image)
        return "", "", "", "No Grade", "Please provide input either by drawing or uploading an image."

def create_app():
    app = JapaneseWordPractice()
    
    with gr.Blocks(title="Japanese Word Practice") as interface:
        gr.Markdown("# Japanese Word Practice")
        
        with gr.Row():
            with gr.Column():
                word_text = gr.Textbox(label="Word to Practice", interactive=False)
                meaning_text = gr.Textbox(label="Meaning", interactive=False)
                generate_btn = gr.Button("Generate New Word")
                
                # Add tabs for different input methods
                with gr.Tabs():
                    with gr.TabItem("Drawing Pad"):
                        sketch_input = gr.Sketchpad(
                            label="Write here",
                            brush_radius=2,
                            brush_color="#000000",
                            height=400,
                            width=400,
                            background_color="#FFFFFF"
                        )
                    with gr.TabItem("Image Upload"):
                        image_input = gr.Image(label="Or upload your handwritten Japanese", type="pil")
                
                submit_btn = gr.Button("Submit for Review")
                clear_btn = gr.Button("Clear")

            with gr.Column():
                target_word = gr.Textbox(label="Target Word", interactive=False)
                transcription = gr.Textbox(label="Your Writing", interactive=False)
                translation = gr.Textbox(label="Meaning", interactive=False)
                grade = gr.Textbox(label="Grade", interactive=False)
                feedback = gr.Textbox(label="Feedback", interactive=False)

        # Event handlers
        generate_btn.click(
            fn=app.generate_new_word,
            outputs=[word_text, meaning_text]
        )
        
        # Update submit button to handle both input types
        submit_btn.click(
            fn=app.process_input,
            inputs=[image_input, sketch_input],
            outputs=[target_word, transcription, translation, grade, feedback]
        )

        # Add clear button functionality
        clear_btn.click(
            lambda: (None, None),
            outputs=[image_input, sketch_input]
        )

        # Generate initial word on load
        initial_word, initial_meaning = app.generate_new_word()
        word_text.value = initial_word
        meaning_text.value = initial_meaning

    return interface

if __name__ == "__main__":
    demo = create_app()
    demo.launch()
