import time
import numpy as np
from falkordb import FalkorDB
from runners.base_runner import BaseGraphRunner

class FalkorDBRunner(BaseGraphRunner):
    def __init__(self, host, port, password, username="default"):
        super().__init__("FalkorDB Cloud")
        self.host = host
        self.port = port
        self.password = password
        self.username = username
        self.db = None
        self.graph = None

    def connect(self):
        if self.db is None:
            self.db = FalkorDB(
                host=self.host,
                port=self.port,
                password=self.password,
                username=self.username
            )
            self.graph = self.db.select_graph("benchmark")
        self.graph.query("RETURN 1")

    def clear_database(self):
        self.graph.delete()
        self.graph = self.db.select_graph("benchmark")

    def load_data(self, nodes_df, edges_df) -> dict:
        start_time = time.time()
        
        # FalkorDB optimized query execution
        for _, row in nodes_df.iterrows():
            self.graph.query(f"CREATE (:User {{id: {row['id']}}})")
            
        for _, row in edges_df.iterrows():
            self.graph.query(
                f"MATCH (s:User {{id: {row['source']}}}), (t:User {{id: {row['target']}}}) "
                f"CREATE (s)-[:FOLLOWS]->(t)"
            )

        total_time = time.time() - start_time
        return {
            "wall_clock_sec": round(total_time, 2),
            "nodes_per_sec": round(len(nodes_df) / total_time, 2),
            "rels_per_sec": round(len(edges_df) / total_time, 2)
        }

    def run_traversals(self, start_nodes, hops=2, iterations=100) -> dict:
        latencies = []
        cypher = f"MATCH (n:User {{id: $id}})-[:FOLLOWS*{hops}]->(m) RETURN count(m)"
        
        for node_id in start_nodes[:iterations]:
            t0 = time.perf_counter()
            self.graph.query(cypher, {"id": int(node_id)})
            latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def run_lookup(self, property_key: str, property_value: str, iterations: int = 100) -> dict:
        latencies = []
        query = f"MATCH (n:User {{{property_key}: $value}}) RETURN count(n) AS total"

        for _ in range(iterations):
            t0 = time.perf_counter()
            self.graph.query(query, {"value": property_value})
            latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def run_aggregation(self, iterations: int = 100) -> dict:
        latencies = []
        query = "MATCH (n:User) RETURN count(n) AS total"

        for _ in range(iterations):
            t0 = time.perf_counter()
            self.graph.query(query)
            latencies.append((time.perf_counter() - t0) * 1000)

        return {
            "p50_ms": round(np.percentile(latencies, 50), 2),
            "p95_ms": round(np.percentile(latencies, 95), 2)
        }

    def close(self):
        pass