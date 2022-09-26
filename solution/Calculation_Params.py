from numpy import floor
class CalculationParams():
	begin:int
	end:int
	def __init__(self, begin, end, step_size) -> None:
		self.begin = begin
		self.end = end #end is always included in the simulation; this may be important for later
		self.step_size = step_size
	def get_simulation_size(self) -> int:
		result = (self.end - self.begin) / self.step_size
		return int(result) + 1