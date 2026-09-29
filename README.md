# True Mark

Copyright © 2026 Spruked / True Mark. All rights reserved. This repository is proprietary; see [LICENSE](LICENSE) and [COPYRIGHT.md](COPYRIGHT.md).

True Mark is an object-authentication, evidence-preservation, certification, and optional digital-extension platform. It is not primarily an NFT storefront.

## Product model

```text
Account
  → Perpetuum
      └─ Project / Object Workbench
          → Evidence Staging
  → READY_FOR_REVIEW
  → COMMIT_PENDING
  → COMMITTED
  → Sealed / Immutable Vault event
  → Canonical Certificate Manifest
  → Prime Layer Certificate
  → Independent Verification
  → Optional NFT / Digital Extension
```

Perpetuum is the account holder's private archive room and mutable working space, with local parsing, object-organization, packaging, and encryption tools. The Immutable Vault is the authoritative append-only record. Uploading a file never makes it authoritative; only an explicit commit/seal operation crosses that boundary.

## Current implementation

- Revised Sanctum dashboard at `/sanctum`.
- Object Workbench at `/objects/new` and `/objects/:objectId`.
- Independent verification surface at `/verify`.
- Governed project states and transition validation in [backend/secretum_models.py](backend/secretum_models.py).
- Prime Layer profiles limited to 2, 3, 5, 7, 11, and 13 layers.
- Canonical manifest generation with a manifest hash; authority remains in the sealed evidence/Vault chain.
- Human Support escalation channel, hidden by default, signed-session authenticated, account-scoped, and persisted in SQLite.
- All mutable runtime state and generated artifacts are stored under [True_Mark_Vault_System](True_Mark_Vault_System), the single authoritative local Vault root.
- Perpetuum organizer at [Perpetuum](Perpetuum), with local parsing, ingestion, package review, and ledger-oriented workspace flows. It is a standalone sibling repository, separate from `GOAT`.

## Compatibility boundary

The existing payment and token-issuance routes remain temporarily available for compatibility. They are legacy surfaces and must be migrated into the canonical Object → Evidence → Commit → Vault path before production authority is expanded. They must not become a second authoritative issuance path.

## Documentation

- [True Mark Revision Doctrine](docs/TRUE_MARK_REVISION_DOCTRINE.md)
- [Product Brochure and Dashboard Manual](docs/TRUE_MARK_PRODUCT_BROCHURE_AND_DASHBOARD_MANUAL.md)
- [Prime Layer Architecture](docs/PRIME_LAYER_ARCHITECTURE.md)
- [Development Log](DEVLOG.md)
- [Repository Tree](true_mark_tree.txt)
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

The backend resolves `TRUEMARK_VAULT_ROOT` to `True_Mark_Vault_System` by default. The Vault owns the database, staged uploads, invoices, receipts, sealed packages, exports, support records, certificate artifacts, audit data, and runtime configuration.

The existing frontend build should pass with `npm run build` from `frontend/`. Do not add payment, blockchain, SMTP, or production credential configuration until the core authentication transaction is deterministic and recovery-safe.

## Human Support

The support channel is not an automated named assistant. It is hidden by default and appears only after a governed escalation case is authorized. Customer ownership is derived from the signed account session, cases survive backend restarts, and agents receive only the approved case context; unrelated Sanctum projects, temporary files, private notes, and encryption keys remain excluded. The production escalation API is integrated into the main backend on port `13001`; the companion `truemark-human-support` service is only a deprecated adapter.
