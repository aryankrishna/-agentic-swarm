import os, re
from typing import Tuple, List
from neo4j import GraphDatabase

# Read connection from env (compose already sets these)
URI  = os.getenv("NEO4J_URI", "bolt://graph:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD", "testtest")

_driver = GraphDatabase.driver(URI, auth=(USER, PWD))

def _ceo_of(company: str) -> Tuple[str, List[str]]:
    q = """
    MATCH (p:Person)-[:CEO_OF]->(c:Company {name:$company})
    RETURN p.name AS ceo, c.name AS company
    LIMIT 1
    """
    with _driver.session(database="neo4j") as s:
        rec = s.run(q, company=company.title()).single()
        if not rec:
            return "", []
        return f"{rec['ceo']} is the CEO of {rec['company']}.", [
            f"Neo4j: (Person)-[:CEO_OF]->(Company name='{company.title()}')"
        ]

def _company_led_by(person: str) -> Tuple[str, List[str]]:
    q = """
    MATCH (p:Person {name:$person})-[:CEO_OF]->(c:Company)
    RETURN p.name AS person, c.name AS company
    LIMIT 1
    """
    with _driver.session(database="neo4j") as s:
        rec = s.run(q, person=person.title()).single()
        if not rec:
            return "", []
        return f"{rec['person']} leads {rec['company']}.", [
            f"Neo4j: (Person name='{person.title()}')-[:CEO_OF]->(Company)"
        ]

def query_graph(question: str) -> Tuple[str, List[str]]:
    qn = (question or "").strip().lower()
    if not qn:
        return "", []

    # CEO of company (cover: "ceo of X", "who runs X", "who is the ceo of X")
    m = (
        re.search(r"ceo\s+of\s+([a-z&\-\s]+)\??$", qn)
        or re.search(r"who\s+runs\s+([a-z&\-\s]+)\??$", qn)
        or re.search(r"who\s+is\s+the\s+ceo\s+of\s+([a-z&\-\s]+)\??$", qn)
    )
    if m:
        return _ceo_of(m.group(1).strip())

    # company led by person (cover both word orders)
    m = (
        re.search(r"(?:which|what)\s+company\s+does\s+([a-z\-\s]+)\s+lead\??", qn)
        or re.search(r"([a-z\-\s]+)\s+leads\s+(?:which|what)\s+company\??", qn)
        or re.search(r"which\s+company\s+is\s+([a-z\-\s]+)\s+(?:the\s+)?ceo\s+of\??", qn)
    )
    if m:
        return _company_led_by(m.group(1).strip())

    return "", []
