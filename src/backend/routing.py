"""SDNC-like routing across the interconnect graph."""
from collections import deque
from typing import List

from .config import InterconnectConfig
from .registration import Participant


class Router:
    def __init__(self, interconnect: InterconnectConfig):
        self.interconnect = interconnect

    def compute_route(self, producer: Participant, consumer: Participant) -> List[str]:
        graph = self.interconnect.grid_nodes
        start_nodes = [node for node in graph if producer.metadata.get("node") == node]
        end_node = consumer.metadata.get("node")
        if not start_nodes:
            raise ValueError("Producer node not set in metadata")
        if not end_node:
            raise ValueError("Consumer node not set in metadata")

        for start in start_nodes:
            route = self._shortest_path(graph, start, end_node)
            if route:
                return route
        raise ValueError(f"No available route from {producer.participant_id} to {consumer.participant_id}")

    @staticmethod
    def _shortest_path(graph, start, goal) -> List[str]:
        queue = deque([(start, [start])])
        visited = set()
        while queue:
            node, path = queue.popleft()
            if node == goal:
                return path
            if node in visited:
                continue
            visited.add(node)
            for neighbor in graph.get(node, []):
                queue.append((neighbor, path + [neighbor]))
        return []
