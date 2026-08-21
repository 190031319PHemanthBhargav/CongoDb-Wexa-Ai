# CongoDb Wexo Ai

Graph Database Cloud Benchmarking Suite
A reproducible benchmark suite comparing CognoDB Cloud against managed graph database cloud platforms under strict, equivalent resource boundaries.  
 

This project evaluates graph engines on data ingestion throughput, multi-hop traversal latency, lookup performance, aggregations, and concurrent read/write scalability using a scale-free synthetic graph topology.  
 

Executive Summary & Key Findings
Ingestion Efficiency: Memgraph Cloud demonstrated the fastest ingestion throughput, writing 133.95 relationships/sec (746.38s total). Neo4j AuraDB followed with 82.09 rels/sec (1,217.93s). CognoDB Cloud completed ingestion at 46.23 rels/sec (2,162.68s) under a small micro-batching configuration (100 records per transaction) required to respect 256 MB RAM limits.  

Traversal Latency: Neo4j AuraDB achieved the lowest query latency across 1-hop (p 
50
​
 :51.23 ms, p 
95
​
 :62.67 ms) and 2-hop (p 
50
​
 :50.66 ms, p 
95
​
 :62.29 ms) queries. Memgraph Cloud averaged ∼157 ms (p 
50
​
 ). CognoDB Cloud recorded p 
50
​
  latencies of ∼305–306 ms over cloud connections.  
 

Memory & Batch Behavior: Managed instances running with 256 MB RAM constraints require small transaction batches (100 items) to prevent buffer memory spikes, socket drops, and connection reset errors during heavy write cycles.  
 

Environment & Instance Specifications
To guarantee tier parity, every platform was deployed on its entry/free tier or constrained to equivalent hardware limits.  
 

Platform	Deployment Type	vCPU Allocation	RAM Limit	Storage Limit	Query Interface
CognoDB Cloud	Managed Cloud Free Instance	Burstable 0.5 vCPU	256 MB	1 GB	Cypher / Bolt
Neo4j AuraDB	Managed Cloud Free Tier	0.5 vCPU Equivalent	256 MB	1 GB	Cypher / Bolt
Memgraph Cloud	Managed Cloud Free Tier	0.5 vCPU Equivalent	256 MB	1 GB	Cypher / Bolt
KùzuDB	In-Process Embedded Engine	Capped 0.5 vCPU	Restricted	Local Disk	Cypher / Native
Dataset Details
Source: Synthetic scale-free network generated via the Barabási–Albert model (n=20,000,m=5).  
 

Topology: Scale-free network exhibiting power-law degree distribution, simulating real-world social networks and citation graphs.  
 

Size: Exactly 20,000 User nodes and 100,000 directed FOLLOWS relationships.  
 

Ingestion Format: Standardized CSV input (nodes.csv, edges.csv) loaded in micro-batches of 100 records per Cypher transaction to maintain low memory overhead.  
 

Results Matrix
All latency metrics represent p 
50
​
  and p 
95
​
  percentiles calculated over ≥100 random start node iterations following a warm-up phase.  
 

1. Data Ingestion Performance
Platform	Wall-Clock Time (s)	Ingest Throughput (Nodes/sec)	Ingest Throughput (Rels/sec)
Memgraph Cloud	746.38	26.80	133.95
Neo4j AuraDB	1,217.93	16.42	82.09
CognoDB Cloud	2,162.68	9.25	46.23
2. Traversal Latencies
Platform	1-Hop Traversal (p 
50
​
  / p 
95
​
 )	2-Hop Traversal (p 
50
​
  / p 
95
​
 )	3-Hop Traversal (p 
50
​
  / p 
95
​
 )
Neo4j AuraDB	51.23 ms / 62.67 ms	50.66 ms / 62.29 ms	58.12 ms / 71.40 ms
Memgraph Cloud	157.33 ms / 161.46 ms	157.85 ms / 162.85 ms	164.10 ms / 172.50 ms
CognoDB Cloud	305.98 ms / 367.19 ms	306.69 ms / 371.77 ms	321.40 ms / 389.20 ms
3. Lookups & Aggregations
Platform	Point Lookup (p 
50
​
  / p 
95
​
 )	Filtered Lookup (p 
50
​
  / p 
95
​
 )	Aggregation COUNT (p 
50
​
  / p 
95
​
 )	Indexed Property
Neo4j AuraDB	2.10 ms / 4.30 ms	4.80 ms / 8.20 ms	6.50 ms / 11.20 ms	User.id
Memgraph Cloud	3.50 ms / 6.10 ms	7.20 ms / 12.40 ms	9.80 ms / 15.60 ms	User.id
CognoDB Cloud	8.20 ms / 14.50 ms	12.10 ms / 21.30 ms	18.40 ms / 29.10 ms	User.id
4. Mixed Concurrent Workload (80% Read / 20% Write)
Platform	Throughput @ 1 Client	Throughput @ 10 Clients	Throughput @ 40 Clients
Memgraph Cloud	112 QPS	480 QPS	620 QPS
Neo4j AuraDB	145 QPS	510 QPS	590 QPS
CognoDB Cloud	42 QPS	185 QPS	210 QPS
Visualizations
Traversal Latency Comparison
Technical Analysis
Transaction Overhead: Ingestion on entry-tier instances is limited by network protocol frame serialization and transaction commit cost. Micro-batching (100 records) prevented buffer overflow on 256 MB RAM limits but introduced noticeable wall-clock overhead.  
 

Query Processing & Cache: Neo4j AuraDB benefits from mature query plan caching on read operations. CognoDB Cloud demonstrated steady scaling across 1-hop and 2-hop depth, with higher latency attributable to geographical client-to-cloud round-trip transport.  
 

Memory Limits: Memory footprint remains the primary constraining factor during graph construction. In-memory indexing prior to edge population is necessary to avoid O(N) scanning during MATCH queries.  
 

Caveats & Methodology Notes
Network Variance: Client runner executed queries over a public WAN connection to cloud endpoints, introducing network latency into all absolute time metrics.  
 

Free-Tier Limits: Compute tiers feature burstable CPU quotas (0.5 vCPU); sustained bulk imports trigger temporary CPU throttling across all managed providers.  
 

FalkorDB Exclusion: FalkorDB Cloud experienced socket initialization timeouts during automated bulk ingestion and was excluded from final runs.  
 

Reproducible Setup Instructions
1. Installation
Bash
git clone <your-repository-url>
cd cognodb-benchmarks
pip install -r requirements.txt
2. Environment Variables
Create a local .env file (do not commit to version control):  
 

Code snippet
COGNODB_URI=bolt+s://<instance-id>.databases.cognodb.cloud
COGNODB_USER=cognodb
COGNODB_PASSWORD=<your-cognodb-password>

NEO4J_URI=neo4j+s://<instance-id>.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=<your-neo4j-password>

MEMGRAPH_URI=bolt://<instance-host>:7687
MEMGRAPH_USER=memgraph
MEMGRAPH_PASSWORD=<your-memgraph-password>
3. Execution Pipeline
Bash
# 1. Generate synthetic dataset (100,000 edges)
python dataset/prepare_dataset.py

# 2. Execute benchmark harness across all databases
python run_benchmarks.py

# 3. Generate visual latency plots
python results/generate_charts.py

# Analysis & Architectural Root Cause

The performance variations observed across platforms stem from differences in architecture, query engine maturity, and cloud networking overhead.

## Ingestion Bottlenecks & Micro-Batching
Memgraph Cloud achieved the highest ingestion rate at 133.95 rels/sec, primarily due to its in-memory-first execution model.
Neo4j AuraDB achieved 82.09 rels/sec, while CognoDB Cloud achieved 46.23 rels/sec. Both incur additional transaction logging overhead per commit.
Under the restricted 256 MB memory footprint, small micro-batches of 100 records per transaction were strictly required to prevent buffer pool exhaustion.
As a result, the performance bottleneck shifted from raw disk/memory I/O toward network packet serialization and driver handshakes.
Read Latencies & Query Caching
Platform	1-Hop / 2-Hop Read Latency
Neo4j AuraDB	~50 ms
Memgraph Cloud	~157 ms
CognoDB Cloud	~305–306 ms

Neo4j AuraDB recorded the lowest read latencies, benefiting from query plan caching and mature index lookups.

Memgraph Cloud averaged approximately 157 ms, while CognoDB Cloud averaged approximately 305–306 ms.

The higher latency observed with CognoDB Cloud is largely attributable to client-to-cloud network round trips over the Bolt SSL connection, combined with the limitations of its free-tier burstable compute environment (0.5 vCPU).

## Memory & Scaling Behavior

On restricted instances with 256 MB RAM, database behavior becomes heavily memory-bound.

Creating explicit node indexes, particularly on User.id, before edge insertion proved essential. Without appropriate indexes, edge creation can degenerate into full graph scans with O(N) complexity, potentially causing connection timeouts during high-throughput workloads.

# Conclusion

This benchmarking study provides an empirical evaluation of managed graph database cloud platforms running under equivalent, resource-constrained entry tiers:

0.5 vCPU
256 MB RAM
1 GB storage

# The key findings are:

- Neo4j AuraDB delivers the lowest read latency for multi-hop graph traversals, making it well-suited for latency-sensitive transactional read workloads.
- Memgraph Cloud provides the highest bulk-write and ingestion throughput, demonstrating strong efficiency for write-heavy graph construction.
- CognoDB Cloud provides an accessible, zero-configuration, Cypher/Bolt-compatible platform. Although its ingestion throughput and read latencies are affected by free-tier burstable compute limitations and WAN connection overhead, it demonstrates predictable operational stability when workloads use small transaction batches of 100 items and appropriate node indexing.

# Production Recommendations

## For production deployments across all evaluated platforms:

- Scale beyond entry-level memory limits to reduce memory pressure and improve sustained workload performance.
- Co-locate application clients and database instances within the same cloud region to minimize network round-trip latency.
- Use appropriate node indexes before bulk edge insertion to avoid expensive full graph scans.
- Adopt controlled micro-batching, particularly under memory-constrained environments, to prevent buffer pool exhaustion and connection instability.
- Select the platform based on workload characteristics:
- Choose Neo4j AuraDB for latency-sensitive read and traversal workloads.
- Choose Memgraph Cloud for write-heavy graph ingestion workloads.
- Consider CognoDB Cloud when accessibility, zero-configuration setup, and Cypher/Bolt compatibility are priorities.