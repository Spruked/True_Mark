"""Printable certificate security-module registry.

These are original, geometric, printer-safe presentation/forensic modules.
They are not a claim of legal currency or banknote equivalence. Module
selection is recorded with the certificate profile and never replaces the
authoritative Vault evidence chain.
"""

from __future__ import annotations

from typing import Dict, List


MODULE_NAMES = [
    ("guilloche-medallions", "Guilloché Medallions", "currency-style mathematical medallion curves"),
    ("guilloche-borders", "Guilloché Borders", "continuous mathematical border curves"),
    ("guilloche-corner-rosettes", "Guilloché Corner Rosettes", "corner rosette fields"),
    ("latent-image-fields", "Latent Image Fields", "angle and scan-responsive geometric field"),
    ("microtext-borders", "Microtext Borders", "small repeated verification text around the frame"),
    ("microtext-corner-blocks", "Microtext Corner Blocks", "small encoded corner text blocks"),
    ("micro-glyph-fields", "Micro-Glyph Fields", "repeating geometric glyph field"),
    ("dot-cluster-encoding", "Dot-Cluster Encoding", "seeded dot clusters at defined coordinates"),
    ("serial-encoded-guilloche", "Serial-Encoded Guilloché", "ID-seeded curve variation"),
    ("serial-encoded-watermark", "Serial-Encoded Watermark", "ID-hash watermark variation"),
    ("radial-seal-watermark", "Radial Seal Watermark", "circular radial seal field"),
    ("generic-crest-watermark", "Generic Crest Watermark", "brand-neutral shield, laurel, or starburst"),
    ("glyph-grid-watermark", "Glyph Grid Watermark", "repeating geometric watermark grid"),
    ("diagonal-ribbon-watermark", "Diagonal Ribbon Watermark", "diagonal security ribbon"),
    ("pattern-seeded-lattice", "Pattern-Seeded Lattice", "seeded lattice geometry"),
    ("noise-field-signature", "Noise-Field Signature", "certificate-hash-derived noise field"),
    ("hidden-coordinate-points", "Hidden Coordinate Points", "encoded border coordinate markers"),
    ("alignment-micro-ticks", "Alignment Micro-Ticks", "angle-specific alignment ticks"),
    ("micro-qr-fragmentation", "Micro-QR Fragmentation", "distributed verification fragments"),
    ("micro-line-engraving", "Micro-Line Engraving", "fine engraved line field"),
    ("micro-diamond-field", "Micro-Diamond Field", "small diamond pattern field"),
    ("corner-anomaly-marks", "Corner-Anomaly Marks", "unique corner variation markers"),
    ("border-thickness-encoding", "Border-Thickness Encoding", "seeded line-weight variation"),
    ("serial-column-encoding", "Serial-Column Encoding", "serial-derived vertical micro-mark column"),
    ("inner-frame-microtext-ring", "Inner-Frame Microtext Ring", "microtext inside the inner frame"),
    ("mandala-watermark", "Mandala Watermark", "radial encoded mandala"),
    ("micro-ribbon-watermark", "Micro-Ribbon Watermark", "thin ribbon with repeated microtext"),
    ("corner-foil-simulation", "Corner Foil Simulation", "printable gradient corner patch"),
    ("strip-foil-simulation", "Strip Foil Simulation", "printable horizontal or vertical gradient"),
    ("diagonal-foil-sweep", "Diagonal Foil Sweep", "printable diagonal gradient sweep"),
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
