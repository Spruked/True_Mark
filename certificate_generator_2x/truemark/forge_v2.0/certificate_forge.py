"""
TrueMark Enterprise Certificate Forge v2.0
Main orchestrator for certificate minting, storage protection, and vault logging.
"""

from pathlib import Path
from datetime import datetime
import argparse
import asyncio
import hashlib
import json
import mimetypes
import sys
import uuid
from typing import Dict, Optional
from layer_profiles import ALLOWED_LAYER_COUNTS, get_layer_profile
from registry import verification_url as registry_verification_url

try:
    from forensic_renderer import ForensicCertificateRenderer, NFT_COLOR_PROFILES
    from crypto_anchor import CryptoAnchorEngine
    from integration_bridge import VaultFusionBridge
    from crypto_vault import ChaChaVault
    from path_config import get_vault_root
except ImportError as error:
    print(f"❌ Import error: {error}")
    sys.exit(1)


SKG_AVAILABLE = False
CertificateSKGBridge = None

ISS_AVAILABLE = False
try:
    iss_root = Path(__file__).resolve().parents[3] / "ISS_Module"
    sys.path.insert(0, str(iss_root))
    from iss_module.core.utils import current_timecodes, format_iss_time, get_iss_time_ns
    ISS_AVAILABLE = True
except ImportError:
    current_timecodes = None
    format_iss_time = None
    get_iss_time_ns = None

try:
    from pathlib import Path as _Path

    skg_path = _Path(__file__).resolve().parents[3] / "True_Mark_Vault_System" / "vault_system" / "skg_core"
    sys.path.insert(0, str(skg_path))
    from skg_integration import CertificateSKGBridge  # type: ignore

    SKG_AVAILABLE = True
except ImportError:
    print("⚠️  SKG not available - running without knowledge graph integration")


class TrueMarkForge:
    """
    Coordinates certificate rendering, signing, encryption, and vault recording.
    """

    def __init__(self, vault_base_path: Path, use_mock_vault: bool = True):
        self.vault_base_path = vault_base_path
        self.vault = VaultFusionBridge(vault_base_path, use_mock=use_mock_vault)
        self.renderer = ForensicCertificateRenderer()
        self.crypto = CryptoAnchorEngine()
        self.skg_bridge = None

        if SKG_AVAILABLE and CertificateSKGBridge is not None:
            try:
                self.skg_bridge = CertificateSKGBridge(vault_base_path)
                print("🧠 SKG Knowledge Graph: ENABLED")
            except Exception as error:
                print(f"⚠️  SKG initialization failed: {error}")

        print("🔥 TrueMark Certificate Forge v2.0 Initialized")
        print(f"   Vault: {vault_base_path}")
        print(f"   Mode: {'Standalone (Mock)' if use_mock_vault else 'Production'}")
        print()

    async def mint_official_certificate(self, metadata: Dict) -> Dict:
        """
        Generate and record an official certificate package.
        """
        print("⚙️  MINTING CERTIFICATE")
        print("=" * 70)

        print("1️⃣  Generating TrueMark certificate number...")
        certificate_number = self._generate_certificate_number()
        print(f"    ✅ Certificate number: {certificate_number}")

        print("2️⃣  Creating cryptographic payload...")
        layer_count = get_layer_profile(metadata.get("layer_count", 13))["layer_count"]
        private_security_manifest = {
            "layer_count": layer_count,
            "module_ids": [
                module["module_id"]
                for module in get_layer_profile(layer_count)["forensic_modules"]
            ],
            "frame_id": metadata.get("frame_id"),
        }
        security_manifest_hash = hashlib.sha256(
            json.dumps(private_security_manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        payload = {
            "certificate_number": certificate_number,
            "owner": metadata["owner_name"],
            "wallet": metadata["wallet_address"],
            "ipfs_hash": metadata["ipfs_hash"],
            **self._iss_evidence(),
            "kep_category": metadata.get("kep_category", "Knowledge"),
            "nft_type": metadata.get("nft_type"),
            "chain_id": metadata.get("chain_id", "Polygon"),
            "asset_title": metadata["asset_title"],
            "security_profile": f"TM-FSP-{layer_count}",
            "security_profile_version": "1.0",
            "security_manifest_hash": security_manifest_hash,
            "renderer_version": "TM-CERT-RENDERER-2.1",
            "nft_backed": bool(metadata.get("nft_backed")),
            "nft_color_profile": (
                NFT_COLOR_PROFILES.get(
                    str(metadata.get("nft_type") or metadata.get("kep_category", "Knowledge")).lower(),
                    NFT_COLOR_PROFILES["knowledge"],
                )["id"]
                if metadata.get("nft_backed")
                else None
            ),
        }
        print(f"    ✅ Payload created ({len(json.dumps(payload))} bytes)")

        print("3️⃣  Signing with Ed25519 root authority...")
        signature_bundle = self.crypto.sign_payload(
            payload=payload,
            issuer_key="Caleon_Prime_Root_v2",
        )
        print(f"    ✅ Signature: {signature_bundle['sig_id']}")
        print(f"    ✅ Hash: {signature_bundle['payload_hash'][:32]}...")

        print("4️⃣  Rendering forensic PDF...")
        pdf_data = {
            **metadata,
            **payload,
            **signature_bundle,
            # Private renderer input; never published as public certificate metadata.
            "layer_count": layer_count,
            "private_security_manifest": private_security_manifest,
        }
        pdf_path = await self.renderer.create_forensic_pdf(
            data=pdf_data,
            output_dir=self.vault.certificates_path,
        )
        print(f"    ✅ PDF: {pdf_path}")
        artifact_paths = dict(self.renderer.last_artifacts)
        nft_metadata_path = None
        if metadata.get("nft_backed"):
            artifact_records = self._describe_artifacts(artifact_paths)
            nft_metadata = {
                "name": metadata["asset_title"],
                "description": "True Mark forensic certificate image.",
                "image": metadata.get("nft_image_uri", "ipfs://PENDING"),
                "external_url": registry_verification_url(certificate_number),
                "attributes": [
                    {"trait_type": "Forensic Security Profile", "value": payload["security_profile"]},
                    {"trait_type": "Security Profile Version", "value": f"{payload['security_profile']}/{payload['security_profile_version']}"},
                    {"trait_type": "Verification Status", "value": "Valid"},
                    {"trait_type": "True Mark Verification ID", "value": certificate_number},
                    {"trait_type": "NFT Color Profile", "value": payload["nft_color_profile"]},
                ],
                "true_mark": {
                    "certificate_hash": signature_bundle["payload_hash"],
                    "security_manifest_hash": payload["security_manifest_hash"],
                    "renderer_version": payload["renderer_version"],
                    "artifacts": artifact_records,
                    "chain_id": metadata.get("chain_id"),
                    "token_id": metadata.get("nft_token_id"),
                },
            }
            nft_metadata["true_mark"]["nft_metadata_hash_scope"] = "canonical metadata excluding nft_metadata_hash fields"
            metadata_hash_input = json.dumps(nft_metadata, sort_keys=True, separators=(",", ":"))
            nft_metadata["true_mark"]["nft_metadata_hash"] = hashlib.sha256(
                metadata_hash_input.encode("utf-8")
            ).hexdigest()
            nft_metadata_path = self.vault.certificates_path / f"{certificate_number}_nft_metadata.json"
            with open(nft_metadata_path, "w", encoding="utf-8") as handle:
                json.dump(nft_metadata, handle, indent=2)
            artifact_paths["nft_metadata"] = nft_metadata_path
            print(f"    ✅ NFT image: {artifact_paths['png']}")
            print(f"    ✅ NFT metadata: {nft_metadata_path}")

        encryption_package = None
        if metadata.get("encrypt_artifacts"):
            print("4.5️⃣ Encrypting PDF for off-chain storage...")
            associated_data = certificate_number.encode("utf-8")
            vault = ChaChaVault()
            encrypted_path = pdf_path.with_suffix(".encrypted.json")
            vault.encrypt_file_to_json(pdf_path, encrypted_path, associated_data=associated_data)
            encryption_package = {
                "encrypted_file": str(encrypted_path),
                "algorithm": vault.algorithm,
                "key_hex": vault.export_key_hex(),
                "associated_data": certificate_number,
            }
            print(f"    ✅ Encrypted package: {encrypted_path}")

        print("5️⃣  Recording to vault...")
        vault_txn = await self.vault.record_certificate_issuance(
            worker_id="certificate_forge_worker_001",
            certificate_number=certificate_number,
            pdf_path=pdf_path,
            payload=payload,
            signature=signature_bundle["ed25519_signature"],
            encryption_package=encryption_package,
        )
        print(f"    ✅ Vault TXN: {vault_txn}")

        skg_payload = None
        if self.skg_bridge:
            print("6️⃣  Updating swarm knowledge graph...")
            try:
                skg_payload = await self.skg_bridge.on_certificate_minted(
                    certificate_data={
                        "certificate_number": certificate_number,
                        "owner_wallet": metadata["wallet_address"],
                        "owner_name": metadata["owner_name"],
                        "ipfs_hash": metadata["ipfs_hash"],
                        "asset_title": metadata["asset_title"],
                        "chain_id": metadata.get("chain_id", "Polygon"),
                        "kep_category": metadata.get("kep_category", "Knowledge"),
                        "signature_id": signature_bundle["sig_id"],
                        "minted_at": datetime.utcnow().isoformat() + "Z",
                    },
                    vault_txn_id=vault_txn,
                )
                print(f"    ✅ SKG TXN: {skg_payload['skg_transaction_id']}")
            except Exception as error:
                print(f"    ⚠️  SKG update failed: {error}")

        print("7️⃣  Broadcasting to swarm...")
        swarm_payload = {
            "certificate_number": certificate_number,
            "event_type": "CERTIFICATE_MINTED",
            "payload_hash": signature_bundle["payload_hash"],
            "signature_id": signature_bundle["sig_id"],
            "vault_transaction_id": vault_txn,
        }
        if encryption_package:
            swarm_payload["encryption"] = {
                "algorithm": encryption_package["algorithm"],
                "encrypted_file": encryption_package["encrypted_file"],
            }
        if skg_payload:
            swarm_payload["skg_payload"] = skg_payload

        swarm_txn = await self.vault.broadcast_to_swarm(swarm_payload)
        print(f"    ✅ Swarm TXN: {swarm_txn}")

        print("8️⃣  Generating verification QR code...")
        qr_code_path = self.renderer.generate_verification_qr(certificate_number)
        print(f"    ✅ QR Code: {qr_code_path}")

        verification_url = registry_verification_url(certificate_number)
        result = {
            "certificate_pdf": str(pdf_path),
            "certificate_number": certificate_number,
            "vault_transaction_id": vault_txn,
            "swarm_broadcast_id": swarm_txn,
            "verification_url": verification_url,
            "qr_code_path": str(qr_code_path),
            "signature_id": signature_bundle["sig_id"],
            "payload_hash": signature_bundle["payload_hash"],
            "certificate_hash": signature_bundle["payload_hash"],
            "security_profile": payload["security_profile"],
            "security_profile_version": payload["security_profile_version"],
            "security_manifest_hash": payload["security_manifest_hash"],
            "renderer_version": payload["renderer_version"],
            "verification_status": "VALID",
            "true_mark_verification_id": certificate_number,
            "nft_backed": bool(metadata.get("nft_backed")),
            "minted_at": datetime.utcnow().isoformat() + "Z",
        }
        if metadata.get("nft_backed"):
            result["certificate_pdf_hash"] = artifact_records["pdf"]["sha256"]
            result["certificate_png_hash"] = artifact_records["png"]["sha256"]
            result["certificate_jpeg_hash"] = artifact_records["jpeg"]["sha256"]
            result["nft_metadata_hash"] = nft_metadata["true_mark"]["nft_metadata_hash"]
        for artifact_type, artifact_path in artifact_paths.items():
            result[f"certificate_{artifact_type}"] = str(artifact_path)
        if encryption_package:
            result["encryption_package"] = encryption_package
        if skg_payload:
            result["skg_transaction_id"] = skg_payload["skg_transaction_id"]
            result["drift_score"] = skg_payload["drift_score"]

        result_path = self.vault.certificates_path / f"{certificate_number}_result.json"
        with open(result_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)

        print()
        print("=" * 70)
        print("✅ CERTIFICATE MINTED & ANCHORED")
        print()
        return result

    @staticmethod
    def _describe_artifacts(artifact_paths: Dict[str, Path]) -> Dict[str, Dict[str, object]]:
        """Describe and hash every issued artifact for deterministic verification."""
        records: Dict[str, Dict[str, object]] = {}
        for artifact_type, artifact_path in artifact_paths.items():
            digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
            mime_type = mimetypes.guess_type(artifact_path.name)[0] or "application/octet-stream"
            record: Dict[str, object] = {
                "path": str(artifact_path),
                "sha256": digest,
                "mime_type": mime_type,
            }
            if artifact_type in {"png", "jpeg"}:
                try:
                    from PIL import Image
                    with Image.open(artifact_path) as image:
                        record["width"] = image.width
                        record["height"] = image.height
                        record["dpi"] = image.info.get("dpi", (300, 300))[0]
                except ImportError:
                    record["width"] = 2550
                    record["height"] = 3300
                    record["dpi"] = 300
            records[artifact_type] = record
        return records

    @staticmethod
    def _generate_certificate_number() -> str:
        """Allocate a TrueMark registry number with a check character.

        Format: TM-XXXX-XXXX-XX-XXXXX-X
        The final character is calculated from the fifteen-character registry
        body so a registry can reject malformed or mistyped identifiers.
        """
        alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        body = uuid.uuid4().hex[:15].upper()
        check = alphabet[sum(alphabet.index(character) for character in body) % len(alphabet)]
        return f"TM-{body[:4]}-{body[4:8]}-{body[8:10]}-{body[10:15]}-{check}"

    def _iss_evidence(self) -> Dict[str, object]:
        """Attach the official ISS timestamp envelope to the signed payload."""
        if not ISS_AVAILABLE:
            return {
                "iss_time_ns": None,
                "iss_timestamp": "ISS unavailable",
                "iss_epoch": None,
                "iss_reference_frame": None,
                "iss_standard_timestamp": None,
                "iss_julian_timestamp": None,
                "stardate": None,
            }
        timecodes = current_timecodes()
        iss_time_ns = get_iss_time_ns()
        return {
            "iss_time_ns": iss_time_ns,
            "iss_timestamp": format_iss_time(iss_time_ns, precision="nanoseconds"),
            "iss_epoch": timecodes["epoch"],
            "iss_reference_frame": timecodes["reference_frame"],
            "iss_standard_timestamp": timecodes["iso_timestamp"],
            "iss_julian_timestamp": timecodes["julian_date"],
            "stardate": round(iss_time_ns / 1_000_000_000, 9),
        }

    def _calculate_stardate(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    async def verify_certificate(self, certificate_number: str) -> Dict:
        print(f"🔍 Verifying certificate: {certificate_number}")
        print("=" * 70)
        verification = await self.vault.verify_certificate_integrity(certificate_number)
        if verification["valid"]:
            print("✅ CERTIFICATE VALID")
            print(f"   Minted: {verification['minted_at']}")
            print(f"   PDF Exists: {verification['pdf_exists']}")
            print(f"   Vault Hash: {verification['vault_integrity_hash']}")
        else:
            print("❌ CERTIFICATE NOT FOUND OR INVALID")
            print(f"   Error: {verification.get('error', 'Unknown error')}")
        print("=" * 70)
        return verification

    async def get_certificate_audit_trail(self, certificate_number: str) -> list:
        print(f"📋 Retrieving audit trail: {certificate_number}")
        audit_trail = await self.vault.get_certificate_audit_trail(certificate_number)
        print(f"   Found {len(audit_trail)} events")
        for index, event in enumerate(audit_trail, start=1):
            event_type = event.get("event", {}).get("event_type", "Unknown")
            print(f"   {index}. {event.get('timestamp', 'N/A')} - {event_type}")
        return audit_trail

    def get_forge_statistics(self) -> Dict:
        issued_today = self.vault.get_certificates_issued_today()
        swarm_status = self.vault.get_swarm_sync_status()
        return {
            "certificates_issued_today": issued_today,
            "swarm_consensus": swarm_status["consensus"],
            "guardians_online": f"{swarm_status['guardians_online']}/{swarm_status['total_guardians']}",
            "vault_path": str(self.vault_base_path),
            "forge_version": "2.0",
        }


def print_banner() -> None:
    banner = """
======================================================================
 TRUE MARK ENTERPRISE CERTIFICATE FORGE v2.0
 Visual Authority + Cryptographic Immutability
======================================================================
"""
    print(banner)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="TrueMark Certificate Forge v2.0 - Mint cryptographically-verifiable certificates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--vault",
        type=str,
        default=str(get_vault_root()),
        help="Path to vault system",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    mint_parser = subparsers.add_parser("mint", help="Mint a new certificate")
    mint_parser.add_argument("--owner", required=True, help="Owner's full name")
    mint_parser.add_argument("--wallet", required=True, help="Web3 wallet address")
    mint_parser.add_argument("--title", required=True, help="Asset title")
    mint_parser.add_argument("--ipfs", required=True, help="IPFS content hash")
    mint_parser.add_argument(
        "--category",
        default="Knowledge",
        choices=["Knowledge", "Asset", "Identity"],
        help="KEP category",
    )
    mint_parser.add_argument("--chain", default="Polygon", help="Blockchain ID")
    mint_parser.add_argument(
        "--officer",
        default="Bryan A Spruk, President and CEO",
        help="Authorized officer printed on the certificate",
    )
    mint_parser.add_argument(
        "--nft-type",
        default=None,
        choices=["H", "K", "L", "B", "HL", "KL", "LL", "BL", "C"],
        help="NFT type used for deterministic color coding",
    )
    mint_parser.add_argument(
        "--encrypt",
        action="store_true",
        help="Encrypt the rendered certificate before storage handoff",
    )
    mint_parser.add_argument(
        "--layers",
        dest="layer_count",
        type=int,
        choices=ALLOWED_LAYER_COUNTS,
        default=13,
        help="Governed forensic depth: 2, 3, 5, 7, 11, or 13 layers",
    )
    mint_parser.add_argument(
        "--frame",
        dest="frame_id",
        default=None,
        help="Optional governed presentation frame ID from truemark/templates/FRAME_CATALOG.json",
    )
    mint_parser.add_argument(
        "--nft-backed",
        action="store_true",
        help="Also produce pixel-faithful PNG/JPEG certificate artwork and NFT metadata JSON",
    )
    mint_parser.add_argument("--nft-image-uri", default=None, help="Final URI for the certificate PNG/JPEG")
    mint_parser.add_argument("--nft-token-id", default=None, help="Confirmed NFT token ID, when available")

    verify_parser = subparsers.add_parser("verify", help="Verify a certificate")
    verify_parser.add_argument("--serial", required=True, help="TrueMark certificate number")

    audit_parser = subparsers.add_parser("audit", help="Get certificate audit trail")
    audit_parser.add_argument("--serial", required=True, help="TrueMark certificate number")

    subparsers.add_parser("stats", help="Get forge statistics")

    args = parser.parse_args()
    if not args.command:
        print_banner()
        parser.print_help()
        return

    print_banner()
    forge = TrueMarkForge(vault_base_path=Path(args.vault), use_mock_vault=True)

    if args.command == "mint":
        metadata = {
            "owner_name": args.owner,
            "wallet_address": args.wallet,
            "asset_title": args.title,
            "ipfs_hash": args.ipfs,
            "kep_category": args.category,
            "chain_id": args.chain,
            "officer": args.officer,
            "nft_type": args.nft_type,
            "encrypt_artifacts": args.encrypt,
            "layer_count": args.layer_count,
            "frame_id": args.frame_id,
            "nft_backed": args.nft_backed,
            "nft_image_uri": args.nft_image_uri,
            "nft_token_id": args.nft_token_id,
        }
        result = await forge.mint_official_certificate(metadata)
        print("📊 MINTING RESULT")
        print("=" * 70)
        print(f"📄 PDF:        {result['certificate_pdf']}")
        print(f"🏷️  Certificate: {result['certificate_number']}")
        print(f"🔒 Vault TXN:  {result['vault_transaction_id']}")
        print(f"🐝 Swarm TXN:  {result['swarm_broadcast_id']}")
        print(f"🔗 Verify URL: {result['verification_url']}")
        print(f"📱 QR Code:    {result['qr_code_path']}")
        if result.get("encryption_package"):
            print(f"🔐 Encrypted:  {result['encryption_package']['encrypted_file']}")
        print("=" * 70)
    elif args.command == "verify":
        await forge.verify_certificate(args.serial)
    elif args.command == "audit":
        await forge.get_certificate_audit_trail(args.serial)
    elif args.command == "stats":
        stats = forge.get_forge_statistics()
        print("📊 FORGE STATISTICS")
        print("=" * 70)
        print(f"Certificates Issued Today: {stats['certificates_issued_today']}")
        print(f"Swarm Consensus:          {stats['swarm_consensus']}")
        print(f"Guardians Online:         {stats['guardians_online']}")
        print(f"Forge Version:            {stats['forge_version']}")
        print(f"Vault Path:               {stats['vault_path']}")
        print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nWARNING: Operation cancelled by user")
        sys.exit(1)
    except Exception as error:
        print(f"\n\nERROR: {error}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
