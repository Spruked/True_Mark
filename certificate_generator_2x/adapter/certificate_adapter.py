"""
Adapter layer for alternate presentation formats built from TrueMark certificates.
"""

from __future__ import annotations

from typing import Dict, List


class DojoCertificateAdapter:
    """
    Wrap the forge with alternate presentation layers without altering core issuance.
    """

    def generate_social_formats(self, cert_data: Dict) -> Dict[str, Dict[str, str]]:
        serial = cert_data.get("dals_serial", "UNKNOWN")
        title = cert_data.get("asset_title", "TrueMark Certificate")
        return {
            "linkedin": {
                "headline": f"{title} verified by TrueMark",
                "caption": f"Certificate {serial} has been anchored and recorded.",
            },
            "instagram": {
                "headline": title,
                "caption": f"Verified record {serial}",
            },
            "twitter": {
                "headline": f"TrueMark verification: {serial}",
                "caption": f"{title} is now recorded and verifiable.",
            },
        }

    def add_visual_personalization(self, template: str, user_prefs: Dict) -> str:
        accent = user_prefs.get("accent", "gold")
        badge = user_prefs.get("badge", "verified")
        return f"{template}|accent={accent}|badge={badge}"

    def create_collection_psychology(self, user_certs: List[Dict]) -> Dict[str, object]:
        total = len(user_certs)
        tier = "foundational" if total < 3 else "established" if total < 10 else "advanced"
        return {
            "total_certificates": total,
            "tier": tier,
            "progress_to_next_tier": max(0, (3 if total < 3 else 10) - total),
        }
