from abc import ABC, abstractmethod

class Knowledge(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def store_all_knowledge(self):
        """
        Store all knowledge: Preferrably store
        all knowledge as an HDF5 file.

        """
        pass
