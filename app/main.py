from fastapi import FastAPI, UploadFile, File, Form
import shutil
import os
from typing import List

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
    files: List[UploadFile] = File(...),
    company: str = Form(...),
    quarter: str = Form(...)
):
    all_chunks = []
    document_ids = []
    total_pages = 0
    total_segments = 0

    try:
        for file in files:
            file_path = os.path.join(UPLOAD_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            result = extract_pdf_content(file_path)
            merged_text = "\n".join([p["text"] for p in result["pages"]])
            segments = parse_transcript_structure(merged_text)
            chunks = chunk_segments(segments)

            if not chunks:
                continue

            doc_id = store_chunks(chunks, company_name=company, quarter=quarter)

            document_ids.append(doc_id)
            all_chunks.extend(chunks[:12])
            
            total_pages += result["total_pages"]
            total_segments += len(segments)

        if not document_ids:
            return {"error": "No documents processed"}

        summary = generate_investor_summary(all_chunks)

        return {
            "document_ids": document_ids,
            "company": company,
            "quarter": quarter,
            "total_pages": total_pages,
            "total_segments": total_segments,
            "total_chunks": len(all_chunks),
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

        # Guard: if nothing was retrieved, return early with a helpful message
        if not retrieved:
            return {
                "query": query,
                "answer": (
                    "⚠️ No relevant content found in your uploaded documents for this query. "
                    "Please make sure you have uploaded a PDF and the document is indexed, "
                    "then try rephrasing your question."
                ),
                "sources": []
            }

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
                    "speaker": r["metadata"].get("speaker_name", "Unknown"),
                    "role": r["metadata"].get("speaker_role", "Unknown"),
                    "section": r["metadata"].get("section_type", "Unknown"),
                    "company": r["metadata"].get("company", "Unknown"),
                    "quarter": r["metadata"].get("quarter", "Unknown"),
                    "score": r["score"]
                }
                for r in retrieved
            ]
        }

    except Exception as e:
        # Return error inside answer key so the frontend can display it
        return {
            "query": query,
            "answer": f"❌ Backend error: {str(e)}",
            "sources": []
        }


@app.get("/advanced-summary/")
async def advanced_summary_endpoint(document_ids: str):
    try:
        doc_idx = document_ids.split(",")
        chunks = []
        for d in doc_idx:
            chunks.extend(get_document_chunks(d, limit=6))
            
        if not chunks:
            return {"error": "Document not found or empty"}
        summary = generate_advanced_summary(chunks)
        return {"advanced_summary": summary}
    except Exception as e:
        return {"error": str(e)}


@app.get("/metrics/")
async def metrics_endpoint(document_ids: str):
    try:
        doc_idx = document_ids.split(",")
        chunks = []
        for d in doc_idx:
            chunks.extend(get_document_chunks(d, limit=8))
            
        if not chunks:
            return {"error": "Document not found or empty"}
        metrics = extract_financial_metrics(chunks)
        return {"metrics": metrics}
    except Exception as e:
        return {"error": str(e)}


@app.get("/risks/")
async def risks_endpoint(document_ids: str):
    try:
        doc_idx = document_ids.split(",")
        chunks = []
        for d in doc_idx:
            chunks.extend(get_document_chunks(d, limit=8))
            
        if not chunks:
            return {"error": "Document not found or empty"}
        risks = extract_risks(chunks)
        return {"risks": risks}
    except Exception as e:
        return {"error": str(e)}
