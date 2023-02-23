from elfe_interfaces.ELFE_data_gatherer import get_machines
from database.EMS_db_types import EMSPowerCurveData, EMSResult
from database.query import fetch, execute_queries
from credentials.db_credentials import db_credentials
from solution.Calculation_Params import CalculationParams
from solution.Problem import Problem
from datetime import datetime
DELTA_TIME_SIMULATION = 15*60
STEP_COUNT = 96
if __name__ == "__main__":
	timestamp = round(datetime.now().timestamp() / DELTA_TIME_SIMULATION) * DELTA_TIME_SIMULATION
	round_start_timestamp = timestamp + DELTA_TIME_SIMULATION
	expected_power = fetch(db_credentials["EMS"], ("SELECT * FROM prediction WHERE data_timestamp >= %s ;", [round_start_timestamp]))
	expected_power = sorted(expected_power, key=lambda x : int(x[0]))
	simulation_datas = expected_power[:STEP_COUNT]
	sim_params = CalculationParams(round_start_timestamp, timestamp + STEP_COUNT * DELTA_TIME_SIMULATION, DELTA_TIME_SIMULATION, DELTA_TIME_SIMULATION, [[-int(simulation_datas[i][1]) for i in range(STEP_COUNT)]])
	consumers = get_machines(timestamp)
	problem = Problem(consumers, sim_params)
	problem.prepare()
	problem.solve(10*60)
	decisions = problem.get_decisions()
	results = []
	for decision in decisions:
		result_type = 0 if decision["reocurring"] == False else 1
		result = EMSResult(0, round_start_timestamp, decision["id"], result_type, result_type, decision["decisions"] )
		results.append(result)
	queries = [result.get_append_in_table_str("result") for result in results]
	execute_queries(db_credentials["EMS"], queries)
	if ("EMS_SORTIE" in db_credentials):
		execute_queries(db_credentials["EMS_SORTIE"], queries)

	