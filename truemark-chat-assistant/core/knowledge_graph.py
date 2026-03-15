# Josephine Knowledge Graph Core

class KnowledgeGraph:
    def __init__(self):
        self.facts = {}

    def add_fact(self, key, value):
        self.facts[key] = value

    def get_fact(self, key):
        return self.facts.get(key)

    def all_facts(self):
        return self.facts
