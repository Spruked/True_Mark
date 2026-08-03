# TrueMark Launch-Readiness Recovery Contract

## Objective

Prepare TrueMark for a clean Website ORB deployment without contaminating or destabilizing the minting, payment, certificate, invoice, registry, or admin subsystems.

The production branch must reach a verified no-legacy-ORB baseline before the new Orb Weaver deployment is installed.

## Protected business boundary

The following capabilities are protected during the ORB cleanup and must not be rewritten casually:

- cart and checkout
- payment session creation and verification
- invoice and receipt generation
- mint authorization and mint submission
- smart-contract interaction
- certificate generation
- certificate and registry identifiers
- public registry exports
- account and admin persistence
- pricing and tax configuration
- customer delivery

Any change touching these areas requires a focused test and a rollback point.

## Current blocking workstreams

### 1. Legacy ORB removal

The production branch must contain no deployable legacy assistant runtime, endpoint, startup hook, public route, generated bundle, asset, or configuration requirement.

Historical code may be preserved through Git history or an archive branch, but it must not remain part of the production package.

Acceptance evidence:

- no legacy ORB mounted in the active frontend
- no legacy ORB route in the sitemap
- no old ORB API or voice listener
- no assistant-only environment variable required
- no stale ORB token in a clean production bundle
- minting and checkout behavior unchanged after removal

### 2. Checkout repair

A browser success page is not payment authority. Minting must be authorized only by a verified payment state.

Required order lifecycle:

```text
cart
-> checkout_started
-> payment_pending
-> payment_verified
-> mint_authorized
-> mint_submitted
-> minted
-> certificate_generated
-> registry_published
-> delivered
```

Failure and cancellation states must never initiate minting.

Acceptance evidence:

- totals and taxes reconcile
- customer and product data persist
- failed/cancelled payment creates no mint
- repeated callbacks do not create duplicate orders or mints
- refresh/restart does not lose authoritative state
- each order has one stable identifier chain

```text
order_id
-> payment_reference
-> mint_request_id
-> transaction_hash
-> certificate_id
-> registry_record_id
-> delivery_status
```

### 3. Certificate repair

The certificate is a customer-facing product artifact, not a debug report.

Required content:

- TrueMark identity and branding
- certificate title
- owner/recipient
- asset description
- certificate identifier
- mint/registry identifier
- network and transaction reference
- issuance date
- issuer
- verification URL and QR code
- authenticity statement
- readable, print-quality layout

The certificate pipeline must be separated into:

```text
canonical certificate record
-> validation
-> visual template
-> PDF render
-> integrity check
-> delivery
```

### 4. Canonical Vault merge

TrueMark must have one persistent source of truth.

The canonical Vault owns normalized local records for:

- customers and accounts
- carts, orders, payments, invoices, and receipts
- mint requests, transactions, and identifiers
- certificate records and rendered artifacts
- registry publication state
- workflow state
- website scans, Site World, and pointer maps
- Website ORB configuration, permissions, diagnostics, and memory
- deployment state, audit records, indexes, and persistent caches

External systems remain authoritative for external facts such as blockchain confirmations, payment settlement, and email delivery. The Vault stores identifiers, normalized state, timestamps, evidence, and last verification status.

No parallel JSON store, database, registry export, or runtime state file may remain silently authoritative outside the Vault.

## Required migration discipline

Before moving persistent data:

1. inventory every current data location
2. classify each source as canonical, external authority, derived/cache, secret, generated output, or legacy data
3. create a backup snapshot
4. map identifiers and schemas
5. calculate checksums where practical
6. migrate without deleting originals
7. verify counts and references
8. make old sources read-only
9. exercise rollback
10. remove old authority only after acceptance

## Immediate repository checks

Run:

```bash
python tools/truemark_readiness_audit.py
python tools/truemark_readiness_audit.py --json > /tmp/truemark-readiness.json
```

The audit is read-only. A blocker result is expected until stale ORB routes, generated bundles, and deployable legacy assistant code are removed.

## Execution order

1. tag the current production baseline
2. run and save the readiness audit
3. record checkout/mint/certificate acceptance behavior
4. remove legacy ORB deployment surfaces
5. rebuild and verify the no-ORB site
6. repair checkout authority and idempotency
7. repair certificate record and visual rendering
8. merge persistence into the canonical Vault
9. rerun all business-flow acceptance tests
10. scan the clean site through Orb Weaver
11. install the new Website ORB
12. manufacture the customer Dock Station
13. complete clean-machine acceptance

## Sale gate

TrueMark is not a valid Orb Weaver proof site until all of the following are true:

- checkout completes reliably in test mode
- failed payment cannot mint
- one verified order cannot mint twice
- certificate PDF is professional and accurate
- registry identifiers reconcile
- one Vault provides the local source of truth
- no legacy ORB exists in deployable output
- new Website ORB voice, pointer, and approved tools are proven
- customer Dock Station installs and reports truthfully on a clean machine
