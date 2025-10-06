import os, glob, pickle, time
from pathlib import Path
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer

RAW_DIR = "./data/raw"
INDEX_PATH = "./data/tfidf_index.pkl"

def read_text_files(raw_dir: str) -> List[Dict]:
    items = []
    for fp in glob.glob(os.path.join(raw_dir, "*.txt")):
        with open(fp, "r", encoding="utf-8") as f:
            text = f.read().strip()
        base = os.path.basename(fp)
        items.append({
            "id": base,
            "title": base.replace(".txt","").replace("_"," ").title(),
            "source_file": base,
            "url": f"local://{base}",
            "text": text
        })
    return items

def main():
    start = time.time()
    Path("./data").mkdir(parents=True, exist_ok=True)

    docs = read_text_files(RAW_DIR)
    if not docs:
        print(f"No .txt files found in {RAW_DIR}. Add some and re-run.")
        return

    corpus = [d["text"] for d in docs]
    vec = TfidfVectorizer(stop_words="english")
    X = vec.fit_transform(corpus)

    with open(INDEX_PATH, "wb") as f:
        pickle.dump({
            "vectorizer": vec,
            "matrix": X,
            "docs": docs
        }, f)

    print(f"Indexed {len(docs)} docs -> {INDEX_PATH}")
    print(f"Done in {time.time()-start:.2f}s")

if __name__ == "__main__":
    main()
