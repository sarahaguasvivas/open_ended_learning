from abc import ABC, abstractmethod

class KnowledgeConsolidator(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def consolidate(self):
        pass
