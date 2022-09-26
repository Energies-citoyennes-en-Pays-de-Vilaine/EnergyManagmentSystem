from solution.Exceptions.ListShapeException import *
import numpy as np
from unittest import TestCase

class ListShapeExceptionTestCase(TestCase):
	def test_empty_to_1(self):
		a = []
		b = (1,)
		with self.assertRaises(ListShapeException) as exceptionReturned:
			check_list_shape(a,b)
		self.assertEqual(exceptionReturned.exception.expected_shape, (1,))
		self.assertEqual(exceptionReturned.exception.actual_shape, (0,))
	def test_empty_to_empty(self):
		a = []
		b = (0,)
		check_list_shape(a, b)

	def test_two_to_two(self):
		a = [[2,2], [3,3]]
		check_list_shape(a, (2, 2))

	def test_wrong_dimension(self):
		a = [[2,2], [3,3]]
		with self.assertRaises(ListShapeException) as exceptionReturned:
			check_list_shape(a, (2, 2, 2))
		self.assertEqual(exceptionReturned.exception.expected_shape, (2,2,2))
		self.assertEqual(exceptionReturned.exception.actual_shape, (2,2))
	
	def test_wrong_dimension(self):
		a = [[2,2], [3,3]]
		with self.assertRaises(ListShapeException) as exceptionReturned:
			check_list_shape(a, (2, 2, 2))
		self.assertEqual(exceptionReturned.exception.expected_shape, (2,2,2))
		self.assertEqual(exceptionReturned.exception.actual_shape, (2,2))