import json
import matplotlib.pyplot as plt
import os

def build_charts():
    if not os.path.exists("results/raw_results.json"):
        print("Run run_benchmarks.py first.")
        return

    with open("results/raw_results.json") as f:
        data = json.load(f)

    platforms = list(data.keys())
    p50_1hop = [data[p]["traversals"]["1_hop"]["p50_ms"] for p in platforms]
    p95_1hop = [data[p]["traversals"]["1_hop"]["p95_ms"] for p in platforms]

    x = range(len(platforms))

    plt.figure(figsize=(10, 5))
    plt.bar(x, p50_1hop, width=0.4, label='p50 Latency (ms)', align='center')
    plt.bar([i + 0.4 for i in x], p95_1hop, width=0.4, label='p95 Latency (ms)', align='center')
    
    plt.xlabel('Graph Engine')
    plt.ylabel('Latency (ms)')
    plt.title('1-Hop Traversal Latency Comparison')
    plt.xticks([i + 0.2 for i in x], platforms)
    plt.legend()
    plt.tight_layout()
    plt.savefig("results/traversal_1hop.png")
    print("Chart saved to results/traversal_1hop.png")

if __name__ == "__main__":
    build_charts()