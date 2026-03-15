# skg_serializer.py
"""
SKG Vault-Compatible Serializer
Serializes SKG transactions to vault-compatible JSONL format
"""

import json
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from skg_node import SKGNode, SKGEdge


class SKGSerializer:
    """
    Serializes SKG transactions to vault-compatible JSONL format.
    Enables historical replay and Caleon ingestion.
    """
    
    def __init__(self, vault_path: Path, worker_id: str):
        self.vault_path = vault_path
        self.worker_id = worker_id
        
        # Create worker-specific SKG vault directory
        self.worker_skg_path = vault_path / "worker_skg" / worker_id
        self.worker_skg_path.mkdir(parents=True, exist_ok=True)
        
        # File handles for append-only JSONL files
        self.nodes_file = None
        self.edges_file = None
        self.transactions_file = None
        
        self._open_files()
    
    def _open_files(self):
        """Open JSONL files for appending."""
        try:
            self.nodes_file = open(self.worker_skg_path / "nodes.jsonl", "a")
            self.edges_file = open(self.worker_skg_path / "edges.jsonl", "a")
            self.transactions_file = open(self.worker_skg_path / "transactions.jsonl", "a")
        except Exception as e:
            print(f"⚠️  Warning: Could not open SKG files: {e}")
    
    def serialize_transaction(self, nodes: List[SKGNode], edges: List[SKGEdge], 
                             event_type: str) -> str:
        """
        Serialize a batch of nodes/edges as a single transaction.
        
        Args:
            nodes: List of nodes to serialize
            edges: List of edges to serialize
            event_type: Type of event (e.g., "CERTIFICATE_INGESTION")
            
        Returns:
            Transaction ID
        """
        
        transaction_id = f"SKG_TXN_{self.worker_id}_{int(datetime.utcnow().timestamp() * 1000000)}"
        
        try:
            # Write transaction header
            txn_record = {
                "transaction_id": transaction_id,
                "event_type": event_type,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "worker_id": self.worker_id,
                "node_count": len(nodes),
                "edge_count": len(edges)
            }
            
            if self.transactions_file:
                self.transactions_file.write(json.dumps(txn_record) + "\n")
                self.transactions_file.flush()
            
            # Write nodes
            for node in nodes:
                node_record = {
                    "transaction_id": transaction_id,
                    "record_type": "node",
                    **node.to_dict()
                }
                
                if self.nodes_file:
                    self.nodes_file.write(json.dumps(node_record) + "\n")
            
            if self.nodes_file:
                self.nodes_file.flush()
            
            # Write edges
            for edge in edges:
                edge_record = {
                    "transaction_id": transaction_id,
                    "record_type": "edge",
                    **edge.to_dict()
                }
                
                if self.edges_file:
                    self.edges_file.write(json.dumps(edge_record) + "\n")
            
            if self.edges_file:
                self.edges_file.flush()
        
        except Exception as e:
            print(f"⚠️  Warning: SKG serialization error: {e}")
        
        return transaction_id
    
    def load_graph(self, nodes_dict: Dict, edges_dict: Dict):
        """
        Load existing graph from vault JSONL files.
        
        Args:
            nodes_dict: Dictionary to populate with nodes
            edges_dict: Dictionary to populate with edges
        """
        
        # Load nodes
        nodes_file = self.worker_skg_path / "nodes.jsonl"
        if nodes_file.exists():
            try:
                with open(nodes_file, "r") as f:
                    loaded_count = 0
                    for line in f:
                        try:
                            record = json.loads(line)
                            # Reconstruct node
                            node = SKGNode.from_dict(record)
                            nodes_dict[node.node_id] = node
                            loaded_count += 1
                        except Exception as e:
                            # Skip corrupted records
                            continue
                    
                    if loaded_count > 0:
                        print(f"✅ Loaded {loaded_count} nodes from vault")
            
            except Exception as e:
                print(f"⚠️  Warning: Could not load nodes: {e}")
        
        # Load edges
        edges_file = self.worker_skg_path / "edges.jsonl"
        if edges_file.exists():
            try:
                with open(edges_file, "r") as f:
                    loaded_count = 0
                    for line in f:
                        try:
                            record = json.loads(line)
                            # Reconstruct edge
                            edge = SKGEdge.from_dict(record)
                            edges_dict[edge.edge_id] = edge
                            loaded_count += 1
                        except Exception as e:
                            # Skip corrupted records
                            continue
                    
                    if loaded_count > 0:
                        print(f"✅ Loaded {loaded_count} edges from vault")
            
            except Exception as e:
                print(f"⚠️  Warning: Could not load edges: {e}")
    
    def get_transaction_log(self, limit: int = 100) -> List[Dict]:
        """
        Retrieve recent SKG transactions for monitoring.
        
        Args:
            limit: Maximum number of transactions to return
            
        Returns:
            List of transaction records
        """
        transactions = []
        txn_file = self.worker_skg_path / "transactions.jsonl"
        
        if not txn_file.exists():
            return transactions
        
        try:
            with open(txn_file, "r") as f:
                all_lines = f.readlines()
                
                # Get last N lines
                for line in all_lines[-limit:]:
                    try:
                        transactions.append(json.loads(line))
                    except:
                        continue
        
        except Exception as e:
            print(f"⚠️  Warning: Could not read transaction log: {e}")
        
        return transactions
    
    def get_vault_statistics(self) -> dict:
        """
        Get statistics about vault storage.
        
        Returns:
            Dictionary with vault statistics
        """
        stats = {
            "worker_id": self.worker_id,
            "vault_path": str(self.worker_skg_path),
            "nodes_file_size": 0,
            "edges_file_size": 0,
            "transactions_file_size": 0,
            "total_size_kb": 0
        }
        
        try:
            nodes_file = self.worker_skg_path / "nodes.jsonl"
            if nodes_file.exists():
                stats["nodes_file_size"] = nodes_file.stat().st_size
            
            edges_file = self.worker_skg_path / "edges.jsonl"
            if edges_file.exists():
                stats["edges_file_size"] = edges_file.stat().st_size
            
            txn_file = self.worker_skg_path / "transactions.jsonl"
            if txn_file.exists():
                stats["transactions_file_size"] = txn_file.stat().st_size
            
            stats["total_size_kb"] = (
                stats["nodes_file_size"] + 
                stats["edges_file_size"] + 
                stats["transactions_file_size"]
            ) / 1024
        
        except Exception as e:
            print(f"⚠️  Warning: Could not get vault statistics: {e}")
        
        return stats
    
    def close(self):
        """Close all file handles."""
        try:
            if self.nodes_file:
                self.nodes_file.close()
            if self.edges_file:
                self.edges_file.close()
            if self.transactions_file:
                self.transactions_file.close()
        except Exception as e:
            print(f"⚠️  Warning: Error closing SKG files: {e}")
    
    def __del__(self):
        """Destructor to ensure files are closed."""
        self.close()


if __name__ == "__main__":
    from skg_node import SKGNode, SKGEdge, SKGNodeType
    from pathlib import Path
    
    print("🧪 SKG Serializer - Self Test")
    print("=" * 60)
    
    # Create temporary vault path
    test_vault_path = Path("T:/certificate generator 2x/Vault_System_1.0/skg_graph")
    test_vault_path.mkdir(parents=True, exist_ok=True)
    
    serializer = SKGSerializer(test_vault_path, "test_worker")
    
    # Create test nodes
    test_nodes = [
        SKGNode(
            node_id="cert:TEST001",
            node_type=SKGNodeType.CERTIFICATE,
            properties={"dals_serial": "TEST001"},
            created_by="test_worker"
        ),
        SKGNode(
            node_id="owner:0xTEST",
            node_type=SKGNodeType.IDENTITY,
            properties={"wallet_address": "0xTEST"},
            created_by="test_worker"
        )
    ]
    
    # Create test edge
    test_edges = [
        SKGEdge(
            edge_id="edge:TEST001",
            source_id="cert:TEST001",
            target_id="owner:0xTEST",
            edge_type="OWNED_BY",
            properties={}
        )
    ]
    
    print("\n📝 Serializing test transaction...")
    txn_id = serializer.serialize_transaction(
        nodes=test_nodes,
        edges=test_edges,
        event_type="TEST_INGESTION"
    )
    print(f"✅ Transaction ID: {txn_id}")
    
    print("\n📊 Vault Statistics:")
    stats = serializer.get_vault_statistics()
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {value}")
    
    print("\n📋 Transaction Log:")
    transactions = serializer.get_transaction_log(limit=5)
    print(f"   Found {len(transactions)} transactions")
    
    print("\n🔄 Testing graph reload...")
    test_nodes_dict = {}
    test_edges_dict = {}
    serializer.load_graph(test_nodes_dict, test_edges_dict)
    print(f"   Loaded {len(test_nodes_dict)} nodes")
    print(f"   Loaded {len(test_edges_dict)} edges")
    
    serializer.close()
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
