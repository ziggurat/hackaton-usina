from .s3_audio_response_handler import S3AudioResponseHandler
from .speech_processor import SpeechProcessor
from .usina_semantic_router import UsinaSemanticRouter
from typing import Annotated
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi import FastAPI, File, UploadFile, Response, APIRouter
import uvicorn
import os
import io
import uuid  # Import the uuid module
from dotenv import load_dotenv

load_dotenv()


# Fast API
app = FastAPI()
speech_processor = SpeechProcessor()
audio_response_handler = S3AudioResponseHandler()
semantic_router = UsinaSemanticRouter()

# CORS configuration
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

# Create a new router for your API endpoints
api_router = APIRouter(prefix="/api")


@api_router.get("/hello")
def read_root():
    return {"Hello": "World"}


@api_router.post("/uploadaudio")
async def create_upload_file(file: UploadFile, response: Response):
    # Generate a unique filename using uuid
    unique_filename = f"{uuid.uuid4()}"
    audio_data = await file.read()
    buffer = io.BytesIO(audio_data)
    buffer.name = f"{unique_filename}.mp3"
    transcript = speech_processor.speech_to_text_from_file(buffer)
    agent = semantic_router.get_route(transcript)
    agent_text_response = process(transcript)
    audio_response = speech_processor.text_to_speech(agent_text_response)
    audio_file_url = audio_response_handler.upload_audio_response_to_s3(
        audio_response,
        os.environ['AWS_REGION'],
        os.environ['S3_BUCKET_NAME']
    )
    return {
        "agent": agent,
        "text_response": agent_text_response,
        "audio_response_url": audio_file_url,
    }

# Include the API router in your main app
app.include_router(api_router)

app.mount("/", StaticFiles(directory="./front-end/dist", html=True), name="static")


def process(transcript):
    #  return semantic_router.get_answer(transcript)
    return transcript


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
