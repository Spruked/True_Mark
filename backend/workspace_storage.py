"""Persistent Perpetuum workspace records in the True Mark Vault DB."""

from __future__ import annotations

import json
import hashlib
from typing import Any, Dict

try:
    from .storage import get_connection, utc_now_iso
    from .vault_audit import record_vault_audit_event
except ImportError:
    from storage import get_connection, utc_now_iso
    from vault_audit import record_vault_audit_event


def init_workspaces() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS sanctum_workspaces (
                account_id TEXT PRIMARY KEY,
                workspace_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )


def get_workspace(account_id: str) -> Dict[str, Any] | None:
    init_workspaces()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT workspace_json FROM sanctum_workspaces WHERE account_id = ?",
            (account_id,),
        ).fetchone()
    if not row:
        return None
    return json.loads(row["workspace_json"])


def save_workspace(account_id: str, workspace: Dict[str, Any]) -> Dict[str, Any]:
    init_workspaces()
    now = utc_now_iso()
    payload = json.dumps(workspace, separators=(",", ":"), sort_keys=True)
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sanctum_workspaces (account_id, workspace_json, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(account_id) DO UPDATE SET
                workspace_json = excluded.workspace_json,
                updated_at = excluded.updated_at
            """,
            (account_id, payload, now),
        )
    record_vault_audit_event("WORKSPACE_SAVED", account_id, {"workspace_hash": hashlib.sha256(payload.encode()).hexdigest()}, account_id)
    return {**workspace, "updatedAt": now}
