from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict


BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
PRICING_PATH = CONFIG_DIR / "pricing.json"


DEFAULT_PRICING: Dict[str, Any] = {
    "version": "1.0",
    "currency": "USD",
    "settlement": {
        "pricing_basis": "fiat_only",
        "display_currency": "USD",
        "crypto_quote_enabled": True,
        "crypto_quote_note": "Crypto is shown only as an equivalent fiat conversion at the time of purchase.",
        "customer_wallet_required": False,
        "mint_execution": "platform_managed",
        "mint_execution_note": "True Mark executes minting through the platform MetaMask account and Alchemy infrastructure.",
    },
    "nft_types": {
        "K-NFT": {"name": "Knowledge NFT", "price": 4.99, "enabled": True},
        "H-NFT": {"name": "Heirloom NFT", "price": 9.99, "enabled": True},
        "L-NFT": {"name": "Legacy NFT", "price": 19.99, "enabled": True},
        "C-NFT": {"name": "Custom NFT", "price": 14.99, "enabled": True},
    },
    "package_tiers": {
        "starter": {
            "name": "Mint Only",
            "price": 0.0,
            "layers": 0,
            "description": "Low-cost Polygon mint with no certificate package.",
        },
        "essential": {
            "name": "Basic Record",
            "price": 12.0,
            "layers": 3,
            "description": "Mint plus a simple 3-layer record package.",
        },
        "secure": {
            "name": "Secure Record",
            "price": 28.0,
            "layers": 5,
            "description": "Mint plus a stronger certificate package.",
        },
        "professional": {
            "name": "Professional Record",
            "price": 45.0,
            "layers": 7,
            "description": "Mint plus a premium 7-layer package.",
        },
        "forensic": {
            "name": "Forensic Record",
            "price": 95.0,
            "layers": 10,
            "description": "Full forensic package for high-assurance records.",
        },
    },
    "encryption_options": {
        "none": {"name": "No Encryption", "price": 0.0},
        "chacha20": {"name": "ChaCha20-Poly1305", "price": 8.0},
    },
    "chains": {
        "polygon": {"name": "Polygon", "surcharge": 0.0},
        "ethereum": {"name": "Ethereum", "surcharge": 125.0},
    },
    "storage": {
        "included_gb": 1.0,
        "additional_gb_price": 5.0,
    },
    "bulk_discounts": [
        {"min_quantity": 10, "discount": 0.05},
        {"min_quantity": 25, "discount": 0.10},
        {"min_quantity": 50, "discount": 0.15},
        {"min_quantity": 100, "discount": 0.20},
        {"min_quantity": 500, "discount": 0.30},
    ],
    "processing_fee": {
        "percentage": 0.029,
        "fixed": 0.30,
    },
}


def _deep_merge(current: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(current)

    for key, value in updates.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value

    return merged


def ensure_pricing_file() -> Path:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if not PRICING_PATH.exists():
        PRICING_PATH.write_text(json.dumps(DEFAULT_PRICING, indent=2), encoding="utf-8")

    return PRICING_PATH


def load_pricing() -> Dict[str, Any]:
    ensure_pricing_file()

    try:
        return json.loads(PRICING_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        PRICING_PATH.write_text(json.dumps(DEFAULT_PRICING, indent=2), encoding="utf-8")
        return deepcopy(DEFAULT_PRICING)


def save_pricing(updates: Dict[str, Any]) -> Dict[str, Any]:
    current = load_pricing()
    merged = _deep_merge(current, updates)
    PRICING_PATH.write_text(json.dumps(merged, indent=2), encoding="utf-8")
    return merged


def calculate_quote(cart: Dict[str, Any], pricing: Dict[str, Any] | None = None) -> Dict[str, Any]:
    active_pricing = pricing or load_pricing()

    nft_type = cart.get("nft_type", "K-NFT")
    package_tier = cart.get("package_tier", "starter")
    encryption = cart.get("encryption", "none")
    chain = cart.get("chain", "polygon")
    quantity = max(int(cart.get("quantity", 1) or 1), 1)
    estimated_storage_gb = max(float(cart.get("estimated_storage_gb", 0.0) or 0.0), 0.0)

    nft_config = active_pricing["nft_types"].get(nft_type)
    if not nft_config or not nft_config.get("enabled", False):
        raise ValueError(f"NFT type {nft_type} is not currently available.")

    tier_config = active_pricing["package_tiers"].get(package_tier)
    if not tier_config:
        raise ValueError(f"Package tier {package_tier} is not available.")

    encryption_config = active_pricing["encryption_options"].get(encryption)
    if not encryption_config:
        raise ValueError(f"Encryption option {encryption} is not available.")

    chain_config = active_pricing["chains"].get(chain)
    if not chain_config:
        raise ValueError(f"Chain {chain} is not available.")

    included_gb = float(active_pricing["storage"]["included_gb"])
    billable_storage_gb = max(estimated_storage_gb - included_gb, 0.0)
    storage_unit_price = float(active_pricing["storage"]["additional_gb_price"])

    base_nft_price = float(nft_config["price"])
    package_price = float(tier_config["price"])
    encryption_price = float(encryption_config["price"])
    chain_surcharge = float(chain_config["surcharge"])
    storage_price = billable_storage_gb * storage_unit_price

    unit_subtotal = base_nft_price + package_price + encryption_price + chain_surcharge + storage_price

    bulk_discount_rate = 0.0
    for bracket in active_pricing.get("bulk_discounts", []):
        if quantity >= int(bracket["min_quantity"]):
            bulk_discount_rate = float(bracket["discount"])

    subtotal = unit_subtotal * quantity
    discount_amount = subtotal * bulk_discount_rate
    after_discount = subtotal - discount_amount

    processing_percentage = float(active_pricing["processing_fee"]["percentage"])
    processing_fixed = float(active_pricing["processing_fee"]["fixed"])
    processing_fee = (after_discount * processing_percentage) + processing_fixed
    total = after_discount + processing_fee

    return {
        "currency": active_pricing.get("currency", "USD"),
        "settlement": active_pricing.get("settlement", {}),
        "cart": {
            "nft_type": nft_type,
            "package_tier": package_tier,
            "encryption": encryption,
            "chain": chain,
            "quantity": quantity,
            "estimated_storage_gb": estimated_storage_gb,
        },
        "breakdown": {
            "base_nft": {
                "name": nft_config["name"],
                "unit_price": round(base_nft_price, 2),
                "total": round(base_nft_price * quantity, 2),
            },
            "package_tier": {
                "name": tier_config["name"],
                "layers": tier_config["layers"],
                "unit_price": round(package_price, 2),
                "total": round(package_price * quantity, 2),
            },
            "encryption": {
                "name": encryption_config["name"],
                "unit_price": round(encryption_price, 2),
                "total": round(encryption_price * quantity, 2),
            },
            "chain": {
                "name": chain_config["name"],
                "unit_price": round(chain_surcharge, 2),
                "total": round(chain_surcharge * quantity, 2),
            },
            "storage": {
                "included_gb": included_gb,
                "billable_gb": round(billable_storage_gb, 4),
                "unit_price_per_gb": round(storage_unit_price, 2),
                "total": round(storage_price * quantity, 2),
            },
            "bulk_discount": {
                "rate": bulk_discount_rate,
                "total": round(-discount_amount, 2),
            },
            "processing_fee": {
                "percentage": processing_percentage,
                "fixed": processing_fixed,
                "total": round(processing_fee, 2),
            },
        },
        "unit_subtotal": round(unit_subtotal, 2),
        "subtotal": round(subtotal, 2),
        "discount_amount": round(discount_amount, 2),
        "after_discount": round(after_discount, 2),
        "processing_fee": round(processing_fee, 2),
        "total": round(total, 2),
        "per_unit_total": round(total / quantity, 2),
    }
