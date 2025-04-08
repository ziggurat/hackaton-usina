from dotenv import load_dotenv

load_dotenv()

import uuid  # Import the uuid module
import io
import os

import uvicorn
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Annotated

from usina_semantic_router import UsinaSemanticRouter
from speech_processor import SpeechProcessor
from s3_audio_response_handler import S3AudioResponseHandler

## Fast API
app = FastAPI()
speech_processor = SpeechProcessor()
audio_response_handler = S3AudioResponseHandler()
semantic_router = UsinaSemanticRouter()

## CORS configuration
origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/uploadaudio/")
async def create_upload_file(file: UploadFile, response: Response):
    # Generate a unique filename using uuid
    unique_filename = f"{uuid.uuid4()}"  # Generate a unique filename with .mp3 extension

    # Read the uploaded file and get the transcript
    audio_data = await file.read()
    buffer = io.BytesIO(audio_data)
    buffer.name = f"{unique_filename}.mp3"
    transcript = speech_processor.speech_to_text_from_file(buffer)

    # Identify the agent from the transcript
    agent = semantic_router.get_route(transcript)

    # Request the agent for a response from the transcript
    agent_text_response = process(transcript)

    # From the text response, generate an audio response
    audio_response = speech_processor.text_to_speech(agent_text_response)

    # Upload to S3 and get the file URL
    audio_file_url = audio_response_handler.upload_audio_response_to_s3(audio_response, os.environ['AWS_REGION'],
                                                                        os.environ['S3_BUCKET_NAME'])

    # Return JSON response with file URL and other data
    return {
        "agent": agent,
        "text_response": agent_text_response,
        "audio_response_url": audio_file_url,
    }


def process(transcript):
    return transcript


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)