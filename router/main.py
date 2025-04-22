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

@api_router.post("/uploadaudio")
async def create_upload_file(file: UploadFile, response: Response):
    # Generate a unique filename using uuid
    unique_filename = f"{uuid.uuid4()}"
    audio_data = await file.read()
    buffer = io.BytesIO(audio_data)
    buffer.name = f"{unique_filename}.mp3"
    transcript = speech_processor.speech_to_text_from_file(buffer)    
    agent, text_response = semantic_router.get_answer(transcript)  
    
    return {
        "question": transcript,
        "agent": agent,
        "text_response": text_response
    }

# Include the API router in your main app
app.include_router(api_router)

app.mount("/", StaticFiles(directory="./front-end/dist", html=True), name="static")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
