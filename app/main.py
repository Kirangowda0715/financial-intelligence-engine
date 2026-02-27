from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.pdf_ingestion import extract_pdf_content
from app.structure_parser import parse_transcript_structure
from app.chunking import chunk_segments
from app.embedding_store import store_chunks

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
        # Step 1: Extract PDF
        result = extract_pdf_content(file_path)

        # Step 2: Merge pages
        merged_text = "\n".join(
            [page["text"] for page in result["pages"]]
        )

        # Step 3: Parse structure
        segments = parse_transcript_structure(merged_text)

        # Step 4: Chunk
        chunks = chunk_segments(segments)

        # Step 5: Store embeddings
        document_id = store_chunks(
            chunks,
            company_name="ITC",
            quarter="Q1 FY25"
        )

        # Final return
        return {
            "document_id": document_id,
            "total_pages": result["total_pages"],
            "total_segments": len(segments),
            "total_chunks": len(chunks)
        }

    except Exception as e:
        return {"error": str(e)}