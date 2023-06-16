from unittest import TestCase
import numpy as np
from solution.Consumer_interface import *
from solution.Calculation_Params import CalculationParams
from solution.Exceptions.ListShapeException import ListShapeException
basic_calculation_params = CalculationParams(0, 5, 1, 1, [[0 for i in range(6)]])
basic_vars = [1.0, 2.0, 3.0]
class Consumer_No_implemented_Methods(Consumer_interface):
	pass

class Consumer_F_contrib_invalid(Consumer_interface):
	def _get_f_contrib(self, calculationParams: CalculationParams):
		return "test"


class Consumer_F_contrib_valid(Consumer_interface):
	def _get_f_contrib(self, calculationParams: CalculationParams):
		return [0.5,1,0.2]

class Consumer_get_integrality_invalid(Consumer_interface):
	def _get_integrality(self, calculationParams: CalculationParams):
		return [1,1.2,0]


class Consumer_get_integrality_valid(Consumer_interface):
	def _get_integrality(self, calculationParams: CalculationParams):
		return [1,1,0]

class Consumer_get_consumption_curve_invalid_list(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return [1,4,5]

class Consumer_get_consumption_curve_invalid_np_type(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return np.array(["definitely not a float"])

class Consumer_get_consumption_curve_valid(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return np.array([5.0, 30, 4.5])



class Consumer_get_minimizing_variables_count(Consumer_interface):
	def _get_minimizing_variables_count(self, calculationParams: CalculationParams):
		return 5
class Consumer_get_constraints_size(Consumer_interface):
	def _get_constraints_size(self, calculationParams: CalculationParams):
		return 42

class Consumer_get_base_consumption_valid_no_function(Consumer_interface):
	def __init__(self) -> None:
		self.has_base_consumption = False

class Consumer_get_base_consumption_invalid_no_function(Consumer_interface):
	def __init__(self) -> None:
		self.has_base_consumption = True

class Consumer_get_base_consumption_invalid_wrong_array_type(Consumer_interface):
	def __init__(self) -> None:
		self.has_base_consumption = True
	def _get_base_consumption(self, calculationParams: CalculationParams):
		return [0.3]

class Consumer_get_base_consumption_invalid_val_type(Consumer_interface):
	def __init__(self) -> None:
		self.has_base_consumption = True
	def _get_base_consumption(self, calculationParams: CalculationParams):
		return np.array(["test"])

class Consumer_get_base_consumption_valid(Consumer_interface):
	def __init__(self) -> None:
		self.has_base_consumption = True
	def _get_base_consumption(self, calculationParams: CalculationParams):
		return np.array([0.3])

class Consumer_fill_minimizing_constraints_valid(Consumer_interface):
	def _fill_minimizing_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpars:List[int], ypars:List[int]):
		for i in range(len(tofill)):
			tofill[i] = xpars[0] + ypars[0] * 2 + i

class Consumer_fill_functionnal_constraints(Consumer_interface):
	def _fill_functionnal_constraints(self, calculationParams: CalculationParams, toFill: np.ndarray, x: int, y: int):
		for i in range(len(toFill)):
			toFill[i] = x + y * 2 + i

class Consumer_get_functionnal_constraints_boundaries_invalid_array_length(Consumer_interface):
	def _get_functionnal_constraints_boundaries(self, calculationParams: CalculationParams):
		return [[1], [2], [3]]

class Consumer_get_functionnal_constraints_boundaries_invalid_global_array_type(Consumer_interface):
	def _get_functionnal_constraints_boundaries(self, calculationParams: CalculationParams):
		return [1, 2]

class Consumer_get_functionnal_constraints_boundaries_invalid_array_type_1(Consumer_interface):
	def _get_functionnal_constraints_boundaries(self, calculationParams: CalculationParams):
		return [[""], [2]]

class Consumer_get_functionnal_constraints_boundaries_invalid_array_type_2(Consumer_interface):
	def _get_functionnal_constraints_boundaries(self, calculationParams: CalculationParams):
		return [[1], [""]]

class Consumer_get_functionnal_constraints_boundaries_valid(Consumer_interface):
	def _get_functionnal_constraints_boundaries(self, calculationParams: CalculationParams):
		return [[1.5], [2]]

class Consumer_interface_TestCase(TestCase):
	def test_Consumer_No_implemented_Methods_integrality(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_integrality(basic_calculation_params)
		self.assertEqual(error.exception.function_name, "_get_integrality")

	def test_Consumer_No_implemented_Methods_F_contrib(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_f_contrib(basic_calculation_params)
		self.assertEqual(error.exception.function_name, "_get_f_contrib")

	def test_Consumer_No_Implemented_Methods_get_minimizing_variables_count(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_minimizing_variables_count(basic_calculation_params)
		self.assertAlmostEqual(error.exception.function_name, "_get_minimizing_variables_count")

	def test_Consumer_No_Implemented_Methods_get_constraints_size(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_constraints_size(basic_calculation_params)
		self.assertAlmostEqual(error.exception.function_name, "_get_constraints_size")

	def test_Consumer_No_Implemented_Methods_get_consumption_curve(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_consumption_curve(basic_calculation_params, basic_vars)
		self.assertAlmostEqual(error.exception.function_name, "_get_consumption_curve")

	def test_Consumer_No_Implemented_Methods_get_base_consumption(self):
		toCheck = Consumer_get_base_consumption_invalid_no_function()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_base_consumption(basic_calculation_params)
		self.assertAlmostEqual(error.exception.function_name, "_get_base_consumption")

	def test_Consumer_No_Implemented_Methods_fill_minimizing_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.fill_minimizing_constraints(basic_calculation_params, np.zeros(2), [0], [1])
		self.assertAlmostEqual(error.exception.function_name, "_fill_minimizing_constraints")

	def test_Consumer_No_Implemented_Methods_fill_functionnal_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.fill_functionnal_constraints(basic_calculation_params, np.zeros(2), [0], [1])
		self.assertAlmostEqual(error.exception.function_name, "_fill_functionnal_constraints")
	
	def test_Consumer_No_Implemented_Methods_get_functionnal_constraints_boundaries(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertAlmostEqual(error.exception.function_name, "_get_functionnal_constraints_boundaries")
	
	def test_Consumer_F_contrib_invalid(self):
		toCheck = Consumer_F_contrib_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_f_contrib(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, float)
	
	def test_Consumer_F_contrib_valid(self):
		toCheck = Consumer_F_contrib_valid()
		self.assertListEqual(toCheck.get_f_contrib(basic_calculation_params),[0.5,1,0.2])

	def test_Consumer_integrality_invalid(self):
		toCheck = Consumer_get_integrality_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_integrality(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, int)
	
	def test_Consumer_integrality_valid(self):
		toCheck = Consumer_get_integrality_valid()
		self.assertListEqual(toCheck.get_integrality(basic_calculation_params),[1,1,0])
	
	def test_Consumer_get_minimizing_variables_count(self):
		toCheck = Consumer_get_minimizing_variables_count()
		self.assertTrue(isinstance(toCheck.get_minimizing_variables_count(basic_calculation_params), int))

	def test_Consumer_get_constraints_size(self):
		toCheck = Consumer_get_constraints_size()
		self.assertTrue(isinstance(toCheck.get_constraints_size(basic_calculation_params), int))
	
	def test_Consumer_get_consumption_curve_invalid_list(self):
		toCheck = Consumer_get_consumption_curve_invalid_list()
		with self.assertRaises(SpecifiedListTypeException) as error:
			result = toCheck.get_consumption_curve(basic_calculation_params, basic_vars)
		self.assertTrue(error.exception.expected_list_type is np.ndarray)

	def test_Consumer_get_consumption_curve_invalid_np_type(self):
		toCheck = Consumer_get_consumption_curve_invalid_np_type()
		with self.assertRaises(SpecifiedListTypeException) as error:
			result = toCheck.get_consumption_curve(basic_calculation_params, basic_vars)
		self.assertTrue(error.exception.expected_type is np.float64)
	
	def test_Consumer_get_consumption_curve_valid(self):
		toCheck = Consumer_get_consumption_curve_valid()
		result = toCheck.get_consumption_curve(basic_calculation_params, basic_vars)
		self.assertTrue(isinstance(result, np.ndarray))
	
	def test_Consumer_get_base_consumption_No_implemented_Methods(self):
		toCheck = Consumer_No_implemented_Methods()
		result = toCheck.get_base_consumption(basic_calculation_params)
		self.assertAlmostEqual(result.all(), np.array([0.0] * basic_calculation_params.get_simulation_size()).all())

	def test_Consumer_get_base_consumption_valid_no_function(self):
		toCheck = Consumer_get_base_consumption_valid_no_function()
		result = toCheck.get_base_consumption(basic_calculation_params)
		self.assertAlmostEqual(result.all(), np.array([0.0] * basic_calculation_params.get_simulation_size()).all())
	
	def test_Consumer_get_base_consumption_invalid_no_function(self):
		toCheck = Consumer_get_base_consumption_invalid_no_function()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_base_consumption(basic_calculation_params)
		self.assertAlmostEqual(error.exception.function_name, "_get_base_consumption")
	
	def test_Consumer_get_base_consumption_invalid_wrong_array_type(self):
		toCheck = Consumer_get_base_consumption_invalid_wrong_array_type()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_base_consumption(basic_calculation_params)
		self.assertEqual(error.exception.expected_list_type, np.ndarray)
	
	def test_Consumer_get_base_consumption_invalid_val_type(self):
		toCheck = Consumer_get_base_consumption_invalid_val_type()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_base_consumption(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, np.float64)
	
	def test_Consumer_get_base_consumption_valid(self):
		toCheck = Consumer_get_base_consumption_valid()
		result = toCheck.get_base_consumption(basic_calculation_params)
		self.assertEqual(result.all(), np.array([0.3]).all())
	
	def test_Consumer_fill_minimizing_constraints_wrong_x_and_y(self):
		toCheck = Consumer_fill_minimizing_constraints_valid()
		toFill = np.zeros((5,))
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.fill_minimizing_constraints(basic_calculation_params, toFill, "hello", [12] )
		self.assertEqual(error.exception.expected_list_type, list)
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.fill_minimizing_constraints(basic_calculation_params, toFill, [12], "hello" )
		self.assertEqual(error.exception.expected_list_type, list)
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.fill_minimizing_constraints(basic_calculation_params, toFill, [10.5], [12] )
		self.assertEqual(error.exception.expected_type, int)
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.fill_minimizing_constraints(basic_calculation_params, toFill, [12], [10.5] )
		self.assertEqual(error.exception.expected_type, int)

	def test_Consumer_fill_minimizing_constraints_valid(self):
		toCheck = Consumer_fill_minimizing_constraints_valid()
		toFill = np.zeros((5,))
		toCheck.fill_minimizing_constraints(basic_calculation_params, toFill,  [12], [14])
		self.assertListEqual(list(toFill), [40., 41., 42., 43., 44.])
	
	def test_Consumer_fill_functionnal_constraints(self):
		toCheck = Consumer_fill_functionnal_constraints()
		toFill = np.zeros((5,))
		toCheck.fill_functionnal_constraints(basic_calculation_params, toFill,  12, 14)
		self.assertListEqual(list(toFill), [40., 41., 42., 43., 44.])
	
	def test_Consumer_get_functionnal_constraints_boundaries_invalid_array_length(self):
		toCheck = Consumer_get_functionnal_constraints_boundaries_invalid_array_length()
		with self.assertRaises(ListShapeException) as error:
			toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertEqual(3, error.exception.actual_shape)
		self.assertEqual(2, error.exception.expected_shape)
	
	def test_Consumer_get_functionnal_constraints_boundaries_invalid_global_array_type(self):
		toCheck = Consumer_get_functionnal_constraints_boundaries_invalid_global_array_type()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, List)

	def test_Consumer_get_functionnal_constraints_boundaries_invalid_array_type_1(self):
		toCheck = Consumer_get_functionnal_constraints_boundaries_invalid_array_type_1()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, float)

	def test_Consumer_get_functionnal_constraints_boundaries_invalid_array_type_2(self):
		toCheck = Consumer_get_functionnal_constraints_boundaries_invalid_array_type_2()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, float)

	def test_Consumer_get_functionnal_constraints_boundaries_valid(self):
		toCheck = Consumer_get_functionnal_constraints_boundaries_valid()
		result = toCheck.get_functionnal_constraints_boundaries(basic_calculation_params)
		self.assertListEqual(result, [[1.5], [2]])
