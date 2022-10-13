from typing import Tuple
from data_reader_interface import DataReaderInterface
import numpy as np
from datetime import datetime
from typing import *
class FileReader(DataReaderInterface):
    def __init__(self, filepath) -> None:
        self.filepath = filepath
    def readData(self, clientID) -> np.ndarray:
        time = []
        data  = []
        
        with open(self.filepath) as inp:
            for line in inp:
                if ord('0') <= ord(line[0]) and ord('9') >= ord(line[0]):
                    time.append(int(line.split(" ")[2]))
                    data.append(float(line.split(" ")[3].replace(",", ".")))
        return np.vstack((np.array(time), np.array(data))).transpose()