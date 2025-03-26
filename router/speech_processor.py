import uuid
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

class SpeechProcessor:
    def __init__(self):
        # Initialize any necessary attributes here
        pass
    
    def speech_to_text_from_file(self, audio_file):
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            response_format="text",
            file=audio_file
        )
        return transcript


    def speech_to_text(self, audio_data):
        with open(audio_data, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                response_format="text",
                file=audio_file
            )
        return transcript


    def text_to_speech(self, input_text):
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=input_text
        )
        webm_file_path = f"{uuid.uuid4()}.mp3"    
        response.stream_to_file(webm_file_path)
        return webm_file_path
    