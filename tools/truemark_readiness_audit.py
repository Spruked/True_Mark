#!/usr/bin/env python3
"""TrueMark launch-readiness audit.

This script is intentionally read-only. It inspects the repository for:
- legacy ORB references in active source and deployable metadata;
- protected minting, checkout, invoice, certificate, and registry surfaces;
- fragmented persistence locations that must be reconciled into one Vault;
- generated build artifacts that may carry stale ORB code.

Run from the repository root:
    python tools/truemark_readiness_audit.py
    python tools/truemark_readiness_audit.py --json

Exit codes:
    0: no blocking findings
    1: one or more blocking findings
    2: audit could not run
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

SKIP_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}

ACTIVE_SOURCE_ROOTS = (
    ROOT / "frontend" / "src",
    ROOT / "frontend" / "public",
    ROOT / "backend",
)

GENERATED_ROOTS = (
    ROOT / "frontend" / "dist",
    ROOT / "frontend" / "build",
)

ARCHIVE_ROOTS = (
    ROOT / "archive",
    ROOT / "truemark-human-support",
)

PROTECTED_PATHS = (
    ROOT / "contracts" / "TrueMarkMintEngine.sol",
    ROOT / "frontend" / "src" / "MintNFT.jsx",
    ROOT / "frontend" / "src" / "DemoMint.jsx",
    ROOT / "frontend" / "src" / "Checkout.jsx",
    ROOT / "frontend" / "src" / "Cart.jsx",
    ROOT / "backend" / "routes.py",
    ROOT / "backend" / "storage.py",
    ROOT / "backend" / "invoices.py",
    ROOT / "backend" / "pricing.py",
    ROOT / "backend" / "mailer.py",
    ROOT / "backend" / "node_config.py",
)

ORB_PATTERN = re.compile(
    r"\b(?:orb|assistant|chatbot|floatingorb|human_support|vite_orb_api|orb_active)\b",
    re.IGNORECASE,
)

STALE_PUBLIC_ROUTE_PATTERN = re.compile(
    r"(?:https?://[^\s<\"]+)?/(?:docs/)?orb(?:[/?#<\"\s]|$)",
    re.IGNORECASE,
)

PERSISTENCE_HINT_PATTERN = re.compile(
    r"(?:\.db$|\.sqlite3?$|\.json$|\.csv$|vault|registry|invoice|receipt|payment|mint|certificate)",
    re.IGNORECASE,
)

TEXT_SUFFIXES = {
    ".css",
    ".html",
    ".js",
    ".jsx",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yml",
    ".yaml",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    path: str
    detail: str


def _iter_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        return
    if root.is_file():
        yield root
        return

    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path


def _relative(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _read_text(path: Path) -> str | None:
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return None
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def audit_protected_surface() -> list[Finding]:
    findings: list[Finding] = []
    for path in PROTECTED_PATHS:
        if not path.exists():
            findings.append(
                Finding(
                    "warning",
                    "protected-surface",
                    _relative(path),
                    "Expected minting/commerce boundary file is absent; confirm the active implementation path before editing.",
                )
            )
    return findings


def audit_active_orb_references() -> list[Finding]:
    findings: list[Finding] = []
    for root in ACTIVE_SOURCE_ROOTS:
        for path in _iter_files(root):
            text = _read_text(path)
            if not text:
                continue

            matches = list(ORB_PATTERN.finditer(text))
            if not matches:
                continue

            # A health declaration that explicitly says the legacy ORB is inactive
            # is evidence, not contamination.
            lowered = text.lower()
            inactive_only = (
                "orb_active" in lowered
                and ("orb_active\": false" in lowered or "orb_active': false" in lowered)
                and len(matches) <= 2
            )
            placeholder_only = "no legacy orb runtime is active" in lowered
            if inactive_only or placeholder_only:
                continue

            findings.append(
                Finding(
                    "blocker",
                    "legacy-orb-active-surface",
                    _relative(path),
                    f"Contains {len(matches)} legacy ORB/assistant reference(s) in active source or public metadata.",
                )
            )

            if STALE_PUBLIC_ROUTE_PATTERN.search(text):
                findings.append(
                    Finding(
                        "blocker",
                        "stale-public-route",
                        _relative(path),
                        "Publishes a stale /orb or /docs/orb route.",
                    )
                )
    return findings


def audit_generated_artifacts() -> list[Finding]:
    findings: list[Finding] = []
    for root in GENERATED_ROOTS:
        if not root.exists():
            continue
        orb_hits = 0
        for path in _iter_files(root):
            text = _read_text(path)
            if text and ORB_PATTERN.search(text):
                orb_hits += 1
        findings.append(
            Finding(
                "blocker" if orb_hits else "warning",
                "generated-artifacts",
                _relative(root),
                (
                    f"Generated output exists and {orb_hits} file(s) contain ORB/assistant terms; remove and rebuild from clean source."
                    if orb_hits
                    else "Generated output exists; verify it was rebuilt from the clean source baseline."
                ),
            )
        )
    return findings


def audit_archives() -> list[Finding]:
    findings: list[Finding] = []
    for root in ARCHIVE_ROOTS:
        if not root.exists():
            continue
        count = sum(1 for _ in _iter_files(root))
        findings.append(
            Finding(
                "warning",
                "legacy-archive",
                _relative(root),
                f"Historical assistant code remains in the production branch ({count} files). Preserve through Git history or an archive branch, then remove from the deployable branch.",
            )
        )
    return findings


def audit_persistence_candidates() -> list[Finding]:
    findings: list[Finding] = []
    candidates: set[str] = set()

    for root in (ROOT / "backend", ROOT / "certificate_generator_2x", ROOT / "vault"):
        for path in _iter_files(root):
            relative = _relative(path)
            if PERSISTENCE_HINT_PATTERN.search(relative):
                candidates.add(relative)

    if candidates:
        preview = ", ".join(sorted(candidates)[:12])
        suffix = "" if len(candidates) <= 12 else f" (+{len(candidates) - 12} more)"
        findings.append(
            Finding(
                "warning",
                "vault-migration",
                ".",
                f"Found {len(candidates)} persistence-related path(s) requiring source-of-truth classification: {preview}{suffix}",
            )
        )
    else:
        findings.append(
            Finding(
                "warning",
                "vault-migration",
                ".",
                "No persistence candidates were detected automatically; perform a manual runtime/configuration inventory.",
            )
        )

    return findings


def run_audit() -> list[Finding]:
    if not ROOT.exists():
        raise RuntimeError(f"Repository root does not exist: {ROOT}")

    findings: list[Finding] = []
    findings.extend(audit_protected_surface())
    findings.extend(audit_active_orb_references())
    findings.extend(audit_generated_artifacts())
    findings.extend(audit_archives())
    findings.extend(audit_persistence_candidates())
    return sorted(findings, key=lambda item: (item.severity != "blocker", item.category, item.path))


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit TrueMark launch-readiness boundaries.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    args = parser.parse_args()

    try:
        findings = run_audit()
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"Audit failed: {exc}", file=sys.stderr)
        return 2

    blockers = [finding for finding in findings if finding.severity == "blocker"]
    warnings = [finding for finding in findings if finding.severity == "warning"]

    if args.json:
        print(
            json.dumps(
                {
                    "repository": str(ROOT),
                    "status": "blocked" if blockers else "review_required" if warnings else "ready",
                    "blocker_count": len(blockers),
                    "warning_count": len(warnings),
                    "findings": [asdict(finding) for finding in findings],
                },
                indent=2,
            )
        )
    else:
        status = "BLOCKED" if blockers else "REVIEW REQUIRED" if warnings else "READY"
        print(f"TrueMark launch-readiness audit: {status}")
        print(f"Blockers: {len(blockers)} | Warnings: {len(warnings)}")
        for finding in findings:
            print(f"[{finding.severity.upper()}] {finding.category}: {finding.path}")
            print(f"  {finding.detail}")

    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
