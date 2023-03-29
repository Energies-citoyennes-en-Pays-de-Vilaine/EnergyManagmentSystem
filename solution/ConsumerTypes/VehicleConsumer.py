
import numpy as np
from typing import *
from solution.Consumer_interface import Consumer_interface
from solution.Calculation_Params import CalculationParams
from solution.Utils.utils import maxi, mini
from typing import TypedDict
class _CalculatedTimeParameters(TypedDict):
	start_time          : int
	end_time            : int
	min_charge_time     : int
	max_charge_time     : int
	end_time_min_charge : int
	end_time_max_charge : int
class VehicleConsumer(Consumer_interface):
	id : int # Elfe_Equipement_pilote_id
	power_watt : int
	capacity_watt_hour : int
	initial_charge_pourc : int
	end_charge_pourc : int
	def __init__(self, id, power_watt, capacity_watt_hour, initial_charge_pourc, end_charge_pourc, start_time, end_time):
		self.id = id
		self.power_watt = power_watt
		self.capacity_watt_hour = capacity_watt_hour
		self.initial_charge_pourc = initial_charge_pourc
		self.end_charge_pourc = end_charge_pourc
		self.start_time = start_time
		self.end_time = end_time #vehicle must be charged up to end_charge_pourc before the end time
		self.has_base_consumption = False
		self.is_reocurring = False
	def _get_f_contrib(self, calculationParams : CalculationParams) -> List[float]:
		self._make_machine_possible(calculationParams)
		return [0.0] * self.get_minimizing_variables_count(calculationParams)
	def _get_integrality(self, calculationParams : CalculationParams) -> List[int]:
		self._make_machine_possible(calculationParams)
		return [1] * self.get_minimizing_variables_count(calculationParams)
	def _get_minimizing_constraints(self, calculationParams : CalculationParams) -> List[np.ndarray]:
		#better mecanism may be thought about in the future
		#DO NOT USE UNTIL THIS MESSAGE DISAPEAR
		self._make_machine_possible(calculationParams)
		raise NotImplementedError()
	def _get_functionnal_constraints(self, calculationParams : CalculationParams) -> np.ndarray:
		self._make_machine_possible(calculationParams)
		return np.ones((1, self._get_constraints_size(calculationParams)))
	def _get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[List[List[float]]]:
		self._make_machine_possible(calculationParams)
		return [[1], [1]]
	
	def _get_calculated_time_parameters(self, calculationParams: CalculationParams) -> _CalculatedTimeParameters:
		start_time        = maxi(self.start_time, calculationParams.begin)
		end_time          = mini(self.end_time, calculationParams.end)
		min_charge_time   = 3600.0 * self.capacity_watt_hour * (self.end_charge_pourc - self.initial_charge_pourc) / (100.0 * self.power_watt)
		max_charge_time   = 3600.0 * self.capacity_watt_hour * (self.end_charge_pourc - self.initial_charge_pourc) / (100.0 * self.power_watt)
		end_time_min_charge = start_time + min_charge_time
		end_time_max_charge = start_time + max_charge_time
		return {
			"start_time" : start_time,
			"end_time": end_time,
	  		"end_time_min_charge" : end_time_min_charge,
			"end_time_max_charge" : end_time_max_charge,
			"max_charge_time" : max_charge_time,
			"min_charge_time" : min_charge_time
			}
	def _make_machine_possible(self, calculationParams: CalculationParams):
		tp = self._get_calculated_time_parameters(calculationParams)
		start_time = maxi(self.start_time, calculationParams.begin)
		end_time = mini(self.end_time, calculationParams.end + calculationParams.step_size)
		if (start_time + len(self.profile) * calculationParams.time_delta  > end_time ):
			print(f"warning, machine {self.id} impossible because user constraints doesn't allow it to fit, rescheduling end constraint")
			self.end_time = self.start_time + len(self.profile) * calculationParams.time_delta
		if (start_time + len(self.profile) * calculationParams.time_delta > calculationParams.end):
			print(f"warning, machine {self.id} impossible because it doesn't fit before the end of simulation. making it earlier so it fits, will be rescheduled later")
			self.start_time = calculationParams.end - len(self.profile) * calculationParams.time_delta
		if (self.end_time <= calculationParams.begin):
			print(f"warning, machine {self.id} impossible because it's supposed to end before the start of simulation. scheduling it for next step")
			self.start_time = calculationParams.begin
			self.end_time = self.start_time + len(self.profile) * calculationParams.time_delta

	def _get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
		self._make_machine_possible(calculationParams)
		start_time = maxi(self.start_time, calculationParams.begin)
		end_time = mini(self.end_time, calculationParams.end + calculationParams.step_size)
		steps_count = (end_time - start_time) / calculationParams.step_size
		steps_count -= len(self.profile)
		steps_count = round(steps_count)
		if steps_count < 0:
			print(steps_count, start_time, end_time, calculationParams.step_size)
		return steps_count + 1

	def _get_constraints_size(self, calculationParams : CalculationParams) -> int:
		return 1 # only a sum constraint

	def _fill_minimizing_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpars: List[int], ypars: List[int]):
		self._make_machine_possible(calculationParams) 
		sim_size = calculationParams.get_simulation_size()
		start_time = maxi(self.start_time, calculationParams.begin)
		start_step = int(round((start_time - calculationParams.begin) / calculationParams.step_size))
		xpar = xpars[0]
		ypar = ypars[0]
		for i in range(self._get_minimizing_variables_count(calculationParams)):
			for j in range(len(self.profile)):
				tofill[start_step + ypar + i + j, xpar + i] = -self.profile[j]

	def _fill_functionnal_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpar: int, ypar: int):
		self._make_machine_possible(calculationParams)
		for x in range(self._get_minimizing_variables_count(calculationParams)):
			tofill[ypar, xpar + x] = 1

	def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		sim_size = calculationParams.get_simulation_size()
		toReturn = np.zeros((sim_size,), np.float64)
		start_time = maxi(self.start_time, calculationParams.begin)
		start_step = int(round((start_time - calculationParams.begin) / calculationParams.step_size))
		for i in range(len(variables)):
			if (variables[i] != 0):
				for j in range(len(self.profile)):
					toReturn[start_step + i + j] = variables[i] * self.profile[j]
		return toReturn
	def _get_decisions(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
		sim_size = calculationParams.get_simulation_size()
		toReturn = np.zeros((sim_size,), np.int64)
		start_time = maxi(self.start_time, calculationParams.begin)
		start_step = int(round((start_time - calculationParams.begin) / calculationParams.step_size))
		for i in range(len(variables)):
			if (variables[i] != 0):
				toReturn[start_step + i] = np.round(variables[i])
		return toReturn