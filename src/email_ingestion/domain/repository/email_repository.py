from abc import ABC, abstractmethod

class EmailRepository(ABC):
    @abstractmethod
    def save(self, email):
        pass