from fastapi import FastAPI, File, UploadFile
import uuid

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

IMAGEDIR = "fastapi-images/"

@app.post("/images/")
async def create_upload_file(file: UploadFile = File(...)):

    file.filename = f"{uuid.uuid4()}.jpg"
    contents = await file.read()  # <-- Important!

    # example of how you can save the file
    with open(f"{IMAGEDIR}{file.filename}", "wb") as f:
        f.write(contents)

    return {"filename": file.filename}