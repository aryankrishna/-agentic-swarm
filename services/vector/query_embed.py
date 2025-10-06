"""
Semantic retrieval using ChromaDB.
Returns (docs, metas, ids, latency_ms)
"""
import time
from pathlib import Path
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = Path(__file__).resolve().parents[2] / "data"

def _get_collection():
    # Use the same collection name/model as ingest_embed.py
    client = chromadb.Client()
    collection = client.get_or_create_collection(
        name="semantic_docs",
        embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        ),
    )
    return collection

def query_vector_semantic(q: str, k: int = 3):
    t0 = time.perf_counter()
    col = _get_collection()
    res = col.query(query_texts=[q], n_results=k)
    # Chroma returns dicts with lists; normalize
    docs   = res.get("documents", [[]])[0]
    ids    = res.get("ids", [[]])[0]
    metas  = res.get("metadatas", [[]])[0] or [{} for _ in docs]
    latency_ms = int((time.perf_counter() - t0) * 1000)
    return docs, metas, ids, latency_ms
