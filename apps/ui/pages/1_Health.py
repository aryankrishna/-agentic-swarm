import os, streamlit as st
st.set_page_config(page_title="Health / Diagnostics", page_icon="🩺")
st.title("🩺 Health / Diagnostics")

# TF-IDF index
idx = os.path.exists(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "tfidf_index.pkl"))
st.subheader("TF-IDF")
st.success("Found tfidf_index.pkl") if idx else st.error("tfidf_index.pkl NOT found")

# Neo4j ping
try:
    from neo4j import GraphDatabase
    uri  = os.getenv("NEO4J_URI","bolt://graph:7687")
    user = os.getenv("NEO4J_USER","neo4j")
    pwd  = os.getenv("NEO4J_PASSWORD","testtest")
    drv = GraphDatabase.driver(uri, auth=(user,pwd))
    with drv.session(database="neo4j") as s:
        c = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    st.subheader("Neo4j")
    st.success(f"Connected, nodes: {c}")
except Exception as e:
    st.subheader("Neo4j")
    st.error(f"Neo4j connection failed: {e}")

# Semantic / Chroma
st.subheader("Semantic Vector Store (Chroma)")
try:
    from services.vector.query_embed import get_collection
    coll = get_collection()
    count = coll.count()
    st.success(f"Chroma collection ready — {count} docs")
except Exception as e:
    st.error(f"Chroma not ready: {e}\nTry:  docker exec -it agentic-app bash -lc 'python services/vector/ingest_embed.py'")
