from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.pdf_ingestion import extract_pdf_content
from app.structure_parser import parse_transcript_structure
from app.chunking import chunk_segments

# FIRST create app
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

        merged_text = "\n".join(
            [page["text"] for page in result["pages"]]
        )

        segments = parse_transcript_structure(merged_text)

        chunks = chunk_segments(segments)

        return {
            "total_pages": result["total_pages"],
            "total_segments": len(segments),
            "total_chunks": len(chunks),
            "chunk_preview": chunks[:3]
        }

    except Exception as e:
        return {"error": str(e)}