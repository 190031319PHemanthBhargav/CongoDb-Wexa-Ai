import os
import json
import pandas as pd
from dotenv import load_dotenv

from runners.cogno_runner import CognoDBRunner
from runners.falkordb_runner import FalkorDBRunner
from runners.neo4j_runner import Neo4jRunner
from runners.memgraph_runner import MemgraphRunner

load_dotenv(override=True)

def run_suite():
    nodes_df = pd.read_csv("datasets/data/nodes.csv")
    edges_df = pd.read_csv("datasets/data/edges.csv")
    sample_nodes = nodes_df['id'].sample(100).tolist()

    runners = [
        CognoDBRunner(os.getenv("COGNODB_URI"), os.getenv("COGNODB_USER"), os.getenv("COGNODB_PASSWORD")),
        Neo4jRunner(os.getenv("NEO4J_URI"), os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")),
        MemgraphRunner(os.getenv("MEMGRAPH_URI"), os.getenv("MEMGRAPH_USER"), os.getenv("MEMGRAPH_PASSWORD")),
        FalkorDBRunner(
            os.getenv("FALKORDB_HOST"),
            int(os.getenv("FALKORDB_PORT", 6379)),
            os.getenv("FALKORDB_PASSWORD"),
            os.getenv("FALKORDB_USERNAME", "default")
        )
    ]

    results = {}

    for runner in runners:
        print(f"\n--- Running Benchmark: {runner.name} ---")
        try:
            runner.connect()
            runner.clear_database()
            
            print(f"[{runner.name}] Loading data...")
            load_metrics = runner.load_data(nodes_df, edges_df)
            
            print(f"[{runner.name}] Running 1-hop traversals...")
            t1_hop = runner.run_traversals(sample_nodes, hops=1)
            
            print(f"[{runner.name}] Running 2-hop traversals...")
            t2_hop = runner.run_traversals(sample_nodes, hops=2)

            results[runner.name] = {
                "load": load_metrics,
                "traversals": {
                    "1_hop": t1_hop,
                    "2_hop": t2_hop
                }
            }
            runner.close()
        except Exception as e:
            print(f"Error on {runner.name}: {e}")

    os.makedirs("results", exist_ok=True)
    with open("results/raw_results.json", "w") as f:
        json.dump(results, f, indent=4)
    print("\nBenchmark Suite Completed! Saved to results/raw_results.json")

if __name__ == "__main__":
    run_suite()