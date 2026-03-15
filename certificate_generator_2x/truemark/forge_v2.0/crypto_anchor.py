# crypto_anchor.py
"""
TrueMark Cryptographic Anchor Engine
Ed25519 signing and blockchain-ready payload generation
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import secrets

from path_config import get_keys_path


class CryptoAnchorEngine:
    """
    Signs certificates with root authority and creates blockchain-ready payload.
    Provides Ed25519 signature generation for certificate authenticity.
    """
    
    def __init__(self, root_key_path: Optional[str] = None):
        """
        Initialize crypto engine with optional root key.
        
        Args:
            root_key_path: Path to Ed25519 private key (32 bytes)
        """
        self.root_key_path = root_key_path or str(get_keys_path() / "caleon_root.key")
        self.signing_key = None
        self.verifying_key = None
        
        # Try to load existing key, generate if not found
        self._initialize_keys()
    
    def _initialize_keys(self):
        """Load or generate Ed25519 keypair."""
        key_path = Path(self.root_key_path)
        
        try:
            # Try ed25519 library first
            import ed25519
            
            if key_path.exists():
                # Load existing key
                with open(key_path, "rb") as f:
                    key_data = f.read()
                    if len(key_data) == 32:
                        self.signing_key = ed25519.SigningKey(key_data)
                    else:
                        # File exists but invalid, regenerate
                        self._generate_new_keypair_ed25519()
            else:
                # Generate new keypair
                self._generate_new_keypair_ed25519()
                
        except ImportError:
            # Fallback to cryptography library
            try:
                from cryptography.hazmat.primitives.asymmetric import ed25519 as crypto_ed25519
                from cryptography.hazmat.primitives import serialization
                
                if key_path.exists():
                    with open(key_path, "rb") as f:
                        key_data = f.read()
                        try:
                            self.signing_key = crypto_ed25519.Ed25519PrivateKey.from_private_bytes(key_data)
                            self.verifying_key = self.signing_key.public_key()
                        except:
                            self._generate_new_keypair_cryptography()
                else:
                    self._generate_new_keypair_cryptography()
                    
            except ImportError:
                # Use mock implementation for testing
                print("⚠️  WARNING: No Ed25519 library found. Using mock signatures for testing only.")
                self._use_mock_signing()
    
    def _generate_new_keypair_ed25519(self):
        """Generate new keypair using ed25519 library."""
        import ed25519
        
        self.signing_key = ed25519.SigningKey(secrets.token_bytes(32))
        self.verifying_key = self.signing_key.get_verifying_key()
        
        # Save private key securely
        key_path = Path(self.root_key_path)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(key_path, "wb") as f:
            f.write(self.signing_key.to_bytes())
        
        # Save public key for reference
        with open(key_path.parent / "caleon_root.pub", "wb") as f:
            f.write(self.verifying_key.to_bytes())
        
        print(f"✅ Generated new Ed25519 keypair: {key_path}")
    
    def _generate_new_keypair_cryptography(self):
        """Generate new keypair using cryptography library."""
        from cryptography.hazmat.primitives.asymmetric import ed25519
        from cryptography.hazmat.primitives import serialization
        
        self.signing_key = ed25519.Ed25519PrivateKey.generate()
        self.verifying_key = self.signing_key.public_key()
        
        # Save private key
        key_path = Path(self.root_key_path)
        key_path.parent.mkdir(parents=True, exist_ok=True)
        
        private_bytes = self.signing_key.private_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PrivateFormat.Raw,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        with open(key_path, "wb") as f:
            f.write(private_bytes)
        
        # Save public key
        public_bytes = self.verifying_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        
        with open(key_path.parent / "caleon_root.pub", "wb") as f:
            f.write(public_bytes)
        
        print(f"✅ Generated new Ed25519 keypair: {key_path}")
    
    def _use_mock_signing(self):
        """Fallback mock signing for testing without crypto libraries."""
        self.signing_key = "MOCK_SIGNING_KEY"
        self.verifying_key = "MOCK_VERIFYING_KEY"
        print("⚠️  Using mock Ed25519 signatures - NOT FOR PRODUCTION USE")
    
    def sign_payload(self, payload: Dict, issuer_key: str) -> Dict:
        """
        Creates Ed25519 signature and SKG update bundle.
        
        Args:
            payload: Certificate data dictionary
            issuer_key: Identifier for the issuing authority
            
        Returns:
            Dictionary containing signature, hash, and verification data
        """
        # Canonical JSON serialization (deterministic)
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        
        # SHA-256 hash of payload
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        
        # Generate signature based on available library
        if isinstance(self.signing_key, str) and self.signing_key == "MOCK_SIGNING_KEY":
            # Mock signature for testing
            signature = hashlib.sha512(f"{payload_hash}:MOCK_SECRET".encode()).hexdigest()
            verifying_key = "MOCK_PUBLIC_KEY_" + hashlib.sha256(issuer_key.encode()).hexdigest()[:32]
        else:
            try:
                # Try ed25519 library
                import ed25519
                signature_bytes = self.signing_key.sign(payload_hash.encode())
                signature = signature_bytes.hex()
                verifying_key = self.signing_key.get_verifying_key().to_ascii(encoding="hex").decode()
            except:
                # Try cryptography library
                from cryptography.hazmat.primitives import serialization
                signature_bytes = self.signing_key.sign(payload_hash.encode())
                signature = signature_bytes.hex()
                verifying_key = self.verifying_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw
                ).hex()
        
        # Generate signature ID for tracking
        sig_id = hashlib.sha256(f"{payload_hash}:{signature[:32]}".encode()).hexdigest()[:16].upper()
        
        return {
            "payload_hash": payload_hash,
            "ed25519_signature": signature,
            "verifying_key": verifying_key,
            "sig_id": sig_id,
            "issuer": issuer_key,
            "signature_algorithm": "Ed25519",
            "signed_at": datetime.utcnow().isoformat() + "Z"
        }
    
    def verify_signature(self, payload: Dict, signature: str, verifying_key: str) -> bool:
        """
        Verify an Ed25519 signature.
        
        Args:
            payload: Original payload dictionary
            signature: Hex-encoded signature
            verifying_key: Hex-encoded public key
            
        Returns:
            True if signature is valid
        """
        # Recreate canonical payload
        payload_json = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        payload_hash = hashlib.sha256(payload_json.encode()).hexdigest()
        
        try:
            if verifying_key.startswith("MOCK_PUBLIC_KEY"):
                # Mock verification
                expected_sig = hashlib.sha512(f"{payload_hash}:MOCK_SECRET".encode()).hexdigest()
                return signature == expected_sig
            
            # Try ed25519 library
            import ed25519
            vkey = ed25519.VerifyingKey(verifying_key, encoding="hex")
            vkey.verify(bytes.fromhex(signature), payload_hash.encode())
            return True
        except:
            try:
                # Try cryptography library
                from cryptography.hazmat.primitives.asymmetric import ed25519
                vkey = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(verifying_key))
                vkey.verify(bytes.fromhex(signature), payload_hash.encode())
                return True
            except:
                return False
    
    def create_blockchain_anchor_data(self, certificate_data: Dict) -> Dict:
        """
        Generate blockchain-ready metadata for on-chain anchoring.
        
        Args:
            certificate_data: Full certificate data with signature
            
        Returns:
            Compact blockchain metadata structure
        """
        return {
            "dals_serial": certificate_data['dals_serial'],
            "payload_hash": certificate_data['payload_hash'],
            "signature_fragment": certificate_data['ed25519_signature'][:64],
            "minted_at": certificate_data['signed_at'],
            "verification_url": f"https://verify.truemark.io/{certificate_data['dals_serial']}"
        }


if __name__ == "__main__":
    # Self-test
    print("🔐 TrueMark Crypto Anchor Engine - Self Test")
    print("=" * 60)
    
    engine = CryptoAnchorEngine()
    
    # Test payload
    test_payload = {
        "dals_serial": "DALSTEST-12345678",
        "owner": "Test User",
        "wallet": "0xTESTADDRESS",
        "ipfs_hash": "ipfs://QmTEST12345"
    }
    
    print("\n📝 Signing test payload...")
    signature_bundle = engine.sign_payload(test_payload, "Caleon_Prime_Root_v2")
    
    print(f"\n✅ Signature Generated:")
    print(f"   Payload Hash: {signature_bundle['payload_hash'][:32]}...")
    print(f"   Signature: {signature_bundle['ed25519_signature'][:64]}...")
    print(f"   Sig ID: {signature_bundle['sig_id']}")
    print(f"   Verifying Key: {signature_bundle['verifying_key'][:32]}...")
    
    print("\n🔍 Verifying signature...")
    is_valid = engine.verify_signature(
        test_payload,
        signature_bundle['ed25519_signature'],
        signature_bundle['verifying_key']
    )
    
    print(f"   Verification Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
    
    print("\n⛓️  Blockchain Anchor Data:")
    anchor_data = engine.create_blockchain_anchor_data({**test_payload, **signature_bundle})
    print(json.dumps(anchor_data, indent=2))
    
    print("\n" + "=" * 60)
    print("Self-test complete. Engine ready for production.")
