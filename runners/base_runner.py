from abc import ABC, abstractmethod
import time

class BaseGraphRunner(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def clear_database(self):
        pass

    @abstractmethod
    def load_data(self, nodes_csv: str, edges_csv: str) -> dict:
        """Loads data and returns dict with wall_clock_time, nodes_per_sec, rels_per_sec"""
        pass

    @abstractmethod
    def run_traversals(self, start_node_ids: list, hops: int, iterations: int = 100) -> dict:
        """Returns dict with p50 and p95 latency in ms"""
        pass

    @abstractmethod
    def run_lookup(self, property_key: str, property_value: str, iterations: int = 100) -> dict:
        """Returns dict with p50 and p95 latency in ms"""
        pass

    @abstractmethod
    def run_aggregation(self, iterations: int = 100) -> dict:
        """Returns dict with p50 and p95 latency in ms"""
        pass

    @abstractmethod
    def close(self):
        pass