# ingestion.py
import hashlib, os
import chromadb
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import *
import PyPDF2

_model   = SentenceTransformer(EMBED_MODEL)
_client  = chromadb.PersistentClient(path=DB_PATH)
_col     = _client.get_or_create_collection(
               COLLECTION, metadata={"hnsw:space": "cosine"})
_splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", ". ", " ", ""])

def _load_pdf(path: str) -> str:
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
    return text

def _chunk_id(source: str, idx: int) -> str:
    return hashlib.md5(f"{source}::{idx}".encode()).hexdigest()[:16]

def ingest_pdf(file_path: str, filename: str) -> dict:
    """Full ingest pipeline. Returns stats."""
    raw  = _load_pdf(file_path)
    if not raw.strip():
        raise ValueError("Could not extract text from PDF.")

    chunks = _splitter.split_text(raw)
    ids    = [_chunk_id(filename, i) for i in range(len(chunks))]
    metas  = [{"source": filename, "chunk_index": i,
               "chunk_total": len(chunks)} for i in range(len(chunks))]

    for start in range(0, len(chunks), BATCH_SIZE):
        sl = slice(start, start + BATCH_SIZE)
        embs = _model.encode(chunks[sl], batch_size=32,
                             show_progress_bar=False).tolist()
        _col.upsert(ids=ids[sl], documents=chunks[sl],
                    embeddings=embs, metadatas=metas[sl])

    return {"filename": filename, "chunks": len(chunks),
            "total_in_db": _col.count()}

def list_sources() -> list[str]:
    """All unique filenames currently in the DB."""
    if _col.count() == 0:
        return []
    all_meta = _col.get(include=["metadatas"])["metadatas"]
    return list({m["source"] for m in all_meta})

def delete_source(filename: str) -> int:
    """Remove all chunks for a given file."""
    results = _col.get(where={"source": filename})
    if results["ids"]:
        _col.delete(ids=results["ids"])
    return len(results["ids"])