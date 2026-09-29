from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

IDENTIFIER_FORMAT = "TYPE-NODE-REGION-YEAR-USER-SEQ"

NFT_TAXONOMY = {
    "H": {"base_type": "H", "licensable": False, "color_profile": "TM-NFT-HEIRLOOM-GREEN", "name": "Heirloom"},
    "K": {"base_type": "K", "licensable": False, "color_profile": "TM-NFT-KNOWLEDGE-BLUE", "name": "Knowledge"},
    "L": {"base_type": "L", "licensable": False, "color_profile": "TM-NFT-LEGACY-VIOLET", "name": "Legacy"},
    "B": {"base_type": "B", "licensable": False, "color_profile": "TM-NFT-BLUE-GOLD", "name": "Bespoke"},
    "HL": {"base_type": "H", "licensable": True, "color_profile": "TM-NFT-HEIRLOOM-GREEN", "name": "Licensable Heirloom"},
    "KL": {"base_type": "K", "licensable": True, "color_profile": "TM-NFT-KNOWLEDGE-BLUE", "name": "Licensable Knowledge"},
    "LL": {"base_type": "L", "licensable": True, "color_profile": "TM-NFT-LEGACY-VIOLET", "name": "Licensable Legacy"},
    "BL": {"base_type": "B", "licensable": True, "color_profile": "TM-NFT-BLUE-GOLD", "name": "Licensable Bespoke"},
    "C": {"base_type": "C", "licensable": False, "color_profile": "TM-NFT-CUSTOM-AMBER", "name": "Custom Contract"},
}

# Accept the former display-style values at integration boundaries, but never
# emit them as the canonical metadata value.
NFT_TYPE_ALIASES = {f"{code}-NFT": code for code in NFT_TAXONOMY}
NFT_TYPE_CODE_MAP = {code: f"{code}NFT" for code in NFT_TAXONOMY}


def normalize_nft_type(nft_type: str | None) -> str:
    value = (nft_type or "K").strip().upper()
    return NFT_TYPE_ALIASES.get(value, value)


def get_nft_taxonomy(nft_type: str | None) -> Dict[str, Any]:
    normalized = normalize_nft_type(nft_type)
    if normalized not in NFT_TAXONOMY:
        raise ValueError(f"Unsupported True Mark NFT type: {nft_type}")
    return {"nft_type": normalized, **NFT_TAXONOMY[normalized]}


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
    normalized_nft_type = normalize_nft_type(nft_type)
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
        "nft_taxonomy": NFT_TAXONOMY,
    }
