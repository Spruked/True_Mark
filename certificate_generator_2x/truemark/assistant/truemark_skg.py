"""
Isolated assistant-side knowledge tracker for the TrueMark chat bubble.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AssistantMemory:
    prompt: str
    response: str


@dataclass
class TrueMarkAssistantSKG:
    """
    Lightweight local memory for the standalone assistant.
    """

    exchanges: List[AssistantMemory] = field(default_factory=list)

    def learn(self, prompt: str, response: str) -> None:
        self.exchanges.append(AssistantMemory(prompt=prompt, response=response))

    def summarize(self) -> Dict[str, int]:
        return {"total_exchanges": len(self.exchanges)}
