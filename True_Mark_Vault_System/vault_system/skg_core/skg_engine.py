# skg_engine.py
"""
Swarm Knowledge Graph Engine
Main orchestrator for distributed knowledge graph learning
Integrates with WorkerVaultWriter and FusionQueueEngine
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from uuid import uuid4
from skg_node import SKGNode, SKGEdge, SKGNodeType
from skg_serializer import SKGSerializer
from skg_pattern_learner import SKGPatternLearner
from skg_drift_analyzer import SKGDriftAnalyzer
from skg_pruner import SKGPruner
from skg_cleaner import SKGCleaner


class SwarmKnowledgeGraphEngine:
    """
    Distributed knowledge graph that learns from certificate forge events.
    Integrates with WorkerVaultWriter and FusionQueueEngine for swarm consensus.
    """
    
    def __init__(self, vault_base_path: Path, worker_id: str):
        self.worker_id = worker_id
        self.vault_path = vault_base_path / "skg_graph"
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        print(f"🧠 Initializing SKG Engine for worker: {worker_id}")
        
        # Core components
        self.serializer = SKGSerializer(self.vault_path, worker_id)
        self.pattern_learner = SKGPatternLearner()
        self.drift_analyzer = SKGDriftAnalyzer()
        self.pruner = SKGPruner()
        self.cleaner = SKGCleaner()
        
        # In-memory graph cache
        self.nodes: Dict[str, SKGNode] = {}
        self.edges: Dict[str, SKGEdge] = {}
        
        # Load existing graph from vault
        self._load_from_vault()
        
        print(f"✅ SKG Engine initialized: {len(self.nodes)} nodes, {len(self.edges)} edges loaded")
    
    def ingest_certificate(self, certificate_data: dict, vault_txn_id: str) -> str:
        """
        Ingest a newly minted certificate into the SKG.
        
        Args:
            certificate_data: Certificate metadata dictionary
            vault_txn_id: Vault transaction ID
            
        Returns:
            SKG transaction ID for tracking
        """
        
        # Create certificate node (immutable anchor point)
        cert_node = SKGNode(
            node_id=f"cert:{certificate_data['dals_serial']}",
            node_type=SKGNodeType.CERTIFICATE,
            properties={
                "dals_serial": certificate_data['dals_serial'],
                "asset_title": certificate_data.get('asset_title', 'Unknown'),
                "ipfs_hash": certificate_data.get('ipfs_hash', ''),
                "minted_at": certificate_data.get('stardate', datetime.utcnow().isoformat() + "Z"),
                "vault_txn_id": vault_txn_id,
                "ed25519_signature": certificate_data.get('ed25519_signature', ''),
                "verifying_key": certificate_data.get('verifying_key', '')
            },
            created_by=self.worker_id
        )
        
        # Create owner node (identity entity)
        owner_node = SKGNode(
            node_id=f"owner:{certificate_data.get('wallet', certificate_data.get('wallet_address', 'unknown'))}",
            node_type=SKGNodeType.IDENTITY,
            properties={
                "wallet_address": certificate_data.get('wallet', certificate_data.get('wallet_address', 'unknown')),
                "owner_name": certificate_data.get('owner', certificate_data.get('owner_name', 'Unknown')),
                "first_seen": certificate_data.get('stardate', datetime.utcnow().isoformat() + "Z")
            },
            created_by=self.worker_id
        )
        
        # Create chain node (blockchain context)
        chain_node = SKGNode(
            node_id=f"chain:{certificate_data.get('chain_id', 'unknown')}:{certificate_data.get('block_height', 'pending')}",
            node_type=SKGNodeType.CHAIN,
            properties={
                "chain_id": certificate_data.get('chain_id', 'unknown'),
                "block_height": certificate_data.get('block_height', 'pending'),
                "contract_address": certificate_data.get('contract_address', 'N/A')
            },
            created_by=self.worker_id
        )
        
        # Create edges (relationships)
        edges = [
            SKGEdge(
                edge_id=f"edge:{uuid4().hex[:8]}",
                source_id=cert_node.node_id,
                target_id=owner_node.node_id,
                edge_type="OWNED_BY",
                properties={"ownership_type": "primary"}
            ),
            SKGEdge(
                edge_id=f"edge:{uuid4().hex[:8]}",
                source_id=cert_node.node_id,
                target_id=chain_node.node_id,
                edge_type="ANCHORED_ON",
                properties={"anchor_type": "blockchain"}
            ),
            SKGEdge(
                edge_id=f"edge:{uuid4().hex[:8]}",
                source_id=owner_node.node_id,
                target_id=chain_node.node_id,
                edge_type="TRANSACTS_ON",
                properties={"wallet_type": "external"}
            )
        ]
        
        # Learn patterns BEFORE drift analysis (needs pattern context)
        self.pattern_learner.learn_from_certificate(cert_node, owner_node, chain_node)
        
        # Analyze drift
        drift_score = self.drift_analyzer.analyze_certificate_drift(cert_node)
        
        # Update node with drift score
        cert_node.properties["drift_score"] = drift_score
        
        # Add to graph (update existing nodes if already present)
        self.nodes[cert_node.node_id] = cert_node
        
        # Only add owner/chain if not already present (prevent duplicates)
        if owner_node.node_id not in self.nodes:
            self.nodes[owner_node.node_id] = owner_node
        
        if chain_node.node_id not in self.nodes:
            self.nodes[chain_node.node_id] = chain_node
        
        for edge in edges:
            self.edges[edge.edge_id] = edge

        self.edges = self.cleaner.clean_edges(self.edges)
        self.nodes, self.edges, prune_metrics = self.pruner.prune_clutter(self.nodes, self.edges)
        
        # Serialize to vault
        skg_txn_id = self.serializer.serialize_transaction(
            nodes=[cert_node, owner_node, chain_node],
            edges=list(self.edges.values()),
            event_type="CERTIFICATE_INGESTION"
        )

        if prune_metrics["nodes_removed"] or prune_metrics["edges_removed"]:
            print(
                f"🧹 SKG prune: removed {prune_metrics['nodes_removed']} nodes "
                f"and {prune_metrics['edges_removed']} edges"
            )
        
        return skg_txn_id
    
    def query_by_wallet(self, wallet_address: str) -> List[Dict[str, Any]]:
        """
        Find all certificates owned by a wallet address.
        
        Args:
            wallet_address: Wallet address to query
            
        Returns:
            List of certificates with ownership information
        """
        results = []
        
        for node in self.nodes.values():
            if node.node_type == SKGNodeType.CERTIFICATE:
                # Traverse OWNED_BY edge to find owner
                for edge in self.edges.values():
                    if edge.source_id == node.node_id and edge.edge_type == "OWNED_BY":
                        owner_node = self.nodes.get(edge.target_id)
                        if owner_node and owner_node.properties.get("wallet_address") == wallet_address:
                            results.append({
                                "certificate": node.properties,
                                "ownership": edge.properties,
                                "certificate_node_id": node.node_id
                            })
        
        return results
    
    def query_by_chain(self, chain_id: str) -> List[Dict[str, Any]]:
        """
        Find all certificates anchored on a specific chain.
        
        Args:
            chain_id: Blockchain identifier
            
        Returns:
            List of certificates on that chain
        """
        results = []
        
        for node in self.nodes.values():
            if node.node_type == SKGNodeType.CERTIFICATE:
                # Traverse ANCHORED_ON edge to find chain
                for edge in self.edges.values():
                    if edge.source_id == node.node_id and edge.edge_type == "ANCHORED_ON":
                        chain_node = self.nodes.get(edge.target_id)
                        if chain_node and chain_node.properties.get("chain_id") == chain_id:
                            results.append({
                                "certificate": node.properties,
                                "chain": chain_node.properties
                            })
        
        return results
    
    def get_swarm_knowledge_summary(self) -> dict:
        """
        Generate summary for Super Worker Guardian monitoring.
        
        Returns:
            Summary dictionary with key metrics
        """
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "certificate_count": len([n for n in self.nodes.values() if n.node_type == SKGNodeType.CERTIFICATE]),
            "unique_owners": len({n.properties["wallet_address"] for n in self.nodes.values() if n.node_type == SKGNodeType.IDENTITY}),
            "unique_chains": len({n.properties["chain_id"] for n in self.nodes.values() if n.node_type == SKGNodeType.CHAIN}),
            "latest_drift_score": self.drift_analyzer.get_global_drift_average(),
            "pattern_clusters": self.pattern_learner.get_cluster_count(),
            "drift_statistics": self.drift_analyzer.get_drift_statistics(),
            "vault_statistics": self.serializer.get_vault_statistics()
        }
    
    def get_certificate_details(self, dals_serial: str) -> Optional[Dict]:
        """
        Get complete details for a specific certificate.
        
        Args:
            dals_serial: DALS serial number
            
        Returns:
            Certificate details or None if not found
        """
        cert_node_id = f"cert:{dals_serial}"
        cert_node = self.nodes.get(cert_node_id)
        
        if not cert_node:
            return None
        
        # Find related nodes
        owner_node = None
        chain_node = None
        
        for edge in self.edges.values():
            if edge.source_id == cert_node_id:
                if edge.edge_type == "OWNED_BY":
                    owner_node = self.nodes.get(edge.target_id)
                elif edge.edge_type == "ANCHORED_ON":
                    chain_node = self.nodes.get(edge.target_id)
        
        return {
            "certificate": cert_node.to_dict(),
            "owner": owner_node.to_dict() if owner_node else None,
            "chain": chain_node.to_dict() if chain_node else None,
            "drift_score": cert_node.properties.get("drift_score", 0.0)
        }
    
    def detect_anomalies(self, threshold: float = 0.7) -> List[Dict]:
        """
        Detect certificates with anomalous drift scores.
        
        Args:
            threshold: Drift threshold for anomaly detection
            
        Returns:
            List of anomalous certificates
        """
        return self.drift_analyzer.detect_anomalies(threshold)
    
    def _load_from_vault(self):
        """Load existing SKG state from vault JSONL files."""
        self.serializer.load_graph(self.nodes, self.edges)
    
    def shutdown(self):
        """Clean shutdown of SKG engine."""
        print("🛑 Shutting down SKG Engine...")
        self.serializer.close()
        print("✅ SKG Engine shut down successfully")


if __name__ == "__main__":
    from pathlib import Path
    
    print("🧪 SKG Engine - Self Test")
    print("=" * 60)
    
    # Initialize engine
    vault_path = Path(__file__).resolve().parents[2]
    engine = SwarmKnowledgeGraphEngine(vault_path, "test_worker_skg")
    
    # Test certificate data
    test_cert = {
        "dals_serial": "DALSTEST_SKG_001",
        "asset_title": "SKG Test Certificate",
        "ipfs_hash": "ipfs://QmTestSKG1234567890",
        "stardate": datetime.utcnow().isoformat() + "Z",
        "owner": "Test Owner",
        "wallet": "0xSKGTEST123",
        "chain_id": "Polygon",
        "ed25519_signature": "a" * 128,
        "verifying_key": "b" * 64
    }
    
    print("\n📝 Ingesting test certificate...")
    skg_txn_id = engine.ingest_certificate(test_cert, "VAULT_TXN_TEST_001")
    print(f"✅ SKG Transaction: {skg_txn_id}")
    
    print("\n🔍 Querying by wallet...")
    wallet_certs = engine.query_by_wallet("0xSKGTEST123")
    print(f"   Found {len(wallet_certs)} certificates for wallet")
    
    print("\n🔍 Querying by chain...")
    chain_certs = engine.query_by_chain("Polygon")
    print(f"   Found {len(chain_certs)} certificates on Polygon")
    
    print("\n📊 Swarm Knowledge Summary:")
    summary = engine.get_swarm_knowledge_summary()
    print(f"   Total Nodes: {summary['total_nodes']}")
    print(f"   Certificates: {summary['certificate_count']}")
    print(f"   Unique Owners: {summary['unique_owners']}")
    print(f"   Drift Score: {summary['latest_drift_score']:.4f}")
    print(f"   Pattern Clusters: {summary['pattern_clusters']['total_clusters']}")
    
    print("\n🔍 Certificate Details:")
    details = engine.get_certificate_details("DALSTEST_SKG_001")
    if details:
        print(f"   Certificate: {details['certificate']['node_id']}")
        print(f"   Owner: {details['owner']['node_id'] if details['owner'] else 'None'}")
        print(f"   Drift: {details['drift_score']:.4f}")
    
    engine.shutdown()
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
