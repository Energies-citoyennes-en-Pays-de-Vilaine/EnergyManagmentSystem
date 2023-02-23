from database.ELFE_db_types import ELFE_BallonECS, ELFE_BallonECSHeuresCreuses, ELFE_ChauffageAsservi, ELFE_ChauffageAsserviModeleThermique, ELFE_ChauffageNonAsservi, ELFE_EquipementPilote, ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_VehiculeElectriqueGenerique
from database.ELFE_db_creator import ELFE_database_names
from database.EMS_db_types import EMSCycle, EMSCycleData, EMSDeviceTemperatureData, EMSMachineData, EMSPowerCurveData, InitialWheatherForecast
from database.query import execute_queries, fetch
from credentials.db_credentials import db_credentials
from typing import List, Union
from solution.ConsumerTypes.HeaterConsumer import HeaterConsumer
from solution.ConsumerTypes.SumConsumer import SumConsumer
from solution.ConsumerTypes.MachineConsumer import MachineConsumer
MODE_PILOTE = 30
DELTA_SIMULATION = 15*60 #TODO this will have to be reloacted

def get_machines(timestamp) -> List[MachineConsumer]:
	MACHINE_ID_INDEX  = 0
	CYCLE_NAME_INDEX  = 1
	MESURE_ELEC_INDEX = 2
	MAX_END_TIMESTAMP_INDEX = 3
	MAX_END_DELTA_INDEX = 4
	to_return : List[MachineConsumer]= []
	machines_not_to_schedule = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result WHERE first_valid_timestamp=%s AND decisions_0=1", [timestamp]))
	machines_not_to_schedule = [int(machine_not_to_schedule[0]) for machine_not_to_schedule in machines_not_to_schedule]
	machines_to_schedule = fetch(db_credentials["ELFE"], f" SELECT machine.equipement_pilote_ou_mesure_id, cycle.nom, machine.mesures_puissance_elec_id, machine.timestamp_de_fin_souhaite, machine.delai_attente_maximale_apres_fin   "
													   + f" FROM {ELFE_database_names['ELFE_MachineGenerique']} AS machine" 
	                                                   + f" INNER JOIN {ELFE_database_names['ELFE_MachineGeneriqueCycle']} AS cycle ON cycle.equipement_pilote_machine_generique_id = machine.id " 
													   + f" INNER JOIN {ELFE_database_names['ELFE_EquipementPilote']} AS equipement ON machine.equipement_pilote_ou_mesure_id = equipement.id "
													   + f" WHERE equipement.equipement_pilote_ou_mesure_mode = {MODE_PILOTE};")
	for machine in machines_to_schedule:
		if int(machine[MACHINE_ID_INDEX]) in machines_not_to_schedule:
			print(f"not to schedule {machine[MACHINE_ID_INDEX]}")
			continue
		#if machine[CYCLE_NAME_INDEX] == "aucun"
		if (True):
			EMS_database_machine = fetch(db_credentials["EMS"], (f" SELECT cd.csv FROM machine AS m"
			                                                   + f" INNER JOIN cycle AS c ON c.id_machine = m.id_machine"
															   + f" INNER JOIN cycledata AS cd ON cd.id_cycle_data = c.id_cycle_data "
															   + f" WHERE m.id_machine_elfe=%s AND c.name=%s",
															   [machine[MESURE_ELEC_INDEX], f"default_cycle_for_machine({machine[MESURE_ELEC_INDEX]})"]
				)
			)[0]
			cycle_data = []
			with open(f"data/in_use/{EMS_database_machine[0]}") as inp:
				for line in inp:
					for data in line.strip().replace(" ", "").split(","):
						cycle_data.append(float(data))
		cycle_duration = DELTA_SIMULATION * len(cycle_data)
		end_time = max( DELTA_SIMULATION + cycle_duration + timestamp, machine[MAX_END_TIMESTAMP_INDEX])
		start_time = machine[MAX_END_TIMESTAMP_INDEX]- machine[MAX_END_DELTA_INDEX] - cycle_duration
		to_return.append(MachineConsumer(machine[MACHINE_ID_INDEX], cycle_data, start_time, end_time))
	return to_return
if __name__ == "__main__":
	from datetime import datetime
	print(get_machines(int(datetime.now().timestamp())))

