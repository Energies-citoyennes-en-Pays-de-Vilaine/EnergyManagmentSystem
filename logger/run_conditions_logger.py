from solution.Calculation_Params import CalculationParams
from solution.Consumer_interface import Consumer_interface
from typing import List
def	log_run_conditions_to_file(path, timestamp : int, round_start_timestamp : int, sim_params : CalculationParams, consumers : List[Consumer_interface]):
	with open(path, "w") as out:
		print(f"timestamp = {timestamp}", file=out)
		print(f"round_start_timestamp = {round_start_timestamp}", file=out)
		print(f"sim_params = {sim_params}", file=out)
		print(f"consumers = [", file=out)
		for consumer in consumers:
			print(f"\t{consumer},", file=out)
		print(f"]", file=out)