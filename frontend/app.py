# app.py
import streamlit as st
import requests, os

API = os.getenv("API_URL", "https://huggingface.co/spaces/Niteshj007/pdf-assistant-backend")

st.set_page_config(
    page_title="PDF Research Assistant",
    page_icon="📄",
    layout="wide"
)

# ── session state ────────────────────────────────────────
if "messages"      not in st.session_state: st.session_state.messages = []
if "last_sources"  not in st.session_state: st.session_state.last_sources = []
if "last_chunks"   not in st.session_state: st.session_state.last_chunks = []

# ── sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.title("📄 PDF Research Assistant")
    st.caption("Upload PDFs · Ask questions · Get cited answers")
    st.divider()

    # Upload
    st.subheader("Upload PDF")
    uploaded = st.file_uploader("Choose a PDF", type="pdf",
                                 label_visibility="collapsed")
    if uploaded:
        with st.spinner(f"Ingesting {uploaded.name}..."):
            resp = requests.post(
                f"{API}/ingest",
                files={"file": (uploaded.name, uploaded.getvalue(),
                                "application/pdf")}
            )
        if resp.status_code == 200:
            d = resp.json()
            st.success(f"✅ {d['filename']} — {d['chunks']} chunks")
        else:
            st.error(resp.json().get("detail", "Upload failed"))

    st.divider()

    # Ingested files
    st.subheader("Ingested documents")
    try:
        sources = requests.get(f"{API}/sources").json()["sources"]
    except Exception:
        sources = []

    if not sources:
        st.caption("No documents yet")
    else:
        for src in sources:
            col1, col2 = st.columns([3, 1])
            col1.caption(f"📄 {src}")
            if col2.button("🗑", key=f"del_{src}"):
                requests.delete(f"{API}/sources/{src}")
                st.rerun()

    st.divider()

    # Settings
    st.subheader("Settings")
    top_k = st.slider("Chunks to retrieve (k)", 1, 8, 3)
    source_filter = st.selectbox(
        "Filter by source", ["All"] + sources)
    filter_val = None if source_filter == "All" else source_filter

    if st.button("🗑 Clear chat"):
        st.session_state.messages = []
        st.session_state.last_sources = []
        st.session_state.last_chunks = []
        st.rerun()

# ── main chat area ────────────────────────────────────────
st.header("Ask your documents anything")

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
if question := st.chat_input("Ask a question about your PDFs..."):
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Call API
    with st.chat_message("assistant"):
        with st.spinner("Searching documents..."):
            # Build history for the API (exclude last user msg)
            history = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages[:-1]
            ]

            resp = requests.post(f"{API}/query", json={
                "question":      question,
                "history":       history,
                "top_k":         top_k,
                "source_filter": filter_val,
            })

        if resp.status_code == 200:
            data = resp.json()
            answer = data["answer"]
            st.markdown(answer)

            # Show sources inline
            if data["sources"]:
                with st.expander(
                    f"📚 Sources ({len(data['sources'])} chunks)", expanded=False):
                    for i, chunk in enumerate(data["chunks"], 1):
                        st.markdown(
                            f"**Source {i}** · `{chunk['source']}` · "
                            f"chunk {chunk['chunk']} · score `{chunk['score']}`"
                        )
                        st.caption(chunk["text"][:300] + "...")
                        if i < len(data["chunks"]):
                            st.divider()

            st.session_state.messages.append(
                {"role": "assistant", "content": answer})
            st.session_state.last_sources = data["sources"]
            st.session_state.last_chunks  = data["chunks"]
        else:
            err = "Something went wrong. Is the backend running?"
            st.error(err)
            st.session_state.messages.append(
                {"role": "assistant", "content": err})
