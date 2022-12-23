import math
from tracemalloc import start
import numpy as np
from typing import *
from solution.Consumer_interface import Consumer_interface
from solution.Calculation_Params import CalculationParams
from solution.Utils.utils import maxi, mini
class MachineConsumer(Consumer_interface):
    def __init__(self, id, profile, start_time, end_time, machine_count = 1):
        self.id = id
        self.profile = profile
        self.start_time = start_time
        self.end_time = end_time #machine MUST have finished BEFORE end_time
        self.machine_count = machine_count
        self.has_base_consumption = False
        self.is_reocurring = False
    def _get_f_contrib(self, calculationParams : CalculationParams) -> List[float]:
        return [0.0] * self.get_minimizing_variables_count(calculationParams)
    def _get_integrality(self, calculationParams : CalculationParams) -> List[int]:
        return [1] * self.get_minimizing_variables_count(calculationParams)
    def _get_minimizing_constraints(self, calculationParams : CalculationParams) -> List[np.ndarray]:
        #better mecanism may be thought about in the future
        #DO NOT USE UNTIL THIS MESSAGE DISAPEAR
        sim_size = calculationParams.get_simulation_size()
        first_constraint = np.zeros((sim_size, self._get_minimizing_variables_count(calculationParams)))
        start_time = maxi(self.start_time, calculationParams.begin)
        start_step = int(round((start_time - calculationParams.begin) / calculationParams.step_size))
        for i in range(self._get_minimizing_variables_count):
            for j in range(len(self.profile)):
                first_constraint[start_step + i + j][i] = self.profile[j]
        return [first_constraint]# has to be modified for tests
    def _get_functionnal_constraints(self, calculationParams : CalculationParams) -> np.ndarray:
        return np.ones((1, self._get_constraints_size(calculationParams)))
    def _get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[List[List[float]]]:
        return [[self.machine_count], [self.machine_count]]
    def _get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
        if (self.start_time + len(self.profile) > calculationParams.end):
            return 0
        if (self.end_time <= calculationParams.begin):
            #should throw an exception here that will have to be caught to check on behaviours
            #because this only occurs if a machine that should have started tries to start
            return 0
        start_time = maxi(self.start_time, calculationParams.begin)
        end_time = mini(self.end_time, calculationParams.end + calculationParams.step_size)
        steps_count = (end_time - start_time) / calculationParams.step_size
        steps_count -= len(self.profile)
        steps_count = round(steps_count)
        return steps_count + 1

    def _get_constraints_size(self, calculationParams : CalculationParams) -> int:
        return 1 # only a sum constraint

    def _fill_minimizing_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpars: List[int], ypars: List[int]):
        sim_size = calculationParams.get_simulation_size()
        start_time = maxi(self.start_time, calculationParams.begin)
        start_step = int(round((start_time - calculationParams.begin) / calculationParams.step_size))
        xpar = xpars[0]
        ypar = ypars[0]
        for i in range(self._get_minimizing_variables_count(calculationParams)):
            for j in range(len(self.profile)):
                tofill[start_step + ypar + i + j, xpar + i] = -self.profile[j]

    def _fill_functionnal_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpar: int, ypar: int):
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