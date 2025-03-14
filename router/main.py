from typing import Annotated
from fastapi import FastAPI, File, UploadFile
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
    return {"filename": file.filename}
