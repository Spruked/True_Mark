"""Printable certificate security-module registry.

These are original, geometric, printer-safe presentation/forensic modules.
Module selection is retained as private verifier configuration and never
replaces the authoritative Vault evidence chain.
"""

from __future__ import annotations

from typing import Dict, List


MODULE_NAMES = [
    ("F01", "Guilloché Medallions", "mathematical medallion curves"),
    ("F02", "Guilloché Borders", "continuous mathematical border curves"),
    ("F03", "Guilloché Corner Rosettes", "corner rosette fields"),
    ("F04", "Latent Image Fields", "angle and scan-responsive geometric field"),
    ("F05", "Microtext Borders", "small repeated verification text around the frame"),
    ("F06", "Microtext Corner Blocks", "small encoded corner text blocks"),
    ("F07", "Micro-Glyph Fields", "repeating geometric glyph field"),
    ("F08", "Dot-Cluster Encoding", "seeded dot clusters at defined coordinates"),
    ("F09", "Serial-Encoded Guilloché", "ID-seeded curve variation"),
    ("F10", "Serial-Encoded Watermark", "ID-hash watermark variation"),
    ("F11", "Radial Seal Watermark", "circular radial seal field"),
    ("F12", "Generic Crest Watermark", "brand-neutral shield, laurel, or starburst"),
    ("F13", "Glyph Grid Watermark", "repeating geometric watermark grid"),
    ("F14", "Diagonal Ribbon Watermark", "diagonal security ribbon"),
    ("F15", "Pattern-Seeded Lattice", "seeded lattice geometry"),
    ("F16", "Noise-Field Signature", "certificate-hash-derived noise field"),
    ("F17", "Hidden Coordinate Points", "encoded border coordinate markers"),
    ("F18", "Alignment Micro-Ticks", "angle-specific alignment ticks"),
    ("F19", "Micro-QR Fragmentation", "distributed verification fragments"),
    ("F20", "Micro-Line Engraving", "fine engraved line field"),
    ("F21", "Micro-Diamond Field", "small diamond pattern field"),
    ("F22", "Corner-Anomaly Marks", "unique corner variation markers"),
    ("F23", "Border-Thickness Encoding", "seeded line-weight variation"),
    ("F24", "Serial-Column Encoding", "serial-derived vertical micro-mark column"),
    ("F25", "Inner-Frame Microtext Ring", "microtext inside the inner frame"),
    ("F26", "Mandala Watermark", "radial encoded mandala"),
    ("F27", "Micro-Ribbon Watermark", "thin ribbon with repeated microtext"),
    ("F28", "Corner Foil Simulation", "printable gradient corner patch"),
    ("F29", "Strip Foil Simulation", "printable horizontal or vertical gradient"),
    ("F30", "Diagonal Foil Sweep", "printable diagonal gradient sweep"),
]

# Deeper profiles add modules without changing the authoritative evidence
# model. The thresholds intentionally match the approved prime depths.
MODULE_THRESHOLDS = [2, 2, 2, 3, 3, 3, 5, 5, 5, 5, 7, 7, 7, 7, 7, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 13, 13, 13, 13, 13]


def list_forensic_modules(layer_count: int = 13) -> List[Dict[str, object]]:
    """Return the printable modules available at a governed depth."""
    count = int(layer_count)
    return [
        {
            "module_id": module_id,
            "name": name,
            "description": description,
            "activation_depth": threshold,
            "printable_on_standard_paper": True,
            "seeded_per_certificate": True,
        }
        for (module_id, name, description), threshold in zip(MODULE_NAMES, MODULE_THRESHOLDS)
        if count >= threshold
    ]


def get_module_catalog() -> List[Dict[str, object]]:
    """Return all 30 registered modules, regardless of profile depth."""
    return list_forensic_modules(13)
