# True Mark Development Log

## 2026-09-28 — ISS and Vault audit integration

- Connected the ISS Scale to the authoritative Vault audit boundary.
- Added `backend/vault_audit.py` with append-only JSONL events under `True_Mark_Vault_System/audit/events.jsonl`.
- Audited order records, mint-event records, and Perpetuum workspace saves now receive the complete ISS timestamp envelope.
- Added sequential `previous_event_hash` and `event_hash` tamper evidence to each audit event.
- Kept the authority boundary explicit: the Vault owns the event and payload; ISS owns canonical timekeeping.
- Verified the audit chain with a two-event isolated test.

## 2026-09-28 — Perpetuum relocation wiring check

- Verified `GOAT/Secretum Privatum` no longer exists.
- Confirmed `Perpetuum/` is the standalone root-level organizer application.
- Confirmed Perpetuum TypeScript imports resolve and its production build passes.
- Confirmed the main frontend production build passes.
- Confirmed backend and tooling Python modules compile successfully.
- Remaining old-name matches are historical DEVLOG entries only; no active code, package, or import wiring targets the deleted path.

## 2026-09-28 — Perpetuum workspace relocation and terminology cleanup

- Moved the Perpetuum application out of `GOAT` and placed it at the repository root: `Perpetuum/`.
- Removed the former `GOAT/Secretum Privatum` application files; only an ignored Vite cache remains there from the previous local run.
- Standardized the customer-facing workspace name as `Perpetuum`.
- Removed the deprecated `Private Sanctum` product wording from the README, UI, procedures, user guide, doctrine, and branding language.
- Confirmed the relocated Perpetuum application builds successfully with `npm run build`.
- Refreshed `true_mark_tree.txt` to reflect the root-level Perpetuum location.

## 2026-09-28 — Perpetuum organizer rename and repository map

- Renamed the local parsing/object-organizer application from `Secretum Privatum` to `Perpetuum`.
- Updated the Perpetuum package name, schema identifier, UI labels, component name, title, and local README.
- Confirmed the application build passes with `npm run build` from `Perpetuum`.
- Regenerated `true_mark_tree.txt` from the current repository state.
- Updated the root README to identify Perpetuum as the account-holder private archive room and local organizer tool.
- The repository tree excludes generated dependencies, build output, caches, virtual environments, and Python bytecode.

## 2026-09-28 — Product revision and human escalation boundary

### Completed

- Reframed the customer-facing product around Account → Secretum Privatum → Object Workbench → Evidence → Commit → Immutable Vault → Certificate → Verify → optional digital extension.
- Added the Sanctum dashboard at `/sanctum`.
- Added Object Workbench routes at `/objects/new` and `/objects/:objectId`.
- Added public verification surface at `/verify`.
- Added project/evidence state contracts and transition validation in `backend/secretum_models.py`.
- Kept `COMMIT_PENDING` and `COMMITTED` as states while treating Commit as an action.
- Enforced the distinction between authoritative sealed records and canonical certificate manifests.
- Limited certificate profiles to 2, 3, 5, 7, 11, and 13 layers.
- Replaced named-assistant references with governed Human Support escalation language.
- Renamed the retained support prototype to `truemark-human-support`.
- Replaced the old pretend-inference API with scoped escalation case endpoints.
- Made the Human Support bubble hidden by default and case-scoped when authorized.
- Updated README, User Guide, Procedures Overview, branding, product brochure, revision doctrine, and Prime Layer documentation.

### Validation

- Frontend production build passes.
- Python backend modules compile.
- Illegal direct `WORKING_COPY → SEALED` transitions are rejected.
- No named-assistant references, old assistant API variables, or old assistant hostnames remain.

## 2026-09-28 — Local development stack verification

- Confirmed True Mark frontend on `http://localhost:3300`.
- Confirmed Secretum Privatum UI on `http://localhost:1420`.
- Moved the local True Mark backend to `http://localhost:13001` because port `13000` is occupied by an unrelated system service in this environment.
- Updated frontend API and Human Support escalation defaults to port `13001`.
- Added and verified the main-backend escalation routes.
- Created `backend/.venv` from `backend/requirements.txt`; the environment remains ignored and is not committed.
- Verified backend root, pricing profiles, escalation creation, message queueing, and case retrieval.

## 2026-09-28 — Human Support hardening

- Added signed account sessions to account login and Human Support requests.
- Derived escalation ownership from the authenticated session instead of accepting caller-supplied account IDs.
- Persisted escalation cases and messages in SQLite so restarts do not erase the queue.
- Scoped case reads and customer messages to the owning account; added authenticated admin assignment.
- Restricted the escalation context envelope to approved object/workflow fields.
- Synchronized the doctrine with `WORKING_COPY → READY_FOR_REVIEW → COMMIT_PENDING → COMMITTED → SEALED`, with Commit defined as the customer-authorized action.

## 2026-09-28 — True Mark Vault System authority migration

- Renamed the added `Vault-Logic-System-Template` directory to `True_Mark_Vault_System` and removed its nested Git metadata.
- Established `True_Mark_Vault_System` as the single local source of truth for runtime state and generated artifacts.
- Moved the existing True Mark database and pricing configuration into the Vault runtime.
- Redirected database, staged uploads, invoices, receipts, sealed packages, mail outbox, exports, pricing, tax, Human Support workspace records, and certificate-forge paths to the Vault.
- Moved the legacy SKG core under the Vault so certificate intelligence data has one governed root.
- Replaced browser-local Sanctum workspace persistence with authenticated Vault-backed workspace persistence.

### Known boundary

The legacy payment/token issuance routes remain available temporarily for compatibility. They must be adapted into the canonical Object → Evidence → Commit → Vault pipeline before they can be treated as an authoritative production path.

## 2026-09-27 — Prime Layer certificate architecture

- Added governed profiles for exactly 2, 3, 5, 7, 11, and 13 layers.
- Added canonical layer inventories and manifest hashing.
- Removed legacy zero-layer and invalid 10-layer package options.
- Updated checkout and pricing configuration.

## Earlier work

- Built the initial React/FastAPI mint workflow, invoices, vault packages, admin tooling, and certificate support.
- Added sitemap and robots configuration for public routes.
## 2026-09-29 — Canonical True Mark NFT taxonomy

### Completed

- Established the governed NFT type set as `H`, `K`, `L`, `B`, `HL`, `KL`, `LL`, `BL`, and `C`.
- Defined the `L` suffix as a licensable flag rather than a new color family.
- Mapped `HL` to H, `KL` to K, `LL` to L, and `BL` to B color profiles.
- Reserved `C` for Custom Contract NFT.
- Kept Enterprise as an Alpha CertSig Mint licensing model, separate from the True Mark NFT taxonomy.
- Added normalized metadata fields: `nft_type`, `base_type`, `licensable`, and `nft_color_profile`.
- Preserved legacy `*-NFT` values only as compatibility inputs; new records use canonical plain codes.
- Updated the mint UI, pricing, backend routes, certificate forge, assistant knowledge base, README, product documentation, and repository tree.

### Validation

- Taxonomy normalization passed for all nine governed types.
- Legacy `K-NFT` input correctly normalizes to `K`.
- Python compilation passed for the updated backend and forge modules.
- Frontend production build passed.
- `git diff --check` passed.
## 2026-09-29 — Independent CertSig registry verification

- Wired the Verify Record action to open `https://certsig.com/verify/{reference}`.
- Labeled CertSig as the independent public registry authority.
- Kept True Mark serial-based internal verification distinct from the NFT verifier.

## 2026-09-29 — Authority workflow and issuance hardening

- Replaced sample Object Workbench state with account-scoped persisted objects, staged evidence, and the enforced transition chain `WORKING_COPY → READY_FOR_REVIEW → COMMIT_PENDING → COMMITTED → SEALED`.
- Added explicit `COMMIT {object_id}` confirmation before committed evidence is recorded.
- Added atomic sealed-object manifests beneath the Vault runtime and linked lifecycle events to the ISS-stamped Vault audit chain.
- Added governed evidence acceptance checks: a profile fails when required proof is absent; layer depth is not a visual upgrade.
- Bound compatibility payment and digital-extension routes to the signed-in owner’s sealed object and matching profile. Unconfigured payment collection produces `payment_pending`, not a false payment-cleared claim.
- Migrated persisted pricing keys from legacy display aliases to the canonical `H`, `K`, `L`, `B`, `HL`, `KL`, `LL`, `BL`, `C` taxonomy while preserving configured prices.
- Removed forge publication of encryption key material, moved signing-key custody beneath Vault secrets, made local Vault writing functional, and removed fictional swarm-consensus reporting.
- Corrected ISS conversion for the 2000 TAI epoch and made system-clock provenance explicit unless an atomic adapter is supplied.

### Validation

- Python compilation passed for backend, ISS, and forge modules.
- Frontend production build passed.
- An integration lifecycle test created, committed, and sealed a p7 object with a generated canonical manifest.
- ISS epoch checks passed: the epoch is zero and 2000-01-01 UTC is 32 elapsed TAI seconds after the stated epoch.

## 2026-09-29 — Certificate example and release cleanup

- Added non-issued Vault examples for K, HL, L, and B color families, with matching 300-DPI PDF, PNG, and JPEG artifacts.
- Kept demonstration artifacts outside `certificates/issued/`, using fictional identifiers and a visible non-issued notice.
- Added visible ornamental and hex-grid frame rendering fallbacks plus signature and compact Tree watermark variants.
- Made the 1200px Tree asset the default print watermark and fixed square centering for the Tree and embedded text.
- Updated the forge Docker configuration to mount the entire authoritative Vault root in local mode rather than mock mode.
- Validated account signup, login, and authenticated object creation/listing before release.
