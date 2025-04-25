import whisper

# Load the Whisper model
model = whisper.load_model("small")  # You can use 'base', 'medium', or 'large'

# Transcribe the audio
result = model.transcribe("audio.mp3", language="ja")  # 'ja' is for Japanese

# Save the transcript in Japanese
with open("transcript_ja.txt", "w", encoding="utf-8") as f:
    f.write(result["text"])

print("Japanese transcription completed. Saved as transcript_ja.txt")
