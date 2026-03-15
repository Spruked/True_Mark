from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict

import httpx


COINGECKO_PRICE_URL = "https://api.coingecko.com/api/v3/simple/price"
ASSET_MAP = {
    "polygon": "matic-network",
    "ethereum": "ethereum",
}


def _fallback_snapshot() -> Dict[str, Any]:
    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "assets": {
            "polygon": {"usd": 0.0, "usd_24h_change": 0.0},
            "ethereum": {"usd": 0.0, "usd_24h_change": 0.0},
        },
    }


def get_market_snapshot() -> Dict[str, Any]:
    ids = ",".join(ASSET_MAP.values())

    try:
        response = httpx.get(
            COINGECKO_PRICE_URL,
            params={
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
            },
            timeout=10.0,
        )
        response.raise_for_status()
        payload = response.json()
    except Exception:
        return _fallback_snapshot()

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "assets": {
            "polygon": {
                "usd": float(payload.get("matic-network", {}).get("usd", 0.0) or 0.0),
                "usd_24h_change": float(payload.get("matic-network", {}).get("usd_24h_change", 0.0) or 0.0),
            },
            "ethereum": {
                "usd": float(payload.get("ethereum", {}).get("usd", 0.0) or 0.0),
                "usd_24h_change": float(payload.get("ethereum", {}).get("usd_24h_change", 0.0) or 0.0),
            },
        },
    }
