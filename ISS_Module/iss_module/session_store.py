"""Persistent local mission/session records for the ISS workstation widget."""

from __future__ import annotations

import json
import os
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from .core.utils import canonical_timestamp, get_iss_time_ns


MODULE_ROOT = Path(__file__).resolve().parents[1]
SESSION_STORE_PATH = Path(
    os.getenv("ISS_SESSION_STORE", str(MODULE_ROOT / "runtime" / "mission_sessions.json"))
).expanduser()
_LOCK = threading.Lock()


def _read() -> Dict[str, Any]:
    if not SESSION_STORE_PATH.exists():
        return {"active_session_id": None, "sessions": []}
    try:
        return json.loads(SESSION_STORE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"active_session_id": None, "sessions": []}


def _write(data: Dict[str, Any]) -> None:
    SESSION_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary = SESSION_STORE_PATH.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")
    temporary.replace(SESSION_STORE_PATH)


def _public_session(session: Dict[str, Any], now_ns: Optional[int] = None) -> Dict[str, Any]:
    result = dict(session)
    if result.get("status") == "active":
        result["mission_elapsed_ns"] = max(0, (now_ns or get_iss_time_ns()) - result["started_iss_time_ns"])
    elif result.get("ended_iss_time_ns") is not None:
        result["mission_elapsed_ns"] = max(0, result["ended_iss_time_ns"] - result["started_iss_time_ns"])
    return result


def current_session() -> Optional[Dict[str, Any]]:
    with _LOCK:
        data = _read()
        active_id = data.get("active_session_id")
        for session in data.get("sessions", []):
            if session.get("id") == active_id and session.get("status") == "active":
                return _public_session(session)
    return None


def start_session(label: str = "Work Session") -> Dict[str, Any]:
    with _LOCK:
        data = _read()
        if data.get("active_session_id"):
            raise ValueError("A mission session is already active.")
        now_ns = get_iss_time_ns()
        session = {
            "id": str(uuid.uuid4()),
            "label": label.strip() or "Work Session",
            "status": "active",
            "started_iss_time_ns": now_ns,
            "started_timestamp": canonical_timestamp(source="ISS Workstation Session"),
            "ended_iss_time_ns": None,
            "ended_timestamp": None,
        }
        data.setdefault("sessions", []).append(session)
        data["active_session_id"] = session["id"]
        _write(data)
        return _public_session(session, now_ns)


def end_session() -> Dict[str, Any]:
    with _LOCK:
        data = _read()
        active_id = data.get("active_session_id")
        for session in data.get("sessions", []):
            if session.get("id") == active_id and session.get("status") == "active":
                now_ns = get_iss_time_ns()
                session["status"] = "completed"
                session["ended_iss_time_ns"] = now_ns
                session["ended_timestamp"] = canonical_timestamp(
                    mission_epoch_ns=session["started_iss_time_ns"],
                    source="ISS Workstation Session",
                )
                data["active_session_id"] = None
                _write(data)
                return _public_session(session, now_ns)
    raise ValueError("No active mission session exists.")


def list_sessions(limit: int = 100) -> List[Dict[str, Any]]:
    with _LOCK:
        sessions = _read().get("sessions", [])
        return [_public_session(session) for session in list(reversed(sessions))[:limit]]
