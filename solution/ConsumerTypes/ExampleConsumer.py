#this is just a template of the functions required to implement, do not use
from solution.Consumer_interface import Consumer_interface
from solution.Calculation_Params import CalculationParams
import numpy as np
from typing import *

class ExampleConsumer(Consumer_interface):
    def _get_f_contrib(self, calculationParams : CalculationParams) -> List[float]:
        raise "not implemented yet"
    def _get_integrality(self, calculationParams : CalculationParams) -> List[int]:
        raise "not implemented yet"
    def _get_minimizing_constraints(self, calculationParams : CalculationParams) -> List[np.ndarray]:
        raise "not implemented yet"
    def _get_functionnal_constraints(self, calculationParams : CalculationParams) -> np.ndarray:
        raise "not implemented yet"
    def _get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[np.ndarray]:
        raise "not implemented yet"
    def _get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
        raise "not implemented yet"
    def _get_constraints_size(self, calculationParams : CalculationParams) -> int:
        raise "not implemented yet"