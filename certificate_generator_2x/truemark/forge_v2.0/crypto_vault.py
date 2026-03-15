"""
ChaCha20-Poly1305 encryption helpers for storage-bound artifacts.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305


class ChaChaVault:
    """
    Encrypt data before it touches durable storage.
    """

    algorithm = "ChaCha20-Poly1305"

    def __init__(self, key: Optional[bytes] = None):
        self.key = key or ChaCha20Poly1305.generate_key()
        self.cipher = ChaCha20Poly1305(self.key)

    def encrypt_before_storage(
        self, plaintext: bytes, associated_data: Optional[bytes] = None
    ) -> Dict[str, Optional[str]]:
        """Encrypt binary data for off-chain storage."""
        nonce = os.urandom(12)
        ciphertext = self.cipher.encrypt(nonce, plaintext, associated_data)
        return {
            "ciphertext": ciphertext.hex(),
            "nonce": nonce.hex(),
            "aad": associated_data.hex() if associated_data else None,
            "algorithm": self.algorithm,
        }

    def decrypt_after_retrieval(self, encrypted_pkg: Dict[str, Optional[str]]) -> bytes:
        """Decrypt a previously encrypted package."""
        nonce = bytes.fromhex(encrypted_pkg["nonce"])
        ciphertext = bytes.fromhex(encrypted_pkg["ciphertext"])
        aad = bytes.fromhex(encrypted_pkg["aad"]) if encrypted_pkg.get("aad") else None
        return self.cipher.decrypt(nonce, ciphertext, aad)

    def export_key_hex(self) -> str:
        """Expose the active key in hex form for controlled handoff."""
        return self.key.hex()

    @classmethod
    def from_key_hex(cls, key_hex: str) -> "ChaChaVault":
        """Rebuild a vault instance from a persisted hex key."""
        return cls(bytes.fromhex(key_hex))

    def encrypt_file_to_json(
        self,
        source_path: Path,
        destination_path: Path,
        associated_data: Optional[bytes] = None,
    ) -> Path:
        """Encrypt a file and persist the package as JSON."""
        destination_path.parent.mkdir(parents=True, exist_ok=True)
        package = self.encrypt_before_storage(source_path.read_bytes(), associated_data)
        with open(destination_path, "w", encoding="utf-8") as handle:
            json.dump(package, handle, indent=2)
        return destination_path
