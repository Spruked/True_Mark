from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

IDENTIFIER_FORMAT = "TYPE-NODE-REGION-YEAR-USER-SEQ"

NFT_TYPE_CODE_MAP = {
    "K-NFT": "KNFT",
    "H-NFT": "HNFT",
    "L-NFT": "LNFT",
    "C-NFT": "CNFT",
}


def normalize_code(value: str | None, fallback: str, *, max_length: int | None = None) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", "", (value or "").upper())
    candidate = cleaned or fallback
    if max_length:
        return candidate[:max_length] or fallback
    return candidate


def get_node_code() -> str:
    raw_value = os.getenv("NODE_CODE") or os.getenv("TRUEMARK_NODE_ID") or "TMK"
    return normalize_code(raw_value, "TMK", max_length=3)


def get_region_code() -> str:
    raw_value = os.getenv("REGION") or os.getenv("TRUEMARK_REGION_CODE") or "US"
    return normalize_code(raw_value, "US", max_length=3)


def get_node_name() -> str:
    return (os.getenv("NODE_NAME") or os.getenv("TRUEMARK_NODE_NAME") or "True Mark Mint").strip()


def get_nft_type_code(nft_type: str | None) -> str:
    normalized_nft_type = (nft_type or "").strip().upper()
    return NFT_TYPE_CODE_MAP.get(normalized_nft_type, normalize_code(normalized_nft_type, "NFT"))


def get_mint_standard() -> Dict[str, Any]:
    node_code = get_node_code()
    region_code = get_region_code()
    return {
        "identifier_format": IDENTIFIER_FORMAT,
        "node_code": node_code,
        "node_id": node_code,
        "node_name": get_node_name(),
        "region": region_code,
        "region_code": region_code,
        "type_codes": NFT_TYPE_CODE_MAP,
    }
