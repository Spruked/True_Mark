"""
TrueMark Enterprise Certificate Forge v2.0
Main orchestrator for certificate minting, storage protection, and vault logging.
"""

from pathlib import Path
from datetime import datetime
import argparse
import asyncio
import json
import sys
import uuid
from typing import Dict, Optional

try:
    from forensic_renderer import ForensicCertificateRenderer
    from crypto_anchor import CryptoAnchorEngine
    from integration_bridge import VaultFusionBridge
    from crypto_vault import ChaChaVault
    from path_config import get_vault_root
except ImportError as error:
    print(f"❌ Import error: {error}")
    sys.exit(1)


SKG_AVAILABLE = False
CertificateSKGBridge = None

try:
    from pathlib import Path as _Path

    skg_path = _Path(__file__).resolve().parents[2] / "Vault_System_1.0" / "vault_system" / "skg_core"
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

        print("1️⃣  Generating DALS serial...")
        dals_serial = self._generate_dals_serial(metadata.get("kep_category", "Knowledge"))
        print(f"    ✅ Serial: {dals_serial}")

        print("2️⃣  Creating cryptographic payload...")
        payload = {
            "dals_serial": dals_serial,
            "owner": metadata["owner_name"],
            "wallet": metadata["wallet_address"],
            "ipfs_hash": metadata["ipfs_hash"],
            "stardate": self._calculate_stardate(),
            "kep_category": metadata.get("kep_category", "Knowledge"),
            "chain_id": metadata.get("chain_id", "Polygon"),
            "asset_title": metadata["asset_title"],
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
        pdf_data = {**metadata, **payload, **signature_bundle}
        pdf_path = await self.renderer.create_forensic_pdf(
            data=pdf_data,
            output_dir=self.vault.certificates_path,
        )
        print(f"    ✅ PDF: {pdf_path}")

        encryption_package = None
        if metadata.get("encrypt_artifacts"):
            print("4.5️⃣ Encrypting PDF for off-chain storage...")
            associated_data = dals_serial.encode("utf-8")
            vault = ChaChaVault()
            encrypted_path = pdf_path.with_suffix(".encrypted.json")
            vault.encrypt_file_to_json(pdf_path, encrypted_path, associated_data=associated_data)
            encryption_package = {
                "encrypted_file": str(encrypted_path),
                "algorithm": vault.algorithm,
                "key_hex": vault.export_key_hex(),
                "associated_data": dals_serial,
            }
            print(f"    ✅ Encrypted package: {encrypted_path}")

        print("5️⃣  Recording to vault...")
        vault_txn = await self.vault.record_certificate_issuance(
            worker_id="certificate_forge_worker_001",
            dals_serial=dals_serial,
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
                        "dals_serial": dals_serial,
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
            "dals_serial": dals_serial,
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
        qr_code_path = self.renderer.generate_verification_qr(dals_serial)
        print(f"    ✅ QR Code: {qr_code_path}")

        verification_url = f"https://verify.truemark.io/{dals_serial}"
        result = {
            "certificate_pdf": str(pdf_path),
            "dals_serial": dals_serial,
            "vault_transaction_id": vault_txn,
            "swarm_broadcast_id": swarm_txn,
            "verification_url": verification_url,
            "qr_code_path": str(qr_code_path),
            "signature_id": signature_bundle["sig_id"],
            "payload_hash": signature_bundle["payload_hash"],
            "minted_at": datetime.utcnow().isoformat() + "Z",
        }
        if encryption_package:
            result["encryption_package"] = encryption_package
        if skg_payload:
            result["skg_transaction_id"] = skg_payload["skg_transaction_id"]
            result["drift_score"] = skg_payload["drift_score"]

        result_path = self.vault.certificates_path / f"{dals_serial}_result.json"
        with open(result_path, "w", encoding="utf-8") as handle:
            json.dump(result, handle, indent=2)

        print()
        print("=" * 70)
        print("✅ CERTIFICATE MINTED & ANCHORED")
        print()
        return result

    def _generate_dals_serial(self, category: str) -> str:
        category_code = {
            "Knowledge": "K",
            "Asset": "A",
            "Identity": "I",
        }.get(category, "X")
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique = uuid.uuid4().hex[:8].upper()
        return f"DALS{category_code}M{timestamp}-{unique}"

    def _calculate_stardate(self) -> str:
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    async def verify_certificate(self, dals_serial: str) -> Dict:
        print(f"🔍 Verifying certificate: {dals_serial}")
        print("=" * 70)
        verification = await self.vault.verify_certificate_integrity(dals_serial)
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

    async def get_certificate_audit_trail(self, dals_serial: str) -> list:
        print(f"📋 Retrieving audit trail: {dals_serial}")
        audit_trail = await self.vault.get_certificate_audit_trail(dals_serial)
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
        "--encrypt",
        action="store_true",
        help="Encrypt the rendered certificate before storage handoff",
    )

    verify_parser = subparsers.add_parser("verify", help="Verify a certificate")
    verify_parser.add_argument("--serial", required=True, help="DALS serial number")

    audit_parser = subparsers.add_parser("audit", help="Get certificate audit trail")
    audit_parser.add_argument("--serial", required=True, help="DALS serial number")

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
            "encrypt_artifacts": args.encrypt,
        }
        result = await forge.mint_official_certificate(metadata)
        print("📊 MINTING RESULT")
        print("=" * 70)
        print(f"📄 PDF:        {result['certificate_pdf']}")
        print(f"🏷️  Serial:     {result['dals_serial']}")
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
