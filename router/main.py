from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from helpers import text_to_speech, speech_to_text
from usina_semantic_router import UsinaSemanticRouter
from fastapi.middleware.cors import CORSMiddleware


 ## OPEN AI
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
openai.api_key = api_key


 ## Fast API
app = FastAPI()

origins = [
    "*",
    "*",
    "*",
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


## <form action='/upload' enctype='multipart/form-data' method='post'>
##    <input name='file' type='file'>
##    <input type='submit'>
## </form>

@app.get("/example-response/")
async def post_media_file():
    return FileResponse("./data/voice.mp3", media_type="audio/mpeg")

@app.get("/dummy-response/")
async def dummyresponse():
    return {"agent": "agentx", "text_response": "lalala", "audio_response": "lalala response"}

@app.post("/uploadaudio/")
async def create_upload_file(file: UploadFile):

    # Write the audio bytes to a file
    webm_file_path = "temp_audio.mp3"
    print(file.filename)
    # get the translation
    transcript = speech_to_text(webm_file_path)
    
    # who is the agent
    semantic_router = UsinaSemanticRouter()
    agent = semantic_router.get_route(transcript)
    
    # send to process
    agent_text_response = process(transcript)
    agent_audio_response = text_to_speech(agent_text_response)

    return {"agent": agent, "text_response": agent_text_response, "audio_response": agent_audio_response}

def who_is_the_agent(transcript):
    return transcript
    
def process(transcript):
    return transcript
