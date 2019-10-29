from abc import ABC, abstractmethod

class EpisodicBuffer(ABC):

    def __init__(self):
        pass


    @abstractmethod
    def push(self):
        pass

    @abstractmethod
    def pop(self):
        pass
