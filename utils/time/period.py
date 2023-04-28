from dataclasses import dataclass
from typing import Union, List
from math import floor, ceil

@dataclass(init=True, repr=True)
class Period():
	start : int
	end : int
	def __sub__(self, value : Union[int, float]):
		if (type(value) in [int, float]):
			value = int(value)
			start = self.start - value
			end = self.end - value
			return Period(start, end )
		else:
			raise TypeError(f"can't substract {type(value)} to Period")
		
	def snap_to(self, time_division : int, offset : int = 0):
		self.start = floor((self.start - offset)/ time_division) * time_division + offset
		self.end   = ceil((self.end - offset) / time_division) * time_division + offset

	def cut(self, start : int, end : int):
		self.start = max([self.start, start])
		self.end = min([self.end, end])

def get_merged_periods(periods : List[Period]) -> List[Period]:
	periods_to_return : List[Period] = []
	has_changed : bool = True
	while (has_changed):
		has_changed = False
		periods_to_include = [True for p in periods]
		for (i, period_1) in enumerate(periods):
			if periods_to_include[i] == False:
				continue
			for j in range(i + 1, len(periods)):
				if periods_to_include[j] == False:
					continue
				period_2 = periods[j]	
				if period_2.start >= period_1.start and period_2.start < period_1.end:
					start = period_1.start
					end = max(period_1.end, period_2.end)
					periods_to_return.append(Period(start, end))
					periods_to_include[i] = False
					periods_to_include[j] = False
					has_changed = True
					break
			if periods_to_include[i] == True:
				periods_to_return.append(period_1)
		periods = periods_to_return
	return periods
