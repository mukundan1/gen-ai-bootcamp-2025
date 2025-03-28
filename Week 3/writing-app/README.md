# Japanese Writing Practice App

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure you're in the correct directory:
```bash
cd writing-app
```

2. Run the application:
```bash
python gradio_app.py
```

3. Open your web browser and navigate to the URL shown in the terminal (typically http://127.0.0.1:7860)

## Notes
- The app will run in demo mode with mock data if the API server is not available
- You can upload handwritten images for grading
- Click "Generate New Sentence" to get new practice sentence
