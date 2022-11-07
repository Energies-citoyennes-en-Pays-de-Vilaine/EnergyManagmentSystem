from solution.Exceptions.FunctionNotExistingException import *
from unittest import TestCase

class test_class():
		def present_method(self):
			return 42
		present_class_field = 5
		def __init__(self) :
			self.present_field = 42

class FunctionNotExistingExceptionTestCase(TestCase):
	
	def test_present_method(self):
		test_object = test_class()
		checkFunctionExist(test_object, "present_method")
		self.assertEqual(test_object.present_method(), 42)
	
	def test_not_present_class_field(self):
		test_object = test_class()
		method_name = "present_class_field"
		with self.assertRaises(FunctionNotExistingException) as exceptionReturned:
			checkFunctionExist(test_object, method_name)
		self.assertEqual(exceptionReturned.exception.function_name, method_name)
		self.assertEqual(exceptionReturned.exception.object, test_object)
		
	def test_not_present_field(self):
		test_object = test_class()
		method_name = "present_field"
		with self.assertRaises(FunctionNotExistingException) as exceptionReturned:
			checkFunctionExist(test_object, method_name)
		self.assertEqual(exceptionReturned.exception.function_name, method_name)
		self.assertEqual(exceptionReturned.exception.object, test_object)
	
	def test_not_absent_field(self):
		test_object = test_class()
		method_name = "absent_field"
		with self.assertRaises(FunctionNotExistingException) as exceptionReturned:
			checkFunctionExist(test_object, method_name)
		self.assertEqual(exceptionReturned.exception.function_name, method_name)
		self.assertEqual(exceptionReturned.exception.object, test_object)
		