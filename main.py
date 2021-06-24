from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, FileResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
import os
from random import randint
import uuid
from logo_detection_tool.predict import Detector, Recognizer
from ocr_tool.ocr import OCR
import zipfile
from io import BytesIO
import pathlib

app = FastAPI()

db = []

root = "C:/Users/Adil/Desktop/jotform/project/logo-detection-ocr"

@app.get("/")
async def root():
    return {"message": "Hello World"}

IMAGEDIR = "images/"

def zipfiles(filenames):
    zip_filename = "archive.zip"

    s = BytesIO()
    zf = zipfile.ZipFile(s, "w")

    for fpath in filenames:
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        print('fpath: ', fpath)
        print('fname: ', fname)
        # Add file, at correct path
        zf.write(fpath, fname)

    # Must close zip for all contents to be written
    zf.close()

    # Grab ZIP file from in-memory, make response with correct MIME-type
    resp = Response(s.getvalue(), media_type="application/x-zip-compressed", headers={
        'Content-Disposition': f'attachment;filename={zip_filename}'
    })

    return resp

@app.post("/logo_image/")
async def logo_detect(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    # example of how you can save the file
    with open(path, "wb") as f:
        f.write(contents)

    detector = Detector(str(file.filename))
    detector.detect()

    image_raw = file.filename[:-4]
    logo_paths = []
    logo_no = 0
    while True:
        path = str(pathlib.Path().absolute()) + '/logos/' + image_raw + '_logo_' + str(logo_no + 1) + '.jpg'
        if os.path.exists(path):
            logo_paths.append(path)
            logo_no += 1
        else:
            break

    return zipfiles(logo_paths)

@app.post("/logo_name/")
async def logo_recognize(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    # example of how you can save the file
    with open(path, "wb") as f:
        f.write(contents)

    recognizer = Recognizer(str(file.filename))
    logo_names = recognizer.recognize()
    return {"logo_names": logo_names}

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
