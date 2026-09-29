"""Authoritative True Mark Vault System paths.

All mutable runtime state, customer artifacts, exports, and operational
records belong under ``True_Mark_Vault_System``. Code may keep its executable
modules in the application repository, but it must not create a parallel
runtime store under ``backend/data`` or another application-local directory.
"""

from __future__ import annotations

import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
_configured_root = os.getenv("TRUEMARK_VAULT_ROOT", "").strip()
VAULT_ROOT = (
    Path(_configured_root).expanduser()
    if _configured_root
    else PROJECT_ROOT / "True_Mark_Vault_System"
)
if not VAULT_ROOT.is_absolute():
    VAULT_ROOT = PROJECT_ROOT / VAULT_ROOT

RUNTIME_ROOT = VAULT_ROOT / "runtime"
DATABASE_PATH = RUNTIME_ROOT / "truemark.db"
PAYMENT_SESSIONS_ROOT = RUNTIME_ROOT / "payment_sessions"
INVOICES_ROOT = RUNTIME_ROOT / "invoices"
VAULT_PACKAGES_ROOT = RUNTIME_ROOT / "vault_packages"
RECEIPTS_ROOT = RUNTIME_ROOT / "receipts"
MAIL_OUTBOX_ROOT = RUNTIME_ROOT / "mail_outbox"
DALS_EXPORTS_ROOT = RUNTIME_ROOT / "dals_exports"
ESCALATION_ROOT = RUNTIME_ROOT / "escalations"
CERTIFICATES_ROOT = VAULT_ROOT / "certificates" / "issued"
AUDIT_ROOT = VAULT_ROOT / "audit"
SECRETS_ROOT = VAULT_ROOT / "secrets"


def ensure_vault_layout() -> Path:
    for path in (
        RUNTIME_ROOT,
        PAYMENT_SESSIONS_ROOT,
        INVOICES_ROOT,
        VAULT_PACKAGES_ROOT,
        RECEIPTS_ROOT,
        MAIL_OUTBOX_ROOT,
        DALS_EXPORTS_ROOT,
        ESCALATION_ROOT,
        CERTIFICATES_ROOT,
        AUDIT_ROOT,
        SECRETS_ROOT,
    ):
        path.mkdir(parents=True, exist_ok=True)
    return VAULT_ROOT
