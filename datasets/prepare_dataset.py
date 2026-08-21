import os
import pandas as pd
import networkx as nx

def generate_graph():
    os.makedirs("datasets/data", exist_ok=True)
    print("Generating synthetic scale-free social graph (100,000 edges)...")
    
    # Generate scale-free graph with ~100,000 edges
    # n = 20,000 nodes, m = 5 edges per new node -> exactly 99,975 edges (~100k)
    num_nodes = 20000
    edges_per_node = 5
    
    graph = nx.barabasi_albert_graph(n=num_nodes, m=edges_per_node, seed=42)
    
    # Format nodes
    nodes_data = [{"id": node, "label": "User"} for node in graph.nodes()]
    nodes_df = pd.DataFrame(nodes_data)
    
    # Format edges
    edges_data = [{"source": u, "target": v} for u, v in graph.edges()]
    edges_df = pd.DataFrame(edges_data)
    
    # Save to disk
    nodes_df.to_csv("datasets/data/nodes.csv", index=False)
    edges_df.to_csv("datasets/data/edges.csv", index=False)
    
    print(f"Dataset generated cleanly: {len(nodes_df)} nodes, {len(edges_df)} relationships.")

if __name__ == "__main__":
    generate_graph()