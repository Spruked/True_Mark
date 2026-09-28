# True Mark Development Log

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
