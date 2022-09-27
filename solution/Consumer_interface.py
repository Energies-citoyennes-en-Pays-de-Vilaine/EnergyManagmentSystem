from typing import *
from solution.Exceptions.ListShapeException import check_list_size
from solution.Exceptions.SpecifiedListTypeException import *
from solution.Exceptions.FunctionNotExistingException import *
from solution.Calculation_Params import CalculationParams
import numpy as np
class Consumer_interface():

	def get_f_contrib(self, calculationParams : CalculationParams) -> List[float]:
		checkFunctionExist(self, "_get_f_contrib")
		f_contrib = self._get_f_contrib(calculationParams)
		check_for_specified_list_type_exception(f_contrib, float)
		return f_contrib

	def get_integrality(self, calculationParams : CalculationParams) -> List[int]:
		checkFunctionExist(self, "_get_integrality")
		integrality = self._get_integrality(calculationParams)
		check_for_specified_list_type_exception(integrality, int)
		return integrality

	def get_minimizing_constraints(self, calculationParams : CalculationParams) -> List[np.ndarray]:
		checkFunctionExist(self, "_get_minimizing_constraints")
		minimizing_constraints = self._get_minimizing_constraints(calculationParams)
		check_for_specified_list_type_exception(minimizing_constraints, np.ndarray)
		return minimizing_constraints

	def get_functionnal_constraints(self, calculationParams : CalculationParams) -> np.ndarray:
		checkFunctionExist(self, "_get_functionnal_constraints")
		functionnal_constraints = self._get_functionnal_constraints(calculationParams)
		check_for_specified_numpy_array_type_exception(functionnal_constraints, np.float64)
		return functionnal_constraints
	
	def get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[List[float]]:
		checkFunctionExist(self, "_get_functionnal_constraints_boundaries")
		functionnal_constraints = self._get_functionnal_constraints_boundaries(calculationParams)
		check_for_specified_list_type_exception(functionnal_constraints, List)
		check_list_size(functionnal_constraints, 2)
		#TODO add better checks once all get_size interfaces will be required
		return functionnal_constraints
	
	def get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
		checkFunctionExist(self, "_get_minimizing_variables_count")
		#TODO add unit tests
		functionnal_constraints = self._get_minimizing_variables_count(calculationParams)
		return functionnal_constraints
	
	def get_constraints_size(self, calculationParams : CalculationParams) -> int:
		checkFunctionExist(self, "_get_constraints_size")
		#TODO add unit tests
		functionnal_constraints = self._get_constraints_size(calculationParams)
		return functionnal_constraints

	def fill_minimizing_constraints(self, calculationParams : CalculationParams, tofill : np.ndarray, xpars : List[int], ypars : List[int]):
		checkFunctionExist(self, "_fill_minimizing_constraints")
		#TODO add unit tests
		self._fill_minimizing_constraints(calculationParams, tofill, xpars, ypars)

	def fill_functionnal_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpar: int, ypar: int):
		checkFunctionExist(self, "_fill_functionnal_constraints")
		#TODO add unit tests
		self._fill_functionnal_constraints(calculationParams, tofill, xpar, ypar)