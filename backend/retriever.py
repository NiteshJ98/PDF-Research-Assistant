# retriever.py
import chromadb
from sentence_transformers import SentenceTransformer
from config import *

_model  = SentenceTransformer(EMBED_MODEL)
_client = chromadb.PersistentClient(path=DB_PATH)
_col    = _client.get_or_create_collection(
              COLLECTION, metadata={"hnsw:space": "cosine"})

def retrieve(query: str, k: int = TOP_K,
             source_filter: str | None = None) -> list[dict]:
    """Embed query → search → return top-k chunks."""
    emb = _model.encode(query).tolist()

    kwargs = dict(
        query_embeddings=[emb],
        n_results=min(k, max(_col.count(), 1)),
        include=["documents", "distances", "metadatas"],
    )
    if source_filter:
        kwargs["where"] = {"source": source_filter}

    res = _col.query(**kwargs)

    return [
        {
            "text":    doc,
            "score":   round(1 - dist, 4),
            "source":  meta.get("source", "?"),
            "chunk":   meta.get("chunk_index", "?"),
        }
        for doc, dist, meta in zip(
            res["documents"][0],
            res["distances"][0],
            res["metadatas"][0],
        )
    ]