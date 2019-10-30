from .observations import *
from keras.datasets import mnist

class MNISTObservations(Observations):
    def __init__(self):
        self.observations = None
        pass


    def observe(self):
        pass
