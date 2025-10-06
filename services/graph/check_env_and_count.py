import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

print("CWD:", os.getcwd())
print("Has .env file?", os.path.exists(".env"))

load_dotenv()
print("URI  =", os.getenv("NEO4J_URI"))
print("USER =", os.getenv("NEO4J_USERNAME"))
print("PWD  =", os.getenv("NEO4J_PASSWORD"))

uri  = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USERNAME", "neo4j")
pwd  = os.getenv("NEO4J_PASSWORD", "testtest")

driver = GraphDatabase.driver(uri, auth=(user, pwd))
with driver.session(database="neo4j") as s:
    nodes = s.run("MATCH (n) RETURN count(n) AS nodes").single()["nodes"]
    print("Node count seen by Python:", nodes)
    rows = list(s.run("MATCH (c:Company)-[:HAS_CEO]->(p:Person) RETURN c.name AS company, p.name AS ceo"))
    print("CEO rows:", len(rows), [r.data() for r in rows])
driver.close()
