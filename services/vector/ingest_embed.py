"""
Semantic embedding ingestion using SentenceTransformers + ChromaDB.
This will create /app/data/chroma folder with stored embeddings.
"""
import os
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_DIR = DATA_DIR / "raw"
CHROMA_DIR = DATA_DIR / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

# Load a small, efficient model
model_name = "sentence-transformers/all-MiniLM-L6-v2"
print(f"Loading model: {model_name}")
model = SentenceTransformer(model_name)

# Initialize Chroma client
client = chromadb.Client()
collection = client.get_or_create_collection(
    name="semantic_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name)
)

# Load all text docs under /data/raw
docs = []
for path in RAW_DIR.glob("*.txt"):
    text = path.read_text(encoding="utf-8").strip()
    if text:
        docs.append((path.name, text))

if not docs:
    print(f"No .txt files found in {RAW_DIR}, please add some sample text documents.")
else:
    print(f"Found {len(docs)} docs — embedding...")
    collection.add(
        documents=[t for _, t in docs],
        ids=[n for n, _ in docs]
    )
    print(f"✅ Embedded {len(docs)} docs into {CHROMA_DIR}")
