from typing import Union
from dataclasses import dataclass

@dataclass(init=False, repr=True)
class SumPeriod():
    def __init__(self, beginning: int, end: int, expected_sum_min: int, expected_sum_max : Union[int, None] = None):
        self.beginning        : int = beginning
        self.end              : int = end
        self.expected_sum_min : int = expected_sum_min
        self.expected_sum_max : int = expected_sum_max if (expected_sum_max != None) else expected_sum_min