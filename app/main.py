from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.pdf_ingestion import extract_pdf_content

app = FastAPI()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = extract_pdf_content(file_path)
        return result
    except Exception as e:
        return {"error": str(e)}