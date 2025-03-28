import boto3
import json
import os
from pathlib import Path
import subprocess
from typing import List, Dict
import tempfile

class AudioGenerator:
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.polly = boto3.client('polly')
        self.voices = {
            'announcer': 'Takumi',
            'male': ['Takumi', 'Tomoko'],
            'female': ['Mizuki', 'Kazuha'],
        }

    def _format_conversation(self, question: Dict) -> Dict:
        """Use Bedrock to format conversation with speaker annotations"""
        prompt = f"""
        Format this JLPT listening question for audio generation.
        Identify speakers and mark them as [Speaker A], [Speaker B], etc.
        Keep the announcer parts marked as [Announcer].
        
        Introduction: {question['introduction']}
        Conversation: {question['conversation']}
        Question: {question['question']}
        """

        response = self.bedrock.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "prompt": prompt,
                "max_tokens": 2000,
                "temperature": 0.7,
            })
        )
        
        result = json.loads(response['body'].read())
        return result['content'][0]['text']

    def _generate_voice_segment(self, text: str, voice_id: str) -> str:
        """Generate audio segment using Amazon Polly"""
        response = self.polly.synthesize_speech(
            Text=text,
            OutputFormat='mp3',
            VoiceId=voice_id,
            LanguageCode='ja-JP'
        )

        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
            temp_file.write(response['AudioStream'].read())
            return temp_file.name

    def generate_audio(self, question: Dict) -> str:
        """Generate full audio file from question"""
        # Create output directory if it doesn't exist
        output_dir = Path("generated_audio")
        output_dir.mkdir(exist_ok=True)

        # Format conversation with speaker annotations
        formatted = self._format_conversation(question)
        segments = []

        # Generate audio segments for each part
        parts = formatted.split('\n')
        for part in parts:
            if '[Announcer]' in part:
                voice = self.voices['announcer']
            elif '[Speaker A]' in part:
                voice = self.voices['male'][0]
            elif '[Speaker B]' in part:
                voice = self.voices['female'][0]
            else:
                continue

            audio_segment = self._generate_voice_segment(part, voice)
            segments.append(audio_segment)

        # Combine audio segments using FFmpeg
        output_file = output_dir / f"question_{hash(question['question'])}.mp3"
        
        # Create FFmpeg concat file
        with tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False) as f:
            for segment in segments:
                f.write(f"file '{segment}'\n")
            concat_list = f.name

        # Combine audio files
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', concat_list,
            '-c', 'copy',
            str(output_file)
        ])

        # Cleanup temporary files
        os.unlink(concat_list)
        for segment in segments:
            os.unlink(segment)

        return str(output_file)
