"""
Self-pruning helpers for the Swarm Knowledge Graph.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict, Tuple

from skg_node import SKGEdge, SKGNode


def _parse_timestamp(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    return datetime.fromisoformat(normalized)


class SKGPruner:
    """
    Remove stale nodes and weak edges before the graph becomes cluttered.
    """

    def __init__(
        self,
        max_nodes: int = 10000,
        max_edges: int = 50000,
        stale_days: int = 30,
        min_confidence: float = 0.1,
    ):
        self.thresholds = {
            "max_nodes": max_nodes,
            "max_edges": max_edges,
            "stale_days": stale_days,
            "min_confidence": min_confidence,
        }

    def prune_clutter(
        self, nodes: Dict[str, SKGNode], edges: Dict[str, SKGEdge]
    ) -> Tuple[Dict[str, SKGNode], Dict[str, SKGEdge], Dict[str, int]]:
        """Remove inactive nodes and weak edges."""
        cutoff = datetime.now(timezone.utc) - timedelta(days=self.thresholds["stale_days"])

        active_edges = {
            edge_id: edge
            for edge_id, edge in edges.items()
            if edge.confidence >= self.thresholds["min_confidence"]
        }

        connected_nodes = set()
        for edge in active_edges.values():
            connected_nodes.add(edge.source_id)
            connected_nodes.add(edge.target_id)

        active_nodes = {}
        for node_id, node in nodes.items():
            node_created = _parse_timestamp(node.created_at)
            if node_id in connected_nodes or node_created >= cutoff:
                active_nodes[node_id] = node

        if len(active_nodes) > self.thresholds["max_nodes"]:
            sorted_nodes = sorted(
                active_nodes.values(),
                key=lambda item: item.created_at,
                reverse=True,
            )[: self.thresholds["max_nodes"]]
            allowed = {node.node_id for node in sorted_nodes}
            active_nodes = {node_id: node for node_id, node in active_nodes.items() if node_id in allowed}
            active_edges = {
                edge_id: edge
                for edge_id, edge in active_edges.items()
                if edge.source_id in allowed and edge.target_id in allowed
            }

        if len(active_edges) > self.thresholds["max_edges"]:
            sorted_edges = sorted(
                active_edges.values(),
                key=lambda item: (item.confidence, item.created_at),
                reverse=True,
            )[: self.thresholds["max_edges"]]
            active_edges = {edge.edge_id: edge for edge in sorted_edges}

        metrics = {
            "nodes_removed": max(len(nodes) - len(active_nodes), 0),
            "edges_removed": max(len(edges) - len(active_edges), 0),
        }

        return active_nodes, active_edges, metrics
