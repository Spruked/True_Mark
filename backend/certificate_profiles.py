"""Governed True Mark certificate profiles.

The layer count is part of the certificate authority model. Render choices are
deliberately kept out of this module so visual presentation cannot change the
evidence represented by a certificate.
"""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from typing import Any, Dict


CERTIFICATE_LAYERS = (
    "identity",
    "issuance",
    "source_integrity",
    "metadata_integrity",
    "creator_authentication",
    "timestamp_proof",
    "provenance",
    "ownership_chain",
    "issuer_signature",
    "anchor_receipt",
    "verification_reference",
    "custody_record",
    "audit_record",
)


CERTIFICATE_PROFILE_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "p2": {
        "name": "2-Layer Certificate",
        "layers": 2,
        "description": "Identity and issuance proof for essential records.",
    },
    "p3": {
        "name": "3-Layer Certificate",
        "layers": 3,
        "description": "Adds source integrity to identity and issuance proof.",
    },
    "p5": {
        "name": "5-Layer Certificate",
        "layers": 5,
        "description": "Adds metadata integrity and creator authentication.",
    },
    "p7": {
        "name": "7-Layer Certificate",
        "layers": 7,
        "description": "Adds timestamp proof and provenance evidence.",
    },
    "p11": {
        "name": "11-Layer Forensic Certificate",
        "layers": 11,
        "description": "Near-complete forensic evidence for high-assurance records.",
    },
    "p13": {
        "name": "13-Layer Elite Forensic Certificate",
        "layers": 13,
        "description": "The complete governed True Mark forensic certificate.",
    },
}


def default_certificate_profiles() -> Dict[str, Dict[str, Any]]:
    """Return a deep copy safe for pricing/config mutation."""
    profiles = deepcopy(CERTIFICATE_PROFILE_DEFINITIONS)
    for profile in profiles.values():
        profile["layer_inventory"] = list(CERTIFICATE_LAYERS[: profile["layers"]])
    return profiles


def get_certificate_profile(profile_id: str) -> Dict[str, Any]:
    profile = CERTIFICATE_PROFILE_DEFINITIONS.get(profile_id)
    if not profile:
        allowed = ", ".join(CERTIFICATE_PROFILE_DEFINITIONS)
        raise ValueError(f"Certificate profile {profile_id!r} is not available. Choose one of: {allowed}.")

    result = deepcopy(profile)
    result["layer_inventory"] = list(CERTIFICATE_LAYERS[: result["layers"]])
    return result


def build_certificate_manifest(profile_id: str, facts: Dict[str, Any]) -> Dict[str, Any]:
    """Build the canonical, render-independent certificate manifest."""
    profile = get_certificate_profile(profile_id)
    return {
        "manifest_version": "1.0",
        "certificate_profile": profile_id,
        "certificate_name": profile["name"],
        "layer_count": profile["layers"],
        "layer_inventory": profile["layer_inventory"],
        "facts": deepcopy(facts),
    }


def manifest_hash(manifest: Dict[str, Any]) -> str:
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
