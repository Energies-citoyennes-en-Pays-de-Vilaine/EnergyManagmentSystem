from credentials.db_credentials import db_credentials
from dataclasses import dataclass
import typing
from typing import Union
from database.query import execute_queries, fetch
from database.EMS_db_types import EMSMachineData, EMSCycle, EMSCycleData ,InitialWheatherForecast, HistoricalInitialWheatherForecast, EMSDeviceTemperatureData, EMSPowerCurveData, EMSResult
def create_tables(credentials):
	tables_queries = [
		EMSCycleData.get_create_table_str("cycledata"),
		["INSERT INTO cycledata(id_cycle_data, start_time, csv, duree, moved_timestamp) Values(%s,%s,%s,%s,%s) ON CONFLICT DO NOTHING;", (0,0,"default.csv", 4, 0)],
		EMSCycle.get_create_table_str("cycle"),
		EMSMachineData.get_create_table_str("machine"),
		InitialWheatherForecast.get_create_table_str("initialweather"),
		HistoricalInitialWheatherForecast.get_create_table_str("historyinitialweather"),
		EMSDeviceTemperatureData.get_create_table_str("devicetemperaturedata"),
		EMSPowerCurveData.get_create_table_str("prediction"),
		EMSResult.get_create_table_str("result"),
		EMSResult.get_create_table_str("result_ecs")
	]
	execute_queries(credentials, tables_queries)

			
if __name__ == '__main__':
	create_tables(db_credentials["EMS"])