# 🔥 TrueMark Enterprise Certificate Forge v2.0

**Visual Authority + Cryptographic Immutability + Swarm Intelligence**

A production-grade certificate generation system combining forensic-quality PDF rendering, Ed25519 cryptographic signatures, immutable vault logging, and distributed knowledge graph learning.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

---

## 🎯 Features

### Core Capabilities
- **🎨 Forensic PDF Rendering**: governed prime-depth rendering with microprint, guilloché patterns, timestamps, seals, and verification evidence
- **🔐 Ed25519 Cryptography**: Quantum-resistant 256-bit signatures with SHA-256 payload hashing
- **📦 Immutable Vault**: JSONL append-only ledger compatible with WorkerVaultWriter architecture
- **🌐 Swarm Broadcasting**: FusionQueue integration for distributed asset awareness
- **🧠 Knowledge Graph Learning**: SKG v1.0 learns patterns from every certificate (wallet behavior, IPFS clustering, drift detection)
- **🖼️ 50 Governed Presentation Frames**: SVG-ready 8.5×11 frame library with optional frame selection
- **🔢 Prime Forensic Depths**: only 2, 3, 5, 7, 11, and 13-layer certificate profiles are accepted

### Certificate depth rule

The certificate engine exposes exactly six forensic depth profiles:

- **2-Layer Certificate**
- **3-Layer Certificate**
- **5-Layer Certificate**
- **7-Layer Certificate**
- **11-Layer Forensic Certificate**
- **13-Layer Elite Forensic Certificate**

No one-layer or composite non-prime profile is valid. Pricing is intentionally
not part of the renderer and will be established separately in the product
catalog.

The ordered layer definitions are recorded in
`truemark/forge_v2.0/layer_profiles.py`. Each deeper profile includes the
earlier governed layers. Presentation frames are independent of depth and are
listed in `truemark/templates/FRAME_CATALOG.json`, with the 50 original SVG
assets in `truemark/templates/frames/`.

Example:

```bash
python truemark/forge_v2.0/certificate_forge.py mint \
  --owner "Alice Johnson" \
  --wallet "0x..." \
  --title "Provenance Record" \
  --ipfs "Qm..." \
  --layers 11 \
  --frame frame-24-art-deco-border
```

`--layers` accepts only `2 3 5 7 11 13`. `--frame` changes visual treatment
only; it never changes the evidence depth or authoritative Vault record.

### Printable forensic module library

The generator also registers 30 original, brand-neutral, printer-safe
forensic modules modeled on geometric security-document techniques: guilloché
fields, microtext, seeded glyphs, serial-derived variations, coordinate marks,
micro-QR fragments, watermark fields, lattice systems, foil simulations, and
other deterministic markers. They are cataloged in
`truemark/forge_v2.0/forensic_modules.py` and activated progressively by the
prime depth profile. The selected module IDs are stored with the certificate
configuration privately and are not published as certificate metadata. Public
certificate output is limited to the forensic security profile, profile
version, verification status, certificate hash, True Mark verification ID,
and—where required by the verification protocol—the security manifest hash.
The authoritative record remains the sealed Vault evidence chain.

### Security & Compliance
- DALS-001 compliant serial numbers with checksums
- Stardate temporal anchoring
- QR code verification integration
- Duplicate detection via pattern learning
- Anomaly detection with drift scoring (0.0-1.0+)

---

## 🚀 Quick Start

### Docker (Recommended)

```bash
# Build and run
docker-compose up -d

# Mint a certificate
docker exec -it truemark-forge python /app/truemark/forge_v2.0/certificate_forge.py mint \
  --name "Alice Johnson" \
  --wallet "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" \
  --title "Blockchain Mastery Certification" \
  --ipfs "QmX9fH3gQkFjD8mN2PqR7sT5vW8yZ1aB3cD4eF6gH7iJ8k" \
  --category Knowledge \
  --chain Polygon
```

### Local Installation

```powershell
# Install dependencies
.\truemark\forge_v2.0\install.ps1

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Mint certificate
python truemark/forge_v2.0/certificate_forge.py mint `
  --name "Alice Johnson" `
  --wallet "0x742d35Cc6634C0532925a3b844Bc454e4438f44e" `
  --title "Blockchain Mastery Certification" `
  --ipfs "QmX9fH3gQkFjD8mN2PqR7sT5vW8yZ1aB3cD4eF6gH7iJ8k" `
  --category Knowledge `
  --chain Polygon
```

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, Linux, macOS
- **Dependencies**: See `truemark/forge_v2.0/requirements.txt`
- **Docker** (optional): For containerized deployment

---

## 🏗️ Architecture

```
certificate_generator_2x/
├── truemark/
│   └── forge_v2.0/
│       ├── certificate_forge.py      # Main orchestrator
│       ├── crypto_anchor.py          # Ed25519 signing engine
│       ├── forensic_renderer.py      # Prime-depth PDF generator
│       ├── layer_profiles.py         # 2/3/5/7/11/13 layer rule
│       ├── integration_bridge.py     # Vault/swarm connector
│       ├── install.ps1               # Automated setup
│       └── requirements.txt
├── True_Mark_Vault_System/
│   ├── certificates/issued/          # Generated PDFs + metadata
│   ├── vault_logs/                   # Immutable JSONL logs
│   ├── swarm_queue/                  # FusionQueue broadcasts
│   └── vault_system/
│       └── skg_core/                 # Knowledge Graph (SKG v1.0)
│           ├── skg_node.py           # Graph entity types
│           ├── skg_pattern_learner.py # Pattern clustering
│           ├── skg_drift_analyzer.py  # Anomaly detection
│           ├── skg_serializer.py      # Vault persistence
│           ├── skg_engine.py          # Main orchestrator
│           └── skg_integration.py     # Forge bridge
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Component Overview

#### 1. **Certificate Forge (`certificate_forge.py`)**
Main orchestrator that coordinates the 7-step minting process:
1. Generate DALS serial with checksum
2. Create cryptographic payload
3. Sign with Ed25519 root authority
4. Render forensic PDF with embedded signature
5. Record to immutable vault ledger
6. Ingest into SKG knowledge graph
7. Broadcast to swarm network

#### 2. **Crypto Anchor (`crypto_anchor.py`)**
Ed25519 cryptographic engine providing:
- 256-bit quantum-resistant signatures
- SHA-256 payload hashing
- Key management (mock + production modes)
- Signature verification

#### 3. **Forensic Renderer (`forensic_renderer.py`)**
Prime-depth forensic rendering uses the following ordered layers:
- **Layer 1**: Certificate substrate and base field
- **Layer 2**: Certificate identity and canonical content
- **Layer 3**: Selected SVG presentation frame
- **Layer 4**: TrueMark watermark treatment
- **Layer 5**: Canonical timestamp display
- **Layer 6**: Certificate seal
- **Layer 7**: Independent verification QR
- **Layer 8**: Authorized signature block
- **Layer 9**: Forensic micro-pattern
- **Layer 10**: Forensic microtexture
- **Layer 11**: Canonical certificate manifest
- **Layer 12**: Cryptographic metadata and signature anchor
- **Layer 13**: Independent verification evidence block

The renderer selects the first `N` ordered layers for the requested governed
profile. Therefore a 2-layer certificate contains layers 1–2, a 7-layer
certificate contains layers 1–7, and a 13-layer certificate contains all 13.

#### 4. **Integration Bridge (`integration_bridge.py`)**
Vault and swarm connectivity:
- **WorkerVaultWriter**: JSONL append-only logging
- **FusionQueue**: Swarm broadcast system
- Mock implementations for standalone testing

#### 5. **Swarm Knowledge Graph (SKG v1.0)**
Distributed learning system that creates "collective memory":

**Pattern Learning** (`skg_pattern_learner.py`):
- Wallet behavior clustering (duplicate detection)
- IPFS content fingerprinting
- Temporal pattern analysis
- Chain activity tracking
- Asset title similarity

**Drift Analysis** (`skg_drift_analyzer.py`):
- Temporal drift (minting velocity anomalies)
- Signature drift (key rotation detection)
- Pattern drift (behavioral outliers)
- Composite drift score: 0.0 (normal) to 1.0+ (suspicious)

**Graph Structure**:
- **Nodes**: CERTIFICATE, IDENTITY, CHAIN, PATTERN, DRIFT_EVENT
- **Edges**: OWNS, ISSUED_ON, DETECTED_IN, CLUSTERS_WITH
- **Storage**: Vault-compatible JSONL (append-only)

---

## 🐳 Docker Deployment

### Build Image

```bash
docker build -t truemark-forge:v2.0 .
```

### Run with Docker Compose

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Volumes

The Docker setup mounts these volumes:
- `./True_Mark_Vault_System/certificates/issued` → Generated certificates
- `./True_Mark_Vault_System/vault_logs` → Immutable logs
- `./True_Mark_Vault_System/swarm_queue` → Swarm broadcasts
- `./True_Mark_Vault_System/vault_system/skg_core/skg_data` → Knowledge graph data

---

## 📖 Usage Examples

### Mint Certificate (CLI)

```bash
python certificate_forge.py mint \
  --name "Bob Smith" \
  --wallet "0x8B3eF2c1A9dF4e5C6b7D8E9F0A1B2C3D4E5F6A7B" \
  --title "AI Research Publication" \
  --ipfs "QmT4vW8yZ1aB3cD4eF6gH7iJ8kL9mN0oP1qR2sT3uV4w" \
  --category Knowledge \
  --chain Ethereum
```

### Mint Certificate (Python API)

```python
import asyncio
from pathlib import Path
from certificate_forge import TrueMarkForge

async def mint_example():
    forge = TrueMarkForge(
        vault_base_path=Path("T:/certificate generator 2x/True_Mark_Vault_System"),
        use_mock_vault=True
    )
    
    result = await forge.mint_official_certificate({
        "owner_name": "Carol White",
        "wallet_address": "0x1A2B3C4D5E6F7A8B9C0D1E2F3A4B5C6D7E8F9A0B",
        "asset_title": "Decentralized Identity Patent",
        "ipfs_hash": "QmP1qR2sT3uV4wX5yZ6aB7cD8eF9gH0iJ1kL2mN3oP4q",
        "kep_category": "Asset",
        "chain_id": "Polygon"
    })
    
    print(f"Certificate: {result['certificate_pdf']}")
    print(f"DALS Serial: {result['dals_serial']}")
    print(f"Verify: {result['verification_url']}")

asyncio.run(mint_example())
```

### Query Knowledge Graph

```python
from skg_integration import CertificateSKGBridge

# Get wallet portfolio
skg = CertificateSKGBridge(Path("T:/certificate generator 2x/True_Mark_Vault_System"))
portfolio = await skg.get_owner_portfolio("0x742d35Cc6634C0532925a3b844Bc454e4438f44e")

print(f"Total certificates: {portfolio['total_certificates']}")
print(f"Categories: {portfolio['categories']}")
print(f"Chains: {portfolio['chains']}")

# Detect suspicious activity
suspicious = await skg.detect_suspicious_certificates(drift_threshold=0.7)
for cert in suspicious:
    print(f"⚠️  {cert['dals_serial']}: drift={cert['drift_score']:.2f}")
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Vault configuration
VAULT_BASE_PATH=/app/True_Mark_Vault_System
VAULT_MODE=mock  # or 'production'

# Certificate settings
DEFAULT_CHAIN=Polygon
DEFAULT_CATEGORY=Knowledge

# SKG settings
SKG_ENABLED=true
SKG_DRIFT_THRESHOLD=0.7
```

### Mock vs Production Mode

**Mock Mode** (default):
- No external dependencies
- JSONL files written to local directories
- Swarm broadcasts logged locally
- Perfect for development/testing

**Production Mode**:
- Requires actual WorkerVaultWriter integration
- Requires FusionQueue swarm access
- Set `use_mock_vault=False` in TrueMarkForge

---

## 🧪 Testing

### Quick Test

```powershell
.\truemark\forge_v2.0\quick_test.ps1
```

### Run Individual Component Tests

```python
# Test crypto anchor
python truemark/forge_v2.0/crypto_anchor.py

# Test forensic renderer
python truemark/forge_v2.0/forensic_renderer.py

# Test SKG engine
python True_Mark_Vault_System/vault_system/skg_core/skg_engine.py
```

---

## 📊 Output Files

Each minted certificate generates:

1. **Certificate PDF** (`DALS{serial}.pdf`)
   - 300 DPI forensic-quality document
   - 10-layer anti-AI artifacts
   - Embedded cryptographic signature
   
2. **Verification QR Code** (`DALS{serial}_qr.png`)
   - Links to verification URL
   - Embedded DALS serial
   
3. **Result Metadata** (`DALS{serial}_result.json`)
   - Complete certificate package
   - Vault transaction ID
   - Swarm broadcast ID
   - SKG transaction ID
   - Drift score

4. **Vault Log Entry** (`vault_logs/worker_*.jsonl`)
   - Immutable JSONL record
   - Append-only ledger

5. **Swarm Broadcast** (`swarm_queue/fusion_*.jsonl`)
   - Distributed event log
   - Includes SKG payload

6. **SKG Graph Data** (`skg_core/skg_data/skg_*.jsonl`)
   - Knowledge graph nodes/edges
   - Pattern clusters
   - Drift events

---

## 🔐 Security Features

### Cryptographic Security
- **Ed25519**: 256-bit elliptic curve signatures
- **SHA-256**: Payload integrity hashing
- **Quantum-Resistant**: Future-proof cryptography

### Anti-Forgery Measures
- DALS serial checksums (collision-resistant)
- Embedded signatures in PDF metadata
- Microprint and guilloché patterns
- Holographic gradient backgrounds
- QR code verification linking

### Anomaly Detection
- Drift scoring (temporal, signature, pattern)
- Wallet behavior clustering
- Duplicate certificate detection
- Suspicious activity flagging (drift >0.7)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ReportLab**: PDF generation framework
- **Ed25519**: High-performance signature library
- **Pillow**: Image processing capabilities
- **Python Cryptography**: Modern cryptographic primitives

---

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Report a bug](https://github.com/Spruked/certificate_generator_2x/issues)
- Documentation: See `truemark/forge_v2.0/docs/`

---

**Built with 🔥 for the decentralized future**
