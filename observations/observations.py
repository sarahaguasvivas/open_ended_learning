"""
Observations:

    This class contains the simualted
    universe that the agent is going to
    experience. In the real world this
    will be an observation

    The reason this class is abstract
    is because we might want to
    stack together multiple different
    observations in the real world, so
    for example, we might want to have
    a camera observation and an IMU ob-
    servation...
"""
from abc import ABC, abstractmethod

class Observations(ABC):

    def __init__(self):
        pass

    @abstractmethod
    def observe(self):
        pass

