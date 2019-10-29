"""
HaveISeen:

    This class represents the process of
    figuring out if an instance belongs to
    existing knowledge or if it should be
    added as new knowledge.
"""
from abc import ABC, abstractmethod

class HaveISeen():

    def __init__(self):
        pass

    @abstractmethod
    def check(self):
        pass



