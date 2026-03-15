"""
Shared path helpers for the TrueMark certificate forge.
"""

from pathlib import Path


def get_repo_root() -> Path:
    """Resolve the repository root from this file."""
    return Path(__file__).resolve().parents[2]


def get_truemark_root() -> Path:
    """Resolve the truemark package root."""
    return Path(__file__).resolve().parents[1]


def get_vault_root() -> Path:
    """Resolve the default Vault_System_1.0 path."""
    return get_repo_root() / "Vault_System_1.0"


def get_templates_path() -> Path:
    """Resolve template asset directory."""
    return get_truemark_root() / "templates"


def get_fonts_path() -> Path:
    """Resolve font directory."""
    return get_truemark_root() / "fonts"


def get_keys_path() -> Path:
    """Resolve signing key directory."""
    return get_truemark_root() / "keys"


def get_temp_vault_dir() -> Path:
    """Resolve the temp_vault directory used by local workflows."""
    return get_repo_root() / "temp_vault"


def ensure_temp_vault_dir() -> Path:
    """Create and return the temp_vault directory."""
    temp_vault_dir = get_temp_vault_dir()
    temp_vault_dir.mkdir(parents=True, exist_ok=True)
    return temp_vault_dir
