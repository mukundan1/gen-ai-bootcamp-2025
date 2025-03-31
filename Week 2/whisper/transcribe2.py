from googletrans import Translator

# Read the Japanese transcript
with open("transcript_ja.txt", "r", encoding="utf-8") as f:
    japanese_text = f.read()

# Initialize the translator
translator = Translator()

# Translate from Japanese to English
translated_text = translator.translate(japanese_text, src="ja", dest="en").text

# Save the English translation
with open("transcript_en.txt", "w", encoding="utf-8") as f:
    f.write(translated_text)

print("Translation to English completed. Saved as transcript_en.txt")
