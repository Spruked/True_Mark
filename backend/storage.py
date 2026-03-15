from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "truemark.db"
load_dotenv(BASE_DIR / ".env")


USER_COLUMNS = {
    "id": "TEXT",
    "name": "TEXT",
    "email": "TEXT",
    "password_hash": "TEXT",
    "address_line1": "TEXT",
    "address_line2": "TEXT",
    "city": "TEXT",
    "state": "TEXT",
    "postal_code": "TEXT",
    "phone": "TEXT",
    "dob": "TEXT",
    "marketing": "INTEGER NOT NULL DEFAULT 0",
    "created_at": "TEXT",
    "updated_at": "TEXT",
}

ORDER_COLUMNS = {
    "id": "TEXT",
    "serial": "TEXT",
    "nft_identifier": "TEXT",
    "type_code": "TEXT",
    "node_id": "TEXT",
    "region_code": "TEXT",
    "registrant_code": "TEXT",
    "identifier_year": "INTEGER",
    "identifier_sequence": "INTEGER",
    "invoice_number": "TEXT",
    "invoice_public_token": "TEXT",
    "vault_public_token": "TEXT",
    "payment_reference": "TEXT",
    "receipt_number": "TEXT",
    "user_id": "TEXT",
    "user_email": "TEXT",
    "user_name": "TEXT",
    "billing_address_line1": "TEXT",
    "billing_address_line2": "TEXT",
    "billing_city": "TEXT",
    "billing_state": "TEXT",
    "billing_postal_code": "TEXT",
    "billing_phone": "TEXT",
    "billing_dob": "TEXT",
    "prefix": "TEXT",
    "industry": "TEXT",
    "nft_type": "TEXT",
    "package_tier": "TEXT",
    "encryption": "TEXT",
    "chain": "TEXT",
    "quantity": "INTEGER NOT NULL DEFAULT 1",
    "file_name": "TEXT",
    "estimated_storage_gb": "REAL NOT NULL DEFAULT 0",
    "subtotal_usd": "REAL NOT NULL DEFAULT 0",
    "tax_rate": "REAL NOT NULL DEFAULT 0",
    "tax_state": "TEXT",
    "tax_amount_usd": "REAL NOT NULL DEFAULT 0",
    "processing_fee_usd": "REAL NOT NULL DEFAULT 0",
    "discount_amount_usd": "REAL NOT NULL DEFAULT 0",
    "total_usd": "REAL NOT NULL DEFAULT 0",
    "payment_method": "TEXT NOT NULL DEFAULT 'fiat'",
    "crypto_token": "TEXT",
    "crypto_spot_price_usd": "REAL",
    "quote_snapshot_json": "TEXT",
    "invoice_email_status": "TEXT NOT NULL DEFAULT 'pending'",
    "invoice_sent_to": "TEXT",
    "invoice_emailed_at": "TEXT",
    "status": "TEXT NOT NULL DEFAULT 'completed'",
    "created_at": "TEXT",
}

PAYMENT_SESSION_COLUMNS = {
    "id": "TEXT",
    "payment_reference": "TEXT",
    "payment_public_token": "TEXT",
    "receipt_number": "TEXT",
    "receipt_public_token": "TEXT",
    "type_code": "TEXT",
    "node_id": "TEXT",
    "region_code": "TEXT",
    "registrant_code": "TEXT",
    "user_id": "TEXT",
    "user_email": "TEXT",
    "user_name": "TEXT",
    "billing_address_line1": "TEXT",
    "billing_address_line2": "TEXT",
    "billing_city": "TEXT",
    "billing_state": "TEXT",
    "billing_postal_code": "TEXT",
    "billing_phone": "TEXT",
    "billing_dob": "TEXT",
    "prefix": "TEXT",
    "industry": "TEXT",
    "nft_type": "TEXT",
    "package_tier": "TEXT",
    "encryption": "TEXT",
    "chain": "TEXT",
    "quantity": "INTEGER NOT NULL DEFAULT 1",
    "file_name": "TEXT",
    "staged_file_path": "TEXT",
    "estimated_storage_gb": "REAL NOT NULL DEFAULT 0",
    "metadata_json": "TEXT",
    "subtotal_usd": "REAL NOT NULL DEFAULT 0",
    "tax_rate": "REAL NOT NULL DEFAULT 0",
    "tax_state": "TEXT",
    "tax_amount_usd": "REAL NOT NULL DEFAULT 0",
    "processing_fee_usd": "REAL NOT NULL DEFAULT 0",
    "discount_amount_usd": "REAL NOT NULL DEFAULT 0",
    "total_usd": "REAL NOT NULL DEFAULT 0",
    "payment_method": "TEXT NOT NULL DEFAULT 'fiat'",
    "crypto_token": "TEXT",
    "crypto_spot_price_usd": "REAL",
    "quote_snapshot_json": "TEXT",
    "cancellation_fee_usd": "REAL NOT NULL DEFAULT 5.0",
    "refund_due_usd": "REAL",
    "minted_order_id": "TEXT",
    "minted_serial": "TEXT",
    "minted_nft_identifier": "TEXT",
    "minted_invoice_number": "TEXT",
    "payment_captured_at": "TEXT",
    "canceled_at": "TEXT",
    "minted_at": "TEXT",
    "status": "TEXT NOT NULL DEFAULT 'payment_cleared'",
    "created_at": "TEXT",
    "updated_at": "TEXT",
}

MINT_EVENT_COLUMNS = {
    "id": "TEXT",
    "order_id": "TEXT",
    "payment_reference": "TEXT",
    "receipt_number": "TEXT",
    "invoice_number": "TEXT",
    "serial": "TEXT",
    "nft_identifier": "TEXT",
    "type_code": "TEXT",
    "node_id": "TEXT",
    "region_code": "TEXT",
    "registrant_code": "TEXT",
    "identifier_year": "INTEGER",
    "identifier_sequence": "INTEGER",
    "prefix": "TEXT",
    "industry": "TEXT",
    "nft_type": "TEXT",
    "package_tier": "TEXT",
    "encryption": "TEXT",
    "chain": "TEXT",
    "quantity": "INTEGER NOT NULL DEFAULT 1",
    "user_id": "TEXT",
    "user_email": "TEXT",
    "user_name": "TEXT",
    "file_name": "TEXT",
    "metadata_json": "TEXT",
    "payment_method": "TEXT",
    "subtotal_usd": "REAL NOT NULL DEFAULT 0",
    "tax_amount_usd": "REAL NOT NULL DEFAULT 0",
    "total_usd": "REAL NOT NULL DEFAULT 0",
    "minted_at": "TEXT",
    "created_at": "TEXT",
}


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def normalize_identifier_component(value: str | None, fallback: str) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", "", (value or "").upper())
    return cleaned or fallback


NFT_TYPE_CODE_MAP = {
    "K-NFT": "KNFT",
    "H-NFT": "HNFT",
    "L-NFT": "LNFT",
    "C-NFT": "CNFT",
}


def get_nft_type_code(nft_type: str | None) -> str:
    normalized_nft_type = (nft_type or "").strip().upper()
    return NFT_TYPE_CODE_MAP.get(normalized_nft_type, normalize_identifier_component(normalized_nft_type, "NFT"))


def get_mint_node_id() -> str:
    return normalize_identifier_component(os.getenv("TRUEMARK_NODE_ID", "TM01"), "TM01")


def get_default_region_code() -> str:
    return normalize_identifier_component(os.getenv("TRUEMARK_REGION_CODE", "US"), "US")


def get_mint_standard() -> Dict[str, Any]:
    return {
        "identifier_format": "TYPE-NODE-REGION-YEAR-USER-SEQ",
        "node_id": get_mint_node_id(),
        "region_code": get_default_region_code(),
        "type_codes": NFT_TYPE_CODE_MAP,
    }


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def _table_columns(connection: sqlite3.Connection, table_name: str) -> set[str]:
    rows = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    return {row["name"] for row in rows}


def _ensure_columns(connection: sqlite3.Connection, table_name: str, columns: Dict[str, str]) -> None:
    existing_columns = _table_columns(connection, table_name)

    for column_name, column_definition in columns.items():
        if column_name in existing_columns:
            continue

        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
        )


def _ensure_indexes(connection: sqlite3.Connection) -> None:
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_serial ON orders(serial)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_nft_identifier ON orders(nft_identifier)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_invoice_number ON orders(invoice_number)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_invoice_public_token ON orders(invoice_public_token)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_vault_public_token ON orders(vault_public_token)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_payment_reference ON orders(payment_reference)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_receipt_number ON orders(receipt_number)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_sessions_reference ON payment_sessions(payment_reference)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_sessions_public_token ON payment_sessions(payment_public_token)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_sessions_receipt_number ON payment_sessions(receipt_number)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_sessions_receipt_public_token ON payment_sessions(receipt_public_token)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_payment_sessions_minted_nft_identifier ON payment_sessions(minted_nft_identifier)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mint_events_nft_identifier ON mint_events(nft_identifier)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_mint_events_order_id ON mint_events(order_id)"
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_mint_events_registry_components ON mint_events(node_id, region_code, registrant_code, identifier_year, identifier_sequence)"
    )


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                address_line1 TEXT,
                address_line2 TEXT,
                city TEXT,
                state TEXT,
                postal_code TEXT,
                phone TEXT,
                dob TEXT,
                marketing INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                serial TEXT NOT NULL UNIQUE,
                nft_identifier TEXT UNIQUE,
                type_code TEXT,
                node_id TEXT,
                region_code TEXT,
                registrant_code TEXT,
                identifier_year INTEGER,
                identifier_sequence INTEGER,
                invoice_number TEXT,
                invoice_public_token TEXT,
                vault_public_token TEXT,
                payment_reference TEXT,
                receipt_number TEXT,
                user_id TEXT,
                user_email TEXT NOT NULL,
                user_name TEXT NOT NULL,
                billing_address_line1 TEXT,
                billing_address_line2 TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_postal_code TEXT,
                billing_phone TEXT,
                billing_dob TEXT,
                prefix TEXT,
                industry TEXT,
                nft_type TEXT NOT NULL,
                package_tier TEXT NOT NULL,
                encryption TEXT NOT NULL,
                chain TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                file_name TEXT,
                estimated_storage_gb REAL NOT NULL DEFAULT 0,
                subtotal_usd REAL NOT NULL DEFAULT 0,
                tax_rate REAL NOT NULL DEFAULT 0,
                tax_state TEXT,
                tax_amount_usd REAL NOT NULL DEFAULT 0,
                processing_fee_usd REAL NOT NULL DEFAULT 0,
                discount_amount_usd REAL NOT NULL DEFAULT 0,
                total_usd REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT 'fiat',
                crypto_token TEXT,
                crypto_spot_price_usd REAL,
                quote_snapshot_json TEXT,
                invoice_email_status TEXT NOT NULL DEFAULT 'pending',
                invoice_sent_to TEXT,
                invoice_emailed_at TEXT,
                status TEXT NOT NULL DEFAULT 'completed',
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_sessions (
                id TEXT PRIMARY KEY,
                payment_reference TEXT NOT NULL UNIQUE,
                payment_public_token TEXT NOT NULL UNIQUE,
                receipt_number TEXT NOT NULL UNIQUE,
                receipt_public_token TEXT NOT NULL UNIQUE,
                type_code TEXT,
                node_id TEXT,
                region_code TEXT,
                registrant_code TEXT,
                user_id TEXT,
                user_email TEXT NOT NULL,
                user_name TEXT NOT NULL,
                billing_address_line1 TEXT,
                billing_address_line2 TEXT,
                billing_city TEXT,
                billing_state TEXT,
                billing_postal_code TEXT,
                billing_phone TEXT,
                billing_dob TEXT,
                prefix TEXT,
                industry TEXT,
                nft_type TEXT NOT NULL,
                package_tier TEXT NOT NULL,
                encryption TEXT NOT NULL,
                chain TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                file_name TEXT,
                staged_file_path TEXT,
                estimated_storage_gb REAL NOT NULL DEFAULT 0,
                metadata_json TEXT,
                subtotal_usd REAL NOT NULL DEFAULT 0,
                tax_rate REAL NOT NULL DEFAULT 0,
                tax_state TEXT,
                tax_amount_usd REAL NOT NULL DEFAULT 0,
                processing_fee_usd REAL NOT NULL DEFAULT 0,
                discount_amount_usd REAL NOT NULL DEFAULT 0,
                total_usd REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT 'fiat',
                crypto_token TEXT,
                crypto_spot_price_usd REAL,
                quote_snapshot_json TEXT,
                cancellation_fee_usd REAL NOT NULL DEFAULT 5.0,
                refund_due_usd REAL,
                minted_order_id TEXT,
                minted_serial TEXT,
                minted_nft_identifier TEXT,
                minted_invoice_number TEXT,
                payment_captured_at TEXT,
                canceled_at TEXT,
                minted_at TEXT,
                status TEXT NOT NULL DEFAULT 'payment_cleared',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS mint_events (
                id TEXT PRIMARY KEY,
                order_id TEXT NOT NULL UNIQUE,
                payment_reference TEXT,
                receipt_number TEXT,
                invoice_number TEXT,
                serial TEXT NOT NULL,
                nft_identifier TEXT NOT NULL UNIQUE,
                type_code TEXT,
                node_id TEXT,
                region_code TEXT,
                registrant_code TEXT,
                identifier_year INTEGER,
                identifier_sequence INTEGER,
                prefix TEXT,
                industry TEXT,
                nft_type TEXT NOT NULL,
                package_tier TEXT,
                encryption TEXT,
                chain TEXT,
                quantity INTEGER NOT NULL DEFAULT 1,
                user_id TEXT,
                user_email TEXT,
                user_name TEXT,
                file_name TEXT,
                metadata_json TEXT,
                payment_method TEXT,
                subtotal_usd REAL NOT NULL DEFAULT 0,
                tax_amount_usd REAL NOT NULL DEFAULT 0,
                total_usd REAL NOT NULL DEFAULT 0,
                minted_at TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        _ensure_columns(connection, "users", USER_COLUMNS)
        _ensure_columns(connection, "orders", ORDER_COLUMNS)
        _ensure_columns(connection, "payment_sessions", PAYMENT_SESSION_COLUMNS)
        _ensure_columns(connection, "mint_events", MINT_EVENT_COLUMNS)
        _ensure_indexes(connection)


def _public_user(row: sqlite3.Row) -> Dict[str, Any]:
    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "address_line1": row["address_line1"] or "",
        "address_line2": row["address_line2"] or "",
        "city": row["city"] or "",
        "state": row["state"] or "",
        "postal_code": row["postal_code"] or "",
        "phone": row["phone"] or "",
        "dob": row["dob"] or "",
        "marketing": bool(row["marketing"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def _public_order(row: sqlite3.Row) -> Dict[str, Any]:
    order = dict(row)

    if order.get("quote_snapshot_json"):
        try:
            order["quote_snapshot"] = json.loads(order["quote_snapshot_json"])
        except json.JSONDecodeError:
            order["quote_snapshot"] = None
    else:
        order["quote_snapshot"] = None

    order.pop("quote_snapshot_json", None)
    return order


def _public_payment_session(row: sqlite3.Row) -> Dict[str, Any]:
    session = dict(row)

    if session.get("quote_snapshot_json"):
        try:
            session["quote_snapshot"] = json.loads(session["quote_snapshot_json"])
        except json.JSONDecodeError:
            session["quote_snapshot"] = None
    else:
        session["quote_snapshot"] = None

    if session.get("metadata_json"):
        try:
            session["metadata"] = json.loads(session["metadata_json"])
        except json.JSONDecodeError:
            session["metadata"] = session["metadata_json"]
    else:
        session["metadata"] = {}

    session.pop("quote_snapshot_json", None)
    return session


def _public_mint_event(row: sqlite3.Row) -> Dict[str, Any]:
    mint_event = dict(row)

    if mint_event.get("metadata_json"):
        try:
            mint_event["metadata"] = json.loads(mint_event["metadata_json"])
        except json.JSONDecodeError:
            mint_event["metadata"] = mint_event["metadata_json"]
    else:
        mint_event["metadata"] = {}

    mint_event.pop("metadata_json", None)
    return mint_event


def hash_password(password: str, salt: str | None = None) -> str:
    active_salt = salt or os.urandom(16).hex()
    derived = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        active_salt.encode("utf-8"),
        200_000,
    ).hex()
    return f"{active_salt}${derived}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, digest = stored_hash.split("$", 1)
    except ValueError:
        return False

    return hmac.compare_digest(hash_password(password, salt), f"{salt}${digest}")


def create_user(account: Dict[str, Any]) -> Dict[str, Any]:
    normalized_email = account["email"].strip().lower()
    now = utc_now_iso()
    row = {
        "id": str(uuid.uuid4()),
        "name": account["name"].strip(),
        "email": normalized_email,
        "password_hash": hash_password(account["password"]),
        "address_line1": account.get("address_line1", "").strip(),
        "address_line2": account.get("address_line2", "").strip(),
        "city": account.get("city", "").strip(),
        "state": account.get("state", "").strip().upper(),
        "postal_code": account.get("postal_code", "").strip(),
        "phone": account.get("phone", "").strip(),
        "dob": account.get("dob", "").strip(),
        "marketing": 1 if account.get("marketing") else 0,
        "created_at": now,
        "updated_at": now,
    }

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (
                    id, name, email, password_hash, address_line1, address_line2,
                    city, state, postal_code, phone, dob, marketing, created_at, updated_at
                ) VALUES (
                    :id, :name, :email, :password_hash, :address_line1, :address_line2,
                    :city, :state, :postal_code, :phone, :dob, :marketing, :created_at, :updated_at
                )
                """,
                row,
            )
    except sqlite3.IntegrityError as error:
        raise ValueError("An account with this email already exists.") from error

    return {
        "id": row["id"],
        "name": row["name"],
        "email": row["email"],
        "address_line1": row["address_line1"],
        "address_line2": row["address_line2"],
        "city": row["city"],
        "state": row["state"],
        "postal_code": row["postal_code"],
        "phone": row["phone"],
        "dob": row["dob"],
        "marketing": bool(row["marketing"]),
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def authenticate_user(email: str, password: str) -> Dict[str, Any]:
    normalized_email = email.strip().lower()

    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()

    if not row or not verify_password(password, row["password_hash"]):
        raise ValueError("That email and password do not match a saved account.")

    return _public_user(row)


def get_user_by_email(email: str | None) -> Optional[Dict[str, Any]]:
    if not email:
        return None

    normalized_email = email.strip().lower()
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE email = ?",
            (normalized_email,),
        ).fetchone()

    return _public_user(row) if row else None


def list_users() -> List[Dict[str, Any]]:
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM users ORDER BY datetime(created_at) DESC"
        ).fetchall()

    return [_public_user(row) for row in rows]


def get_next_truemark_serial() -> str:
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT serial
            FROM orders
            WHERE serial LIKE 'TM-%'
            ORDER BY CAST(SUBSTR(serial, 4) AS INTEGER) DESC
            LIMIT 1
            """
        ).fetchone()

    if not row:
        return "TM-00001"

    last_serial = row["serial"]
    last_value = int(last_serial.split("-", 1)[1])
    return f"TM-{last_value + 1:05d}"


def get_next_nft_identifier(
    nft_type: str,
    node_id: str | None,
    region_code: str | None,
    registrant_code: str | None,
    minted_at: str | None = None,
) -> tuple[str, int, int, str]:
    year = parse_iso_datetime(minted_at).year if minted_at else datetime.now(timezone.utc).year
    type_code = get_nft_type_code(nft_type)
    normalized_node_id = normalize_identifier_component(node_id, get_mint_node_id())
    normalized_region_code = normalize_identifier_component(region_code, get_default_region_code())
    normalized_registrant_code = normalize_identifier_component(registrant_code, "PUBLIC")

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT identifier_sequence
            FROM mint_events
            WHERE node_id = ? AND region_code = ? AND registrant_code = ? AND identifier_year = ?
            ORDER BY identifier_sequence DESC
            LIMIT 1
            """,
            (normalized_node_id, normalized_region_code, normalized_registrant_code, year),
        ).fetchone()

    if not row or row["identifier_sequence"] is None:
        next_counter = 1
    else:
        next_counter = int(row["identifier_sequence"]) + 1

    identifier = f"{type_code}-{normalized_node_id}-{normalized_region_code}-{year}-{normalized_registrant_code}-{next_counter:06d}"
    return identifier, year, next_counter, type_code


def get_next_invoice_number() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT invoice_number
            FROM orders
            WHERE invoice_number LIKE ?
            ORDER BY invoice_number DESC
            LIMIT 1
            """,
            (f"TMI-{stamp}-%",),
        ).fetchone()

    if not row or not row["invoice_number"]:
        return f"TMI-{stamp}-00001"

    last_counter = int(row["invoice_number"].split("-")[-1])
    return f"TMI-{stamp}-{last_counter + 1:05d}"


def get_next_payment_reference() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT payment_reference
            FROM payment_sessions
            WHERE payment_reference LIKE ?
            ORDER BY payment_reference DESC
            LIMIT 1
            """,
            (f"TMP-{stamp}-%",),
        ).fetchone()

    if not row or not row["payment_reference"]:
        return f"TMP-{stamp}-00001"

    last_counter = int(row["payment_reference"].split("-")[-1])
    return f"TMP-{stamp}-{last_counter + 1:05d}"


def get_next_receipt_number() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")

    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT receipt_number
            FROM payment_sessions
            WHERE receipt_number LIKE ?
            ORDER BY receipt_number DESC
            LIMIT 1
            """,
            (f"TMR-{stamp}-%",),
        ).fetchone()

    if not row or not row["receipt_number"]:
        return f"TMR-{stamp}-00001"

    last_counter = int(row["receipt_number"].split("-")[-1])
    return f"TMR-{stamp}-{last_counter + 1:05d}"


def _order_row_from_payload(order: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "serial": order["serial"],
        "nft_identifier": order.get("nft_identifier"),
        "type_code": order.get("type_code") or get_nft_type_code(order.get("nft_type")),
        "node_id": normalize_identifier_component(order.get("node_id"), get_mint_node_id()),
        "region_code": normalize_identifier_component(order.get("region_code"), get_default_region_code()),
        "registrant_code": normalize_identifier_component(order.get("registrant_code"), "PUBLIC"),
        "identifier_year": int(order.get("identifier_year") or 0),
        "identifier_sequence": int(order.get("identifier_sequence") or 0),
        "invoice_number": order["invoice_number"],
        "invoice_public_token": order["invoice_public_token"],
        "vault_public_token": order["vault_public_token"],
        "payment_reference": order.get("payment_reference"),
        "receipt_number": order.get("receipt_number"),
        "user_id": order.get("user_id"),
        "user_email": order["user_email"].strip().lower(),
        "user_name": order["user_name"].strip(),
        "billing_address_line1": order.get("billing_address_line1", "").strip(),
        "billing_address_line2": order.get("billing_address_line2", "").strip(),
        "billing_city": order.get("billing_city", "").strip(),
        "billing_state": order.get("billing_state", "").strip().upper(),
        "billing_postal_code": order.get("billing_postal_code", "").strip(),
        "billing_phone": order.get("billing_phone", "").strip(),
        "billing_dob": order.get("billing_dob", "").strip(),
        "prefix": normalize_identifier_component(order.get("prefix"), "GENERAL"),
        "industry": normalize_identifier_component(order.get("industry"), "DIGITAL"),
        "nft_type": order["nft_type"],
        "package_tier": order.get("package_tier", "starter"),
        "encryption": order.get("encryption", "none"),
        "chain": order.get("chain", "polygon"),
        "quantity": int(order.get("quantity", 1) or 1),
        "file_name": order.get("file_name"),
        "estimated_storage_gb": float(order.get("estimated_storage_gb", 0.0) or 0.0),
        "subtotal_usd": float(order.get("subtotal_usd", 0.0) or 0.0),
        "tax_rate": float(order.get("tax_rate", 0.0) or 0.0),
        "tax_state": order.get("tax_state", "").strip().upper(),
        "tax_amount_usd": float(order.get("tax_amount_usd", 0.0) or 0.0),
        "processing_fee_usd": float(order.get("processing_fee_usd", 0.0) or 0.0),
        "discount_amount_usd": float(order.get("discount_amount_usd", 0.0) or 0.0),
        "total_usd": float(order.get("total_usd", 0.0) or 0.0),
        "payment_method": order.get("payment_method", "fiat"),
        "crypto_token": order.get("crypto_token"),
        "crypto_spot_price_usd": order.get("crypto_spot_price_usd"),
        "quote_snapshot_json": json.dumps(order.get("quote_snapshot", {})),
        "invoice_email_status": order.get("invoice_email_status", "pending"),
        "invoice_sent_to": order.get("invoice_sent_to"),
        "invoice_emailed_at": order.get("invoice_emailed_at"),
        "status": order.get("status", "completed"),
        "created_at": order.get("created_at", utc_now_iso()),
    }


def _insert_order(connection: sqlite3.Connection, row: Dict[str, Any]) -> None:
    connection.execute(
        """
            INSERT INTO orders (
            id, serial, nft_identifier, type_code, node_id, region_code, registrant_code, identifier_year, identifier_sequence,
            invoice_number, invoice_public_token, vault_public_token, payment_reference,
            receipt_number, user_id, user_email,
            user_name, billing_address_line1, billing_address_line2, billing_city, billing_state,
            billing_postal_code, billing_phone, billing_dob, prefix, industry, nft_type, package_tier, encryption,
            chain, quantity, file_name, estimated_storage_gb, subtotal_usd, tax_rate, tax_state,
            tax_amount_usd, processing_fee_usd, discount_amount_usd, total_usd, payment_method,
            crypto_token, crypto_spot_price_usd, quote_snapshot_json, invoice_email_status,
            invoice_sent_to, invoice_emailed_at, status, created_at
        ) VALUES (
            :id, :serial, :nft_identifier, :type_code, :node_id, :region_code, :registrant_code, :identifier_year, :identifier_sequence,
            :invoice_number, :invoice_public_token, :vault_public_token, :payment_reference,
            :receipt_number, :user_id, :user_email,
            :user_name, :billing_address_line1, :billing_address_line2, :billing_city, :billing_state,
            :billing_postal_code, :billing_phone, :billing_dob, :prefix, :industry, :nft_type, :package_tier, :encryption,
            :chain, :quantity, :file_name, :estimated_storage_gb, :subtotal_usd, :tax_rate, :tax_state,
            :tax_amount_usd, :processing_fee_usd, :discount_amount_usd, :total_usd, :payment_method,
            :crypto_token, :crypto_spot_price_usd, :quote_snapshot_json, :invoice_email_status,
            :invoice_sent_to, :invoice_emailed_at, :status, :created_at
        )
        """,
        row,
    )


def _mint_event_row_from_payload(mint_event: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": str(uuid.uuid4()),
        "order_id": mint_event["order_id"],
        "payment_reference": mint_event.get("payment_reference"),
        "receipt_number": mint_event.get("receipt_number"),
        "invoice_number": mint_event.get("invoice_number"),
        "serial": mint_event["serial"],
        "nft_identifier": mint_event["nft_identifier"],
        "type_code": mint_event.get("type_code") or get_nft_type_code(mint_event.get("nft_type")),
        "node_id": normalize_identifier_component(mint_event.get("node_id"), get_mint_node_id()),
        "region_code": normalize_identifier_component(mint_event.get("region_code"), get_default_region_code()),
        "registrant_code": normalize_identifier_component(mint_event.get("registrant_code"), "PUBLIC"),
        "identifier_year": int(mint_event.get("identifier_year") or 0),
        "identifier_sequence": int(mint_event.get("identifier_sequence") or 0),
        "prefix": normalize_identifier_component(mint_event.get("prefix"), "GENERAL"),
        "industry": normalize_identifier_component(mint_event.get("industry"), "DIGITAL"),
        "nft_type": mint_event["nft_type"],
        "package_tier": mint_event.get("package_tier"),
        "encryption": mint_event.get("encryption"),
        "chain": mint_event.get("chain"),
        "quantity": int(mint_event.get("quantity", 1) or 1),
        "user_id": mint_event.get("user_id"),
        "user_email": mint_event.get("user_email"),
        "user_name": mint_event.get("user_name"),
        "file_name": mint_event.get("file_name"),
        "metadata_json": json.dumps(mint_event.get("metadata", {})),
        "payment_method": mint_event.get("payment_method"),
        "subtotal_usd": float(mint_event.get("subtotal_usd", 0.0) or 0.0),
        "tax_amount_usd": float(mint_event.get("tax_amount_usd", 0.0) or 0.0),
        "total_usd": float(mint_event.get("total_usd", 0.0) or 0.0),
        "minted_at": mint_event.get("minted_at", utc_now_iso()),
        "created_at": mint_event.get("created_at", utc_now_iso()),
    }


def _insert_mint_event(connection: sqlite3.Connection, row: Dict[str, Any]) -> None:
    connection.execute(
        """
        INSERT INTO mint_events (
            id, order_id, payment_reference, receipt_number, invoice_number, serial, nft_identifier, type_code, node_id, region_code,
            registrant_code, identifier_year, identifier_sequence, prefix, industry,
            nft_type, package_tier, encryption, chain, quantity, user_id, user_email, user_name, file_name,
            metadata_json, payment_method, subtotal_usd, tax_amount_usd, total_usd, minted_at, created_at
        ) VALUES (
            :id, :order_id, :payment_reference, :receipt_number, :invoice_number, :serial, :nft_identifier, :type_code, :node_id, :region_code,
            :registrant_code, :identifier_year, :identifier_sequence, :prefix, :industry,
            :nft_type, :package_tier, :encryption, :chain, :quantity, :user_id, :user_email, :user_name, :file_name,
            :metadata_json, :payment_method, :subtotal_usd, :tax_amount_usd, :total_usd, :minted_at, :created_at
        )
        """,
        row,
    )


def record_order(order: Dict[str, Any]) -> Dict[str, Any]:
    row = _order_row_from_payload(order)

    with get_connection() as connection:
        _insert_order(connection, row)

    return row


def record_order_and_mint_event(order: Dict[str, Any], mint_event: Dict[str, Any]) -> Dict[str, Any]:
    order_row = _order_row_from_payload(order)
    mint_event_row = _mint_event_row_from_payload({
        **mint_event,
        "order_id": order_row["id"],
        "created_at": mint_event.get("created_at", order_row["created_at"]),
    })

    with get_connection() as connection:
        _insert_order(connection, order_row)
        _insert_mint_event(connection, mint_event_row)

    return order_row


def create_payment_session(payment_session: Dict[str, Any]) -> Dict[str, Any]:
    now = payment_session.get("created_at", utc_now_iso())
    row = {
        "id": str(uuid.uuid4()),
        "payment_reference": payment_session["payment_reference"],
        "payment_public_token": payment_session["payment_public_token"],
        "receipt_number": payment_session["receipt_number"],
        "receipt_public_token": payment_session["receipt_public_token"],
        "type_code": payment_session.get("type_code") or get_nft_type_code(payment_session.get("nft_type")),
        "node_id": normalize_identifier_component(payment_session.get("node_id"), get_mint_node_id()),
        "region_code": normalize_identifier_component(payment_session.get("region_code"), get_default_region_code()),
        "registrant_code": normalize_identifier_component(payment_session.get("registrant_code"), "PUBLIC"),
        "user_id": payment_session.get("user_id"),
        "user_email": payment_session["user_email"].strip().lower(),
        "user_name": payment_session["user_name"].strip(),
        "billing_address_line1": payment_session.get("billing_address_line1", "").strip(),
        "billing_address_line2": payment_session.get("billing_address_line2", "").strip(),
        "billing_city": payment_session.get("billing_city", "").strip(),
        "billing_state": payment_session.get("billing_state", "").strip().upper(),
        "billing_postal_code": payment_session.get("billing_postal_code", "").strip(),
        "billing_phone": payment_session.get("billing_phone", "").strip(),
        "billing_dob": payment_session.get("billing_dob", "").strip(),
        "prefix": normalize_identifier_component(payment_session.get("prefix"), "GENERAL"),
        "industry": normalize_identifier_component(payment_session.get("industry"), "DIGITAL"),
        "nft_type": payment_session["nft_type"],
        "package_tier": payment_session.get("package_tier", "starter"),
        "encryption": payment_session.get("encryption", "none"),
        "chain": payment_session.get("chain", "polygon"),
        "quantity": int(payment_session.get("quantity", 1) or 1),
        "file_name": payment_session.get("file_name"),
        "staged_file_path": payment_session.get("staged_file_path"),
        "estimated_storage_gb": float(payment_session.get("estimated_storage_gb", 0.0) or 0.0),
        "metadata_json": json.dumps(payment_session.get("metadata", {})),
        "subtotal_usd": float(payment_session.get("subtotal_usd", 0.0) or 0.0),
        "tax_rate": float(payment_session.get("tax_rate", 0.0) or 0.0),
        "tax_state": payment_session.get("tax_state", "").strip().upper(),
        "tax_amount_usd": float(payment_session.get("tax_amount_usd", 0.0) or 0.0),
        "processing_fee_usd": float(payment_session.get("processing_fee_usd", 0.0) or 0.0),
        "discount_amount_usd": float(payment_session.get("discount_amount_usd", 0.0) or 0.0),
        "total_usd": float(payment_session.get("total_usd", 0.0) or 0.0),
        "payment_method": payment_session.get("payment_method", "fiat"),
        "crypto_token": payment_session.get("crypto_token"),
        "crypto_spot_price_usd": payment_session.get("crypto_spot_price_usd"),
        "quote_snapshot_json": json.dumps(payment_session.get("quote_snapshot", {})),
        "cancellation_fee_usd": float(payment_session.get("cancellation_fee_usd", 5.0) or 5.0),
        "refund_due_usd": payment_session.get("refund_due_usd"),
        "minted_order_id": payment_session.get("minted_order_id"),
        "minted_serial": payment_session.get("minted_serial"),
        "minted_nft_identifier": payment_session.get("minted_nft_identifier"),
        "minted_invoice_number": payment_session.get("minted_invoice_number"),
        "payment_captured_at": payment_session.get("payment_captured_at", now),
        "canceled_at": payment_session.get("canceled_at"),
        "minted_at": payment_session.get("minted_at"),
        "status": payment_session.get("status", "payment_cleared"),
        "created_at": now,
        "updated_at": payment_session.get("updated_at", now),
    }

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO payment_sessions (
                id, payment_reference, payment_public_token, receipt_number, receipt_public_token, type_code, node_id, region_code,
                registrant_code, user_id, user_email,
                user_name, billing_address_line1, billing_address_line2, billing_city, billing_state,
                billing_postal_code, billing_phone, billing_dob, prefix, industry, nft_type, package_tier, encryption,
                chain, quantity, file_name, staged_file_path, estimated_storage_gb, metadata_json,
                subtotal_usd, tax_rate, tax_state, tax_amount_usd, processing_fee_usd, discount_amount_usd,
                total_usd, payment_method, crypto_token, crypto_spot_price_usd, quote_snapshot_json,
                cancellation_fee_usd, refund_due_usd, minted_order_id, minted_serial, minted_nft_identifier, minted_invoice_number,
                payment_captured_at, canceled_at, minted_at, status, created_at, updated_at
            ) VALUES (
                :id, :payment_reference, :payment_public_token, :receipt_number, :receipt_public_token, :type_code, :node_id, :region_code,
                :registrant_code, :user_id, :user_email,
                :user_name, :billing_address_line1, :billing_address_line2, :billing_city, :billing_state,
                :billing_postal_code, :billing_phone, :billing_dob, :prefix, :industry, :nft_type, :package_tier, :encryption,
                :chain, :quantity, :file_name, :staged_file_path, :estimated_storage_gb, :metadata_json,
                :subtotal_usd, :tax_rate, :tax_state, :tax_amount_usd, :processing_fee_usd, :discount_amount_usd,
                :total_usd, :payment_method, :crypto_token, :crypto_spot_price_usd, :quote_snapshot_json,
                :cancellation_fee_usd, :refund_due_usd, :minted_order_id, :minted_serial, :minted_nft_identifier, :minted_invoice_number,
                :payment_captured_at, :canceled_at, :minted_at, :status, :created_at, :updated_at
            )
            """,
            row,
        )

    return row


def get_payment_session_by_token(payment_public_token: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM payment_sessions WHERE payment_public_token = ?",
            (payment_public_token,),
        ).fetchone()

    return _public_payment_session(row) if row else None


def get_payment_session_by_receipt_token(receipt_public_token: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM payment_sessions WHERE receipt_public_token = ?",
            (receipt_public_token,),
        ).fetchone()

    return _public_payment_session(row) if row else None


def update_payment_session_status(
    payment_public_token: str,
    *,
    status: str,
    refund_due_usd: float | None = None,
    canceled_at: str | None = None,
    minted_order_id: str | None = None,
    minted_serial: str | None = None,
    minted_nft_identifier: str | None = None,
    minted_invoice_number: str | None = None,
    minted_at: str | None = None,
) -> None:
    with get_connection() as connection:
        current = connection.execute(
            "SELECT * FROM payment_sessions WHERE payment_public_token = ?",
            (payment_public_token,),
        ).fetchone()

        if not current:
            return

        connection.execute(
            """
            UPDATE payment_sessions
            SET status = ?, refund_due_usd = ?, canceled_at = ?, minted_order_id = ?,
                minted_serial = ?, minted_nft_identifier = ?, minted_invoice_number = ?, minted_at = ?, updated_at = ?
            WHERE payment_public_token = ?
            """,
            (
                status,
                refund_due_usd if refund_due_usd is not None else current["refund_due_usd"],
                canceled_at if canceled_at is not None else current["canceled_at"],
                minted_order_id if minted_order_id is not None else current["minted_order_id"],
                minted_serial if minted_serial is not None else current["minted_serial"],
                minted_nft_identifier if minted_nft_identifier is not None else current["minted_nft_identifier"],
                minted_invoice_number if minted_invoice_number is not None else current["minted_invoice_number"],
                minted_at if minted_at is not None else current["minted_at"],
                utc_now_iso(),
                payment_public_token,
            ),
        )


def update_invoice_delivery(
    invoice_number: str,
    *,
    email_status: str,
    sent_to: str | None = None,
    emailed_at: str | None = None,
) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            UPDATE orders
            SET invoice_email_status = ?, invoice_sent_to = ?, invoice_emailed_at = ?
            WHERE invoice_number = ?
            """,
            (email_status, sent_to, emailed_at, invoice_number),
        )


def get_order_by_invoice_number(invoice_number: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE invoice_number = ?",
            (invoice_number,),
        ).fetchone()

    return _public_order(row) if row else None


def get_order_by_invoice_token(invoice_public_token: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE invoice_public_token = ?",
            (invoice_public_token,),
        ).fetchone()

    return _public_order(row) if row else None


def get_order_by_vault_token(vault_public_token: str) -> Optional[Dict[str, Any]]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM orders WHERE vault_public_token = ?",
            (vault_public_token,),
        ).fetchone()

    return _public_order(row) if row else None


def list_orders(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    query = "SELECT * FROM orders ORDER BY datetime(created_at) DESC"
    parameters: tuple[Any, ...] = ()

    if limit:
        query += " LIMIT ?"
        parameters = (limit,)

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [_public_order(row) for row in rows]


def list_mint_events(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    query = "SELECT * FROM mint_events ORDER BY datetime(minted_at) DESC"
    parameters: tuple[Any, ...] = ()

    if limit:
        query += " LIMIT ?"
        parameters = (limit,)

    with get_connection() as connection:
        rows = connection.execute(query, parameters).fetchall()

    return [_public_mint_event(row) for row in rows]


def summarize_orders(orders: List[Dict[str, Any]]) -> Dict[str, Any]:
    orders_count = len(orders)
    gross_revenue = round(sum(float(order["total_usd"]) for order in orders), 2)
    taxes_collected = round(sum(float(order["tax_amount_usd"]) for order in orders), 2)
    processing_fees = round(sum(float(order["processing_fee_usd"]) for order in orders), 2)
    discount_total = round(sum(float(order["discount_amount_usd"]) for order in orders), 2)
    average_order = round(gross_revenue / orders_count, 2) if orders_count else 0.0
    net_revenue = round(gross_revenue - taxes_collected - processing_fees, 2)

    return {
        "orders_count": orders_count,
        "gross_revenue_usd": gross_revenue,
        "taxes_collected_usd": taxes_collected,
        "processing_fees_usd": processing_fees,
        "discounts_usd": discount_total,
        "net_revenue_usd": net_revenue,
        "average_order_usd": average_order,
    }


def get_analytics() -> Dict[str, Any]:
    all_orders = list_orders()
    now = datetime.now(timezone.utc)
    day_boundary = now - timedelta(days=1)
    week_boundary = now - timedelta(days=7)
    month_boundary = now - timedelta(days=30)

    def filter_since(boundary: datetime) -> List[Dict[str, Any]]:
        return [
            order
            for order in all_orders
            if parse_iso_datetime(order["created_at"]) >= boundary
        ]

    return {
        "lifetime": summarize_orders(all_orders),
        "daily": summarize_orders(filter_since(day_boundary)),
        "weekly": summarize_orders(filter_since(week_boundary)),
        "monthly": summarize_orders(filter_since(month_boundary)),
        "recent_orders": all_orders[:10],
    }


init_db()
