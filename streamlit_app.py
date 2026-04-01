import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Financial Intelligence Engine", layout="wide")

st.title("📊 Financial Intelligence Engine")

# ================================
# 🔥 CLAUDE/GROK UI CSS INJECTION
# ================================
st.markdown("""
<style>
    /* Global Background and Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main App Background (Grok Dark) */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    
    /* Sidebar Background & Border */
    [data-testid="stSidebar"] {
        background-color: #121826 !important;
        border-right: 1px solid #1E293B;
    }

    /* Hide default Streamlit headers and menus for a proprietary feel */
    header[data-testid="stHeader"] {
        background: transparent;
        height: 0px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Input Fields (Sleek Claude Style) */
    div[data-baseweb="input"] > div, div[data-baseweb="select"] > div {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        color: white !important;
    }
    
    /* Buttons */
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
    
    /* Chat Message Bubbles (Claude Style) */
    [data-testid="chatAvatarIcon-user"] {
        background-color: #3B82F6;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background-color: #10B981;
    }
    .stChatMessage {
        background-color: #121826;
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #1E293B;
    }

    /* Metrics Cards */
    [data-testid="metric-container"] {
        background-color: #121826;
        border: 1px solid #1E293B;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Expander / Accoridan */
    [data-testid="stExpander"] {
        background-color: #121826;
        border: 1px solid #1E293B;
        border-radius: 12px;
    }

    /* Top Padding killer */
    .block-container {
        padding-top: 2rem !important;
    }
    
    /* Tabs */
    button[data-baseweb="tab"] {
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("---")

# Persistence Engine
import os
import json
import uuid

STATE_FILE = "data/user_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                if "documents" in data:
                    st.session_state["documents"] = data["documents"]
                if "active_doc_id" in data:
                    st.session_state["active_doc_id"] = data["active_doc_id"]
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
        "active_doc_id": st.session_state.get("active_doc_id"),
        "chat_sessions": st.session_state.get("chat_sessions", {}),
        "active_chat_id": st.session_state.get("active_chat_id")
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# Initialize tracking state
if "state_loaded" not in st.session_state:
    st.session_state["state_loaded"] = True
    load_state()

if "documents" not in st.session_state:
    st.session_state["documents"] = []
if "active_doc_id" not in st.session_state:
    st.session_state["active_doc_id"] = None

# Chat History tracking
if "chat_sessions" not in st.session_state:
    initial_id = str(uuid.uuid4())
    st.session_state["chat_sessions"] = {initial_id: {"name": "New Chat", "messages": []}}
if "active_chat_id" not in st.session_state:
    st.session_state["active_chat_id"] = list(st.session_state["chat_sessions"].keys())[0]


# ------------------------
# SIDEBAR
# ------------------------
st.sidebar.header("Document Library")

if st.session_state["documents"]:
    doc_options = {d["id"]: f"{d.get('filename', d['company'])} ({d['quarter']})" for d in st.session_state["documents"]}
    
    # Optional "All Documents" (for cross-query chat) could be added, but we stick to specific doc or None tracking
    selected_id = st.sidebar.selectbox(
        "Active Document", 
        options=list(doc_options.keys()), 
        format_func=lambda x: doc_options[x],
        index=list(doc_options.keys()).index(st.session_state["active_doc_id"]) if st.session_state["active_doc_id"] in doc_options else 0
    )
    
    if selected_id != st.session_state["active_doc_id"]:
        st.session_state["active_doc_id"] = selected_id
        # Trigger rerun transparently when switching happens
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("Upload New Document")

with st.sidebar.form("upload_form", clear_on_submit=True):
    uploaded_files = st.file_uploader("Upload PDFs (Batch)", type=["pdf"], accept_multiple_files=True)
    company = st.text_input("Shared Company/Tag")
    quarter = st.text_input("Shared Quarter/Tag")
    submitted = st.form_submit_button("Process Batch")

if submitted:
    if uploaded_files and company and quarter:
        with st.spinner(f"Processing {len(uploaded_files)} document(s)..."):
            success_count = 0
            for f in uploaded_files:
                files = {"file": (f.name, f, "application/pdf")}
                data = {"company": company, "quarter": quarter}
                res = requests.post(f"{API_URL}/upload-pdf/", files=files, data=data)

                if res.status_code == 200:
                    response = res.json()
                    doc_id = response.get("document_id")
                    
                    if not any(d["id"] == doc_id for d in st.session_state["documents"]):
                        st.session_state["documents"].append({
                            "id": doc_id,
                            "company": company,
                            "quarter": quarter,
                            "summary": response.get("investor_summary", "No summary generated"),
                            "filename": f.name
                        })
                    
                    st.session_state["active_doc_id"] = doc_id
                    success_count += 1
                else:
                    st.sidebar.error(f"Error processing {f.name}")
            
            if success_count > 0:
                save_state()
                st.sidebar.success(f"{success_count} Document(s) Uploaded!")
                st.rerun()
    else:
        st.sidebar.warning("Fill all fields")

st.sidebar.markdown("---")
st.sidebar.header("Chat History")

# New Chat Button
if st.sidebar.button("➕ New Chat", use_container_width=True):
    new_chat_id = str(uuid.uuid4())
    st.session_state["chat_sessions"][new_chat_id] = {"name": "New Chat", "messages": []}
    st.session_state["active_chat_id"] = new_chat_id
    save_state()
    st.rerun()

st.sidebar.markdown("---")
# List past chats
for session_id, session_data in reversed(st.session_state["chat_sessions"].items()):
    btn_label = session_data["name"]
    # Highlight active chat
    if session_id == st.session_state["active_chat_id"]:
        btn_label = f"🟢 {btn_label}"
    else:
        btn_label = f"⚪ {btn_label}"
        
    if st.sidebar.button(btn_label, key=f"chat_{session_id}", use_container_width=True):
        st.session_state["active_chat_id"] = session_id
        st.rerun()

# ------------------------
# MAIN AREA
# ------------------------

active_doc = next((d for d in st.session_state["documents"] if d["id"] == st.session_state["active_doc_id"]), None)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📝 Base Summary", "💼 Advanced Decision", "📊 Key Metrics", "⚠️ Risk Profile", "💬 Ask Q&A"])

# 📝 Base Summary
with tab1:
    st.subheader("📈 Investor Summary")
    if active_doc:
        st.write(active_doc.get("summary", "No summary available"))
    else:
        st.info("Upload a document to see summary")

# 💼 Advanced Decision
with tab2:
    st.subheader("💼 Executive Summary & Long-Term Decision")
    if active_doc:
        cache_key = f"adv_summary_{active_doc['id']}"
        if cache_key in st.session_state:
            st.markdown(st.session_state[cache_key])
        elif st.button("Generate Advanced Decision"):
            with st.spinner("Generating advanced investor insights..."):
                res = requests.get(f"{API_URL}/advanced-summary/", params={"document_id": active_doc["id"]})
                if res.status_code == 200:
                    summary = res.json().get("advanced_summary", "No summary generated")
                    st.session_state[cache_key] = summary
                    st.markdown(summary)
                else:
                    st.error("Failed to generate advanced summary.")
    else:
        st.info("Upload a document first")

# 📊 Key Metrics
with tab3:
    st.subheader("📊 Key Financial Metrics")
    if active_doc:
        cache_key = f"metrics_{active_doc['id']}"
        if cache_key in st.session_state:
            metrics = st.session_state[cache_key]
        else:
            metrics = None
        
        if metrics is None and st.button("Extract Metrics"):
            with st.spinner("Extracting metrics..."):
                res = requests.get(f"{API_URL}/metrics/", params={"document_id": active_doc["id"]})
                if res.status_code == 200:
                    metrics = res.json().get("metrics", {})
                    st.session_state[cache_key] = metrics
                else:
                    st.error("Failed to extract metrics.")
        
        if metrics is not None:
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Revenue Growth", metrics.get("revenue_growth") or "N/A")
            col_m2.metric("Margin/EBITDA", metrics.get("margin") or "N/A")
            col_m3.metric("Guidance", metrics.get("guidance") or "N/A")
            
            st.markdown("### Segment Performance")
            segments = metrics.get("segments", [])
            if segments:
                for seg in segments:
                    st.markdown(f"- {seg}")
            else:
                st.write("No specific segment performance identified.")
    else:
        st.info("Upload a document first")

# ⚠️ Risk Profile
with tab4:
    st.subheader("⚠️ Top Risks Extracted")
    if active_doc:
        cache_key = f"risks_{active_doc['id']}"
        if cache_key in st.session_state:
            risks_list = st.session_state[cache_key]
        else:
            risks_list = None
            
        if risks_list is None and st.button("Extract Risks"):
            with st.spinner("Analyzing risks..."):
                res = requests.get(f"{API_URL}/risks/", params={"document_id": active_doc["id"]})
                if res.status_code == 200:
                    risks_list = res.json().get("risks", [])
                    st.session_state[cache_key] = risks_list
                else:
                    st.error("Failed to extract risks.")
        
        if risks_list is not None:
            if isinstance(risks_list, list) and len(risks_list) > 0:
                for r in risks_list:
                    if not isinstance(r, dict):
                        continue
                    severity = r.get('severity', 'Unknown')
                    emoji = "🔴" if str(severity).lower() == "high" else ("🟡" if str(severity).lower() == "medium" else "🟢")
                    with st.expander(f"{emoji} {r.get('risk_name', 'Risk')} ({severity})"):
                        st.write(r.get("description", ""))
                        st.caption(f"**Source:** {r.get('source_reference', 'N/A')}")
            else:
                st.success("No major risks identified in query.")
    else:
        st.info("Upload a document first")

# 💬 Query Section (Chat History)
with tab5:
    active_chat = st.session_state["chat_sessions"][st.session_state["active_chat_id"]]
    chat_name = active_chat.get("name", "New Chat")
    st.subheader(f"💬 {chat_name}")
    
    col_chat1, col_chat2 = st.columns([0.8, 0.2])
    with col_chat2:
        if st.button("Clear Thread"):
            st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"] = []
            st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["name"] = "New Chat"
            save_state()
            st.rerun()

    # Display chat history
    for message in active_chat["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("sources"):
                with st.expander("View Sources"):
                    for s in message["sources"]:
                        st.write(f"- **{s['speaker']}** ({s['role']}) | {s['company']} {s['quarter']} | Score: {round(s['score'], 3)}")

    # Chat input
    if query := st.chat_input("Ask a question about your documents..."):
        # Set chat name based on first query if it's "New Chat"
        if active_chat["name"] == "New Chat":
            short_name = (query[:25] + '...') if len(query) > 25 else query
            st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["name"] = short_name

        # Add user message to state
        st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"].append({"role": "user", "content": query})
        
        # Display user message dynamically
        with st.chat_message("user"):
            st.markdown(query)

        # Call API
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                params = {"query": query}
                if active_doc:
                    params["company"] = active_doc["company"]
                    params["quarter"] = active_doc["quarter"]
                
                res = requests.post(f"{API_URL}/query/", params=params)
                
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "No answer generated")
                    sources = data.get("sources", [])
                    
                    st.markdown(answer)
                    if sources:
                        with st.expander("View Sources"):
                            for s in sources:
                                st.write(f"- **{s['speaker']}** ({s['role']}) | {s['company']} {s['quarter']} | Score: {round(s['score'], 3)}")
                    
                    # Store assistant response in state
                    st.session_state["chat_sessions"][st.session_state["active_chat_id"]]["messages"].append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    save_state()
                else:
                    st.error("Query failed")