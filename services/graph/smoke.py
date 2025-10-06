import os
from neo4j import GraphDatabase

URI  = os.getenv("NEO4J_URI", "bolt://graph:7687")   
USER = os.getenv("NEO4J_USER", "neo4j")
PWD  = os.getenv("NEO4J_PASSWORD", "testtest")

driver = GraphDatabase.driver(URI, auth=(USER, PWD))

with driver.session() as s:
    c = s.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    print("Node count:", c)
