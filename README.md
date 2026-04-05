# 📊 Financial Intelligence Engine

> An AI-powered financial document analysis platform that turns earnings call transcripts into structured research insights — summaries, key metrics, risk profiles, and interactive Q&A — all in a unified chat interface.

---

## ✨ What It Does

Upload any earnings call PDF and instantly get:

| Feature | Description |
|---|---|
| 📈 **Investor Summary** | Auto-generated on upload — key highlights from the transcript |
| 📋 **Executive Summary** | Deep strategic analysis with a Buy / Watch / Avoid decision |
| 📊 **Key Metrics** | Revenue growth, margins, EBITDA, guidance, segment performance |
| ⚠️ **Risk Profile** | Explicit + implicit risks ranked by severity (High / Medium / Low) |
| 💬 **Q&A Chat** | Ask any question about your documents — backed by semantic search |
| 🕘 **Chat History** | All research sessions saved permanently — resume anytime |

---

## 🖼️ Architecture

```
PDF Upload
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
    ├─► /advanced-summary/    → Executive summary + investor decision
    ├─► /metrics/             → Structured JSON financial metrics
    └─► /risks/               → Risk profiling with severity scores

Streamlit Frontend (port 8501)
    │
    ├─► Unified Chat Interface (Claude/Grok dark UI)
    ├─► Sidebar: Upload PDFs (batch)
    ├─► Sidebar: Chat History (persistent sessions)
    └─► Local JSON state: data/user_state.json
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit + Custom CSS (Claude/Grok dark mode) |
| **Backend** | FastAPI + Uvicorn |
| **LLM** | Ollama (`llama3:latest`) — runs locally |
| **Embeddings** | SentenceTransformers (`all-MiniLM-L6-v2`) |
| **Vector DB** | ChromaDB (persistent local storage) |
| **PDF Parsing** | pdfplumber |
| **State** | JSON file (`data/user_state.json`) |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- `llama3` model pulled in Ollama

### 1. Clone the Repository

```bash
git clone https://github.com/Kirangowda0715/financial-intelligence-engine.git
cd financial-intelligence-engine
```

### 2. Create and Activate Virtual Environment

```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Pull the LLM Model

```bash
ollama pull llama3
```

---

## ▶️ Running the Project

You need **3 terminals** open simultaneously:

### Terminal 1 — Start LLM (Ollama)
```bash
ollama serve
```

### Terminal 2 — Start Backend (FastAPI)
```bash
.\venv\Scripts\activate
uvicorn app.main:app --reload
```

### Terminal 3 — Start Frontend (Streamlit)
```bash
.\venv\Scripts\activate
streamlit run streamlit_app.py
```

### Access the App

| Service | URL |
|---|---|
| 🖥️ Streamlit App | http://localhost:8501 |
| ⚡ FastAPI Docs | http://localhost:8000/docs |
| 🤖 Ollama API | http://localhost:11434 |

---

## 📖 How to Use

1. **Upload a PDF** — Use the sidebar to upload one or more earnings call PDFs. Enter the company name and quarter, then click **"⚡ Process Batch"**. The investor summary appears in the chat automatically.

2. **Run Analysis** — Use the toolbar buttons at the top of the chat:
   - **📝 Summary** → Executive decision analysis
   - **📊 Metrics** → Revenue, margin, guidance table
   - **⚠️ Risks** → Ranked risk profile

3. **Ask Questions** — Type any question in the chat input at the bottom. The system will semantically search your documents and generate a structured analyst-style answer with source citations.

4. **Switch Research Sessions** — Click **"➕ New Chat"** in the sidebar to start a fresh session. Click any past session to resume your previous research exactly where you left off.

---

## 📁 Project Structure

```
financial-intelligence-engine/
│
├── app/
│   ├── main.py                # FastAPI routes
│   ├── pdf_ingestion.py       # PDF text extraction
│   ├── structure_parser.py    # Transcript segmentation
│   ├── chunking.py            # Text chunking
│   ├── embedding_store.py     # ChromaDB + embeddings
│   ├── retrieval.py           # Semantic search
│   ├── answer_generator.py    # LLM Q&A generation
│   ├── investor_summary.py    # Base summary
│   ├── advanced_summary.py    # Executive summary + decision
│   ├── metrics_extractor.py   # Financial metrics JSON
│   └── risk_extractor.py      # Risk profiling
│
├── data/                      # Uploaded PDFs + user_state.json
├── chroma_storage/            # Persistent vector embeddings
├── streamlit_app.py           # Frontend UI
├── requirements.txt
└── README.md
```

---

## ⚙️ Environment Notes

- `data/` and `chroma_storage/` are **gitignored** — your uploaded documents and embeddings stay private.
- State is saved to `data/user_state.json` automatically — no database setup needed.
- The system is designed for **local, private use** — no data leaves your machine.

---

## 🧠 How the Q&A Works

1. Your question is embedded using `all-MiniLM-L6-v2`
2. ChromaDB retrieves the top 8 most semantically relevant chunks from your uploaded transcripts
3. The chunks are assembled into a structured prompt with source context
4. Ollama (`llama3`) generates a structured analyst response covering: Key Insights, Management Commentary, Key Drivers, Risks, and Analyst Perspective
5. Source citations are attached to every answer

---

## 🗺️ Roadmap

- [ ] **Phase 3:** Multi-quarter trend comparison (revenue, margins, tone)
- [ ] **Phase 3:** Q&A section deep-analysis (analyst sentiment scoring)
- [ ] **Phase 4:** Cloud LLM support (Groq / Gemini API fallback)
- [ ] **Phase 4:** Export research report as PDF/Word
- [ ] **Phase 5:** Multi-company cross-analysis dashboard

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with ❤️ for financial research automation.*
