from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import HTTPException, Request, status


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DEFAULT_SESSION_TTL_SECONDS = 60 * 60 * 12


def _b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(f"{value}{padding}".encode("ascii"))


def _configuration_error() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Admin authentication is not configured on the backend.",
    )


def get_admin_email() -> str:
    admin_email = os.getenv("TRUEMARK_ADMIN_EMAIL", "").strip().lower()
    if not admin_email:
        raise _configuration_error()
    return admin_email


def get_admin_password() -> str:
    admin_password = os.getenv("TRUEMARK_ADMIN_PASSWORD", "")
    if not admin_password:
        raise _configuration_error()
    return admin_password


def get_admin_session_secret() -> str:
    session_secret = os.getenv("TRUEMARK_ADMIN_SESSION_SECRET", "").strip()
    if not session_secret:
        raise _configuration_error()
    return session_secret


def get_admin_session_ttl_seconds() -> int:
    raw_ttl = os.getenv("TRUEMARK_ADMIN_SESSION_TTL_SECONDS", "").strip()

    if not raw_ttl:
        return DEFAULT_SESSION_TTL_SECONDS

    try:
        return max(int(raw_ttl), 900)
    except ValueError:
        return DEFAULT_SESSION_TTL_SECONDS


def _sign_message(message: str) -> str:
    digest = hmac.new(
        get_admin_session_secret().encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()
    return _b64url_encode(digest)


def create_admin_session(email: str) -> Dict[str, Any]:
    issued_at = int(time.time())
    expires_at = issued_at + get_admin_session_ttl_seconds()
    normalized_email = email.strip().lower()
    payload = {
        "sub": normalized_email,
        "iat": issued_at,
        "exp": expires_at,
    }
    encoded_payload = _b64url_encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    token = f"{encoded_payload}.{_sign_message(encoded_payload)}"
    return {
        "email": normalized_email,
        "token": token,
        "expires_at": expires_at,
    }


def authenticate_admin(email: str, password: str) -> Dict[str, Any]:
    configured_email = get_admin_email()
    configured_password = get_admin_password()
    normalized_email = email.strip().lower()

    email_matches = hmac.compare_digest(normalized_email, configured_email)
    password_matches = hmac.compare_digest(password, configured_password)

    if not email_matches or not password_matches:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin email or password.",
        )

    return create_admin_session(normalized_email)


def decode_admin_token(token: str) -> Dict[str, Any]:
    try:
        encoded_payload, provided_signature = token.split(".", 1)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin session token.",
        ) from error

    expected_signature = _sign_message(encoded_payload)
    if not hmac.compare_digest(provided_signature, expected_signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin session token.",
        )

    try:
        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
    except (json.JSONDecodeError, ValueError, UnicodeDecodeError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin session token.",
        ) from error

    expires_at = int(payload.get("exp", 0))
    subject = str(payload.get("sub", "")).strip().lower()

    if not subject or not hmac.compare_digest(subject, get_admin_email()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin session token.",
        )

    if expires_at <= int(time.time()):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin session has expired. Please sign in again.",
        )

    return payload


def require_admin_session(request: Request) -> Dict[str, Any]:
    authorization = request.headers.get("Authorization", "")
    scheme, _, credentials = authorization.partition(" ")

    if scheme.lower() != "bearer" or not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin authentication is required.",
        )

    return decode_admin_token(credentials.strip())
