# Josephine Inference Engine

try:
    from .knowledge_graph import KnowledgeGraph
except ImportError:
    from knowledge_graph import KnowledgeGraph

class InferenceEngine:
    def __init__(self, kg: KnowledgeGraph):
        self.kg = kg

    def answer(self, question: str) -> str:
        # Simple rule-based response for demo
        if "privacy" in question.lower():
            return "True Mark Mint Engine values your privacy. All data is purged after minting. Josephine can answer more!"
        if "certificate" in question.lower():
            return "Each NFT comes with a forensic-grade certificate, including a cryptographic glyph trace."
        return "Josephine is here to help! Please ask your question."
