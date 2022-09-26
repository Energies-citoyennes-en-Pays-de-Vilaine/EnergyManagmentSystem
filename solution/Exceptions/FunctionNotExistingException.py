
class FunctionNotExistingException(Exception):
	def __init__(self, object, function_name):
		self.object = object
		self.function_name = function_name
		self.message = f"object {self.object} doesn't have function {function_name}"
		super().__init__(self.message)

def checkFunctionExist(object, function_name):
	object_methods = [method_name for method_name in dir(object) if callable(getattr(object, method_name))]
	if function_name not in object_methods:
		raise FunctionNotExistingException(object, function_name)