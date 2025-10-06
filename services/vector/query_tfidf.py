import os, time, pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

INDEX_PATH = "./data/tfidf_index.pkl"

def query_vector(question: str, k: int = 6):
    t0 = time.time()
    if not os.path.exists(INDEX_PATH):
        raise FileNotFoundError("TF-IDF index not found. Run: python services/vector/ingest_tfidf.py")

    data = pickle.load(open(INDEX_PATH, "rb"))
    vec, X, docs = data["vectorizer"], data["matrix"], data["docs"]

    qv = vec.transform([question])
    sims = cosine_similarity(qv, X)[0]
    top_idx = np.argsort(-sims)[:k]

    results_docs, results_meta, results_ids = [], [], []
    for rank, i in enumerate(top_idx):
        d = docs[i]
        results_docs.append(d["text"])
        results_meta.append({
            "source_file": d["source_file"],
            "title": d["title"],
            "url": d["url"],
            "score": float(sims[i]),
            "rank": int(rank+1),
        })
        results_ids.append(d["id"])

    latency = time.time() - t0
    return results_docs, results_meta, results_ids, latency
