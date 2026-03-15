from __future__ import annotations

import hashlib
import hmac
import json
import os
import sqlite3
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "truemark.db"


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
    "invoice_number": "TEXT",
    "invoice_public_token": "TEXT",
    "vault_public_token": "TEXT",
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


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


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
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_invoice_number ON orders(invoice_number)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_invoice_public_token ON orders(invoice_public_token)"
    )
    connection.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_vault_public_token ON orders(vault_public_token)"
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
                invoice_number TEXT,
                invoice_public_token TEXT,
                vault_public_token TEXT,
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
        _ensure_columns(connection, "users", USER_COLUMNS)
        _ensure_columns(connection, "orders", ORDER_COLUMNS)
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


def record_order(order: Dict[str, Any]) -> Dict[str, Any]:
    row = {
        "id": str(uuid.uuid4()),
        "serial": order["serial"],
        "invoice_number": order["invoice_number"],
        "invoice_public_token": order["invoice_public_token"],
        "vault_public_token": order["vault_public_token"],
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

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO orders (
                id, serial, invoice_number, invoice_public_token, vault_public_token, user_id, user_email,
                user_name, billing_address_line1, billing_address_line2, billing_city, billing_state,
                billing_postal_code, billing_phone, billing_dob, nft_type, package_tier, encryption,
                chain, quantity, file_name, estimated_storage_gb, subtotal_usd, tax_rate, tax_state,
                tax_amount_usd, processing_fee_usd, discount_amount_usd, total_usd, payment_method,
                crypto_token, crypto_spot_price_usd, quote_snapshot_json, invoice_email_status,
                invoice_sent_to, invoice_emailed_at, status, created_at
            ) VALUES (
                :id, :serial, :invoice_number, :invoice_public_token, :vault_public_token, :user_id, :user_email,
                :user_name, :billing_address_line1, :billing_address_line2, :billing_city, :billing_state,
                :billing_postal_code, :billing_phone, :billing_dob, :nft_type, :package_tier, :encryption,
                :chain, :quantity, :file_name, :estimated_storage_gb, :subtotal_usd, :tax_rate, :tax_state,
                :tax_amount_usd, :processing_fee_usd, :discount_amount_usd, :total_usd, :payment_method,
                :crypto_token, :crypto_spot_price_usd, :quote_snapshot_json, :invoice_email_status,
                :invoice_sent_to, :invoice_emailed_at, :status, :created_at
            )
            """,
            row,
        )

    return row


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
