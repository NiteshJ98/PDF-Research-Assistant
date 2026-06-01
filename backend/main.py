# main.py
import os, shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingestion import ingest_pdf, list_sources, delete_source
from retriever import retrieve
from prompt    import build_messages
from generator import generate
from config    import UPLOAD_DIR, TOP_K

app = FastAPI(title="PDF Research Assistant API")

app.add_middleware(CORSMiddleware, allow_origins=["*"],
                   allow_methods=["*"], allow_headers=["*"])

# ── request / response models ─────────────────────────────

class QueryRequest(BaseModel):
    question:      str
    history:       list[dict] = []
    top_k:         int        = TOP_K
    source_filter: str | None = None

class QueryResponse(BaseModel):
    answer:  str
    sources: list[dict]
    chunks:  list[dict]

# ── endpoints ─────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "PDF Research Assistant API"}

@app.post("/ingest")
async def ingest_endpoint(file: UploadFile = File(...)):
    """Upload and ingest a PDF."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported.")

    save_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        stats = ingest_pdf(save_path, file.filename)
    except ValueError as e:
        raise HTTPException(422, str(e))

    return stats

@app.post("/query", response_model=QueryResponse)
def query_endpoint(req: QueryRequest):
    """Ask a question against ingested documents."""
    if not req.question.strip():
        raise HTTPException(400, "Question cannot be empty.")

    chunks   = retrieve(req.question, k=req.top_k,
                        source_filter=req.source_filter)

    if not chunks:
        return QueryResponse(
            answer="No documents have been ingested yet. "
                   "Please upload a PDF first.",
            sources=[], chunks=[]
        )

    messages = build_messages(req.question, chunks, req.history)
    answer   = generate(messages)

    sources  = [{"source": c["source"], "chunk": c["chunk"],
                 "score": c["score"]} for c in chunks]

    return QueryResponse(answer=answer, sources=sources, chunks=chunks)

@app.get("/sources")
def sources_endpoint():
    """List all ingested PDF filenames."""
    return {"sources": list_sources()}

@app.delete("/sources/{filename}")
def delete_endpoint(filename: str):
    """Remove all chunks for a given PDF."""
    deleted = delete_source(filename)
    return {"deleted_chunks": deleted, "filename": filename}