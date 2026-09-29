"""Generate clearly marked, non-authoritative certificate presentation examples."""

from __future__ import annotations

import asyncio
import hashlib
import sys
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = FORGE_ROOT.parents[2]
ISS_ROOT = REPOSITORY_ROOT / "ISS_Module"
sys.path.insert(0, str(FORGE_ROOT))
sys.path.insert(0, str(ISS_ROOT))

from forensic_renderer import ForensicCertificateRenderer
from iss_module.core.utils import canonical_timestamp


# Examples belong in the Vault's non-authoritative examples area, never in
# source folders or the issued-certificate authority path.
OUTPUT_ROOT = REPOSITORY_ROOT / "True_Mark_Vault_System" / "examples" / "certificates"
OFFICER = "Bryan A Spruk, President and CEO, Pro Prime Series"
OWNER = "Bryan A Spruk"


def sample_payload(nft_type: str, layers: int, sequence: int, frame_id: str, watermark_variant: str) -> dict:
    serial = f"TM-DEMO-{nft_type}-{layers}L-2026-{sequence:05d}-X"
    timestamp = canonical_timestamp(source="True Mark demonstration generator")
    payload_hash = hashlib.sha256(f"{serial}:demonstration-only".encode()).hexdigest()
    return {
        "demonstration": True,
        "certificate_number": serial,
        "owner": OWNER,
        "wallet": "0xDEMO000000000000000000000000000000000000",
        "ipfs_hash": "ipfs://DEMONSTRATION-NOT-AN-ISSUED-RECORD",
        "asset_title": f"Pro Prime Series {nft_type} Demonstration Certificate",
        "kep_category": {
            "K": "Knowledge",
            "HL": "Licensable Heirloom",
            "L": "Legacy",
            "B": "Bespoke",
        }[nft_type],
        "chain_id": "Polygon (demonstration only)",
        "nft_type": nft_type,
        "nft_backed": True,
        "layer_count": layers,
        "frame_id": frame_id,
        "watermark_variant": watermark_variant,
        "officer": OFFICER,
        "payload_hash": payload_hash,
        "manifest_hash": hashlib.sha256(f"manifest:{serial}".encode()).hexdigest(),
        "sig_id": f"DEMO-SIG-{nft_type}-{layers}",
        "ed25519_signature": "DEMONSTRATION-SIGNATURE-NOT-VALID-FOR-VERIFICATION",
        "verification_status": "DEMONSTRATION — NOT ISSUED",
        "iss_time_ns": timestamp["iss_time_ns"],
        "iss_timestamp": timestamp["iss_timestamp"],
        "iss_standard_timestamp": timestamp["standard_timestamp"],
        "stardate": timestamp["stardate"],
    }


async def main() -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    renderer = ForensicCertificateRenderer()
    examples = (
        ("K", 7, 1, "frame-01-engraved-single-line", "signature"),
        ("K", 13, 1, "frame-24-art-deco-border", "signature"),
        ("HL", 7, 1, "frame-01-engraved-single-line", "signature"),
        ("HL", 13, 1, "frame-24-art-deco-border", "signature"),
        # Alternate color families and presentation treatments. Their unique
        # sequence numbers preserve all prior examples.
        ("L", 7, 2, "frame-22-victorian-border", "compact"),
        ("B", 13, 3, "frame-15-hex-grid-border", "signature"),
    )
    for nft_type, layers, sequence, frame_id, watermark_variant in examples:
        payload = sample_payload(nft_type, layers, sequence, frame_id, watermark_variant)
        existing_pdf = OUTPUT_ROOT / f"{payload['certificate_number']}_DEMONSTRATION.pdf"
        if existing_pdf.exists() and sequence == 1:
            print(f"Preserved existing {payload['certificate_number']}")
            continue
        await renderer.create_forensic_pdf(payload, OUTPUT_ROOT)
        print(f"Created {payload['certificate_number']}")


if __name__ == "__main__":
    asyncio.run(main())
