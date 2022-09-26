from solution.Exceptions.SpecifiedListTypeException import *
from unittest import TestCase
import numpy as np
class SpecifiedListExceptionTestCase(TestCase):
	def test_not_list_raises_exception(self):
		a = {}
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_list_type_exception(a, int)
		try :
			check_for_specified_list_type_exception(a, int)
		except SpecifiedListTypeException as e:
			self.assertFalse(e.is_list)
			self.assertEqual(e.expected_list_type, type([]))

	def test_not_correct_type_raise_exception_index_0(self):
		a = ["hello",6]
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_list_type_exception(a, int)
		try :
			check_for_specified_list_type_exception(a, int)
		except SpecifiedListTypeException as e:
			self.assertTrue(e.is_list)
			self.assertEqual(e.index, 0)
			self.assertEqual(e.expected_type, int)

	def test_not_correct_type_raise_exception_index_1(self):
		a = [6, "hello"]
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_list_type_exception(a, int)
		try :
			check_for_specified_list_type_exception(a, int)
		except SpecifiedListTypeException as e:
			self.assertTrue(e.is_list)
			self.assertEqual(e.index, 1)
			self.assertEqual(e.expected_type, int)

	def test_no_exception_int(self):
		a = [4,3,2]
		check_for_specified_list_type_exception(a, int)
	
	def test_no_exception_pure_float(self):
		a = [4.1,3.2,2.3]
		check_for_specified_list_type_exception(a, float)
	
	def test_no_exception_mixed_float_int(self):
		a = [4.1,3,2.3]
		check_for_specified_list_type_exception(a, float)
		
class SpecifiedNumpyArrayExceptionTestCase(TestCase):
	def test_not_list_raises_exception(self):
		a = {}
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_numpy_array_type_exception(a, np.int64)
		try :
			check_for_specified_numpy_array_type_exception(a, np.int64)
		except SpecifiedListTypeException as e:
			self.assertFalse(e.is_list)
			self.assertEqual(e.expected_list_type, np.ndarray)

	def test_not_correct_type_raise_exception_index_0(self):
		a = np.array(["hello",6])
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_numpy_array_type_exception(a, np.int64)
		try :
			check_for_specified_numpy_array_type_exception(a, np.int64)
		except SpecifiedListTypeException as e:
			self.assertTrue(e.is_list)
			self.assertEqual(e.index, 0)
			self.assertEqual(e.expected_type, np.int64)

	def test_not_correct_type_raise_exception_index_1(self):
		a = np.array([6, "hello"])
		with self.assertRaises((SpecifiedListTypeException,)) as context:
			check_for_specified_numpy_array_type_exception(a, np.int64)
		try :
			check_for_specified_numpy_array_type_exception(a, np.int64)
		except SpecifiedListTypeException as e:
			self.assertTrue(e.is_list)
			self.assertEqual(e.index, 0)
			self.assertEqual(e.expected_type, np.int64)

	def test_no_exception_int(self):
		a = np.array([4,3,2])
		check_for_specified_numpy_array_type_exception(a, np.int64)
	
	def test_no_exception_pure_float(self):
		a = np.array([4.1,3.2,2.3])
		check_for_specified_numpy_array_type_exception(a, np.float64)
	
	def test_no_exception_mixed_float_int(self):
		a = np.array([4.1,3,2.3])
		check_for_specified_numpy_array_type_exception(a, np.float64)
		


