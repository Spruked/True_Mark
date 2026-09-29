"""Append-only Vault audit events stamped by the ISS Scale."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

try:
    from iss_module.core.utils import canonical_timestamp
except ModuleNotFoundError:  # Allow execution from the backend directory.
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "ISS_Module"))
    from iss_module.core.utils import canonical_timestamp

try:
    from .vault_paths import AUDIT_ROOT, ensure_vault_layout
except ImportError:
    from vault_paths import AUDIT_ROOT, ensure_vault_layout


AUDIT_EVENTS_PATH = AUDIT_ROOT / "events.jsonl"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _previous_event_hash() -> str | None:
    if not AUDIT_EVENTS_PATH.exists():
        return None
    lines = AUDIT_EVENTS_PATH.read_text(encoding="utf-8").splitlines()
    line = lines[-1].strip() if lines else ""
    if not line:
        return None
    try:
        return json.loads(line).get("event_hash")
    except json.JSONDecodeError:
        return None


def record_vault_audit_event(
    event_type: str,
    subject_id: str,
    payload: Dict[str, Any] | None = None,
    actor_id: str | None = None,
) -> Dict[str, Any]:
    """Append one Vault event with the complete ISS timestamp envelope."""

    ensure_vault_layout()
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": event_type,
        "subject_id": subject_id,
        "actor_id": actor_id,
        "payload": payload or {},
        "iss_timestamp": canonical_timestamp(
            source="True Mark Vault System",
            clock_id="ISS-PRIMARY-ATOMIC-01",
        ),
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "previous_event_hash": _previous_event_hash(),
    }
    event["event_hash"] = hashlib.sha256(_canonical_json(event).encode("utf-8")).hexdigest()
    with AUDIT_EVENTS_PATH.open("a", encoding="utf-8") as stream:
        stream.write(_canonical_json(event) + "\n")
    return event
