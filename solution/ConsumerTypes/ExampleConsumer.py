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
    def _get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[List[float]]:
        raise "not implemented yet"
    def _get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
        raise "not implemented yet"
    def _get_constraints_size(self, calculationParams : CalculationParams) -> int:
        raise "not implemented yet"
    def _fill_minimizing_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpars: List[int], ypars: List[int]):
        raise "not implemented yet"
    def _fill_functionnal_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpar: int, ypar: int):
        raise "not implemented yet"
    def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
        raise "not implemented yet"
    #ONLY IF it hase a base consumption ie it consumes no matter what
    def _get_base_consumption(self, calculationParams : CalculationParams) -> np.ndarray:
        raise "not implemented yet"
    def _get_decisions(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
        raise "not implemented yet"