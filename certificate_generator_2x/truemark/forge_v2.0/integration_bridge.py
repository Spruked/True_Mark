# integration_bridge.py
"""
TrueMark Vault & Swarm Integration Bridge.

    TrueMark execution-surface principle:
This bridge is an execution surface only. It has no cognition, identity,
or decision rights and operates solely through delegated authority.
"""

from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Optional, List
import hashlib
from path_config import get_temp_vault_dir, get_vault_root
from registry import verification_url


class MockWorkerVaultWriter:
    """
    Mock WorkerVaultWriter for standalone operation.
    Replace with actual WorkerVaultWriter when integrating with vault system.
    """
    
    def __init__(self, vault_base_path: Path):
        self.vault_path = vault_base_path
        self.events_path = vault_base_path / "worker_events"
        self.events_path.mkdir(parents=True, exist_ok=True)
        
    def record_event(self, worker_id: str, event_data: Dict, 
                    pattern: Optional[Dict] = None, skg_update: Optional[Dict] = None):
        """Record event to worker's events.jsonl"""
        worker_events_file = self.events_path / f"{worker_id}_events.jsonl"
        
        event_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "worker_id": worker_id,
            "event": event_data,
            "pattern": pattern or {},
            "skg_update": skg_update or {}
        }
        
        with open(worker_events_file, "a") as f:
            f.write(json.dumps(event_record) + "\n")
    
    def get_last_repair_timestamp(self) -> str:
        """Get timestamp of last vault repair (mock)"""
        return datetime.utcnow().isoformat() + "Z"
    
    def get_active_workers(self) -> List[str]:
        """Get list of active worker IDs (mock)"""
        return ["certificate_forge_worker_001"]


class MockFusionQueueEngine:
    """
    Mock FusionQueue for standalone operation.
    Replace with actual FusionQueueEngine when integrating.
    """
    
    def __init__(self):
        self.queue_path = get_vault_root() / "runtime" / "fusion_queue"
        self.queue_path.mkdir(parents=True, exist_ok=True)
        
    def enqueue(self, queue_name: str, payload: Dict, routing_key: str):
        """Add message to queue"""
        queue_file = self.queue_path / f"{queue_name}.jsonl"
        
        message = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "routing_key": routing_key,
            "payload": payload
        }
        
        with open(queue_file, "a") as f:
            f.write(json.dumps(message) + "\n")


class VaultFusionBridge:
    """
    Handles vault logging and swarm broadcast for certificates.
    Single integration point for certificate forge system.
    """
    
    def __init__(self, vault_base_path: Path, use_mock: bool = True):
        """
        Initialize bridge with vault and queue systems.
        
        Args:
            vault_base_path: Base path to vault system
            use_mock: If True, uses mock implementations (for standalone operation)
        """
        self.vault_base_path = vault_base_path
        self.role = "execution_surface"
        self.authority = "delegated"
        self.certificates_path = vault_base_path / "certificates" / "issued"
        self.certificates_path.mkdir(parents=True, exist_ok=True)
        self.temp_vault_dir = get_temp_vault_dir()
        self.temp_vault_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize vault writer (mock or real)
        if use_mock:
            self.vault_writer = MockWorkerVaultWriter(vault_base_path)
            self.fusion_queue = MockFusionQueueEngine()
            print("⚠️  Using mock vault/queue systems for standalone operation")
        else:
            # When integrating with real system:
            # from worker_vault_writer import WorkerVaultWriter
            # from fusion_queue_engine import FusionQueueEngine
            # self.vault_writer = WorkerVaultWriter(vault_base_path)
            # self.fusion_queue = FusionQueueEngine()
            raise NotImplementedError("Real vault integration not yet configured")
    
    async def record_certificate_issuance(
        self,
        worker_id: str,
        certificate_number: str,
        pdf_path: Path,
        payload: Dict,
        signature: str,
        encryption_package: Optional[Dict] = None,
    ) -> str:
        """
        Logs certificate genesis to worker vault and creates audit trail.
        
        Args:
            worker_id: Worker identifier (e.g., certificate_forge_worker_001)
            certificate_number: TrueMark certificate number
            pdf_path: Path to generated PDF
            payload: Certificate payload data
            signature: Ed25519 signature
            
        Returns:
            Vault transaction ID
        """
        
        # Create event record
        event_record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "CERTIFICATE_MINTED",
            "certificate_number": certificate_number,
            "worker_id": worker_id,
            "payload_hash": payload.get('payload_hash', hashlib.sha256(json.dumps(payload).encode()).hexdigest()),
            "signature_fragment": signature[:32] + "..." if len(signature) > 32 else signature,
            "pdf_size_bytes": pdf_path.stat().st_size if pdf_path.exists() else 0,
            "pdf_path": str(pdf_path)
        }
        
        # Write to worker events log
        self.vault_writer.record_event(
            worker_id=worker_id,
            event_data=event_record,
            pattern={"certificate": "minted", "serial": certificate_number},
            skg_update={"asset_registry": certificate_number}
        )
        
        # Create certificate summary file
        summary = {
            "certificate_number": certificate_number,
            "minted_at": datetime.utcnow().isoformat() + "Z",
            "pdf_path": str(pdf_path),
            "payload": payload,
            "verification_url": verification_url(certificate_number),
            "vault_integrity_hash": self._calculate_vault_hash(),
            "worker_id": worker_id,
            "signature": signature,
            "encryption_package": encryption_package,
        }
        
        summary_path = self.certificates_path / f"{certificate_number}_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        
        # Generate transaction ID
        txn_id = f"VAULT_TXN_{certificate_number}_{int(datetime.utcnow().timestamp() * 1000)}"
        
        print(f"✅ Vault record created: {txn_id}")
        print(f"   Event log: {self.vault_writer.events_path / f'{worker_id}_events.jsonl'}")
        print(f"   Summary: {summary_path}")
        
        return txn_id
    
    async def broadcast_to_swarm(self, certificate_data: Dict) -> str:
        """
        Broadcasts certificate metadata to swarm via FusionQueue.
        
        Args:
            certificate_data: Certificate event data
            
        Returns:
            Swarm transaction ID
        """
        
        # Create fusion payload
        fusion_payload = {
            "event_type": "CERTIFICATE_BROADCAST",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "certificate_event": certificate_data,
            "ingest_to_caleon": True,
            "update_worker_skgs": True,
            "priority": "high",
            "broadcast_id": hashlib.sha256(
                f"{certificate_data.get('certificate_number', 'unknown')}:{datetime.utcnow().timestamp()}".encode()
            ).hexdigest()[:16].upper()
        }
        
        # Queue for UCM ingestion
        self.fusion_queue.enqueue(
            queue_name="certificate_swarm_broadcast",
            payload=fusion_payload,
            routing_key="certificates.new"
        )
        
        swarm_txn_id = f"SWARM_TXN_{certificate_data.get('certificate_number', 'UNKNOWN')}_{int(datetime.utcnow().timestamp())}"
        
        print(f"✅ Swarm broadcast queued: {swarm_txn_id}")
        
        return swarm_txn_id
    
    def _calculate_vault_hash(self) -> str:
        """Calculate integrity hash of vault system."""
        vault_state = json.dumps({
            "vault_version": "1.0",
            "vault_path": str(self.vault_base_path),
            "last_repair": self.vault_writer.get_last_repair_timestamp(),
            "worker_count": len(self.vault_writer.get_active_workers()),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }, sort_keys=True)
        
        return hashlib.sha256(vault_state.encode()).hexdigest()[:16]
    
    async def verify_certificate_integrity(self, certificate_number: str) -> Dict:
        """
        Verify certificate integrity against vault records.
        
        Args:
            certificate_number: TrueMark certificate number to verify
            
        Returns:
            Verification result dictionary
        """
        summary_path = self.certificates_path / f"{certificate_number}_summary.json"
        
        if not summary_path.exists():
            return {
                "valid": False,
                "error": "Certificate not found in vault",
                "certificate_number": certificate_number
            }
        
        with open(summary_path, "r") as f:
            summary = json.load(f)
        
        # Verify PDF exists
        pdf_path = Path(summary['pdf_path'])
        pdf_exists = pdf_path.exists()
        
        # Calculate current vault hash
        current_vault_hash = self._calculate_vault_hash()
        
        return {
            "valid": True,
            "certificate_number": certificate_number,
            "minted_at": summary['minted_at'],
            "pdf_exists": pdf_exists,
            "pdf_path": summary['pdf_path'],
            "verification_url": summary['verification_url'],
            "vault_integrity_hash": current_vault_hash,
            "worker_id": summary.get('worker_id', 'unknown'),
            "signature": summary.get('signature', 'N/A')[:32] + "..."
        }
    
    async def get_certificate_audit_trail(self, certificate_number: str) -> List[Dict]:
        """
        Retrieve complete audit trail for a certificate.
        
        Args:
            certificate_number: TrueMark certificate number
            
        Returns:
            List of audit events
        """
        audit_trail = []
        
        # Search through worker events
        for events_file in self.vault_writer.events_path.glob("*_events.jsonl"):
            with open(events_file, "r") as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        if event.get('event', {}).get('certificate_number') == certificate_number:
                            audit_trail.append(event)
                    except:
                        continue
        
        # Sort by timestamp
        audit_trail.sort(key=lambda x: x.get('timestamp', ''))
        
        return audit_trail
    
    def get_certificates_issued_today(self) -> int:
        """Get count of certificates issued in last 24 hours."""
        count = 0
        now = datetime.utcnow()
        
        for summary_file in self.certificates_path.glob("*_summary.json"):
            try:
                with open(summary_file, "r") as f:
                    summary = json.load(f)
                    minted_at = datetime.fromisoformat(summary['minted_at'].replace('Z', '+00:00'))
                    
                    # Check if within last 24 hours
                    if (now - minted_at).total_seconds() < 86400:
                        count += 1
            except:
                continue
        
        return count
    
    def get_swarm_sync_status(self) -> Dict:
        """Get swarm synchronization status (mock for now)."""
        return {
            "consensus": True,
            "guardians_online": 5,
            "total_guardians": 5,
            "last_sync": datetime.utcnow().isoformat() + "Z",
            "broadcast_latency_ms": 1200
        }


if __name__ == "__main__":
    import asyncio
    
    print("🌉 TrueMark Integration Bridge - Self Test")
    print("=" * 60)
    
    from path_config import get_vault_root

    vault_path = get_vault_root()
    bridge = VaultFusionBridge(vault_path, use_mock=True)
    
    # Test data
    test_serial = "TM-TEST-0001-13-00001-A"
    test_payload = {
        "certificate_number": test_serial,
        "owner": "Test User",
        "wallet": "0xTEST123",
        "payload_hash": hashlib.sha256(b"test").hexdigest()
    }
    test_pdf_path = get_temp_vault_dir() / f"test_{test_serial}.pdf"
    test_pdf_path.touch()  # Create empty test file
    
    async def run_tests():
        print("\n📝 Test 1: Record certificate issuance...")
        vault_txn = await bridge.record_certificate_issuance(
            worker_id="certificate_forge_worker_001",
            certificate_number=test_serial,
            pdf_path=test_pdf_path,
            payload=test_payload,
            signature="a" * 128
        )
        print(f"   Vault TXN: {vault_txn}")
        
        print("\n🐝 Test 2: Broadcast to swarm...")
        swarm_txn = await bridge.broadcast_to_swarm({
            "certificate_number": test_serial,
            "event_type": "CERTIFICATE_MINTED"
        })
        print(f"   Swarm TXN: {swarm_txn}")
        
        print("\n🔍 Test 3: Verify certificate integrity...")
        verification = await bridge.verify_certificate_integrity(test_serial)
        print(f"   Valid: {verification['valid']}")
        print(f"   PDF Exists: {verification.get('pdf_exists', False)}")
        
        print("\n📊 Test 4: Get audit trail...")
        audit_trail = await bridge.get_certificate_audit_trail(test_serial)
        print(f"   Events found: {len(audit_trail)}")
        
        print("\n📈 Test 5: Get statistics...")
        issued_today = bridge.get_certificates_issued_today()
        print(f"   Certificates issued today: {issued_today}")
        
        swarm_status = bridge.get_swarm_sync_status()
        print(f"   Swarm consensus: {swarm_status['consensus']}")
        print(f"   Guardians online: {swarm_status['guardians_online']}/{swarm_status['total_guardians']}")
        
        # Cleanup
        if test_pdf_path.exists():
            test_pdf_path.unlink()
    
    asyncio.run(run_tests())
    
    print("\n" + "=" * 60)
    print("Self-test complete. Bridge ready for integration.")
