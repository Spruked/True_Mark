# True Mark User Guide

## 1. Start in Secretum Privatum

Sign in to open your private Sanctum. The Sanctum is a mutable working space for projects, notes, evidence staging, images, provenance, ownership information, and supporting documents.

The Sanctum is not the Immutable Vault. Draft uploads can be replaced or deleted according to policy and are not authoritative merely because they exist.

## 2. Create an Object Project

From My Sanctum, choose **Create New Project**. A project can represent a painting, heirloom, collectible, photograph, manuscript, invention, software artifact, research package, professional work product, digital asset, intellectual property, or another object.

Use the Object Workbench to complete:

- Identity
- Ownership and creator information
- Provenance
- Evidence files
- Images
- Supporting documents
- Notes and metadata
- Certificate configuration

## 3. Authority transition

Every project follows:

```text
WORKING COPY → READY FOR REVIEW → COMMIT action → COMMITTED → SEALED
```

Commit is an action, not a durable state. A successful commit creates the governed evidence package. Sealing creates the authoritative Immutable Vault event. A crash or interrupted request must be recoverable without silently changing submitted bytes.

## 4. Prime Layer Certificates

After the object is ready for review, choose one governed profile:

- 2-Layer Certificate
- 3-Layer Certificate
- 5-Layer Certificate
- 7-Layer Certificate
- 11-Layer Forensic Certificate
- 13-Layer Elite Forensic Certificate

Certificate depth and certificate design are separate. Frames, typography, paper, seal, watermark, layout, orientation, color family, and image placement do not change the evidence-layer count.

## 5. Canonical record and certificate

The sealed evidence and Vault events are authoritative. The certificate manifest is a canonical machine-readable representation of that authority. A rendered certificate is a presentation artifact derived from the canonical manifest.

## 6. Verification

Use Verify to check an object identifier, certificate ID, or verification reference. The verifier should compare the canonical manifest, evidence hashes, Vault event, and any applicable signatures or anchors.

## 7. Digital extensions

NFTs, licensing, transfer, inheritance, and other digital extensions occur after authentication and certification. They do not create authenticity by themselves.

## 8. Human Support

Human Support is available only after a governed escalation. A human agent sees only the authorized case context, never the full Sanctum by default. Encryption keys, unrelated projects, unrelated temporary files, and private notes remain excluded.
