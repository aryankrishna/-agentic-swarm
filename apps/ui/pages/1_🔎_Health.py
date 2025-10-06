import os
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Health Checks", page_icon="🔎")
st.title("🔎 Health / Diagnostics")

# --- TF-IDF index check ---
st.subheader("TF-IDF Index")
idx_path = Path(__file__).resolve().parents[3] / "data" / "tfidf_index.pkl"
if idx_path.exists():
    st.success(f"✅ Found TF-IDF index at {idx_path}")
else:
    st.error("❌ TF-IDF index NOT found.\nRun inside container:\n`python services/vector/ingest_tfidf.py`")

# --- Semantic / Chroma check ---
st.subheader("Semantic Vector Store (Chroma)")
try:
    from services.vector.query_embed import get_collection
    coll = get_collection()
    count = coll.count()
    st.success(f"✅ Chroma collection ready — {count} docs")
except Exception as e:
    st.error(f"❌ Chroma not ready: {e}\nTry: `python services/vector/ingest_embed.py`")

# --- Neo4j check ---
st.subheader("Neo4j Connectivity")
try:
    from neo4j import GraphDatabase
    URI = os.getenv("NEO4J_URI", "bolt://graph:7687")
    USER = os.getenv("NEO4J_USER", "neo4j")
    PWD = os.getenv("NEO4J_PASSWORD", "testtest")

    drv = GraphDatabase.driver(URI, auth=(USER, PWD))
    with drv.session(database="neo4j") as s:
        c = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
        st.success(f"✅ Connected to Neo4j — {c} nodes found.")
        rows = s.run("MATCH (p:Person)-[:CEO_OF]->(c:Company) RETURN p.name AS person, c.name AS company LIMIT 5").data()
        if rows:
            st.write("Sample CEO edges:")
            for r in rows:
                st.write(f"• {r['person']} → CEO_OF → {r['company']}")
        else:
            st.info("No CEO edges found.")
except Exception as e:
    st.error(f"❌ Neo4j connection failed: {e}")
