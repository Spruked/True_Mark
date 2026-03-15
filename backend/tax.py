from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
TAX_PATH = CONFIG_DIR / "tax_table.json"


DEFAULT_TAX_TABLE: Dict[str, Any] = {
    "default_rate": 0.0,
    "state_rates": {
        "TX": 0.0825,
        "CA": 0.0725,
        "NY": 0.0400,
        "FL": 0.0600,
    },
    "notes": "Adjust state rates here for planning, quote estimation, and accounting visibility.",
}


def _deep_merge(current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(current)

    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def ensure_tax_file() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not TAX_PATH.exists():
        TAX_PATH.write_text(json.dumps(DEFAULT_TAX_TABLE, indent=2), encoding="utf-8")

    return TAX_PATH


def load_tax_table() -> Dict[str, Any]:
    ensure_tax_file()

    try:
        return json.loads(TAX_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        TAX_PATH.write_text(json.dumps(DEFAULT_TAX_TABLE, indent=2), encoding="utf-8")
        return deepcopy(DEFAULT_TAX_TABLE)


def save_tax_table(updates: Dict[str, Any]) -> Dict[str, Any]:
    current = load_tax_table()
    merged = _deep_merge(current, updates)
    TAX_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def resolve_tax_rate(state: str | None, tax_table: Dict[str, Any] | None = None) -> float:
    active_tax_table = tax_table or load_tax_table()
    normalized_state = (state or "").strip().upper()

    if normalized_state and normalized_state in active_tax_table.get("state_rates", {}):
        return float(active_tax_table["state_rates"][normalized_state])

    return float(active_tax_table.get("default_rate", 0.0))
