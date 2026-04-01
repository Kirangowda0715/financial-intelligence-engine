# Feature Implementation Plan: Financial Intelligence Engine

The user has requested a comprehensive suite of advanced financial analysis features. To keep the system robust and avoids over-complication, we will split these features into two phases: **Phase 1 (Do Now)** and **Phase 2 (Do Later)**.

## 🟢 Better to Add NOW (Phase 1)

These features fit naturally into our current Document Processing and RAG architecture. We can implement them by adding specific new prompt endpoints and frontend UI widgets without overhauling the database.

1. **Structured Executive Summary & Investor Decision** *(Combines features 6 & 7)*
   - **What it does:** Upgrades the existing `investor_summary` generation. It will now force a structured output acting as a long-term investor, providing:
     - Concise 150-word summary (Highlights, Drivers, Risks, Outlook)
     - Business Quality & Growth Potential
     - Final Decision (Buy / Watch / Avoid) with explanation.
   - **Why now:** It's a direct upgrade to our existing summary block and provides immediate high value.

2. **Financial Metrics Extraction (JSON)** *(Feature 2)*
   - **What it does:** A specialized extraction prompt that forces the LLM to return exactly: `{"revenue_growth": "...", "margin": "...", "guidance": "...", "segments": [...]}`.
   - **Why now:** We can easily add a backend endpoint `/extract-metrics/` that queries the document context and a frontend widget to display these KPIs cleanly.

3. **Financial Risks Extraction** *(Feature 1)*
   - **What it does:** Dedicated mechanism to isolate and list key risks, implicit risks, and their severity (Low/Medium/High).
   - **Why now:** High value for financial analysis. We can add a "Risk Analysis" tab in the UI that uses a specialized retrieval prompt.

## 🟡 Better to Add LATER (Phase 2)

These features require significant architectural changes, such as cross-document processing, more complex chunking, or advanced NLP techniques.

1. **Multi-Quarter Comparison** *(Feature 3)*
   - **Why later:** Our current system is designed to upload and query a single document at a time. Comparing trends across quarters requires storing document metadata hierarchically, allowing the user to select multiple past reports, and generating comparative RAG queries.
   
2. **Deep Q&A Analysis** *(Feature 4)*
   - **Why later:** To effectively analyze Q&A, our `structure_parser.py` needs to guarantee it can perfectly separate the "Prepared Remarks" from the "Q&A" section across arbitrary PDF formats. We should harden the parser first before building analytics on top of it.

3. **Linguistic Tone Analysis** *(Feature 5)*
   - **Why later:** General tone is captured in the "Management Quality" part of the summary. A granular, sentence-by-sentence linguistic cue analyzer is better suited for a dedicated sentiment analysis model (like FinBERT) rather than standard LLM prompting, to keep costs and latency low.

---

## User Review Required

> [!IMPORTANT]  
> Are you happy with this prioritization? If you approve, I will proceed to:
> 1. Upgrade the current `investor_summary.py` prompt to include the Executive Summary and Investor Decision.
> 2. Create a new `metrics_extractor.py` and `risk_extractor.py` in the backend.
> 3. Update `main.py` with the new API endpoints.
> 4. Update the Streamlit frontend UI to display these new insights cleanly.

Please let me know if you would like me to proceed with Phase 1!
