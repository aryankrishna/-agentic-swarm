CREATE (ibu:Drug {name:'Ibuprofen'})
CREATE (asp:Drug {name:'Aspirin'})
CREATE (acet:Drug {name:'Acetaminophen'})
CREATE (ns:Class {name:'NSAID'})
MERGE (ibu)-[:INTERACTS_WITH]->(asp)
MERGE (ibu)-[:CLASS]->(ns)
MERGE (asp)-[:CLASS]->(ns);
