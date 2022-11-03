from unittest import TestCase
import numpy as np
from solution.Consumer_interface import *
from solution.Calculation_Params import CalculationParams
basic_calculation_params = CalculationParams(0, 5, 1, 1, [0 for i in range(6)])
basic_vars = [1.0, 2.0, 3.0]
class Consumer_No_implemented_Methods(Consumer_interface):
	def unused(self):
		return

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

class Consumer_get_minimizing_constraints_invalid(Consumer_interface):
	def _get_minimizing_constraints(self, calculationParams: CalculationParams):
		return [1,1.2,0]


class Consumer_get_minimizing_constraints_valid(Consumer_interface):
	def _get_minimizing_constraints(self, calculationParams: CalculationParams):
		return [np.array((0,1))]

class Consumer_get_functionnal_constraints_invalid(Consumer_interface):
	def _get_functionnal_constraints(self, calculationParams: CalculationParams):
		return [1,1.2,0]

class Consumer_get_consumption_curve_invalid_list(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return [1,4,5]

class Consumer_get_consumption_curve_invalid_np_type(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return np.array(["definitely not a float"])

class Consumer_get_consumption_curve_valid(Consumer_interface):
	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		return np.array([5.0, 30, 4.5])


class Consumer_get_functionnal_constraints_valid(Consumer_interface):
	def _get_functionnal_constraints(self, calculationParams: CalculationParams):
		return np.array([0,1])

class Consumer_get_minimizing_variables_count(Consumer_interface):
	def _get_minimizing_variables_count(self, calculationParams: CalculationParams):
		return 5
class Consumer_get_constraints_size(Consumer_interface):
	def _get_constraints_size(self, calculationParams: CalculationParams):
		return 42
class Consumer_interface_TestCase(TestCase):
	def test_Consumer_No_implemented_Methods_integrality(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_integrality(basic_calculation_params)
		self.assertEqual(error.exception.function_name, "_get_integrality")

	def test_Consumer_No_implemented_Methods_minimizing_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_minimizing_constraints(basic_calculation_params)
		self.assertEqual(error.exception.function_name, "_get_minimizing_constraints")
	
	def test_Consumer_No_implemented_Methods_functionnal_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_functionnal_constraints(basic_calculation_params)
		self.assertEqual(error.exception.function_name, "_get_functionnal_constraints")
	
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

	def test_Consumer_No_Implemented_Methods_get_constraints_size(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_consumption_curve(basic_calculation_params, basic_vars)
		self.assertAlmostEqual(error.exception.function_name, "_get_consumption_curve")

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
	
	def test_Consumer_minimizing_constraints_invalid(self):
		toCheck = Consumer_get_minimizing_constraints_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_minimizing_constraints(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, np.ndarray)
	
	def test_Consumer_minimizing_constraints_valid(self):
		toCheck = Consumer_get_minimizing_constraints_valid()
		self.assertTrue( toCheck.get_minimizing_constraints(basic_calculation_params)[0].all() == [np.array((0,1))][0].all())
	
	def test_Consumer_functionnal_constraints_invalid(self):
		toCheck = Consumer_get_functionnal_constraints_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_functionnal_constraints(basic_calculation_params)
		self.assertEqual(error.exception.expected_type, np.float64)
	
	def test_Consumer_functionnal_constraints_valid(self):
		toCheck = Consumer_get_functionnal_constraints_valid()
		self.assertTrue( toCheck.get_functionnal_constraints(basic_calculation_params).all() == np.array([0,1]).all())
		#TODO check for boundaries
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