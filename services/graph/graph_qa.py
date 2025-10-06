# services/graph/graph_qa.py
import os
from typing import Tuple, List
from neo4j import GraphDatabase

URI  = os.getenv("NEO4J_URI", "bolt://graph:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD", "testtest")

def _session():
    drv = GraphDatabase.driver(URI, auth=(USER, PWD))
    return drv.session(database="neo4j")

def query_graph(q: str) -> Tuple[str, List[str]]:
    """
    Simple router for graph queries:
      - 'ceo of tesla' → returns CEO name from (Person)-[:CEO_OF]->(Company{name:'Tesla'})
      - 'ibuprofen' & 'aspirin' & 'interact' → checks INTERACTS_WITH between the two drugs
    Returns: (answer_text, sources_list)
    """
    text = (q or "").lower().strip()
    sources = ["Neo4j (local)"]

    # --- Case A: CEO of Tesla ---
    if "ceo" in text and "tesla" in text:
        cypher = """
        MATCH (p:Person)-[:CEO_OF]->(c:Company {name:'Tesla'})
        RETURN p.name AS ceo, c.name AS company
        LIMIT 1
        """
        with _session() as s:
            rows = [r.data() for r in s.run(cypher)]
        if rows:
            return f"{rows[0]['ceo']} is the CEO of {rows[0]['company']}.", sources
        return "No CEO found for Tesla in the graph.", sources

    # --- Case B: Drug interaction: Ibuprofen & Aspirin ---
    if ("interact" in text) and ("ibuprofen" in text) and ("aspirin" in text):
        cypher = """
        MATCH (a:Drug {name:'Ibuprofen'})-[:INTERACTS_WITH]-(b:Drug {name:'Aspirin'})
        RETURN a.name AS a, b.name AS b
        LIMIT 1
        """
        with _session() as s:
            rows = [r.data() for r in s.run(cypher)]
        if rows:
            return f"{rows[0]['a']} can interact with {rows[0]['b']}.", sources
        return "No interaction between Ibuprofen and Aspirin found in the graph.", sources

    # Fallback
    return "", sources