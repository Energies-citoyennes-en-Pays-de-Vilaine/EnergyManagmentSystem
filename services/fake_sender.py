from learning.database.ELFE_db_types import ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_EquipementPilote
from learning.database.ELFE_db_creator import ELFE_database_names
from learning.database.EMS_db_creator import execute_queries, fetch
from credentials.db_credentials import db_credentials
from datetime import datetime

DELTA_TIME_SIMULATION = 15*60
STEP_COUNT = 96
MODE_PILOTE = 30
if __name__ == "__main__":
	timestamp = round(datetime.now().timestamp() / DELTA_TIME_SIMULATION) * DELTA_TIME_SIMULATION
	scheduled_machines = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result WHERE first_valid_timestamp=%s AND decisions_0=1;", [timestamp]))
	scheduled_machines = [int(scheduled_machine[0]) for scheduled_machine in scheduled_machines]
	from data.temp.generated_study_case import sc
	queries = []
	for scheduled_machine in scheduled_machines:
		machine_index = 0
		for machine in sc.machines:
			if(int(sc.machines[machine][0].Id) == scheduled_machine):
				machine_index = machine
				break
		sc.machines[machine_index][0].equipement_pilote_ou_mesure_mode = 0
		queries.append(sc.machines[machine_index][0].get_update_in_table_str(ELFE_database_names["ELFE_EquipementPilote"]))
		print(timestamp, "sending info to machine", scheduled_machine )
	for machine in sc.machines:
			if(sc.machines[machine][0].equipement_pilote_ou_mesure_mode == MODE_PILOTE and sc.machines[machine][1].timestamp_de_fin_souhaite < timestamp):
				sc.machines[machine][0].equipement_pilote_ou_mesure_mode = 0
				queries.append(sc.machines[machine][0].get_update_in_table_str(ELFE_database_names["ELFE_EquipementPilote"]))
				print(timestamp, "machine", sc.machines[machine][0].Id, "was never scheduled" )
	execute_queries(db_credentials["ELFE"], queries)
	sc.save_to_loadable_py_file("sc", "data/temp/generated_study_case.py")