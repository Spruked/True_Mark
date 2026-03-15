"""
Simple guidance layer for encryption-related assistant prompts.
"""

from __future__ import annotations

from typing import Dict


class EncryptionAdvisor:
    """Answer common encryption workflow questions."""

    def get_guidance(self) -> Dict[str, str]:
        return {
            "algorithm": "ChaCha20-Poly1305",
            "when_to_encrypt": "Encrypt artifacts before IPFS, Arweave, or any other persistent storage handoff.",
            "key_handling": "Store encryption keys separately from certificate payloads and never embed raw keys in public metadata.",
            "associated_data": "Use serial numbers and asset identifiers as associated data so tampering breaks decryption.",
        }
