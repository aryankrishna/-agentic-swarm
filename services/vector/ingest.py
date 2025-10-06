import os
import glob
import time
from typing import List, Dict
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma")
RAW_DIR = "./data/raw"
COLLECTION_NAME = "docs"

# Approx chunk ~400 tokens via ~1600 chars; overlap to keep context
CHUNK_CHARS = 1600
CHUNK_OVERLAP = 200

def read_text_files(raw_dir: str) -> List[Dict]:
    items = []
    for fp in glob.glob(os.path.join(raw_dir, "*.txt")):
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read().strip()
        items.append({"path": fp, "text": text})
    return items

def chunk_text(text: str, chunk_chars: int = CHUNK_CHARS, overlap: int = CHUNK_OVERLAP) -> List[str]:
    chunks = []
    i = 0
    n = len(text)
    while i < n:
        end = min(i + chunk_chars, n)
        chunks.append(text[i:end])
        i = end - overlap
        if i < 0:
            i = 0
        if i >= n:
            break
    return chunks

def main():
    start = time.time()
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    # Sentence-Transformers MiniLM (384-dim)
    embedder = embedding_functions.DefaultEmbeddingFunction()

    # Create or get collection with embedder bound
    try:
        col = client.get_collection(COLLECTION_NAME, embedding_function=embedder)
    except:
        col = client.create_collection(COLLECTION_NAME, embedding_function=embedder)

    # Clear existing docs (safe on first run)
    try:
        col.delete(where={})
    except:
        pass

    docs = read_text_files(RAW_DIR)
    if not docs:
        print(f"No .txt files found in {RAW_DIR}. Add some and re-run.")
        return

    ids, metadatas, contents = [], [], []
    doc_id = 0
    for d in docs:
        base = os.path.basename(d["path"])
        chunks = chunk_text(d["text"])
        for j, ch in enumerate(chunks):
            ids.append(f"doc{doc_id}_chunk{j}")
            contents.append(ch)
            metadatas.append({
                "source_file": base,
                "title": base.replace(".txt","").replace("_"," ").title(),
                "url": f"local://{base}",
                "chunk_index": j
            })
        doc_id += 1

    col.add(ids=ids, documents=contents, metadatas=metadatas)
    print(f"Ingested {len(contents)} chunks from {len(docs)} files into collection '{COLLECTION_NAME}'.")
    print(f"Chroma path: {CHROMA_PATH}")
    print(f"Done in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
