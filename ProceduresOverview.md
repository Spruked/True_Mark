# True Mark Procedures Overview

## Product boundary

True Mark authenticates objects and preserves evidence before offering certificates or optional digital extensions. Perpetuum is the private preparation layer and archive room. The Immutable Vault is the authoritative record.

## Customer procedure

1. Create or access an account.
2. Enter Perpetuum.
3. Create an Object Project.
4. Stage evidence, provenance, ownership information, images, documents, and notes.
5. Move the project to **Ready for Review**.
6. Explicitly invoke the **Commit** action.
7. Validate the evidence package and create the Immutable Vault event.
8. Seal the object record.
9. Select a Prime Layer Certificate profile and separate render design.
10. Review the canonical manifest and use independent verification.
11. Add an optional NFT or digital extension only after certification.

## State and retention rules

Project states include `WORKING_COPY`, `READY_FOR_REVIEW`, `COMMIT_PENDING`, `COMMITTED`, `SEALED`, `RELEASED`, `DELETED`, and `EXPIRED`. Evidence uses a separate lifecycle and must not be deleted as ordinary temporary content after it contributes to a sealed record.

Retention periods remain a product-policy decision and must not be invented in implementation defaults.

## Security

- Account ownership resolves through account → Sanctum → project → object → evidence.
- Cross-account reads, updates, commits, and downloads deny by default.
- ChaCha20-Poly1305 belongs at the storage boundary; keys do not travel in project JSON or certificate records.
- Human Support cases disclose only explicitly authorized context.

## Administrative boundary

Legacy payment and token routes remain compatibility surfaces only. They must be adapted to the canonical project/evidence/commit pipeline before they can create authoritative records.
