from numpy import floor
from typing import *
class CalculationParams():
	begin                         : int
	end                           : int
	step_size                     : int
	base_minimization_constraints : List[List[float]]
	def __init__(self, begin, end, step_size, base_minimization_constraints : List[List[float]]) -> None:
		self.base_minimization_constraints = base_minimization_constraints
		self.begin = begin
		self.end = end #end is always included in the simulation; this may be important for later
		self.step_size = step_size
	def get_simulation_size(self) -> int:
		result = (self.end - self.begin) / self.step_size
		return int(result) + 1
	def get_time_array(self):
		return [i * self.step_size + self.begin for i in range(self.get_simulation_size())]