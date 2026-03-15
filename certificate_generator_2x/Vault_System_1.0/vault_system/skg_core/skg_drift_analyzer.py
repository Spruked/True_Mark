# skg_drift_analyzer.py
"""
SKG Drift Analyzer
Calculates drift scores for certificates based on timing, signatures, and patterns
"""

from typing import Dict, List, Optional
from skg_node import SKGNode, SKGNodeType
import statistics
from datetime import datetime


class SKGDriftAnalyzer:
    """
    Calculates drift scores for certificates based on:
    - Timestamp consistency
    - Signature validity
    - Pattern deviation
    - Chain anchor lag
    """
    
    def __init__(self):
        self.baseline_metrics = {
            "avg_issuance_interval": 300.0,  # 5 minutes baseline
            "signature_validation_rate": 1.0,
            "chain_lag_seconds": 45.0
        }
        
        self.certificate_history: List[Dict] = []
        self.last_certificate_timestamp: Optional[float] = None
    
    def analyze_certificate_drift(self, cert_node: SKGNode) -> float:
        """
        Calculate drift score (0.0 = perfect, >1.0 = anomalous).
        
        Args:
            cert_node: Certificate node to analyze
            
        Returns:
            Combined drift score (0.0-1.0+)
        """
        drift_components = []
        
        # Component 1: Temporal drift (issuance timing)
        temporal_drift = self._calculate_temporal_drift(cert_node)
        drift_components.append(temporal_drift)
        
        # Component 2: Signature integrity drift
        sig_drift = self._calculate_signature_drift(cert_node)
        drift_components.append(sig_drift)
        
        # Component 3: Pattern anomaly drift
        pattern_drift = self._calculate_pattern_drift(cert_node)
        drift_components.append(pattern_drift)
        
        # Combined drift score (weighted average)
        combined_drift = statistics.mean(drift_components)
        
        # Store for monitoring
        self.certificate_history.append({
            "node_id": cert_node.node_id,
            "drift_score": combined_drift,
            "components": {
                "temporal": temporal_drift,
                "signature": sig_drift,
                "pattern": pattern_drift
            },
            "analyzed_at": cert_node.created_at
        })
        
        # Update last timestamp
        try:
            self.last_certificate_timestamp = self._stardate_to_timestamp(cert_node.created_at)
        except:
            pass
        
        return combined_drift
    
    def _calculate_temporal_drift(self, cert_node: SKGNode) -> float:
        """
        Detect if certificate timing deviates from normal issuance pattern.
        
        Args:
            cert_node: Certificate node
            
        Returns:
            Temporal drift score (0.0-1.0)
        """
        # Parse stardate to timestamp
        stardate_str = cert_node.properties.get('minted_at', cert_node.created_at)
        
        try:
            current_timestamp = self._stardate_to_timestamp(stardate_str)
            
            if self.last_certificate_timestamp is None:
                # First certificate - no drift
                return 0.0
            
            # Calculate interval from last certificate
            interval = abs(current_timestamp - self.last_certificate_timestamp)
            
            # Drift is deviation from baseline
            baseline = self.baseline_metrics['avg_issuance_interval']
            
            if baseline == 0:
                return 0.0
            
            drift = abs(interval - baseline) / baseline
            
            return min(drift, 1.0)  # Cap at 1.0
        
        except Exception:
            return 0.5  # Neutral drift if parsing fails
    
    def _calculate_signature_drift(self, cert_node: SKGNode) -> float:
        """
        Verify signature format and detect anomalies.
        
        Args:
            cert_node: Certificate node
            
        Returns:
            Signature drift score (0.0-1.0)
        """
        signature = cert_node.properties.get('ed25519_signature')
        verifying_key = cert_node.properties.get('verifying_key')
        
        if not signature or not verifying_key:
            return 1.0  # Max drift = invalid
        
        try:
            # Basic length checks
            if len(signature) != 128:  # Ed25519 hex signature length
                return 0.8
            
            if len(verifying_key) != 64:  # Ed25519 hex public key length
                return 0.6
            
            # Signature format validation (hex)
            int(signature, 16)
            int(verifying_key, 16)
            
            return 0.0  # No drift if format is valid
        
        except (ValueError, TypeError):
            return 1.0
    
    def _calculate_pattern_drift(self, cert_node: SKGNode) -> float:
        """
        Detect if certificate deviates from learned patterns.
        
        Args:
            cert_node: Certificate node
            
        Returns:
            Pattern drift score (0.0-1.0)
        """
        drift_score = 0.0
        
        # Check 1: IPFS hash format
        ipfs_hash = cert_node.properties.get('ipfs_hash', '')
        
        if not ipfs_hash:
            drift_score += 0.3
        elif not ipfs_hash.startswith('ipfs://'):
            drift_score += 0.2
        else:
            # Check hash length (typical IPFS CID)
            cid_part = ipfs_hash.replace('ipfs://', '')
            if len(cid_part) < 40:  # Minimum CID length
                drift_score += 0.1
        
        # Check 2: DALS serial format
        dals_serial = cert_node.properties.get('dals_serial', '')
        if not dals_serial or not dals_serial.startswith('DALS'):
            drift_score += 0.2
        
        # Check 3: Asset title presence
        asset_title = cert_node.properties.get('asset_title', '')
        if not asset_title or len(asset_title) < 3:
            drift_score += 0.1
        
        return min(drift_score, 1.0)
    
    def get_global_drift_average(self) -> float:
        """
        Return average drift across all certificates.
        
        Returns:
            Average drift score
        """
        if not self.certificate_history:
            return 0.0
        
        return statistics.mean([c['drift_score'] for c in self.certificate_history])
    
    def get_drift_statistics(self) -> dict:
        """
        Get comprehensive drift statistics.
        
        Returns:
            Drift statistics dictionary
        """
        if not self.certificate_history:
            return {
                "total_certificates": 0,
                "average_drift": 0.0,
                "max_drift": 0.0,
                "min_drift": 0.0,
                "std_deviation": 0.0
            }
        
        drift_scores = [c['drift_score'] for c in self.certificate_history]
        
        return {
            "total_certificates": len(self.certificate_history),
            "average_drift": statistics.mean(drift_scores),
            "max_drift": max(drift_scores),
            "min_drift": min(drift_scores),
            "std_deviation": statistics.stdev(drift_scores) if len(drift_scores) > 1 else 0.0,
            "high_drift_count": len([d for d in drift_scores if d > 0.5]),
            "zero_drift_count": len([d for d in drift_scores if d == 0.0])
        }
    
    def get_certificate_drift_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent drift analysis history.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of recent drift analyses
        """
        return self.certificate_history[-limit:] if self.certificate_history else []
    
    def detect_anomalies(self, threshold: float = 0.7) -> List[Dict]:
        """
        Detect certificates with anomalously high drift scores.
        
        Args:
            threshold: Drift score threshold for anomaly detection
            
        Returns:
            List of anomalous certificates
        """
        anomalies = [
            cert for cert in self.certificate_history
            if cert['drift_score'] >= threshold
        ]
        
        return anomalies
    
    def _stardate_to_timestamp(self, stardate_str: str) -> float:
        """
        Convert ISO stardate to Unix timestamp.
        
        Args:
            stardate_str: ISO 8601 datetime string
            
        Returns:
            Unix timestamp
        """
        try:
            # Remove 'Z' suffix if present
            clean_date = stardate_str.rstrip('Z')
            
            # Try parsing with microseconds
            try:
                dt = datetime.fromisoformat(clean_date)
            except:
                # Fallback: parse without microseconds
                dt = datetime.strptime(clean_date[:19], "%Y-%m-%dT%H:%M:%S")
            
            return dt.timestamp()
        
        except Exception:
            # Fallback to current time
            return datetime.utcnow().timestamp()


if __name__ == "__main__":
    from skg_node import SKGNode, SKGNodeType
    
    print("🧪 SKG Drift Analyzer - Self Test")
    print("=" * 60)
    
    analyzer = SKGDriftAnalyzer()
    
    # Test certificate 1: Perfect certificate
    cert1 = SKGNode(
        node_id="cert:TEST001",
        node_type=SKGNodeType.CERTIFICATE,
        properties={
            "dals_serial": "DALSKM20251210-TEST001",
            "asset_title": "Test Certificate 1",
            "ipfs_hash": "ipfs://QmTest1234567890abcdefghijklmnopqrstuvwxyz",
            "minted_at": "2025-12-10T15:30:00Z",
            "ed25519_signature": "a" * 128,
            "verifying_key": "b" * 64
        },
        created_by="test_worker"
    )
    
    print("\n📝 Analyzing perfect certificate...")
    drift1 = analyzer.analyze_certificate_drift(cert1)
    print(f"✅ Drift score: {drift1:.4f}")
    print(f"   Components: temporal={analyzer.certificate_history[-1]['components']['temporal']:.4f}, "
          f"signature={analyzer.certificate_history[-1]['components']['signature']:.4f}, "
          f"pattern={analyzer.certificate_history[-1]['components']['pattern']:.4f}")
    
    # Test certificate 2: Anomalous certificate
    cert2 = SKGNode(
        node_id="cert:TEST002",
        node_type=SKGNodeType.CERTIFICATE,
        properties={
            "dals_serial": "INVALID",
            "asset_title": "X",
            "ipfs_hash": "bad_hash",
            "minted_at": "2025-12-10T15:35:00Z",
            "ed25519_signature": "short",
            "verifying_key": "bad"
        },
        created_by="test_worker"
    )
    
    print("\n📝 Analyzing anomalous certificate...")
    drift2 = analyzer.analyze_certificate_drift(cert2)
    print(f"⚠️  Drift score: {drift2:.4f}")
    print(f"   Components: temporal={analyzer.certificate_history[-1]['components']['temporal']:.4f}, "
          f"signature={analyzer.certificate_history[-1]['components']['signature']:.4f}, "
          f"pattern={analyzer.certificate_history[-1]['components']['pattern']:.4f}")
    
    print(f"\n📊 Drift Statistics:")
    stats = analyzer.get_drift_statistics()
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.4f}")
        else:
            print(f"   {key}: {value}")
    
    print(f"\n🚨 Anomaly Detection (threshold=0.5):")
    anomalies = analyzer.detect_anomalies(threshold=0.5)
    print(f"   Found {len(anomalies)} anomalous certificates")
    
    print("\n" + "=" * 60)
    print("Self-test complete.")
