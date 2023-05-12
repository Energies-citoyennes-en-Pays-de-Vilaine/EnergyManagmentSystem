from typing import List
from dataclasses import dataclass
from database.query import fetch
from database.ELFE_db_types import ELFE_database_names
from psycopg2 import sql

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
	query = (sql.SQL(f" SELECT machine.equipement_pilote_ou_mesure_id, cycle.nom, machine.mesures_puissance_elec_id, machine.timestamp_de_fin_souhaite, machine.delai_attente_maximale_apres_fin, equipement.equipement_pilote_ou_mesure_type_id"
			+ " FROM {0} AS machine" 
	    	+ " INNER JOIN {1} AS cycle ON cycle.id = machine.cycle_equipement_pilote_machine_generique_id " 
			+ " INNER JOIN {2} AS equipement ON machine.equipement_pilote_ou_mesure_id = equipement.id "
			+ " WHERE equipement.equipement_pilote_ou_mesure_mode_id = %s;").format(
				sql.Identifier(ELFE_database_names['ELFE_MachineGenerique']),
    			sql.Identifier(ELFE_database_names['ELFE_MachineGeneriqueCycle']),
				sql.Identifier(ELFE_database_names['ELFE_EquipementPilote'])
			),  [MODE_PILOTE])
	result = fetch(credentials, query)
	result_typed : List[MachineToScheduleType] = [MachineToScheduleType(r[0], r[1], r[2], r[3], r[4], r[5]) for r in result]
	return result_typed
@dataclass
class ECSToScheduleType():
	Id             : int
	zabbix_id      : int
	volume_L       : str
	power_W        : int
	start          : int
	end            : int
	equipment_type : int

def get_ECS_to_schedule(credentials) -> List[ECSToScheduleType]:
	query = (sql.SQL(f" SELECT epm.id, ecs.mesures_puissance_elec_id, machine.mesures_puissance_elec_id, machine.timestamp_de_fin_souhaite, machine.delai_attente_maximale_apres_fin, equipement.equipement_pilote_ou_mesure_type_id"
			+ f" FROM {0} AS machine" 
	    	+ f" INNER JOIN {1} AS cycle ON cycle.id = machine.cycle_equipement_pilote_machine_generique_id " 
			+ f" INNER JOIN {2} AS equipement ON machine.equipement_pilote_ou_mesure_id = equipement.id "
			+ f" WHERE equipement.equipement_pilote_ou_mesure_mode_id = %s;").format(
				sql.Identifier(ELFE_database_names['ELFE_MachineGenerique']),
				sql.Identifier(ELFE_database_names['ELFE_MachineGeneriqueCycle']),
				sql.Identifier(ELFE_database_names['ELFE_EquipementPilote']),
			), 
			[MODE_PILOTE])
	result = fetch(credentials, query)
	result_typed : List[ECSToScheduleType] = [ECSToScheduleType(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in result]
	return result_typed
