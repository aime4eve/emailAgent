import json
from ..domain.repository.knowledge_graph_repository import KnowledgeGraphRepository
from ..domain.model.graph import KnowledgeGraph

class FileKnowledgeGraphRepository(KnowledgeGraphRepository):
    def __init__(self, file_path='data/knowledge_graph.json'):
        self.file_path = file_path

    def save(self, graph):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(graph.to_dict(), f, indent=4)

    def load(self):
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return KnowledgeGraph.from_dict(data)
        except FileNotFoundError:
            return KnowledgeGraph()