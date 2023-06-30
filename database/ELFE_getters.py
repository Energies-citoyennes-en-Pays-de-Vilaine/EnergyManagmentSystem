from typing import List, Dict, Union
from dataclasses import dataclass
from database.query import fetch
from database.ELFE_db_types import ELFE_database_names
from psycopg2 import sql
from database.ELFE_db_types import ELFE_ChauffageNonAsservi
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
	print("[debug info machine]", result_typed)
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

def get_ECS_to_schedule(credentials, timestamp, ECS_not_to_schedule: Union[List[int], None] = None) -> List[ECSToScheduleType]:
	query = (sql.SQL(" SELECT epm.id, ecs.mesures_puissance_elec_id ,ecs.volume_ballon, ecs.puissance_chauffe, hc.debut, hc.fin, epm.equipement_pilote_ou_mesure_type_id"
			+ " FROM {0} AS epm" 
	    	+ " INNER JOIN {1} AS ecs ON epm.id=ecs.equipement_pilote_ou_mesure_id" 
			+ " INNER JOIN {2} AS hc ON ecs.id = hc.equipement_pilote_ballon_ecs_id"
			+ " WHERE hc.actif=true and epm.equipement_pilote_ou_mesure_mode_id=%s AND epm.timestamp_derniere_mise_en_marche + 12 * 3600 <= %s").format(
				sql.Identifier(ELFE_database_names['ELFE_EquipementPilote']),
				sql.Identifier(ELFE_database_names['ELFE_BallonECS']),
				sql.Identifier(ELFE_database_names['ELFE_BallonECSHeuresCreuses'])
			), 
			[MODE_PILOTE, timestamp])
	result = fetch(credentials, query)
	result_typed : List[ECSToScheduleType] = [ECSToScheduleType(r[0], r[1], r[2], r[3], r[4], r[5], r[6]) for r in result]
	
	#gets only the biggest period where it can be scheduled
	biggest_period_ecs : Dict[int, ECSToScheduleType] = {}
	for ecs in result_typed:
		if ECS_not_to_schedule != None and ecs.Id in ECS_not_to_schedule:
			continue
		if ecs.Id not in biggest_period_ecs:
			biggest_period_ecs[ecs.Id] = ecs
		elif (ecs.end - ecs.start > biggest_period_ecs[ecs.Id].end - biggest_period_ecs[ecs.Id].start):
			biggest_period_ecs[ecs.Id] = ecs
	print("[debug info ECS]", biggest_period_ecs)
	return biggest_period_ecs

@dataclass
class ElectricVehicleToScheduleType:
	Id : int
	current_charge_left_percent : int
	target_charge_percent       : int
	end_timestamp               : int
	power_W                     : int
	capa_WH                     : int
	equipement_type             : int

def get_electric_vehicle_to_schedule(credentials, vehicle_not_to_schedule : Union[List[int], None] = None) -> List[ElectricVehicleToScheduleType]:
	query = (
		sql.SQL("SELECT m.id, ve.pourcentage_charge_restant, ve.pourcentage_charge_finale_minimale_souhaitee, \
	    ve.timestamp_dispo_souhaitee, ve.puissance_de_charge, ve.capacite_de_batterie, m.equipement_pilote_ou_mesure_type_id\
		FROM {0} AS m\
		INNER JOIN {1} AS ve ON ve.equipement_pilote_ou_mesure_id = m.id\
		WHERE m.equipement_pilote_ou_mesure_mode_id=%s").format(
			sql.Identifier(ELFE_database_names['ELFE_EquipementPilote']),
			sql.Identifier(ELFE_database_names['ELFE_VehiculeElectriqueGenerique'])
		),
		[MODE_PILOTE]
	)
	result = fetch(credentials, query)
	if result == None:
		print("error, returning empty list for electric vehicle to prevent crash")
		return []
	result_typed : List[ElectricVehicleToScheduleType] = []
	for r in result:
		if vehicle_not_to_schedule == None or r[0] not in vehicle_not_to_schedule:
			result_typed.append(ElectricVehicleToScheduleType(r[0], r[1], r[2], r[3], r[4], r[5], r[6]))
	print("[debug info Electric vehicle]", result_typed)
	return result_typed

def get_elfe_not_piloted_heater(credentials) -> List[ELFE_ChauffageNonAsservi]:
	#not piloted means that we have no temperature sensor here
	query = (sql.SQL("SELECT heater.*, epm.equipement_pilote_ou_mesure_type \
		FROM {0} AS heater\
		INNER JOIN {1} AS epm ON epm.id = heater.equipement_pilote_ou_mesure_id\
		WHERE epm.equipement_pilote_ou_mesure_mode_id = %s").format(
			sql.Identifier(ELFE_database_names['ELFE_ChauffageNonAsservi']),
			sql.Identifier(ELFE_database_names['ELFE_EquipementPilote'])
		),
		[MODE_PILOTE])
	result = fetch(credentials, query)
	to_return : List[ELFE_ChauffageNonAsservi] = []
	if (result == None):
		print("an error occured in ELFE_Chauffage_non_asservi, sending back empty array not to block")
		return []
	for r in result:
		new_elem = ELFE_ChauffageNonAsservi.create_from_select_output(r[:-1])
		new_elem.equipement_type = r[-1]
		to_return.append(new_elem)
	print("[debug info chauffage non asservi]", to_return)
	return to_return
