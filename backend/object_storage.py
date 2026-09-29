"""Account-owned Object → Evidence → Commit → Seal persistence.

This module is deliberately separate from the mutable Perpetuum workspace.
An object becomes authoritative only through the governed transition methods
below; the sealed manifest is written beneath the Vault root and an ISS-stamped
audit event is appended for each material transition.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable

try:
    from .certificate_profiles import build_certificate_manifest, get_certificate_profile, manifest_hash, validate_evidence_acceptance
    from .secretum_models import ProjectState, require_transition
    from .storage import get_connection
    from .vault_audit import record_vault_audit_event
    from .vault_paths import RUNTIME_ROOT, ensure_vault_layout
except ImportError:
    from certificate_profiles import build_certificate_manifest, get_certificate_profile, manifest_hash, validate_evidence_acceptance
    from secretum_models import ProjectState, require_transition
    from storage import get_connection
    from vault_audit import record_vault_audit_event
    from vault_paths import RUNTIME_ROOT, ensure_vault_layout


OBJECT_EVIDENCE_ROOT = RUNTIME_ROOT / "object_evidence"
SEALED_OBJECTS_ROOT = RUNTIME_ROOT / "sealed_objects"
_SAFE_FILENAME = re.compile(r"[^A-Za-z0-9._-]+")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _json(value: Any) -> str:
    return json.dumps(value or {}, sort_keys=True, separators=(",", ":"))


def _decode(value: str | None) -> Any:
    return json.loads(value) if value else {}


def _row(row: sqlite3.Row | None, evidence: Iterable[Dict[str, Any]] = ()) -> Dict[str, Any] | None:
    if not row:
        return None
    result = dict(row)
    for key in ("provenance", "ownership", "notes", "manifest"):
        result[key] = _decode(result.pop(f"{key}_json", None))
    result["evidence"] = list(evidence)
    return result


def init_object_store() -> None:
    ensure_vault_layout()
    OBJECT_EVIDENCE_ROOT.mkdir(parents=True, exist_ok=True)
    SEALED_OBJECTS_ROOT.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS vault_objects (
                id TEXT PRIMARY KEY, account_id TEXT NOT NULL, title TEXT NOT NULL,
                object_type TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
                certificate_profile TEXT NOT NULL DEFAULT 'p2', state TEXT NOT NULL,
                provenance_json TEXT NOT NULL DEFAULT '{}', ownership_json TEXT NOT NULL DEFAULT '{}',
                notes_json TEXT NOT NULL DEFAULT '{}', manifest_json TEXT, manifest_hash TEXT,
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL, committed_at TEXT, sealed_at TEXT
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS vault_object_evidence (
                id TEXT PRIMARY KEY, object_id TEXT NOT NULL, filename TEXT NOT NULL,
                sha256 TEXT NOT NULL, size_bytes INTEGER NOT NULL, stored_path TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}', state TEXT NOT NULL,
                created_at TEXT NOT NULL, committed_at TEXT,
                FOREIGN KEY(object_id) REFERENCES vault_objects(id)
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_vault_objects_account ON vault_objects(account_id, updated_at DESC)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_vault_evidence_object ON vault_object_evidence(object_id)")


def _evidence(connection: sqlite3.Connection, object_id: str) -> list[Dict[str, Any]]:
    rows = connection.execute("SELECT * FROM vault_object_evidence WHERE object_id = ? ORDER BY created_at", (object_id,)).fetchall()
    return [{**dict(row), "metadata": _decode(row["metadata_json"])} for row in rows]


def get_object(account_id: str, object_id: str) -> Dict[str, Any] | None:
    init_object_store()
    with get_connection() as connection:
        row = connection.execute("SELECT * FROM vault_objects WHERE id = ? AND account_id = ?", (object_id, account_id)).fetchone()
        return _row(row, _evidence(connection, object_id))


def list_objects(account_id: str, state: str | None = None) -> list[Dict[str, Any]]:
    init_object_store()
    with get_connection() as connection:
        params: list[str] = [account_id]
        sql = "SELECT * FROM vault_objects WHERE account_id = ?"
        if state:
            sql += " AND state = ?"
            params.append(state)
        sql += " ORDER BY updated_at DESC"
        return [_row(row, _evidence(connection, row["id"])) for row in connection.execute(sql, params).fetchall()]


def create_object(account_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    init_object_store()
    title = str(payload.get("title", "")).strip()
    if not title:
        raise ValueError("An object title is required.")
    profile = str(payload.get("certificate_profile", "p2"))
    get_certificate_profile(profile)
    object_id, now = str(uuid.uuid4()), _now()
    with get_connection() as connection:
        connection.execute("""INSERT INTO vault_objects
            (id, account_id, title, object_type, description, certificate_profile, state, provenance_json, ownership_json, notes_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (object_id, account_id, title, str(payload.get("object_type", "object")).strip() or "object",
             str(payload.get("description", "")), profile, ProjectState.WORKING_COPY.value,
             _json(payload.get("provenance")), _json(payload.get("ownership")), _json(payload.get("notes")), now, now))
    record_vault_audit_event("OBJECT_CREATED", object_id, {"title": title, "certificate_profile": profile}, account_id)
    return get_object(account_id, object_id)  # type: ignore[return-value]


def update_object(account_id: str, object_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    current = get_object(account_id, object_id)
    if not current:
        raise LookupError("Object not found.")
    if current["state"] not in {ProjectState.WORKING_COPY.value, ProjectState.READY_FOR_REVIEW.value}:
        raise ValueError("A committed or sealed object cannot be edited.")
    profile = str(payload.get("certificate_profile", current["certificate_profile"]))
    get_certificate_profile(profile)
    with get_connection() as connection:
        connection.execute("""UPDATE vault_objects SET title=?, object_type=?, description=?, certificate_profile=?, provenance_json=?, ownership_json=?, notes_json=?, updated_at=? WHERE id=? AND account_id=?""",
            (str(payload.get("title", current["title"])).strip() or current["title"], str(payload.get("object_type", current["object_type"])),
             str(payload.get("description", current["description"])), profile, _json(payload.get("provenance", current["provenance"])),
             _json(payload.get("ownership", current["ownership"])), _json(payload.get("notes", current["notes"])), _now(), object_id, account_id))
    record_vault_audit_event("OBJECT_UPDATED", object_id, {"certificate_profile": profile}, account_id)
    return get_object(account_id, object_id)  # type: ignore[return-value]


def add_evidence(account_id: str, object_id: str, filename: str, source_path: Path, metadata: Dict[str, Any] | None = None) -> Dict[str, Any]:
    current = get_object(account_id, object_id)
    if not current:
        raise LookupError("Object not found.")
    if current["state"] != ProjectState.WORKING_COPY.value:
        raise ValueError("Evidence may be added only while the object is a working copy.")
    safe_name = _SAFE_FILENAME.sub("_", Path(filename).name).strip("._") or "evidence.bin"
    evidence_id = str(uuid.uuid4())
    destination = OBJECT_EVIDENCE_ROOT / account_id / object_id / f"{evidence_id}_{safe_name}"
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    now = _now()
    with get_connection() as connection:
        connection.execute("INSERT INTO vault_object_evidence (id, object_id, filename, sha256, size_bytes, stored_path, metadata_json, state, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (evidence_id, object_id, safe_name, digest, destination.stat().st_size, str(destination), _json(metadata), "STAGED", now))
        connection.execute("UPDATE vault_objects SET updated_at=? WHERE id=?", (now, object_id))
    record_vault_audit_event("EVIDENCE_STAGED", evidence_id, {"object_id": object_id, "sha256": digest, "filename": safe_name}, account_id)
    return {"id": evidence_id, "filename": safe_name, "sha256": digest, "size_bytes": destination.stat().st_size, "state": "STAGED"}


def _assert_ready(current: Dict[str, Any]) -> None:
    if not current["evidence"]:
        raise ValueError("At least one evidence file is required before review.")


def transition_object(account_id: str, object_id: str, target_state: str, confirmation: str | None = None) -> Dict[str, Any]:
    current = get_object(account_id, object_id)
    if not current:
        raise LookupError("Object not found.")
    try:
        target = ProjectState(target_state)
        require_transition(ProjectState(current["state"]), target)
    except (ValueError, KeyError) as error:
        raise ValueError(str(error)) from error
    if target == ProjectState.READY_FOR_REVIEW:
        _assert_ready(current)
    if target == ProjectState.COMMITTED:
        if confirmation != f"COMMIT {object_id}":
            raise ValueError("Commit requires the explicit confirmation phrase for this object.")
    now = _now()
    with get_connection() as connection:
        connection.execute("UPDATE vault_objects SET state=?, updated_at=?, committed_at=CASE WHEN ?='COMMITTED' THEN ? ELSE committed_at END WHERE id=? AND account_id=?", (target.value, now, target.value, now, object_id, account_id))
        if target == ProjectState.COMMITTED:
            connection.execute("UPDATE vault_object_evidence SET state='COMMITTED', committed_at=? WHERE object_id=?", (now, object_id))
    record_vault_audit_event(f"OBJECT_{target.value}", object_id, {"from": current["state"], "to": target.value}, account_id)
    return get_object(account_id, object_id)  # type: ignore[return-value]


def seal_object(account_id: str, object_id: str) -> Dict[str, Any]:
    current = get_object(account_id, object_id)
    if not current:
        raise LookupError("Object not found.")
    if current["state"] != ProjectState.COMMITTED.value:
        raise ValueError("Only a committed object can be sealed.")
    profile = get_certificate_profile(current["certificate_profile"])
    facts = {
        "object_id": object_id, "account_id": account_id, "title": current["title"], "object_type": current["object_type"],
        "description": current["description"], "provenance": current["provenance"], "ownership": current["ownership"],
        "evidence": [{key: item[key] for key in ("id", "filename", "sha256", "size_bytes", "state", "created_at", "committed_at")} for item in current["evidence"]],
        "committed_at": current["committed_at"],
    }
    validate_evidence_acceptance(current["certificate_profile"], facts)
    manifest = build_certificate_manifest(current["certificate_profile"], facts)
    digest = manifest_hash(manifest)
    sealed_record = {"object_id": object_id, "state": "SEALED", "manifest": manifest, "manifest_hash": digest, "sealed_at": _now()}
    target = SEALED_OBJECTS_ROOT / f"{object_id}.json"
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(sealed_record, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, target)
    with get_connection() as connection:
        connection.execute("UPDATE vault_objects SET state=?, manifest_json=?, manifest_hash=?, sealed_at=?, updated_at=? WHERE id=? AND account_id=?", (ProjectState.SEALED.value, _json(manifest), digest, sealed_record["sealed_at"], sealed_record["sealed_at"], object_id, account_id))
    event = record_vault_audit_event("OBJECT_SEALED", object_id, {"manifest_hash": digest, "profile": profile["name"], "sealed_record": str(target)}, account_id)
    sealed_record["audit_event_hash"] = event["event_hash"]
    temporary.write_text(json.dumps(sealed_record, indent=2, sort_keys=True), encoding="utf-8")
    os.replace(temporary, target)
    return get_object(account_id, object_id)  # type: ignore[return-value]
