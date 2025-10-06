:use neo4j
MATCH (n) DETACH DELETE n;

MERGE (met:Drug {name:"Metformin"});
MERGE (t2d:Condition {name:"Type 2 Diabetes"});
MERGE (nausea:Symptom {name:"Nausea"});
MERGE (ibuprofen:Drug {name:"Ibuprofen"});
MERGE (aspirin:Drug {name:"Aspirin"});
MERGE (tsla:Company {name:"Tesla", ticker:"TSLA"});
MERGE (musk:Person {name:"Elon Musk"});
MERGE (rev2024:Metric {name:"Revenue", value:"$97B", period:"2024"});

MERGE (met)-[:TREATS]->(t2d);
MERGE (met)-[:HAS_SIDE_EFFECT]->(nausea);
MERGE (ibuprofen)-[:INTERACTS_WITH]->(aspirin);
MERGE (tsla)-[:HAS_CEO]->(musk);
MERGE (tsla)-[:REPORTS]->(rev2024);
