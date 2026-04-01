from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os

from app.pdf_ingestion import extract_pdf_content
from app.structure_parser import parse_transcript_structure
from app.chunking import chunk_segments
from app.embedding_store import store_chunks
from app.retrieval import retrieve_chunks, get_document_chunks
from app.answer_generator import generate_answer
from app.investor_summary import generate_investor_summary
from app.advanced_summary import generate_advanced_summary
from app.metrics_extractor import extract_financial_metrics
from app.risk_extractor import extract_risks

app = FastAPI()

UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/upload-pdf/")
async def upload_pdf(
    file: UploadFile = File(...),
    company: str = Form(...),
    quarter: str = Form(...)
):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        result = extract_pdf_content(file_path)

        merged_text = "\n".join([p["text"] for p in result["pages"]])

        segments = parse_transcript_structure(merged_text)
        chunks = chunk_segments(segments)

        document_id = store_chunks(
            chunks,
            company_name=company,
            quarter=quarter
        )

        summary = generate_investor_summary(chunks)

        return {
            "document_id": document_id,
            "company": company,
            "quarter": quarter,
            "total_pages": result["total_pages"],
            "total_segments": len(segments),
            "total_chunks": len(chunks),
            "investor_summary": summary
        }

    except Exception as e:
        return {"error": str(e)}


@app.post("/query/")
async def query_documents(
    query: str,
    company: str = None,
    quarter: str = None,
    section_type: str = None
):
    try:
        retrieved = retrieve_chunks(
            query,
            company=company,
            quarter=quarter,
            section_type=section_type
        )

        answer = generate_answer(query, retrieved)

        return {
            "query": query,
            "filters": {
                "company": company,
                "quarter": quarter,
                "section_type": section_type
            },
            "answer": answer,
            "sources": [
                {
                    "speaker": r["metadata"]["speaker_name"],
                    "role": r["metadata"]["speaker_role"],
                    "section": r["metadata"]["section_type"],
                    "company": r["metadata"]["company"],
                    "quarter": r["metadata"]["quarter"],
                    "score": r["score"]
                }
                for r in retrieved
            ]
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/advanced-summary/")
async def advanced_summary_endpoint(document_id: str):
    try:
        chunks = get_document_chunks(document_id, limit=12)
        if not chunks:
            return {"error": "Document not found or empty"}
        summary = generate_advanced_summary(chunks)
        return {"advanced_summary": summary}
    except Exception as e:
        return {"error": str(e)}

@app.get("/metrics/")
async def metrics_endpoint(document_id: str):
    try:
        chunks = get_document_chunks(document_id, limit=20)
        if not chunks:
            return {"error": "Document not found or empty"}
        metrics = extract_financial_metrics(chunks)
        return {"metrics": metrics}
    except Exception as e:
        return {"error": str(e)}

@app.get("/risks/")
async def risks_endpoint(document_id: str):
    try:
        chunks = get_document_chunks(document_id, limit=15)
        if not chunks:
            return {"error": "Document not found or empty"}
        risks = extract_risks(chunks)
        return {"risks": risks}
    except Exception as e:
        return {"error": str(e)}
