from abc import ABC, abstractmethod

class KnowledgeGraphRepository(ABC):
    @abstractmethod
    def save(self, graph):
        pass

    @abstractmethod
    def load(self):
        pass