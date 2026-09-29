"""Governed TrueMark forensic certificate depth profiles.

Pricing belongs to the product/catalog layer. This module only governs which
forensic evidence-layer counts the certificate engine may render.
"""

from __future__ import annotations

from typing import Dict, List

from forensic_modules import list_forensic_modules


ALLOWED_LAYER_COUNTS = (2, 3, 5, 7, 11, 13)

LAYER_DEFINITIONS = [
    (1, "substrate", "Certificate substrate and base field"),
    (2, "content", "Certificate identity and canonical content"),
    (3, "frame", "Selected presentation frame"),
    (4, "watermark", "TrueMark watermark treatment"),
    (5, "timestamp", "Canonical timestamp display"),
    (6, "seal", "Certificate seal"),
    (7, "verification_qr", "Independent verification QR"),
    (8, "signature", "Authorized signature block"),
    (9, "micro_pattern", "Forensic micro-pattern"),
    (10, "micro_noise", "Forensic microtexture"),
    (11, "manifest", "Canonical certificate manifest"),
    (12, "cryptographic_metadata", "Cryptographic metadata and signature anchor"),
    (13, "verification_block", "Independent verification evidence block"),
]


def validate_layer_count(layer_count: int) -> int:
    """Validate and return an approved forensic depth."""
    try:
        value = int(layer_count)
    except (TypeError, ValueError) as error:
        raise ValueError(f"Certificate layer count must be one of {ALLOWED_LAYER_COUNTS}.") from error
    if value not in ALLOWED_LAYER_COUNTS:
        raise ValueError(
            f"Unsupported certificate layer count {value}. "
            f"Only {ALLOWED_LAYER_COUNTS} are governed profiles."
        )
    return value


def get_layer_profile(layer_count: int = 13) -> Dict[str, object]:
    """Return a stable, serializable profile for an approved depth."""
    count = validate_layer_count(layer_count)
    layers: List[Dict[str, object]] = [
        {"number": number, "id": layer_id, "name": name}
        for number, layer_id, name in LAYER_DEFINITIONS[:count]
    ]
    labels = {
        2: "2-Layer Certificate",
        3: "3-Layer Certificate",
        5: "5-Layer Certificate",
        7: "7-Layer Certificate",
        11: "11-Layer Forensic Certificate",
        13: "13-Layer Elite Forensic Certificate",
    }
    return {
        "layer_count": count,
        "label": labels[count],
        "layers": layers,
        "forensic_modules": list_forensic_modules(count),
        "pricing": None,
        "pricing_status": "not established",
    }


def list_layer_profiles() -> List[Dict[str, object]]:
    """Return all customer-selectable profiles in governed order."""
    return [get_layer_profile(count) for count in ALLOWED_LAYER_COUNTS]
