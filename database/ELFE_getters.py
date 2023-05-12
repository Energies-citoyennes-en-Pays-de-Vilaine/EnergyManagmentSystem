from typing import List
from dataclasses import dataclass
from database.query import fetch
from database.ELFE_db_types import ELFE_database_names

MODE_PILOTE = 30

@dataclass
class MachineToScheduleType():
	Id             : int
	cycle_name     : str
	zabbix_id      : int
	end_timestamp  : int
	max_delay      : int
	equipment_type : int
def get_machines_to_schedule(credentials) -> List[MachineToScheduleType]:
	fields = [
						"machine.equipement_pilote_ou_mesure_id", 
						"cycle.nom", 
						"machine.mesures_puissance_elec_id",
						"machine.timestamp_de_fin_souhaite",
						"machine.delai_attente_maximale_apres_fin",
						"equipement.equipement_pilote_ou_mesure_type_id"
						]
	fields_as_s = ','.join(['%s' for field in fields])
	query = (f" SELECT {fields_as_s}"
			+ f" FROM %s AS machine" 
	    	+ f" INNER JOIN %s AS cycle ON cycle.id = machine.cycle_equipement_pilote_machine_generique_id " 
			+ f" INNER JOIN %s AS equipement ON machine.equipement_pilote_ou_mesure_id = equipement.id "
			+ f" WHERE equipement.equipement_pilote_ou_mesure_mode_id = %s;", 
			fields + 
			[ELFE_database_names['ELFE_MachineGenerique'],
    		ELFE_database_names['ELFE_MachineGeneriqueCycle'],
			ELFE_database_names['ELFE_EquipementPilote'],
			MODE_PILOTE])
	result = fetch(credentials, query)
	result_typed : List[MachineToScheduleType] = [MachineToScheduleType(r[0], r[1], r[2], r[3], r[4], r[5]) for r in result]
	return result_typed
