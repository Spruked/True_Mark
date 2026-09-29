"""Governed certificate frame registry.

Frames are presentation templates only. They do not alter the certificate's
evidence-layer profile, cryptographic payload, or Vault authority.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


FRAME_GROUPS = {
    "classic_forensic": "Classic Government / Forensic",
    "modern_tech": "Modern / Tech",
    "ornamental": "Ornamental / Decorative",
    "heavy_elite": "Heavy / Elite",
    "ultra_minimal": "Ultra-Minimal / Clean",
}

CERTIFICATE_TYPES = [
    "certificate-of-authentication", "certificate-of-ownership",
    "digital-asset-certificate", "blockchain-provenance-certificate",
    "diploma", "degree-certificate", "training-certificate",
    "professional-certification", "mastery-certificate",
    "birth-certificate", "marriage-certificate", "court-issued-certificate",
    "notarized-certificate", "compliance-certificate",
    "software-license-certificate", "device-serial-certificate",
    "cryptographic-certificate", "nft-certificate", "provenance-certificate",
    "certificate-of-incorporation", "certificate-of-good-standing",
    "product-certificate-of-authenticity", "award-certificate",
    "membership-certificate", "forensic-certificate",
    "chain-of-custody-certificate", "audit-certificate",
    "verification-certificate",
]


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


_NAMES = [
    ("classic_forensic", "Engraved Single-Line"),
    ("classic_forensic", "Engraved Double-Line"),
    ("classic_forensic", "Heavy Treasury Border"),
    ("classic_forensic", "Micro-Engraved Pattern"),
    ("classic_forensic", "Triple-Layer Forensic Border"),
    ("classic_forensic", "Archival Document Border"),
    ("classic_forensic", "Antiquarian Scroll Border"),
    ("classic_forensic", "Diplomatic Border"),
    ("classic_forensic", "Federal-Style Block Border"),
    ("classic_forensic", "Ornate Corner Flourish"),
    ("modern_tech", "Minimal Tech Border"),
    ("modern_tech", "Thin-Line Precision Border"),
    ("modern_tech", "Geometric Lattice"),
    ("modern_tech", "Circuit-Style Border"),
    ("modern_tech", "Hex-Grid Border"),
    ("modern_tech", "Matrix-Style Border"),
    ("modern_tech", "Precision Dot-Grid"),
    ("modern_tech", "Angular Tech Frame"),
    ("modern_tech", "Minimal Double-Tech"),
    ("modern_tech", "ORB-Style Glyph Border"),
    ("ornamental", "Floral Corners"),
    ("ornamental", "Victorian Border"),
    ("ornamental", "Scrollwork Border"),
    ("ornamental", "Art Deco Border"),
    ("ornamental", "Filigree Border"),
    ("ornamental", "Royal Crest Border"),
    ("ornamental", "Laurel Border"),
    ("ornamental", "Ribbon Border"),
    ("ornamental", "Crest-Corner Border"),
    ("ornamental", "Decorative Diamond Border"),
    ("heavy_elite", "Heavy Double-Frame"),
    ("heavy_elite", "Thick Engraved Border"),
    ("heavy_elite", "Institutional Border"),
    ("heavy_elite", "Gothic Border"),
    ("heavy_elite", "Royal Heavy Border"),
    ("heavy_elite", "Elite Crest Border"),
    ("heavy_elite", "Heavy Ribbon Border"),
    ("heavy_elite", "Thick Lattice Border"),
    ("heavy_elite", "Heavy Diamond Border"),
    ("heavy_elite", "Elite Micro-Engraved Border"),
    ("ultra_minimal", "Ultra-Thin Border"),
    ("ultra_minimal", "Minimal Corners"),
    ("ultra_minimal", "Dot-Corner Border"),
    ("ultra_minimal", "Line-Break Border"),
    ("ultra_minimal", "Soft-Corner Border"),
    ("ultra_minimal", "Thin Double-Line"),
    ("ultra_minimal", "Minimal Box"),
    ("ultra_minimal", "Light Grid"),
    ("ultra_minimal", "Soft Lattice"),
    ("ultra_minimal", "Minimal Glyph Border"),
]


FRAME_CATALOG: List[Dict[str, object]] = []
for index, (group, name) in enumerate(_NAMES, start=1):
    FRAME_CATALOG.append({
        "frame_id": f"frame-{index:02d}-{_slug(name)}",
        "name": name,
        "number": index,
        "group": group,
        "group_label": FRAME_GROUPS[group],
        "format": "US Letter portrait / 8.5 x 11 in",
        "asset": f"frames/frame-{index:02d}-{_slug(name)}.svg",
        "presentation_only": True,
        "recommended_certificate_types": (
            ["forensic-certificate", "chain-of-custody-certificate", "audit-certificate"]
            if group in {"classic_forensic", "heavy_elite"}
            else ["certificate-of-authentication", "provenance-certificate", "verification-certificate"]
        ),
    })

DEFAULT_FRAME_ID = FRAME_CATALOG[0]["frame_id"]


def list_frames(group: str | None = None) -> List[Dict[str, object]]:
    """Return the selectable frame catalog, optionally filtered by group."""
    if group is None:
        return [dict(frame) for frame in FRAME_CATALOG]
    return [dict(frame) for frame in FRAME_CATALOG if frame["group"] == group]


def get_frame(frame_id: str | None = None) -> Dict[str, object]:
    """Resolve a frame ID, defaulting to the first governed frame."""
    requested = frame_id or DEFAULT_FRAME_ID
    for frame in FRAME_CATALOG:
        if frame["frame_id"] == requested:
            return dict(frame)
    valid = ", ".join(str(frame["frame_id"]) for frame in FRAME_CATALOG)
    raise ValueError(f"Unknown certificate frame '{requested}'. Valid frames: {valid}")


def get_frame_asset_path(template_root: Path, frame_id: str | None = None) -> Path:
    """Return the SVG asset path for a governed frame."""
    frame = get_frame(frame_id)
    return template_root / str(frame["asset"])
