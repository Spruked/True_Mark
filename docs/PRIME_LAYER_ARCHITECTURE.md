# True Mark Prime Layer Architecture

True Mark issues only six governed certificate profiles:

| ID | Customer-facing label | Layers |
| --- | --- | ---: |
| `p2` | 2-Layer Certificate | 2 |
| `p3` | 3-Layer Certificate | 3 |
| `p5` | 5-Layer Certificate | 5 |
| `p7` | 7-Layer Certificate | 7 |
| `p11` | 11-Layer Forensic Certificate | 11 |
| `p13` | 13-Layer Elite Forensic Certificate | 13 |

The engine rejects zero-layer, one-layer, arbitrary, and non-prime certificate packages. The layer count is governed by `backend/certificate_profiles.py` and is not editable through pricing administration.

## Authority and presentation

Each completed issuance writes a canonical `certificate_manifest.json` into the vault package. The manifest contains the selected profile, exact layer inventory, canonical object facts, and a SHA-256 `certificate_manifest_hash`; authority remains in the sealed evidence and Vault event.

Visual presentation is intentionally separate. Frame, palette, seal, typography, watermark, and layout choices can be added as render profiles without changing the certificate manifest or its layer count.

## Required decisions before production

1. Confirm the six prices currently seeded in `backend/config/pricing.json`.
2. Approve the exact meaning and evidence source for each governed layer in `backend/certificate_profiles.py`.
3. Provide the first approved render profile: frame family, palette, seal, typography, layout, page size, and watermark treatment.
4. Provide production payment credentials and webhook configuration.
5. Provide the production blockchain network, RPC/Alchemy URL, deployer wallet, contract address, and final metadata hosting strategy.
6. Provide SMTP credentials and the approved sender addresses for invoices and certificate delivery.
7. Confirm the public API and frontend URLs, including whether `truemarkmint.com` remains canonical.
8. Confirm retention, encryption-key custody, and whether the source asset should be destroyed immediately after the vault package is finalized.

## Current implementation boundary

The prime profile catalog, checkout pricing options, backend quote validation, and immutable manifest record are implemented. The existing mint flow still produces the current invoice/vault artifacts; a production certificate PDF/image renderer and independent render-profile catalog should be wired to the manifest after the first visual profile is approved.
