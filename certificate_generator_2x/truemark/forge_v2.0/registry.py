"""Canonical public True Mark verification-registry URL handling."""

from __future__ import annotations

import os
from urllib.parse import quote


DEFAULT_REGISTRY_VERIFY_BASE = "https://certsig.com/verify"


def verification_url(verification_id: str, base_url: str | None = None) -> str:
    """Build the stable public registry URL for a certificate."""
    base = (base_url or os.getenv("TRUEMARK_REGISTRY_VERIFY_BASE", DEFAULT_REGISTRY_VERIFY_BASE)).rstrip("/")
    return f"{base}/{quote(str(verification_id), safe='')}"
