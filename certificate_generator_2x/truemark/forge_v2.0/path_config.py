"""
Shared path helpers for the TrueMark certificate forge.
"""

from pathlib import Path


def get_repo_root() -> Path:
    """Resolve the True Mark application root from this file."""
    return Path(__file__).resolve().parents[3]


def get_truemark_root() -> Path:
    """Resolve the truemark package root."""
    return Path(__file__).resolve().parents[1]


def get_vault_root() -> Path:
    """Resolve the single authoritative True Mark Vault System."""
    return get_repo_root() / "True_Mark_Vault_System"


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
    """Resolve the temporary working area inside the authoritative Vault System."""
    return get_vault_root() / "runtime" / "temp_vault"


def ensure_temp_vault_dir() -> Path:
    """Create and return the temp_vault directory."""
    temp_vault_dir = get_temp_vault_dir()
    temp_vault_dir.mkdir(parents=True, exist_ok=True)
    return temp_vault_dir
