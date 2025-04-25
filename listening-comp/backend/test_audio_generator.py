import unittest
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent))

from audio_generator import AudioGenerator

class TestAudioGenerator(unittest.TestCase):
    def setUp(self):
        self.audio_gen = AudioGenerator()
        self.sample_question = {
            'introduction': '今から対話を聞きます。',
            'conversation': '''
            男：すみません、図書館はどこですか。
            女：この建物の2階です。
            男：ありがとうございます。
            ''',
            'question': 'この会話は、どこで行われていますか。'
        }

    def test_format_conversation(self):
        formatted = self.audio_gen._format_conversation(self.sample_question)
        self.assertIsInstance(formatted, str)
        self.assertIn('[Announcer]', formatted)
        self.assertIn('[Speaker', formatted)

    def test_generate_voice_segment(self):
        test_text = "[Announcer] 今から対話を聞きます。"
        audio_file = self.audio_gen._generate_voice_segment(test_text, 'Takumi')
        self.assertTrue(audio_file.endswith('.mp3'))

    def test_generate_audio(self):
        output_file = self.audio_gen.generate_audio(self.sample_question)
        self.assertTrue(output_file.endswith('.mp3'))
        self.assertTrue(output_file.startswith('generated_audio/question_'))

if __name__ == '__main__':
    unittest.main()