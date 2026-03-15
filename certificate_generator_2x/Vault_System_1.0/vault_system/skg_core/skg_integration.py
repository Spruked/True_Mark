# skg_integration.py
"""
Certificate SKG Bridge
Bridge between Certificate Forge and SKG
Automatically ingests certificates into swarm knowledge
"""

from pathlib import Path
from skg_engine import SwarmKnowledgeGraphEngine
from typing import Dict, List


class CertificateSKGBridge:
    """
    Bridge between Certificate Forge and SKG.
    Automatically ingests certificates into swarm knowledge.
    """
    
    def __init__(self, vault_base_path: Path, worker_id: str = "certificate_forge_worker_001"):
        self.skg = SwarmKnowledgeGraphEngine(
            vault_base_path=vault_base_path,
            worker_id=worker_id
        )
        print(f"🌉 SKG Bridge initialized for worker: {worker_id}")
    
    async def on_certificate_minted(self, certificate_data: dict, vault_txn_id: str) -> Dict:
        """
        Hook called by certificate_forge.py after minting.
        
        Args:
            certificate_data: Complete certificate data dictionary
            vault_txn_id: Vault transaction ID
            
        Returns:
            FusionQueue payload for swarm broadcast
        """
        
        # Ingest into SKG
        skg_txn_id = self.skg.ingest_certificate(certificate_data, vault_txn_id)
        
        # Get drift score for monitoring
        cert_details = self.skg.get_certificate_details(certificate_data['dals_serial'])
        drift_score = cert_details['drift_score'] if cert_details else 0.0
        
        # Prepare FusionQueue payload for swarm broadcast
        fusion_payload = {
            "event_type": "SKG_CERTIFICATE_INGESTED",
            "skg_transaction_id": skg_txn_id,
            "vault_transaction_id": vault_txn_id,
            "dals_serial": certificate_data['dals_serial'],
            "drift_score": drift_score,
            "pattern_clusters": self.skg.pattern_learner.get_cluster_count(),
            "requires_swarm_sync": True,
            "timestamp": certificate_data.get('stardate', '')
        }
        
        print(f"✅ Certificate ingested to SKG: {skg_txn_id}")
        print(f"   Drift Score: {drift_score:.4f}")
        
        return fusion_payload
    
    def get_owner_portfolio(self, wallet_address: str) -> dict:
        """
        Query SKG for all certificates owned by a wallet.
        Useful for customer dashboard.
        
        Args:
            wallet_address: Wallet address to query
            
        Returns:
            Portfolio dictionary with certificates and analytics
        """
        certificates = self.skg.query_by_wallet(wallet_address)
        
        if not certificates:
            return {
                "wallet_address": wallet_address,
                "certificate_count": 0,
                "certificates": [],
                "drift_analysis": {
                    "average_drift": 0.0,
                    "highest_drift_certificate": None
                }
            }
        
        # Calculate drift statistics
        drift_scores = [c['certificate'].get('drift_score', 0.0) for c in certificates]
        avg_drift = sum(drift_scores) / len(drift_scores) if drift_scores else 0.0
        
        highest_drift_cert = max(
            certificates, 
            key=lambda c: c['certificate'].get('drift_score', 0.0)
        ) if certificates else None
        
        return {
            "wallet_address": wallet_address,
            "certificate_count": len(certificates),
            "certificates": certificates,
            "drift_analysis": {
                "average_drift": avg_drift,
                "highest_drift": max(drift_scores) if drift_scores else 0.0,
                "lowest_drift": min(drift_scores) if drift_scores else 0.0,
                "highest_drift_certificate": highest_drift_cert
            }
        }
    
    def get_chain_analytics(self, chain_id: str) -> dict:
        """
        Get analytics for a specific blockchain.
        
        Args:
            chain_id: Blockchain identifier
            
        Returns:
            Chain analytics dictionary
        """
        certificates = self.skg.query_by_chain(chain_id)
        
        return {
            "chain_id": chain_id,
            "certificate_count": len(certificates),
            "certificates": certificates,
            "activity_score": min(len(certificates) / 100.0, 1.0)  # Normalized
        }
    
    def get_skg_health_metrics(self) -> dict:
        """
        Health metrics for Super Worker Guardian.
        
        Returns:
            Comprehensive health metrics
        """
        summary = self.skg.get_swarm_knowledge_summary()
        
        # Add health indicators
        summary["health_status"] = "healthy" if summary["latest_drift_score"] < 0.3 else "warning"
        summary["knowledge_density"] = (
            summary["total_edges"] / summary["total_nodes"] 
            if summary["total_nodes"] > 0 else 0
        )
        
        return summary
    
    def detect_suspicious_certificates(self, threshold: float = 0.7) -> List[Dict]:
        """
        Detect certificates with high drift scores (potential forgery attempts).
        
        Args:
            threshold: Drift threshold (0.0-1.0)
            
        Returns:
            List of suspicious certificates
        """
        anomalies = self.skg.detect_anomalies(threshold)
        
        # Enrich with certificate details
        suspicious = []
        for anomaly in anomalies:
            cert_details = self.skg.get_certificate_details(
                anomaly['node_id'].replace('cert:', '')
            )
            
            if cert_details:
                suspicious.append({
                    "dals_serial": cert_details['certificate']['properties'].get('dals_serial'),
                    "drift_score": anomaly['drift_score'],
                    "components": anomaly['components'],
                    "owner": cert_details['owner']['properties'].get('wallet_address') if cert_details['owner'] else 'Unknown',
                    "analyzed_at": anomaly['analyzed_at']
                })
        
        return suspicious
    
    def get_pattern_insights(self) -> dict:
        """
        Get insights from pattern learning.
        
        Returns:
            Pattern insights dictionary
        """
        return self.skg.pattern_learner.get_pattern_summary()
    
    def get_drift_trends(self) -> dict:
        """
        Get drift trend analysis.
        
        Returns:
            Drift trends dictionary
        """
        return self.skg.drift_analyzer.get_drift_statistics()
    
    def shutdown(self):
        """Clean shutdown of SKG bridge."""
        self.skg.shutdown()


if __name__ == "__main__":
    from pathlib import Path
    from datetime import datetime
    import asyncio
    
    print("🧪 SKG Integration Bridge - Self Test")
    print("=" * 60)
    
    # Initialize bridge
    vault_path = Path(__file__).resolve().parents[2]
    bridge = CertificateSKGBridge(vault_path, "test_bridge_worker")
    
    # Test certificate
    test_cert = {
        "dals_serial": "DALSTEST_BRIDGE_001",
        "asset_title": "Bridge Test Certificate",
        "ipfs_hash": "ipfs://QmTestBridge123",
        "stardate": datetime.utcnow().isoformat() + "Z",
        "owner": "Bridge Test Owner",
        "wallet": "0xBRIDGETEST456",
        "chain_id": "Ethereum",
        "ed25519_signature": "c" * 128,
        "verifying_key": "d" * 64
    }
    
    async def run_tests():
        print("\n📝 Test 1: Certificate minting hook...")
        fusion_payload = await bridge.on_certificate_minted(
            test_cert, 
            "VAULT_TXN_BRIDGE_001"
        )
        print(f"   Fusion Payload: {fusion_payload['event_type']}")
        print(f"   SKG TXN: {fusion_payload['skg_transaction_id']}")
        
        print("\n📊 Test 2: Owner portfolio...")
        portfolio = bridge.get_owner_portfolio("0xBRIDGETEST456")
        print(f"   Wallet: {portfolio['wallet_address']}")
        print(f"   Certificates: {portfolio['certificate_count']}")
        print(f"   Avg Drift: {portfolio['drift_analysis']['average_drift']:.4f}")
        
        print("\n📊 Test 3: Chain analytics...")
        chain_analytics = bridge.get_chain_analytics("Ethereum")
        print(f"   Chain: {chain_analytics['chain_id']}")
        print(f"   Certificates: {chain_analytics['certificate_count']}")
        
        print("\n🏥 Test 4: Health metrics...")
        health = bridge.get_skg_health_metrics()
        print(f"   Total Nodes: {health['total_nodes']}")
        print(f"   Health Status: {health['health_status']}")
        print(f"   Knowledge Density: {health['knowledge_density']:.2f}")
        
        print("\n🚨 Test 5: Suspicious certificate detection...")
        suspicious = bridge.detect_suspicious_certificates(threshold=0.5)
        print(f"   Found {len(suspicious)} suspicious certificates")
        
        print("\n🎯 Test 6: Pattern insights...")
        patterns = bridge.get_pattern_insights()
        print(f"   Total Certificates: {patterns['total_certificates_analyzed']}")
        print(f"   Cluster Stats: {patterns['cluster_statistics']}")
        
        print("\n📈 Test 7: Drift trends...")
        trends = bridge.get_drift_trends()
        print(f"   Average Drift: {trends['average_drift']:.4f}")
        print(f"   High Drift Count: {trends['high_drift_count']}")
    
    asyncio.run(run_tests())
    
    bridge.shutdown()
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
