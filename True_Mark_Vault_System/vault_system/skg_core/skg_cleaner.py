"""
Relationship cleanup helpers for the SKG.
"""

from __future__ import annotations

from typing import Dict

from skg_node import SKGEdge


class SKGCleaner:
    """
    Deduplicate edges and strengthen repeated relationships.
    """

    def clean_edges(self, edges: Dict[str, SKGEdge]) -> Dict[str, SKGEdge]:
        cleaned: Dict[str, SKGEdge] = {}
        by_signature = {}

        for edge in edges.values():
            signature = (edge.source_id, edge.target_id, edge.edge_type)
            existing = by_signature.get(signature)

            if existing is None:
                by_signature[signature] = edge
                cleaned[edge.edge_id] = edge
                continue

            existing.confidence = max(existing.confidence, edge.confidence)
            existing.properties.update(edge.properties)

        return cleaned
