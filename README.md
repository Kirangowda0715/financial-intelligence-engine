# 📊 Financial Intelligence Engine

> An AI-powered financial document analysis platform that turns earnings call transcripts into structured research insights — summaries, key metrics, risk profiles, and interactive Q&A — all in a unified chat interface.

---

## 🎓 The Codebase Masterclass (Learning Guide)

This repository is designed not just as a powerful product, but as an educational blueprint for building production-grade **Retrieval-Augmented Generation (RAG)** systems. If you are learning AI Engineering, study the codebase systematically through these 8 modules:

### 📖 The Extraction Layer
- **Module 1: PDF Ingestion (`app/pdf_ingestion.py`)** 
  *Concepts:* Extracting unstructured raw text from binary PDFs using `pdfplumber`, filtering out noise, and setting up strict quality gates.
- **Module 2: Structure Parsing (`app/structure_parser.py`)**
  *Concepts:* Using heuristic state-machines to analyze NLP semantics, auto-tagging speakers, and differentiating "Management Remarks" from "Analyst Q&A".

### 🧠 The Mathematical Layer
- **Module 3: Text Chunking (`app/chunking.py`)**
  *Concepts:* The math behind LLM token limits and the critical need for "Overlapping Sliding Windows" to prevent context loss across paragraph boundaries.
- **Module 4: Vector Embeddings (`app/embedding_store.py`)**
  *Concepts:* Transforming text into 384-dimensional conceptual space using `SentenceTransformers`, and utilizing ChromaDB as a stateful, persistent vector search engine.
- **Module 5: Semantic Retrieval (`app/retrieval.py`)**
  *Concepts:* Executing mathematical nearest-neighbor searches (Cosine Similarity) coupled with strict metadata filtering (by Company, Quarter, and Section).

### 🤖 The Intelligence Layer
- **Module 6: LLM Orchestration (`app/answer_generator.py` & extractors)**
  *Concepts:* Defensive Prompt Engineering. Enforcing JSON output schemas, designing specialized LLM Personas, and building aggressive fallback parsers to handle LLM format hallucinations.
  
### 🌐 The Integration & Product Layer
- **Module 7: API Design (`app/main.py`)**
  *Concepts:* Building a highly asynchronous, fault-tolerant REST API using FastAPI. Understanding stateful batch file uploads vs stateless GET requests.
- **Module 8: UI & State Management (`streamlit_app.py`)**
  *Concepts:* Pushing Streamlit to its limits with custom CSS (Claude/Grok aesthetics), and building a lightweight persistent database (`user_state.json`) to bypass Streamlit's stateless page reloads.

---

## ✨ Features

Upload earnings call PDFs (even in batches!) and instantly get:

| Feature | Description |
|---|---|
| 📈 **Unified Batch Summary** | Auto-synthesized analysis of all uploaded documents at once. |
| 📋 **Executive Summary** | Deep qualitative strategic analysis focusing on business fundamentals. |
| 📊 **Key Metrics** | Auto-extracted JSON tables for revenue growth, margins, and guidance. |
| ⚠️ **Risk Profile** | Explicit + implicit risks ranked by severity (High / Medium / Low). |
| 💬 **Q&A Chat** | Ask any question about your documents — backed by semantic search. |
| 🕘 **Persistent Chat** | All research sessions saved permanently — resume anytime. |

---

## 🖼️ Architecture

```text
PDF Upload (Batch)
    │
    ▼
FastAPI Backend (port 8000)
    │
    ├─► PDF Ingestion         (pdfplumber)
    ├─► Structure Parser      (segments: management, Q&A)
    ├─► Chunking              (1000-char overlapping chunks)
    ├─► Embedding             (SentenceTransformer: all-MiniLM-L6-v2)
    ├─► Vector Store          (ChromaDB — persistent local storage)
    │
    ├─► /query/               → Semantic retrieval + Ollama LLM answer
    ├─► /advanced-summary/    → Executive fundamental summary
    ├─► /metrics/             → Structured JSON financial exacts
    └─► /risks/               → Risk profiling with severity scores

Streamlit Frontend (port 8501)
    │
    ├─► Unified Chat Interface (Claude/Grok dark UI)
    ├─► Sidebar: Upload PDFs (batch processing)
    ├─► Toolbar: 1-Click extraction algorithms
    └─► Local JSON state: data/user_state.json
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/download) running locally with the `llama3` model pulled (`ollama pull llama3`)

### 1. Installation
```bash
git clone https://github.com/Kirangowda0715/financial-intelligence-engine.git
cd financial-intelligence-engine

# Create & activate environment
python -m venv venv
.\venv\Scripts\activate   # Windows
# source venv/bin/activate # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Running the System
You need **3 terminals** running simultaneously:

**Terminal 1 — Local Brain**
```bash
ollama serve
```

**Terminal 2 — Traffic Cop (Backend)**
```bash
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

**Terminal 3 — Frontend UI**
```bash
.\venv\Scripts\activate
streamlit run streamlit_app.py
```

### 3. Access
Go to **http://localhost:8501** in your browser.

---

## 📁 Project Structure

```text
financial-intelligence-engine/
│
├── app/                       # Core backend modules
│   ├── main.py                
│   ├── pdf_ingestion.py       
│   ├── structure_parser.py    
│   ├── chunking.py            
│   ├── embedding_store.py     
│   ├── retrieval.py           
│   ├── answer_generator.py    
│   ├── investor_summary.py    
│   ├── advanced_summary.py    
│   ├── metrics_extractor.py   
│   └── risk_extractor.py      
│
├── data/                      # Auto-created: user_state.json
├── chroma_storage/            # Auto-created: Persistent embeddings
├── streamlit_app.py           # Unified Frontend UI
├── requirements.txt
└── README.md
```

---

## 📄 License

MIT License — free to use, modify, and distribute.

*Built with ❤️ for financial research automation & AI Engineering education.*
