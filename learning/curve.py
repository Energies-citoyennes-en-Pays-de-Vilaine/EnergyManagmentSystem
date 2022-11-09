import numpy as np
from typing import List
import matplotlib.pyplot as plt
class Curve():
	delta_T : int # delta time int seconds
	points : np.ndarray
	origin : List[np.ndarray]
	def __init__(self, delta_T: int, points:np.ndarray, origin: List[np.ndarray]) -> None:
		self.delta_T = delta_T
		self.points = np.array(points, dtype=np.float64)
		self.origin = origin

def get_full_curve(times: List[int], data: List[int], period : int, base_index : int):
	#we assume the list is ordered by time ascending
	current_list = []
	current_time_list = []
	current_curve = []
	base_time = times[base_index]
	for i in range(base_index, len(times)):
		if int((times[i] - base_time) / period) > len(current_curve):
			toAdd = 0.0
			toAddDelta = 0.0
			for j in range(len(current_list) - 1):
				toAdd += current_list[j] * (current_time_list[j + 1] - current_time_list[j])
				toAddDelta += (current_time_list[j + 1] - current_time_list[j])
			if (toAddDelta != 0):
				toAdd /= toAddDelta
				current_curve.append(toAdd)
			current_list = []
			current_time_list = []
		current_list.append(data[i])
		current_time_list.append(times[i])
	if (len(current_list) != 0):
		toAdd = 0.0
		toAddDelta = 0.0
		for j in range(len(current_list) - 1):
			toAdd += current_list[j] * (current_time_list[j + 1] - current_time_list[j])
			toAddDelta += current_time_list[j + 1] - current_time_list[j]
		if toAddDelta != 0:
			toAdd /= toAddDelta
			current_curve.append(toAdd)
	return np.array(current_curve, dtype = np.float64)



def make_curve(times : List[int], data: List[float], threshold_begin : float, threshold_end : float, period: int, required_low_period_count : int = 0) -> List[Curve]:
	i = 0
	toReturn = []
	start_time = []
	while (i < len(times)):
		if data[i] > threshold_begin:
			curve = get_full_curve(times, data, period, i)
			start_curve_time = times[i]
			start_time.append(times[i])
			j = 0
			test = False
			count = 0
			while (j < len(curve) and not test):
				if curve[j] >= threshold_end:
					count = 0
				else:
					count = count + 1
				if count > required_low_period_count:
					test = True
				j = j + 1
			if test:
				origin = [[], []]
				while (i < len(times) and start_curve_time + j * period > times[i]):
					origin[0].append(times[i])
					origin[1].append(data[i])
					i = i + 1
				toReturn.append(Curve(period, curve[0:j], origin))
			else:
				return toReturn
					
		i = i + 1

	return toReturn