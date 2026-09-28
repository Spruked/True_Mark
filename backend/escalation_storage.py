from __future__ import annotations

import json
import sqlite3
import uuid
from typing import Any, Dict, Optional

try:
    from .storage import get_connection, utc_now_iso
except ImportError:
    from storage import get_connection, utc_now_iso


def init_escalations() -> None:
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS escalation_cases (
                id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                object_id TEXT,
                reason_code TEXT NOT NULL,
                authorized_context_json TEXT NOT NULL DEFAULT '{}',
                status TEXT NOT NULL,
                assigned_agent_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                closed_at TEXT
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS escalation_messages (
                id TEXT PRIMARY KEY,
                case_id TEXT NOT NULL,
                sender_type TEXT NOT NULL CHECK(sender_type IN ('CUSTOMER','AGENT','SYSTEM')),
                sender_id TEXT,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        connection.execute("CREATE INDEX IF NOT EXISTS idx_escalation_cases_account ON escalation_cases(account_id)")
        connection.execute("CREATE INDEX IF NOT EXISTS idx_escalation_messages_case ON escalation_messages(case_id)")


def create_case(account_id: str, reason_code: str, object_id: Optional[str], context: Dict[str, Any]) -> Dict[str, Any]:
    init_escalations()
    case_id = f"CASE-TM-{uuid.uuid4().hex[:12].upper()}"
    now = utc_now_iso()
    with get_connection() as connection:
        connection.execute("INSERT INTO escalation_cases (id, account_id, object_id, reason_code, authorized_context_json, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (case_id, account_id, object_id, reason_code, json.dumps(context), "WAITING_FOR_AGENT", now, now))
    return get_case(case_id, account_id)


def get_case(case_id: str, account_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    init_escalations()
    with get_connection() as connection:
        query = "SELECT * FROM escalation_cases WHERE id = ?"
        params: list[Any] = [case_id]
        if account_id is not None:
            query += " AND account_id = ?"
            params.append(account_id)
        row = connection.execute(query, params).fetchone()
    if not row:
        return None
    case = dict(row)
    case["authorized_context"] = json.loads(case.pop("authorized_context_json") or "{}")
    return case


def add_message(case_id: str, account_id: str, sender_type: str, sender_id: str, message: str) -> bool:
    init_escalations()
    now = utc_now_iso()
    with get_connection() as connection:
        case = connection.execute("SELECT id FROM escalation_cases WHERE id = ? AND account_id = ? AND status NOT IN ('CLOSED', 'RESOLVED')", (case_id, account_id)).fetchone()
        if not case:
            return False
        connection.execute("INSERT INTO escalation_messages (id, case_id, sender_type, sender_id, message, created_at) VALUES (?, ?, ?, ?, ?, ?)", (str(uuid.uuid4()), case_id, sender_type, sender_id, message, now))
        connection.execute("UPDATE escalation_cases SET updated_at = ? WHERE id = ?", (now, case_id))
    return True


def close_case(case_id: str, account_id: Optional[str] = None) -> bool:
    init_escalations()
    now = utc_now_iso()
    with get_connection() as connection:
        query = "UPDATE escalation_cases SET status = 'CLOSED', closed_at = ?, updated_at = ? WHERE id = ? AND status NOT IN ('CLOSED', 'RESOLVED')"
        params: list[Any] = [now, now, case_id]
        if account_id is not None:
            query += " AND account_id = ?"
            params.append(account_id)
        cursor = connection.execute(query, params)
    return cursor.rowcount == 1


def assign_case(case_id: str, agent_id: str) -> bool:
    init_escalations()
    now = utc_now_iso()
    with get_connection() as connection:
        cursor = connection.execute(
            "UPDATE escalation_cases SET assigned_agent_id = ?, status = 'ASSIGNED', updated_at = ? WHERE id = ? AND status NOT IN ('CLOSED', 'RESOLVED')",
            (agent_id, now, case_id),
        )
    return cursor.rowcount == 1
