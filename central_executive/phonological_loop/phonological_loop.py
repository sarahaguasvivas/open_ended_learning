from abc import ABC, abstractmethod

class PhonologicalLoop(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def rehearse(self):
        pass
