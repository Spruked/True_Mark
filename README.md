# True Mark

True Mark is an object-authentication, evidence-preservation, certification, and optional digital-extension platform. It is not primarily an NFT storefront.

## Product model

```text
Account
  → Secretum Privatum / Private Sanctum
  → Project / Object Workbench
  → Evidence Staging
  → Ready for Review
  → Commit action
  → Sealed / Immutable Vault event
  → Canonical Certificate Manifest
  → Prime Layer Certificate
  → Independent Verification
  → Optional NFT / Digital Extension
```

Secretum Privatum is private, mutable working space. The Immutable Vault is the authoritative append-only record. Uploading a file never makes it authoritative; only an explicit commit/seal operation crosses that boundary.

## Current implementation

- Revised Sanctum dashboard at `/sanctum`.
- Object Workbench at `/objects/new` and `/objects/:objectId`.
- Independent verification surface at `/verify`.
- Governed project states and transition validation in [backend/secretum_models.py](backend/secretum_models.py).
- Prime Layer profiles limited to 2, 3, 5, 7, 11, and 13 layers.
- Canonical manifest generation with a manifest hash; authority remains in the sealed evidence/Vault chain.
- Human Support escalation channel, hidden by default and limited to scoped cases.

## Compatibility boundary

The existing payment and token-issuance routes remain temporarily available for compatibility. They are legacy surfaces and must be migrated into the canonical Object → Evidence → Commit → Vault path before production authority is expanded. They must not become a second authoritative issuance path.

## Documentation

- [True Mark Revision Doctrine](docs/TRUE_MARK_REVISION_DOCTRINE.md)
- [Product Brochure and Dashboard Manual](docs/TRUE_MARK_PRODUCT_BROCHURE_AND_DASHBOARD_MANUAL.md)
- [Prime Layer Architecture](docs/PRIME_LAYER_ARCHITECTURE.md)
- [Development Log](DEVLOG.md)
- [User Guide](UserGuide.md)
- [Procedures Overview](ProceduresOverview.md)

## Local development

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Backend:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 13001
```

The existing frontend build should pass with `npm run build` from `frontend/`. Do not add payment, blockchain, SMTP, or production credential configuration until the core authentication transaction is deterministic and recovery-safe.

## Human Support

The support channel is not an automated named assistant. It is hidden by default and appears only after a governed escalation case is authorized. Agents receive only the approved case context; unrelated Sanctum projects, temporary files, private notes, and encryption keys remain excluded.
