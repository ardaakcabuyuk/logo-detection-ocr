from fastapi import FastAPI, File, UploadFile
from fastapi.responses import Response, FileResponse, PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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
async def logo_recognize_name(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    # example of how you can save the file
    with open(path, "wb") as f:
        f.write(contents)

    recognizer = Recognizer(str(file.filename))
    logo_names = recognizer.recognize()
    return {"logo_names": logo_names}

@app.post("/keywords/")
async def recognize_keywords(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    # example of how you can save the file
    with open(path, "wb") as f:
        f.write(contents)

    ocr = OCR(path)
    keywords = ocr.extract_key_words()
    return {"logo_keywords": keywords}

@app.post("/ocr/")
async def ocr(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    with open(path, "wb") as f:
        f.write(contents)

    ocr = OCR(path)
    text = ocr.extract()


    return HTMLResponse(content = html_content, status_code=200, media_type='text/html')

@app.post("/ocr/visual")
async def ocr_visual(file: UploadFile = File(...)):
    file.filename = f"{uuid.uuid4()}.jpg"

    contents = await file.read()  # <-- Important!
    path = f"{IMAGEDIR}{file.filename}"

    with open(path, "wb") as f:
        f.write(contents)

    ocr = OCR(path)
    text = ocr.extract()
    text = text.replace('\n', '<br>')

    html_content = \
    '''
    <!DOCTYPE html>
    <html>
    <head>
      <style>
        * {
            box-sizing: border-box;
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
          }

          body {
            font-family: 'Montserrat', sans-serif;
            background: #2a3344;
          }

          .wrapper {
            margin: auto;
            max-width: 1000px;
            padding-top: 60px;
            text-align: center;
          }

          .container {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            /*border: 0.5px solid rgba(130, 130, 130, 0.25);*/
            /*box-shadow: 0 2px 3px rgba(0, 0, 0, 0.1),
                        0 0 0 1px rgba(0, 0, 0, 0.1);*/
          }

          h1 {
            color: #130f40;
            font-family: 'Varela Round', sans-serif;
            letter-spacing: -.5px;
            font-weight: 700;
            padding-bottom: 10px;
          }

          .logo {
            display: block;
            margin-left: auto;
            margin-right: auto;
            margin-top: 75px;
            width: 30%;
          }
      </style>
    </head>
    <body>
      <div class="wrapper">
        <div class="container">
          <h1>OCR Result</h1>
          <p style="margin-bottom: 20px;>''' + text + '''</p>
        </div>
      </div>
      <img class="logo" src="https://www.jotform.com/tr/resources/assets/logo/jotform-logo-transparent-800x200.png">
    </body>
    </html>
    '''
    return HTMLResponse(content = html_content, status_code=200, media_type='text/html')
