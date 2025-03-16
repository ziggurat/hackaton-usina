import tempfile
from typing import Annotated

import boto3
from boto3.s3.transfer import S3UploadFailedError
from botocore.exceptions import ClientError, NoCredentialsError

import aiofiles
import uvicorn
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.responses import FileResponse
from helpers import text_to_speech, speech_to_text
from usina_semantic_router import UsinaSemanticRouter
from fastapi.middleware.cors import CORSMiddleware


 ## OPEN AI
import os
import openai
from openai import OpenAI
from dotenv import load_dotenv
import uuid  # Import the uuid module

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=api_key)
openai.api_key = api_key


 ## Fast API
app = FastAPI()

origins = [
    "*",  # Allow all origins
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
async def create_upload_file(file: UploadFile, response: Response):
    # Generate a unique filename using uuid
    unique_filename = f"{uuid.uuid4()}"  # Generate a unique filename with .mp3 extensio    n

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_file_path = temp_file.name
    temp_file.close()  # Close the file so aiofiles can open it

    # Write content to the temporary file asynchronously
    async with aiofiles.open(temp_file_path, 'wb') as out_file:
        content = await file.read()  # Read the content of the UploadFile
        await out_file.write(content)
        webm_file_path = temp_file_path

    """
    # Get the translation
    transcript = speech_to_text(webm_file_path)

    # Who is the agent
    semantic_router = UsinaSemanticRouter()
    agent = semantic_router.get_route(transcript)

    # Send to process
    agent_text_response = process(transcript)
    agent_audio_response = text_to_speech(agent_text_response)

    # Upload to S3 and get the file URL
    audio_file_url = upload_file_to_s3(agent_audio_response, "s3-hackaton-usina")

    # Return JSON response with file URL and other data    
    return {
        "agent": agent,
        "text_response": agent_text_response,
        "audio_response_url": audio_file_url,
        "Access-Control-Allow-Origin": "*"
    }
    """
    return {"Hola": "Mundo"}

    # Get the translation
def who_is_the_agent(transcript):
    return transcript
    
def process(transcript):
    return transcript

def upload_file_to_s3(file_name: str, bucket: str, object_name: str = None):
    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Create an S3 client
    s3_client = boto3.client('s3')

    try:
        # Upload the file
        s3_client.upload_file(file_name, bucket, object_name)
        print(f"File {file_name} uploaded to {bucket}/{object_name}")

        # Construct the full URL of the uploaded file
        file_url = f"https://{bucket}.s3.us-east-1.amazonaws.com/{object_name}"        
        return file_url  # Return the full URL
    except FileNotFoundError:
        print(f"The file {file_name} was not found")
    except NoCredentialsError:
        print("Credentials not available")
    except ClientError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)