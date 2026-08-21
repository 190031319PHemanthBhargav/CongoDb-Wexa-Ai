from neo4j import GraphDatabase

driver = GraphDatabase.driver(
    "bolt+s://db-b1378c8c.bravo.databases.cognodb.com",
    auth=("cognodb", "e2abf7fb9c945aa966dece1b772f810a"),
)
driver.verify_connectivity()