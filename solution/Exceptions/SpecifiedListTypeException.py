import numpy as np
class SpecifiedListTypeException(Exception):
	def __init__(self, object, is_list, expected_list_type, expected_type, index=0):
		self.object = object
		self.is_list = is_list
		self.expected_list_type = expected_list_type
		self.expected_type = expected_type
		self.index = index
		if not is_list:
			self.message = f"Object({self.object} of type {type(self.object)}) is not of expected {expected_list_type}. consider converting it."
			super().__init__(self.message)
			return
		self.message = f"{index}th element of the list is not of the specified type {expected_type}. got {type(self.object[index])}"


def check_for_specified_list_type_exception(list_to_check, expected_type):
	if (type(list_to_check) != type([])):
		raise SpecifiedListTypeException(list_to_check, False, list, expected_type)
	for key, element in enumerate(list_to_check):
		if not isinstance(element, expected_type):
			if (expected_type == float and type(element) == int):
				continue
			raise SpecifiedListTypeException(list_to_check, True, list, expected_type, key)

def check_for_specified_numpy_array_type_exception(list_to_check, expected_type):
	if (type(list_to_check) != np.ndarray):
		raise SpecifiedListTypeException(list_to_check, False, np.ndarray, expected_type)
	if (list_to_check.dtype != expected_type):
		if (expected_type == np.float64 and list_to_check.dtype == np.int64):
				return
		raise SpecifiedListTypeException(list_to_check, True, np.ndarray, expected_type)
