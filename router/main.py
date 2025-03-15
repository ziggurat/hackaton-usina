from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse


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

@app.get("/example-response/")
async def post_media_file():
    return FileResponse("./data/voice.mp3", media_type="audio/mpeg")
