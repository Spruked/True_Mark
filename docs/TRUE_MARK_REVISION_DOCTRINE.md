# True Mark Revision Doctrine

This document freezes the revised product boundary for True Mark.

## Product model

```text
Account
  → Secretum Privatum / Private Sanctum
  → Project / Object Workspace
  → Evidence Staging
  → Authentication Record
  → Immutable Vault Commitment
  → Prime Layer Certificate
  → Independent Verification
  → Optional NFT / Digital Object Extension
```

Secretum Privatum is the private, mutable preparation layer. It is not the Immutable Vault. Draft files, notes, replacement uploads, and uncommitted work belong in the Sanctum. Only committed evidence enters the append-only authoritative record.

## Authority boundary

```text
WORKING_COPY → READY_FOR_REVIEW → COMMIT_PENDING → COMMITTED → SEALED
```

Upload alone never creates authority. Commit is the customer-authorized action that moves a ready object through `COMMIT_PENDING` to `COMMITTED`; sealing then establishes the immutable record. The operation establishes exact submitted bytes, canonical metadata, identities, timestamps, hashes, signatures, applicable encryption, anchors, and chain of custody. The certificate manifest is canonical, not authoritative; authority resides in the evidence, issuing authority, and Vault events.

## Account hierarchy

```text
True Mark Account
  └── Identity
       └── Secretum Privatum
            ├── Projects
            ├── Temporary Evidence
            ├── Authenticated Objects
            ├── Certificates
            ├── Verification Records
            ├── Optional Digital Extensions
            ├── Transaction History
            └── Security / Audit History
```

Initially, one account owns one primary Sanctum with unlimited or plan-governed projects.

## Object Workbench

Every project represents an object such as a painting, family heirloom, collectible, photograph, manuscript, invention, software artifact, research package, professional work product, digital asset, or intellectual property.

Workbench areas: identity, ownership, provenance, evidence, images, supporting documents, notes, hash preview, certificate configuration, render design, and pending actions.

## Certificate model

Prime Layer profiles are exactly 2, 3, 5, 7, 11, and 13 layers. Forensic depth and visual design are separate dimensions: frame, typography, paper, seal, watermark, layout, orientation, color family, image placement, and evidence presentation do not alter evidence depth.

## Vocabulary

| Legacy | Revised |
| --- | --- |
| Mint an NFT | Authenticate an Object |
| Mint | Commit / Seal / Issue |
| NFT | Object |
| NFT Dashboard | My Objects / Secretum Privatum |
| NFT Category | Object Type |
| Mint Package | Certificate Profile |
| Wallet Address | Optional Digital Extension Wallet |
| Minted | Authenticated / Sealed / Certified |
| NFT Metadata | Object Evidence / Record Metadata |
| Blockchain Certificate | Prime Layer Certificate |

The word “mint” remains only where a token is genuinely being minted. Digital extensions occur after authentication and certification.

## Architecture boundary

The public site explains authentication, evidence, sealing, certificates, verification, object types, digital extensions, pricing, and My Sanctum. The authenticated application opens on the Sanctum dashboard and routes each project into an Object Workbench. SKG may provide derived intelligence beside the chain, but it never becomes authority.
