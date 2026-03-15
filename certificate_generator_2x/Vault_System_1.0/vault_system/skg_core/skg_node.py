# skg_node.py
"""
SKG Node & Edge Type Definitions
Immutable structures representing entities and relationships in the knowledge graph
"""

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any


class SKGNodeType(Enum):
    """Node types in the knowledge graph."""
    CERTIFICATE = "certificate"
    IDENTITY = "identity"
    CHAIN = "chain"
    PATTERN = "pattern"
    DRIFT_EVENT = "drift_event"


@dataclass
class SKGNode:
    """Immutable node representing an entity in the graph."""
    node_id: str
    node_type: SKGNodeType
    properties: Dict[str, Any]
    created_by: str
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    version: int = 1
    is_active: bool = True
    
    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type.value,
            "properties": self.properties,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "version": self.version,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruct node from dictionary."""
        return cls(
            node_id=data["node_id"],
            node_type=SKGNodeType(data["node_type"]),
            properties=data["properties"],
            created_by=data["created_by"],
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            version=data.get("version", 1),
            is_active=data.get("is_active", True)
        )


@dataclass
class SKGEdge:
    """Directed edge representing a relationship."""
    edge_id: str
    source_id: str
    target_id: str
    edge_type: str
    properties: Dict[str, Any]
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    confidence: float = 1.0
    
    def to_dict(self) -> dict:
        return {
            "edge_id": self.edge_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "edge_type": self.edge_type,
            "properties": self.properties,
            "created_at": self.created_at,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """Reconstruct edge from dictionary."""
        return cls(
            edge_id=data["edge_id"],
            source_id=data["source_id"],
            target_id=data["target_id"],
            edge_type=data["edge_type"],
            properties=data["properties"],
            created_at=data.get("created_at", datetime.utcnow().isoformat() + "Z"),
            confidence=data.get("confidence", 1.0)
        )


if __name__ == "__main__":
    # Self-test
    print("🧪 SKG Node Types - Self Test")
    print("=" * 60)
    
    # Test node creation
    test_node = SKGNode(
        node_id="cert:TEST001",
        node_type=SKGNodeType.CERTIFICATE,
        properties={"dals_serial": "TEST001", "owner": "Test User"},
        created_by="test_worker"
    )
    
    print(f"✅ Created node: {test_node.node_id}")
    print(f"   Type: {test_node.node_type.value}")
    print(f"   Properties: {test_node.properties}")
    
    # Test edge creation
    test_edge = SKGEdge(
        edge_id="edge:TEST001",
        source_id="cert:TEST001",
        target_id="owner:0xTEST",
        edge_type="OWNED_BY",
        properties={"ownership_type": "primary"}
    )
    
    print(f"\n✅ Created edge: {test_edge.edge_id}")
    print(f"   Relationship: {test_edge.source_id} -> {test_edge.edge_type} -> {test_edge.target_id}")
    
    # Test serialization
    node_dict = test_node.to_dict()
    reconstructed = SKGNode.from_dict(node_dict)
    
    print(f"\n✅ Serialization test:")
    print(f"   Original ID: {test_node.node_id}")
    print(f"   Reconstructed ID: {reconstructed.node_id}")
    print(f"   Match: {test_node.node_id == reconstructed.node_id}")
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
