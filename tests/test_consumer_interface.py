from unittest import TestCase
import numpy as np
from solution.Consumer_interface import *
from solution.Calculation_Params import CalculationParams
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


class Consumer_get_functionnal_constraints_valid(Consumer_interface):
	def _get_functionnal_constraints(self, calculationParams: CalculationParams):
		return np.array([0,1])

class Consumer_interface_TestCase(TestCase):
	def test_Consumer_No_implemented_Methods_integrality(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_integrality(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.function_name, "_get_integrality")

	def test_Consumer_No_implemented_Methods_minimizing_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_minimizing_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.function_name, "_get_minimizing_constraints")
	
	def test_Consumer_No_implemented_Methods_functionnal_constraints(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_functionnal_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.function_name, "_get_functionnal_constraints")
	
	def test_Consumer_No_implemented_Methods_F_contrib(self):
		toCheck = Consumer_No_implemented_Methods()
		with self.assertRaises(FunctionNotExistingException) as error:
			toCheck.get_f_contrib(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.function_name, "_get_f_contrib")

	def test_Consumer_F_contrib_invalid(self):
		toCheck = Consumer_F_contrib_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_f_contrib(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.expected_type, float)
	
	def test_Consumer_F_contrib_valid(self):
		toCheck = Consumer_F_contrib_valid()
		self.assertListEqual(toCheck.get_f_contrib(CalculationParams(0, 5, 1, 1, [0 for i in range(6)])),[0.5,1,0.2])

	def test_Consumer_integrality_invalid(self):
		toCheck = Consumer_get_integrality_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_integrality(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.expected_type, int)
	
	def test_Consumer_integrality_valid(self):
		toCheck = Consumer_get_integrality_valid()
		self.assertListEqual(toCheck.get_integrality(CalculationParams(0, 5, 1, 1, [0 for i in range(6)])),[1,1,0])
	
	def test_Consumer_minimizing_constraints_invalid(self):
		toCheck = Consumer_get_minimizing_constraints_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_minimizing_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.expected_type, np.ndarray)
	
	def test_Consumer_minimizing_constraints_valid(self):
		toCheck = Consumer_get_minimizing_constraints_valid()
		self.assertTrue( toCheck.get_minimizing_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))[0].all() == [np.array((0,1))][0].all())
	
	def test_Consumer_functionnal_constraints_invalid(self):
		toCheck = Consumer_get_functionnal_constraints_invalid()
		with self.assertRaises(SpecifiedListTypeException) as error:
			toCheck.get_functionnal_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)]))
		self.assertEqual(error.exception.expected_type, np.float64)
	
	def test_Consumer_functionnal_constraints_valid(self):
		toCheck = Consumer_get_functionnal_constraints_valid()
		self.assertTrue( toCheck.get_functionnal_constraints(CalculationParams(0, 5, 1, 1, [0 for i in range(6)])).all() == np.array([0,1]).all())
#TODO check for boundaries