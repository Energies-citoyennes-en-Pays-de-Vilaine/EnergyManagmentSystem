import numpy as np

class ListShapeException(Exception):
	def __init__(self, expected_shape, actual_shape):
		self.expected_shape = expected_shape
		self.actual_shape   = actual_shape
		self.message        = f"expecting shape {self.expected_shape} but got {self.actual_shape}"
		super().__init__(self.message)

def check_numpy_array_shape(list_to_check : np.ndarray, expected_shape):
	if (len(list_to_check.shape) != len(expected_shape)):
		raise ListShapeException(expected_shape, list_to_check.shape)
	for i in range(len(expected_shape)):
		if (list_to_check.shape[i] != expected_shape[i]):
			raise ListShapeException(expected_shape, list_to_check.shape)

def check_list_shape(list_to_check, expected_shape):
	try:
		check_numpy_array_shape(np.array(list_to_check), expected_shape)
	except ListShapeException as exp:
		raise exp

def check_list_size(list_to_check, expected_size):
	if (len(list_to_check) != expected_size):
		raise ListShapeException(expected_size, len(list_to_check))