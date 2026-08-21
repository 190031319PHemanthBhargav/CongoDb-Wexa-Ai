import time
import numpy as np
from neo4j import GraphDatabase
from runners.base_runner import BaseGraphRunner

BATCH_SIZE = 100

class CognoDBRunner(BaseGraphRunner):
    def __init__(self, uri, user, password):
        super().__init__("CognoDB Cloud")
        self.driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            connection_timeout=15,
            max_connection_lifetime=1800
        )

    def connect(self):
        self.driver.verify_connectivity()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def load_data(self, nodes_df, edges_df) -> dict:
        start_time = time.time()
        
        # Batch load nodes
        nodes = nodes_df.to_dict('records')
        edges = edges_df.to_dict('records')

        with self.driver.session() as session:
            for start in range(0, len(nodes), BATCH_SIZE):
                session.run(
                    "UNWIND $batch AS row MERGE (u:User {id: row.id})",
                    batch=nodes[start:start + BATCH_SIZE]
                ).consume()
            for start in range(0, len(edges), BATCH_SIZE):
                session.run(
                    """
                    UNWIND $batch AS row
                    MATCH (s:User {id: row.source}), (t:User {id: row.target})
                    MERGE (s)-[:FOLLOWS]->(t)
                    """,
                    batch=edges[start:start + BATCH_SIZE]
                ).consume()

        total_time = time.time() - start_time
        return {
            "wall_clock_sec": round(total_time, 2),
            "nodes_per_sec": round(len(nodes_df) / total_time, 2),
            "rels_per_sec": round(len(edges_df) / total_time, 2)
        }

    def run_traversals(self, start_nodes, hops=2, iterations=100) -> dict:
        latencies = []
        cypher = f"MATCH (n:User {{id: $id}})-[:FOLLOWS*{hops}]->(m) RETURN count(m)"
        
        with self.driver.session() as session:
            for node_id in start_nodes[:iterations]:
                t0 = time.perf_counter()
                session.run(cypher, id=int(node_id)).consume()
                latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def run_lookup(self, property_key: str, property_value: str, iterations: int = 100) -> dict:
        latencies = []
        query = f"MATCH (n:User {{{property_key}: $value}}) RETURN count(n) AS total"

        with self.driver.session() as session:
            for _ in range(iterations):
                t0 = time.perf_counter()
                session.run(query, value=property_value).consume()
                latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def run_aggregation(self, iterations: int = 100) -> dict:
        latencies = []
        query = "MATCH (n:User) RETURN count(n) AS total"

        with self.driver.session() as session:
            for _ in range(iterations):
                t0 = time.perf_counter()
                session.run(query).consume()
                latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def close(self):
        self.driver.close()