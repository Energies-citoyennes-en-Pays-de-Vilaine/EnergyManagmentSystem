import numpy as np
from solution.Calculation_Params import CalculationParams
from solution.Consumer_interface import Consumer_interface
from typing import *
#TODO think about how to use it as a cooler
#power -> Tinit -> Text
#TODO add some strong testing that text and Twish has values for all sim_size
class HeaterConsumer(Consumer_interface):
    """
        temperatures are in K
    """
    T_init        : float
    initial_state : bool
    T_ext         : np.ndarray #note T_ext[0] has to be the current temperature
    T_wish_low    : np.ndarray
    T_wish_high   : np.ndarray
    R_th          : float
    C_th          : float
    P_rad         : float
    def __init__(self, id, T_init: float, initial_state: bool, T_ext: np.ndarray, T_wish_low: np.ndarray, T_wish_high: np.ndarray, R_th: float, C_th: float, P_rad: float) -> None:
        self.T_init        = T_init 
        self.initial_state = initial_state 
        self.T_ext         = T_ext   
        self.T_wish_low    = T_wish_low
        self.T_wish_high   = T_wish_high
        self.R_th          = R_th    
        self.C_th          = C_th    
        self.P_rad         = P_rad
        self.has_base_consumption = False
        self.id = id   
    def _get_f_contrib(self, calculationParams : CalculationParams) -> List[float]:
        return [0.0 for i in range(self._get_minimizing_variables_count(calculationParams))]
    def _get_integrality(self, calculationParams : CalculationParams) -> List[int]:
        return [1 for i in range(calculationParams.get_simulation_size())] + [0] + [0 for i in range(calculationParams.get_simulation_size())]
    
    def _get_minimizing_constraints(self, calculationParams : CalculationParams) -> List[np.ndarray]:
        raise "not implemented yet"
    def _get_functionnal_constraints(self, calculationParams : CalculationParams) -> np.ndarray:
        raise "not implemented yet"
    def _get_functionnal_constraints_boundaries(self, calculationParams : CalculationParams) -> List[List[float]]:
        #start with Power constraints
        #form : - Prad(i) + a2 Tin(i) + a1 Tin(i + 1)  == a2 Text(i) + a1 Text(i + 1)
        a1 = self.C_th / calculationParams.time_delta
        a2 = 1.0 / self.R_th - a1
        sim_size = calculationParams.get_simulation_size()
        to_return_low  : List[float] = []
        to_return_high : List[float] = []
        #power constraint:
        #only one heater
        for i in range(sim_size):
            to_return_low.append(0)
            to_return_high.append(1)
        #physics is ok
        for i in range(1, sim_size + 1):
            power_ok = a2 * self.T_ext[i] + a1 * self.T_ext[i + 1]
            to_return_low.append(power_ok)
            to_return_high.append(power_ok)
        #temperature target
        initial_delta_T = self.T_init - self.T_ext[0]
        if self.initial_state == True:
            T_init = self.T_ext[1] + (calculationParams.time_delta / self.C_th) * (self.P_rad - initial_delta_T / self.R_th) + initial_delta_T
        else:
            T_init = self.T_ext[1] + (calculationParams.time_delta / self.C_th) * (0 - initial_delta_T / self.R_th) + initial_delta_T
        to_return_low .append(T_init)
        to_return_high.append(T_init)
        current_max_heat = T_init
        for i in range(1, sim_size + 1):
            current_delta_T = current_max_heat - self.T_ext[i]
            current_max_heat = self.T_ext[i + 1] + (calculationParams.time_delta / self.C_th) * (self.P_rad - current_delta_T / self.R_th) + current_delta_T
            current_target_temperature = min(current_max_heat, self.T_wish_low[i - 1])
            to_return_low.append(current_target_temperature)
            to_return_high.append(self.T_wish_high[i - 1])
        return [to_return_low, to_return_high]

    def _get_minimizing_variables_count(self, calculationParams : CalculationParams) -> int:
        return 2 * calculationParams.get_simulation_size() + 1
    def _get_constraints_size(self, calculationParams : CalculationParams) -> int:
        return 3 * calculationParams.get_simulation_size() + 1
    def _fill_minimizing_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpars: List[int], ypars: List[int]):
        x = xpars[0]
        y = ypars[0]
        for i in range(calculationParams.get_simulation_size()):
            tofill[y + i, x + i] = - self.P_rad
    def _fill_functionnal_constraints(self, calculationParams: CalculationParams, tofill: np.ndarray, xpar: int, ypar: int):
        #start with Power constraints
        #power is 0 or one
        sim_size = calculationParams.get_simulation_size()
        x = xpar
        y = ypar
        for i in range(sim_size):
            tofill[y + i, x + i] = 1
        y = y + sim_size
        #form : - Prad(i) + a2 Tin(i) + a1 Tin(i + 1)  == a2 Text(i) + a1 Text(i + 1)
        a1 = self.C_th / calculationParams.time_delta
        a2 = 1.0 / self.R_th - a1
        for i in range(sim_size):
            tofill[y + i, x + i] = - self.P_rad
            tofill[y + i, x + i + sim_size] = a2
            tofill[y + i, x + i + sim_size + 1] = a1
            #Temperature constraint
            tofill[y + i + 1 + sim_size, x + i + sim_size + 1] = 1
        tofill[y + sim_size, x + sim_size] = 1
    def _get_consumption_curve(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
        return self.P_rad * np.array(variables[:calculationParams.get_simulation_size()])
    def _get_decisions(self, calculationParams : CalculationParams, variables : List[float]) -> np.ndarray:
        decisions = [np.round(i) for i in variables[:calculationParams.get_simulation_size()]]
        return np.array(decisions, dtype=np.int64)
    def get_temperature(self, calculationParams : CalculationParams, variables : List[float]):
        return np.array(variables[calculationParams.get_simulation_size() + 1:])
   