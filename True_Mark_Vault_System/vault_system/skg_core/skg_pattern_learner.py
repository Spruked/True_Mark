# skg_pattern_learner.py
"""
SKG Pattern Learning Engine
Detects patterns in certificate data for deduplication and anomaly detection
"""

from collections import defaultdict
from typing import List, Dict, Set
from skg_node import SKGNode, SKGNodeType
import hashlib


class SKGPatternLearner:
    """
    Detects patterns in certificate data for deduplication and anomaly detection.
    Runs in FusionQueueEngine for swarm-wide pattern convergence.
    """
    
    def __init__(self):
        self.pattern_clusters: Dict[str, List[str]] = defaultdict(list)
        self.owner_fingerprint_cache: Dict[str, str] = {}
        self.certificate_count = 0
    
    def learn_from_certificate(self, cert_node: SKGNode, owner_node: SKGNode, chain_node: SKGNode):
        """
        Extract patterns and cluster similar certificates.
        
        Args:
            cert_node: Certificate node
            owner_node: Owner identity node
            chain_node: Blockchain node
        """
        
        self.certificate_count += 1
        
        # Pattern 1: Wallet ownership frequency
        wallet_hash = self._hash_wallet_behavior(owner_node)
        self.pattern_clusters[f"wallet_behavior:{wallet_hash}"].append(cert_node.node_id)
        
        # Pattern 2: IPFS storage pattern (detects duplicate content)
        ipfs_hash = cert_node.properties.get('ipfs_hash', '')
        if ipfs_hash:
            ipfs_pattern = ipfs_hash[:16] if len(ipfs_hash) >= 16 else ipfs_hash
            self.pattern_clusters[f"ipfs_prefix:{ipfs_pattern}"].append(cert_node.node_id)
        
        # Pattern 3: Temporal issuance pattern
        minted_at = cert_node.properties.get('minted_at', '')
        if len(minted_at) >= 13:
            hour_bucket = minted_at[:13]  # YYYY-MM-DDTHH
            self.pattern_clusters[f"issuance_hour:{hour_bucket}"].append(cert_node.node_id)
        
        # Pattern 4: Chain activity pattern
        chain_id = chain_node.properties.get('chain_id', 'unknown')
        self.pattern_clusters[f"chain_activity:{chain_id}"].append(cert_node.node_id)
        
        # Pattern 5: Asset title patterns (semantic clustering)
        title = cert_node.properties.get('asset_title', '')
        if title:
            title_hash = hashlib.md5(title.lower().encode()).hexdigest()[:8]
            self.pattern_clusters[f"title_cluster:{title_hash}"].append(cert_node.node_id)
    
    def _hash_wallet_behavior(self, owner_node: SKGNode) -> str:
        """
        Create behavior fingerprint from wallet metadata.
        
        Args:
            owner_node: Owner identity node
            
        Returns:
            8-character hash representing wallet behavior
        """
        wallet = owner_node.properties.get("wallet_address", "unknown")
        name = owner_node.properties.get("owner_name", "unknown")
        
        # Simple behavioral hash (expand with transaction history)
        behavior_string = f"{wallet}:{name}"
        return hashlib.md5(behavior_string.encode()).hexdigest()[:8]
    
    def detect_duplicates(self, cert_node: SKGNode) -> Set[str]:
        """
        Check if this certificate is a duplicate of existing ones.
        
        Args:
            cert_node: Certificate node to check
            
        Returns:
            Set of certificate IDs that might be duplicates
        """
        duplicates = set()
        ipfs_hash = cert_node.properties.get('ipfs_hash', '')
        
        if not ipfs_hash or len(ipfs_hash) < 16:
            return duplicates
        
        ipfs_prefix = ipfs_hash[:16]
        
        for pattern_key, cert_ids in self.pattern_clusters.items():
            if pattern_key.startswith("ipfs_prefix:") and ipfs_prefix in pattern_key:
                duplicates.update(cert_ids)
        
        # Remove self from duplicates
        duplicates.discard(cert_node.node_id)
        
        return duplicates
    
    def get_cluster_count(self) -> dict:
        """
        Return pattern cluster statistics.
        
        Returns:
            Dictionary with cluster counts by type
        """
        return {
            "total_clusters": len(self.pattern_clusters),
            "wallet_behavior_clusters": len([k for k in self.pattern_clusters if k.startswith("wallet_behavior:")]),
            "ipfs_clusters": len([k for k in self.pattern_clusters if k.startswith("ipfs_prefix:")]),
            "temporal_clusters": len([k for k in self.pattern_clusters if k.startswith("issuance_hour:")]),
            "chain_clusters": len([k for k in self.pattern_clusters if k.startswith("chain_activity:")]),
            "title_clusters": len([k for k in self.pattern_clusters if k.startswith("title_cluster:")])
        }
    
    def get_wallet_activity(self, wallet_address: str) -> dict:
        """
        Get activity metrics for a specific wallet.
        
        Args:
            wallet_address: Wallet address to query
            
        Returns:
            Activity metrics dictionary
        """
        certificates = []
        
        for pattern_key, cert_ids in self.pattern_clusters.items():
            if pattern_key.startswith("wallet_behavior:"):
                # Would need full node lookup to verify wallet
                # This is a simplified version
                certificates.extend(cert_ids)
        
        return {
            "wallet_address": wallet_address,
            "certificate_count": len(certificates),
            "activity_score": min(len(certificates) / 10.0, 1.0)  # Normalized 0-1
        }
    
    def get_pattern_summary(self) -> dict:
        """
        Get comprehensive pattern learning summary.
        
        Returns:
            Summary of all learned patterns
        """
        cluster_counts = self.get_cluster_count()
        
        # Find most active patterns
        most_active = sorted(
            self.pattern_clusters.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]
        
        return {
            "total_certificates_analyzed": self.certificate_count,
            "cluster_statistics": cluster_counts,
            "most_active_patterns": [
                {"pattern": key, "certificate_count": len(certs)}
                for key, certs in most_active
            ],
            "average_certificates_per_cluster": (
                sum(len(certs) for certs in self.pattern_clusters.values()) / len(self.pattern_clusters)
                if self.pattern_clusters else 0
            )
        }


if __name__ == "__main__":
    from skg_node import SKGNode, SKGNodeType
    
    print("🧪 SKG Pattern Learner - Self Test")
    print("=" * 60)
    
    learner = SKGPatternLearner()
    
    # Create test nodes
    cert_node = SKGNode(
        node_id="cert:TEST001",
        node_type=SKGNodeType.CERTIFICATE,
        properties={
            "dals_serial": "TEST001",
            "asset_title": "Test Certificate",
            "ipfs_hash": "ipfs://QmTest12345678",
            "minted_at": "2025-12-10T15:30:00Z"
        },
        created_by="test_worker"
    )
    
    owner_node = SKGNode(
        node_id="owner:0xTEST",
        node_type=SKGNodeType.IDENTITY,
        properties={
            "wallet_address": "0xTEST123",
            "owner_name": "Test Owner"
        },
        created_by="test_worker"
    )
    
    chain_node = SKGNode(
        node_id="chain:polygon:12345",
        node_type=SKGNodeType.CHAIN,
        properties={
            "chain_id": "Polygon",
            "block_height": "12345"
        },
        created_by="test_worker"
    )
    
    print("\n📝 Learning patterns from test certificate...")
    learner.learn_from_certificate(cert_node, owner_node, chain_node)
    
    print(f"✅ Patterns learned")
    
    cluster_stats = learner.get_cluster_count()
    print(f"\n📊 Cluster Statistics:")
    for key, value in cluster_stats.items():
        print(f"   {key}: {value}")
    
    print(f"\n🔍 Checking for duplicates...")
    duplicates = learner.detect_duplicates(cert_node)
    print(f"   Found {len(duplicates)} potential duplicates")
    
    summary = learner.get_pattern_summary()
    print(f"\n📈 Pattern Summary:")
    print(f"   Total certificates analyzed: {summary['total_certificates_analyzed']}")
    print(f"   Average certs per cluster: {summary['average_certificates_per_cluster']:.2f}")
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
