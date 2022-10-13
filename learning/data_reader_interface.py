import numpy as np
class DataReaderInterface():
    def readData(self, clientID) -> np.ndarray:
        raise "not supported, you have to overload this method"
    