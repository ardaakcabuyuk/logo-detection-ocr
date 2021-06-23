from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
import os
from random import randint
import uuid
from logo_detection_tool.predict import Detector
from ocr_tool.ocr import OCR

app = FastAPI()

db = []

root = "C:/Users/Adil/Desktop/jotform/project/logo-detection-ocr"

@app.get("/")
async def root():
    return {"message": "Hello World"}

IMAGEDIR = "images/"

@app.post("/logo/")
async def logo_detect(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    # example of how you can save the file
    with open(path, "wb") as f:
        f.write(contents)

    return {"filename": file.filename}

@app.post("/ocr/")
async def ocr(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    with open(path, "wb") as f:
        f.write(contents)

    print(path)
    ocr = OCR(path)
    text = ocr.extract()
    return {"response": text}
