"""
Local knowledge base for the public TrueMark assistant.
"""

NFT_TYPES = {
    "H": "Heirloom NFTs for family, lineage, memory, and intergenerational preservation.",
    "K": "Knowledge NFTs for research, methods, proofs, and intellectual property records.",
    "L": "Legacy NFTs for institutional frameworks, operational systems, and governance records.",
    "B": "Bespoke NFTs for specialized True Mark object and certificate workflows.",
    "HL": "Licensable Heirloom NFTs; HL keeps the H color family and adds licensing.",
    "KL": "Licensable Knowledge NFTs; KL keeps the K color family and adds licensing.",
    "LL": "Licensable Legacy NFTs; LL keeps the L color family and adds licensing.",
    "BL": "Licensable Bespoke NFTs; BL keeps the B color family and adds licensing.",
    "C": "Custom Contract NFTs for specialized contract-based issuance workflows.",
}

COMMON_TOPICS = {
    "encryption": "TrueMark can encrypt storage-bound artifacts with ChaCha20-Poly1305 before durable storage.",
    "certificate": "Certificates combine a printable forensic PDF with cryptographic signatures and audit traces.",
    "verification": "Verification relies on serial lookup, vault records, signature checks, and QR-linked evidence.",
}
