from database.ELFE_db_types import ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_EquipementPilote
from database.ELFE_db_creator import ELFE_database_names
from database.query import execute_queries, fetch
from credentials.db_credentials import db_credentials
from datetime import datetime
from random import randrange, randint
from datetime import datetime
DELTA_TIME_SIMULATION = 15*60
STEP_COUNT = 96
MODE_PILOTE = 30

TO_SCHEDULE_POTENTIAL = 4
TO_SCHEDULE_TIME_FROM_NOW = [3*15*60, 6*3600]
TO_SCHEDULE_DELTA_TIME = [1*15*60, 6*3600]
if __name__ == "__main__":
	from data.temp.generated_study_case import sc
	timestamp = round(int(datetime.now().timestamp()) / DELTA_TIME_SIMULATION) * DELTA_TIME_SIMULATION
	not_scheduled = []
	for machine in sc.machines:
		if sc.machines[machine][0].equipement_pilote_ou_mesure_mode != MODE_PILOTE:
			not_scheduled.append(machine)
	queries = []
	for i in range(randint(1, TO_SCHEDULE_POTENTIAL)):
		machine = randrange(0, len(not_scheduled))
		machine_last_end = timestamp + randint(TO_SCHEDULE_TIME_FROM_NOW[0], TO_SCHEDULE_TIME_FROM_NOW[1])
		machine_delta    = randint(TO_SCHEDULE_DELTA_TIME[0], TO_SCHEDULE_DELTA_TIME[1]) 
		machine_index = not_scheduled[machine]
		sc.machines[machine_index][0].equipement_pilote_ou_mesure_mode = MODE_PILOTE
		sc.machines[machine_index][1].delai_attente_maximale_apres_fin = machine_delta
		sc.machines[machine_index][1].timestamp_de_fin_souhaite = machine_last_end
		print(f"scheduling machine {machine_index} for timestamp {machine_last_end}")
		queries.append(sc.machines[machine_index][0].get_update_in_table_str(ELFE_database_names["ELFE_EquipementPilote"]))
		queries.append(sc.machines[machine_index][1].get_update_in_table_str(ELFE_database_names["ELFE_MachineGenerique"]))
		not_scheduled.remove(machine_index)
	execute_queries(db_credentials["ELFE"], queries)
	sc.save_to_loadable_py_file("sc", "data/temp/generated_study_case.py")