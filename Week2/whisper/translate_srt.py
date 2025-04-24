from deep_translator import GoogleTranslator
import re

# Initialize the translator
translator = GoogleTranslator(source="ja", target="en") 

# Read the Japanese subtitle file
with open("subtitles_ja.srt", "r", encoding="utf-8") as f:
    srt_content = f.readlines()

translated_srt = []
for line in srt_content:
    if re.match(r"^\d+$", line.strip()) or "-->" in line:  # Keep timing unchanged
        translated_srt.append(line)
    elif line.strip():
        translated_text = translator.translate(line.strip())
        translated_srt.append(translated_text + "\n")
    else:
        translated_srt.append("\n")

# Save the translated subtitles
with open("subtitles_en.srt", "w", encoding="utf-8") as f:
    f.writelines(translated_srt)

print("English subtitles generated: subtitles_en.srt")
