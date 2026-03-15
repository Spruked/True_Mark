"""
Local knowledge base for the public TrueMark assistant.
"""

NFT_TYPES = {
    "K-NFT": "Knowledge NFTs for research, methods, proofs, and intellectual property records.",
    "H-NFT": "Heirloom NFTs for family, lineage, memory, and intergenerational preservation.",
    "L-NFT": "Legacy NFTs for institutional frameworks, operational systems, and governance records.",
    "C-NFT": "Custom NFTs for specialized certification and tailored issuance workflows.",
}

COMMON_TOPICS = {
    "encryption": "TrueMark can encrypt storage-bound artifacts with ChaCha20-Poly1305 before durable storage.",
    "certificate": "Certificates combine a printable forensic PDF with cryptographic signatures and audit traces.",
    "verification": "Verification relies on serial lookup, vault records, signature checks, and QR-linked evidence.",
}
