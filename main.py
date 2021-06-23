from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
import os
from random import randint
import uuid


app = FastAPI()

db = []

root = "C:/Users/Adil/Desktop/jotform/project/logo-detection-ocr"

@app.get("/")
async def root():
    return {"message": "Hello World"}

IMAGEDIR = "images/"

@app.post("/images/")
async def create_upload_file(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!

    # example of how you can save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return PlainTextResponse(str(exc), status_code=400)

@app.get("/images/")
async def read_random_file():
    # get a random file from the image directory
    files = os.listdir(IMAGEDIR)
    random_index = randint(0, len(files) - 1)

    path = f"{IMAGEDIR}{files[random_index]}"
    # notice you can use FileResponse now because it expects a path
    return FileResponse(path)

'''@app.post("/images/")
async def create_upload_file(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()  # <-- Important!

    db.append(contents)

    return {"filename": file.filename}


@app.get("/images/")
async def read_random_file():

    # get a random file from the image db
    random_index = randint(0, len(db) - 1)

    # return a response object directly as FileResponse expects a file-like object
    # and StreamingResponse expects an iterator/generator
    response = Response(content=db[random_index])

    return response'''