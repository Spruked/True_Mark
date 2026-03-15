"""
Standalone TrueMark chat bubble assistant.
"""

from __future__ import annotations

from knowledge_base import COMMON_TOPICS, NFT_TYPES
from encryption_advisor import EncryptionAdvisor
from truemark_skg import TrueMarkAssistantSKG


class TrueMarkChatBubbleAssistant:
    """
    Self-contained assistant with TrueMark-specific responses.
    """

    def __init__(self):
        self.memory = TrueMarkAssistantSKG()
        self.encryption = EncryptionAdvisor()

    def respond(self, prompt: str) -> str:
        lower_prompt = prompt.lower()

        for nft_type, description in NFT_TYPES.items():
            if nft_type.lower() in lower_prompt:
                response = description
                self.memory.learn(prompt, response)
                return response

        for topic, response in COMMON_TOPICS.items():
            if topic in lower_prompt:
                self.memory.learn(prompt, response)
                return response

        if "encrypt" in lower_prompt:
            response = self.encryption.get_guidance()["when_to_encrypt"]
            self.memory.learn(prompt, response)
            return response

        response = "TrueMark certifies, encrypts, and verifies digital records through a certificate-first minting flow."
        self.memory.learn(prompt, response)
        return response
