from typing import Annotated
from fastapi import FastAPI, File, UploadFile

 ## Helper
from helpers import text_to_speech, autoplay_audio, speech_to_text


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

@app.get("/")
def read_root():
    return {"Hello": "World"}


## <form action='/upload' enctype='multipart/form-data' method='post'>
##    <input name='file' type='file'>
##    <input type='submit'>
## </form>

@app.post("/uploadaudio/")
async def create_upload_file(file: UploadFile):

    # Write the audio bytes to a file
    webm_file_path = "temp_audio.mp3"
    with open(webm_file_path, "wb") as f:
        f.write(UploadFile)
    # get the translation
    transcript = speech_to_text(webm_file_path)
    
    # who is the agent
    agent = who_is_the_agent(tgranscript)
    
    # send to process
    agent_text_response = process(transcript)
    agent_audio_response = text_to_speech(final_response)
    
    
    return {"agent": agent, "text_response": agent_text_response, "audio_response": agent_audio_response}


