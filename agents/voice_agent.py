import whisper
from gtts import gTTS
import os
from typing import Optional

def speech_to_text(audio_file: str) -> str:
    """Convert audio to text using Whisper."""
    try:
        model = whisper.load_model('base')
        result = model.transcribe(audio_file)
        return result['text']
    except Exception as e:
        raise ValueError(f"STT error: {str(e)}")

def text_to_speech(text: str, output_file: str = 'output.mp3') -> Optional[str]:
    """Convert text to speech and save as audio file."""
    try:
        tts = gTTS(text, lang='en')
        tts.save(output_file)
        return output_file
    except Exception as e:
        raise ValueError(f"TTS error: {str(e)}")
