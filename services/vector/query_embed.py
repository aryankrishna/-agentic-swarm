from chromadb import PersistentClient

def get_collection():
    """Return an active Chroma collection used for semantic vector search."""
    client = PersistentClient(path="/app/data/chroma")
    return client.get_or_create_collection("semantic_docs")

def query_vector_semantic(query: str, k: int = 4):
    """Retrieve top-k documents from the semantic (Chroma) store."""
    coll = get_collection()
    results = coll.query(query_texts=[query], n_results=k)
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    ids = results.get("ids", [[]])[0]
    return docs, metas, ids, results