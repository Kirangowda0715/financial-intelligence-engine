import streamlit as st
import requests
import os
import json
import uuid

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Financial Intelligence Engine", layout="wide")

# ================================
# 🔥 CLAUDE/GROK UI CSS INJECTION
# ================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }

    [data-testid="stSidebar"] {
        background-color: #121826 !important;
        border-right: 1px solid #1E293B;
    }

    header[data-testid="stHeader"] {
        background: transparent;
        height: 0px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: white !important;
    }

    button[kind="secondary"] {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: #E2E8F0 !important;
        font-weight: 500 !important;
        transition: all 0.2s ease;
    }
    button[kind="secondary"]:hover {
        background-color: #334155 !important;
        border-color: #475569 !important;
        color: white !important;
    }

    button[kind="primary"] {
        background-color: #3B82F6 !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    button[kind="primary"]:hover {
        background-color: #2563EB !important;
    }

    [data-testid="chatAvatarIcon-user"] { background-color: #3B82F6; }
    [data-testid="chatAvatarIcon-assistant"] { background-color: #10B981; }

    .stChatMessage {
        background-color: #121826;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #1E293B;
    }

    [data-testid="metric-container"] {
        background-color: #121826;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }

    [data-testid="stExpander"] {
        background-color: #121826;
        border: 1px solid #1E293B;
        border-radius: 12px;
    }

    .block-container { padding-top: 1.5rem !important; }

    button[data-baseweb="tab"] { font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

# ================================
# PERSISTENCE ENGINE
# ================================
STATE_FILE = "data/user_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                if "documents" in data:
                    st.session_state["documents"] = data["documents"]
                if "chat_sessions" in data:
                    st.session_state["chat_sessions"] = data["chat_sessions"]
                if "active_chat_id" in data:
                    st.session_state["active_chat_id"] = data["active_chat_id"]
        except Exception:
            pass

def save_state():
    os.makedirs("data", exist_ok=True)
    state = {
        "documents": st.session_state.get("documents", []),
        "chat_sessions": st.session_state.get("chat_sessions", {}),
        "active_chat_id": st.session_state.get("active_chat_id")
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def add_to_chat(role, content, tag=None, sources=None):
    """Append a message to the active chat session."""
    msg = {"role": role, "content": content}
    if tag:
        msg["tag"] = tag
    if sources:
        msg["sources"] = sources
    st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"].append(msg)
    save_state()

# ================================
# INITIALIZE STATE
# ================================
if "state_loaded" not in st.session_state:
    st.session_state["state_loaded"] = True
    load_state()

if "documents" not in st.session_state:
    st.session_state["documents"] = []

if "chat_sessions" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state["chat_sessions"] = {initial_id: {"name": "New Chat", "messages": []}}
if "active_chat_id" not in st.session_state:
    st.session_state["active_chat_id"] = list(st.session_state["chat_sessions"].keys())[0]

# ================================
# SIDEBAR
# ================================
st.sidebar.markdown(
    "<h2 style='color:#E2E8F0;margin-bottom:0'>📊 FinIntel</h2>"
    "<p style='color:#64748B;font-size:13px;margin-top:4px'>AI Financial Research Engine</p>",
    unsafe_allow_html=True
)
st.sidebar.markdown("---")

# ---- Upload Section ----
st.sidebar.subheader("📁 Upload Documents")
with st.sidebar.form("upload_form", clear_on_submit=True):
    uploaded_files = st.file_uploader("Upload PDFs (Batch)", type=["pdf"], accept_multiple_files=True)
    company = st.text_input("Company / Tag")
    quarter = st.text_input("Quarter (e.g. Q1 FY25)")
    submitted = st.form_submit_button("⚡ Process Batch", use_container_width=True)

if submitted:
    if uploaded_files and company and quarter:
        success_count = 0
        for f in uploaded_files:
            with st.spinner(f"Processing {f.name}..."):
                files = {"file": (f.name, f, "application/pdf")}
                data_payload = {"company": company, "quarter": quarter}
                res = requests.post(f"{API_URL}/upload-pdf/", files=files, data=data_payload)

                if res.status_code == 200:
                    response = res.json()
                    doc_id = response.get("document_id")
                    summary = response.get("investor_summary", "No summary available.")

                    if not any(d["id"] == doc_id for d in st.session_state["documents"]):
                        st.session_state["documents"].append({
                            "id": doc_id,
                            "company": company,
                            "quarter": quarter,
                            "summary": summary,
                            "filename": f.name
                        })

                    # Auto-name the chat if it's "New Chat"
                    active_chat = st.session_state["chat_sessions"][st.session_state["active_chat_id"]]
                    if active_chat["name"] == "New Chat":
                        st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["name"] = f"{company} {quarter}"

                    # Add upload confirmation + summary as a chat message
                    upload_msg = (
                        f"📄 **Document uploaded:** `{f.name}` ({company} — {quarter})\n\n"
                        f"---\n### 📈 Investor Summary\n\n{summary}"
                    )
                    add_to_chat("assistant", upload_msg, tag="upload")
                    success_count += 1
                else:
                    st.sidebar.error(f"Error: {f.name}")

        if success_count > 0:
            save_state()
            st.sidebar.success(f"✅ {success_count} file(s) uploaded!")
            st.rerun()
    else:
        st.sidebar.warning("Please fill all fields and select files.")

st.sidebar.markdown("---")

# ---- Chat History ----
st.sidebar.header("💬 Chat History")

if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_id = str(uuid.uuid4())
    st.session_state["chat_sessions"][new_id] = {"name": "New Chat", "messages": []}
    st.session_state["active_chat_id"] = new_id
    save_state()
    st.rerun()

st.sidebar.markdown("---")

for session_id, session_data in reversed(list(st.session_state["chat_sessions"].items())):
    label = session_data.get("name", "New Chat")
    is_active = session_id == st.session_state["active_chat_id"]
    btn_label = f"🟢 {label}" if is_active else f"⚪ {label}"
    if st.sidebar.button(btn_label, key=f"chat_{session_id}", use_container_width=True):
        st.session_state["active_chat_id"] = session_id
        st.rerun()

# ================================
# MAIN AREA — UNIFIED CHAT
# ================================
active_chat = st.session_state["chat_sessions"][st.session_state["active_chat_id"]]
chat_name = active_chat.get("name", "New Chat")

st.markdown(
    f"<h2 style='color:#E2E8F0;margin-bottom:0'>💬 {chat_name}</h2>",
    unsafe_allow_html=True
)

# Toolbar row
col_tools = st.columns([1, 1, 1, 1, 3])
with col_tools[0]:
    if st.button("📝 Summary", help="Generate Executive Summary", use_container_width=True):
        if st.session_state["documents"]:
            doc = st.session_state["documents"][-1]
            with st.spinner("Generating executive summary..."):
                res = requests.get(f"{API_URL}/advanced-summary/", params={"document_id": doc["id"]})
                if res.status_code == 200:
                    summary = res.json().get("advanced_summary", "No summary generated.")
                    msg = f"📋 **Executive Summary** — _{doc['company']} {doc['quarter']}_\n\n---\n\n{summary}"
                    add_to_chat("assistant", msg, tag="summary")
                    st.rerun()
                else:
                    st.error("Failed to generate summary.")
        else:
            st.warning("Upload a document first.")

with col_tools[1]:
    if st.button("📊 Metrics", help="Extract Key Financial Metrics", use_container_width=True):
        if st.session_state["documents"]:
            doc = st.session_state["documents"][-1]
            with st.spinner("Extracting financial metrics..."):
                res = requests.get(f"{API_URL}/metrics/", params={"document_id": doc["id"]})
                if res.status_code == 200:
                    m = res.json().get("metrics", {})
                    segs = "\n".join([f"  - {s}" for s in m.get("segments", [])]) or "  - Not mentioned"
                    msg = (
                        f"📊 **Key Metrics** — _{doc['company']} {doc['quarter']}_\n\n---\n\n"
                        f"| Metric | Value |\n|---|---|\n"
                        f"| Revenue Growth | {m.get('revenue_growth') or 'N/A'} |\n"
                        f"| Margin / EBITDA | {m.get('margin') or 'N/A'} |\n"
                        f"| Guidance | {m.get('guidance') or 'N/A'} |\n\n"
                        f"**Segment Performance:**\n{segs}"
                    )
                    add_to_chat("assistant", msg, tag="metrics")
                    st.rerun()
                else:
                    st.error("Failed to extract metrics.")
        else:
            st.warning("Upload a document first.")

with col_tools[2]:
    if st.button("⚠️ Risks", help="Extract Risk Profile", use_container_width=True):
        if st.session_state["documents"]:
            doc = st.session_state["documents"][-1]
            with st.spinner("Analyzing risks..."):
                res = requests.get(f"{API_URL}/risks/", params={"document_id": doc["id"]})
                if res.status_code == 200:
                    risks = res.json().get("risks", [])
                    if isinstance(risks, list) and risks:
                        lines = [f"⚠️ **Risk Profile** — _{doc['company']} {doc['quarter']}_\n\n---\n"]
                        for r in risks:
                            if not isinstance(r, dict):
                                continue
                            sev = r.get("severity", "Unknown")
                            emoji = "🔴" if sev.lower() == "high" else ("🟡" if sev.lower() == "medium" else "🟢")
                            lines.append(
                                f"{emoji} **{r.get('risk_name','Risk')}** ({sev})\n"
                                f"> {r.get('description','')}\n"
                                f"> *Source: {r.get('source_reference','N/A')}*\n"
                            )
                        msg = "\n".join(lines)
                    else:
                        msg = f"✅ No major risks identified for _{doc['company']} {doc['quarter']}_."
                    add_to_chat("assistant", msg, tag="risks")
                    st.rerun()
                else:
                    st.error("Failed to extract risks.")
        else:
            st.warning("Upload a document first.")

with col_tools[3]:
    if st.button("🗑️ Clear", help="Clear this chat thread", use_container_width=True):
        st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"] = []
        st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["name"] = "New Chat"
        save_state()
        st.rerun()

st.markdown("---")

# ---- Render unified chat messages ----
messages = active_chat.get("messages", [])

if not messages:
    st.markdown(
        "<div style='text-align:center;color:#475569;padding:60px 0'>"
        "<h3>Start your research session</h3>"
        "<p>Upload a PDF in the sidebar, then use the toolbar buttons above or ask a question below.</p>"
        "</div>",
        unsafe_allow_html=True
    )

for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📌 View Sources"):
                for s in msg["sources"]:
                    st.write(f"- **{s.get('speaker','?')}** ({s.get('role','?')}) | {s.get('company','?')} {s.get('quarter','?')} | Score: {round(s.get('score', 0), 3)}")

# ---- Chat input ----
if query := st.chat_input("Ask anything about your documents…"):
    # Auto-name the chat from first question
    if active_chat["name"] == "New Chat":
        short = (query[:28] + "…") if len(query) > 28 else query
        st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["name"] = short

    add_to_chat("user", query)

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            # Use the most recently uploaded doc for context filtering if available
            recent_doc = st.session_state["documents"][-1] if st.session_state["documents"] else None
            params = {"query": query}
            if recent_doc:
                params["company"] = recent_doc["company"]
                params["quarter"] = recent_doc["quarter"]

            res = requests.post(f"{API_URL}/query/", params=params)

            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "No answer generated.")
                sources = data.get("sources", [])

                st.markdown(answer)
                if sources:
                    with st.expander("📌 View Sources"):
                        for s in sources:
                            st.write(f"- **{s.get('speaker','?')}** ({s.get('role','?')}) | {s.get('company','?')} {s.get('quarter','?')} | Score: {round(s.get('score',0), 3)}")

                st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"].append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })
                save_state()
            else:
                st.error(f"Query failed (HTTP {res.status_code})")