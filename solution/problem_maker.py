import typing
from solution.Consumer_interface import Consumer_interface
from Calculation_Params import CalculationParams
from solution.Exceptions.SpecifiedListTypeException import SpecifiedListTypeException, check_for_specified_list_type_exception
from typing import *
import numpy as np


class Problem():
    constraint_matrix     : np.ndarray
    constraint_bound_low  : List[float]
    constraint_bound_high : List[float]
    minimizing_matrix     : np.ndarray
    integrality           : List[int]
    def __init__(self, constraint_matrix : np.ndarray, constraint_bound_low : List[float], constraint_bound_high : List[float], minimizing_matrix : np.ndarray, integrality : List[int]) -> None:
        self.constraint_matrix     = constraint_matrix
        self.constraint_bound_low  = constraint_bound_low
        self.constraint_bound_high = constraint_bound_high
        self.minimizing_matrix     = minimizing_matrix
        self.integrality           = integrality

def get_base_variables_matrix(calculationParams : CalculationParams) -> np.ndarray: 
    return np.eye(calculationParams.get_simulation_size())

def get_constraint_matrix(consumers : List[Consumer_interface], calculationParams : CalculationParams):
    check_for_specified_list_type_exception(consumers, Consumer_interface)
    constraint_matrix_width  = calculationParams.get_simulation_size()
    constraint_matrix_height = calculationParams.get_simulation_size()
    for consumer in consumers:
        constraint_matrix_width  += consumer.get_minimizing_variables_count(calculationParams)
        constraint_matrix_height += consumer.get_constraints_size()
    constraint_matrix = np.zeros((constraint_matrix_height, constraint_matrix_width), dtype=np.float64)
    current_x = 0
    current_y = 0
    for i in range(calculationParams.get_simulation_size()):
        constraint_matrix[i, i] = 1
    current_x += calculationParams.get_simulation_size()
    current_y += calculationParams.get_simulation_size()
    constraint_low    = [0.0 for i in range(calculationParams.get_simulation_size())]
    constraint_high   = [np.inf for i in range(calculationParams.get_simulation_size())]
    minimizing_matrix = [1 for i in range(calculationParams.get_simulation_size())]
    integrality       = [0 for i in range(calculationParams.get_simulation_size())]
    for consumer in consumers:
        consumer.fill_minimizing_constraints(calculationParams, constraint_matrix, [current_x], [0])
        consumer.fill_functionnal_constraints(calculationParams, constraint_matrix, current_x, current_y)
        current_x += consumer.get_minimizing_variables_count()
        current_y += consumer.get_constraints_size()
        consumer_constraints_boundaries = consumer.get_functionnal_constraints_boundaries(calculationParams)
        constraint_low    += consumer_constraints_boundaries[0].tolist()
        constraint_high   += consumer_constraints_boundaries[1].tolist()
        minimizing_matrix += consumer.get_f_contrib(calculationParams)
        integrality       += consumer.get_integrality(calculationParams)
    return Problem(constraint_matrix, constraint_low, constraint_high, minimizing_matrix, integrality)