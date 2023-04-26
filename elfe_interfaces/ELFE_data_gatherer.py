from database.ELFE_db_types import ELFE_BallonECS, ELFE_BallonECSHeuresCreuses, ELFE_ChauffageAsservi, ELFE_ChauffageAsserviModeleThermique, ELFE_ChauffageNonAsservi, ELFE_EquipementPilote, ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_VehiculeElectriqueGenerique
from database.ELFE_db_creator import ELFE_database_names
from database.EMS_db_types import EMSCycle, EMSCycleData, EMSDeviceTemperatureData, EMSMachineData, EMSPowerCurveData, InitialWheatherForecast
from database.query import execute_queries, fetch
from credentials.db_credentials import db_credentials
from typing import List, Union, Tuple
from solution.ConsumerTypes.HeaterConsumer import HeaterConsumer
from solution.ConsumerTypes.SumConsumer import SumConsumer
from solution.ConsumerTypes.MachineConsumer import MachineConsumer
from solution.ConsumerTypes.ECSConsumer import ECSConsumer
from solution.ConsumerTypes.VehicleConsumer import VehicleConsumer
from solution.Calculation_Params import CalculationParams
from math import ceil, floor
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
MODE_PILOTE = 30
DAY_TIME_SECONDS = 24 * 60 * 60
DELTA_SIMULATION = 15*60 #TODO this will have to be reloacted

def get_midnight_date(timestamp : int) -> datetime:
	#TODO this have to be relocated in a specific time module
	date : datetime = datetime.fromtimestamp(timestamp, timezone.utc)
	midnight : datetime = date - timedelta(0, date.second + date.hour * 3600 + date.minute * 60)
	return midnight

def get_midnight_timestamp(timestamp : int) -> datetime:
	date : datetime = datetime.fromtimestamp(timestamp, timezone.utc)
	midnight : datetime = date - timedelta(0, date.second + date.hour * 3600 + date.minute * 60)
	return int(midnight.timestamp())

@dataclass(init=True, repr=True)
class Period():
	start : int
	end : int
	def __sub__(self, value : Union[int, float]):
		if (type(value) in [int, float]):
			value = int(value)
			start = self.start - value
			end = self.end - value
			return Period(start, end )
		else:
			raise TypeError(f"can't substract {type(value)} to Period")
	def snap_to(self, time_division : int, offset : int = 0):
		self.start = floor((self.start - offset)/ time_division) * time_division + offset
		self.end   = ceil((self.end - offset) / time_division) * time_division + offset

def get_merged_periods_and_has_changed(periods : List[Period]) -> Tuple[List[Period], bool]:
	periods_to_return : List[Period] = []
	has_changed : bool = False
	periods_to_include = [True for p in periods]
	for (i, period_1) in enumerate(periods):
		if periods_to_include[i] == False:
			continue
		for j in range(i + 1, len(periods)):
			if periods_to_include[j] == False:
				continue
			period_2 = periods[j]	
			if period_2.start >= period_1.start and period_2.start < period_1.end:
				start = period_1.start
				end = max(period_1.end, period_2.end)
				periods_to_return.append(Period(start, end))
				periods_to_include[i] = False
				periods_to_include[j] = False
				has_changed = True
				break
		if periods_to_include[i] == True:
			periods_to_return.append(period_1)
	return (periods_to_return, has_changed)

def get_machines(timestamp) -> List[MachineConsumer]:
	MACHINE_ID_INDEX  = 0
	CYCLE_NAME_INDEX  = 1
	MESURE_ELEC_INDEX = 2
	MAX_END_TIMESTAMP_INDEX = 3
	MAX_END_DELTA_INDEX = 4
	MACHINE_TYPE_INDEX  = 5
	to_return : List[MachineConsumer]= []
	machines_not_to_schedule = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result WHERE first_valid_timestamp=%s AND decisions_0=1", [timestamp]))
	machines_not_to_schedule = [int(machine_not_to_schedule[0]) for machine_not_to_schedule in machines_not_to_schedule]
	machines_to_schedule = fetch(db_credentials["ELFE"], f" SELECT machine.equipement_pilote_ou_mesure_id, cycle.nom, machine.mesures_puissance_elec_id, machine.timestamp_de_fin_souhaite, machine.delai_attente_maximale_apres_fin, equipement.equipement_pilote_ou_mesure_type_id   "
													   + f" FROM {ELFE_database_names['ELFE_MachineGenerique']} AS machine" 
	                                                   + f" INNER JOIN {ELFE_database_names['ELFE_MachineGeneriqueCycle']} AS cycle ON cycle.id = machine.cycle_equipement_pilote_machine_generique_id " 
													   + f" INNER JOIN {ELFE_database_names['ELFE_EquipementPilote']} AS equipement ON machine.equipement_pilote_ou_mesure_id = equipement.id "
													   + f" WHERE equipement.equipement_pilote_ou_mesure_mode_id = {MODE_PILOTE};")
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
				)
			print(EMS_database_machine)
			try: 
				EMS_database_machine = EMS_database_machine[0]
			except IndexError:
				EMS_database_machine = ["default.csv"]
				print("not found in database", machine[MESURE_ELEC_INDEX])
			cycle_data = []
			with open(f"data/in_use/{EMS_database_machine[0]}") as inp:
				for line in inp:
					for data in line.strip().replace(" ", "").split(","):
						cycle_data.append(float(data))
		cycle_duration = DELTA_SIMULATION * len(cycle_data)
		end_time = max( DELTA_SIMULATION + cycle_duration + timestamp, machine[MAX_END_TIMESTAMP_INDEX])
		start_time = machine[MAX_END_TIMESTAMP_INDEX]- machine[MAX_END_DELTA_INDEX] - cycle_duration
		machine_consumer = MachineConsumer(machine[MACHINE_ID_INDEX], cycle_data, start_time, end_time)
		machine_consumer.consumer_machine_type = machine[MACHINE_TYPE_INDEX]
		to_return.append(machine_consumer)
	return to_return
 
def get_ECS(timestamp) -> List[ECSConsumer]:
	#ECS means "Eau Chaude Sanitaire" which is the hot water tank
	midnight = get_midnight_date(timestamp)
	midnight_timestamp = midnight.timestamp()
	ECS_not_to_schedule = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result_ecs WHERE first_valid_timestamp=%s AND decisions_0=1", [timestamp]))
	ECS_not_to_schedule = [i[0] for i in ECS_not_to_schedule]
	query = (f"SELECT epm.id, ecs.mesures_puissance_elec_id ,ecs.volume_ballon, ecs.puissance_chauffe, hc.actif, hc.debut, hc.fin, epm.equipement_pilote_ou_mesure_type_id\
		FROM {ELFE_database_names['ELFE_EquipementPilote']} AS epm\
		INNER JOIN {ELFE_database_names['ELFE_BallonECS']} AS ecs ON epm.id = ecs.equipement_pilote_ou_mesure_id\
		INNER JOIN {ELFE_database_names['ELFE_BallonECSHeuresCreuses']} AS hc ON ecs.id = hc.equipement_pilote_ballon_ecs_id\
		WHERE hc.actif=true and epm.equipement_pilote_ou_mesure_mode_id={MODE_PILOTE} AND epm.timestamp_derniere_mise_en_marche + 12 * 3600 <= %s", [timestamp])
	query_results = fetch(db_credentials["ELFE"], query)
	ECS_ELFE_in_piloted_mode = {}
	for result in query_results:
		(epmid, zabbixid, volume, power, actif, start, end, epmtype) = result
		if epmid in ECS_not_to_schedule:
			continue
		if epmid not in ECS_ELFE_in_piloted_mode:
			ECS_ELFE_in_piloted_mode[epmid] = {
				"epmid"     : epmid,
				"zabbixid"  : zabbixid,
				"volume"    : volume,
				"power"     : power,
				"actif"     : actif,
				"start"     : start,
				"end"       : end,
				"epmtype"   : epmtype,
				}
		elif (end - start > ECS_ELFE_in_piloted_mode[epmid]["end"] - ECS_ELFE_in_piloted_mode[epmid]["start"]):
			ECS_ELFE_in_piloted_mode[epmid] = {
				"epmid"     : epmid,
				"zabbixid"  : zabbixid,
				"volume"    : volume,
				"power"     : power,
				"actif"     : actif,
				"start"     : start,
				"end"       : end,
				"epmtype"   : epmtype,
				}
	ecs_consumers = []
	for ecs_id in ECS_ELFE_in_piloted_mode:
		ecs = ECS_ELFE_in_piloted_mode[ecs_id]
		last_consumption = fetch(db_credentials["EMS"], ("SELECT last_energy FROM ems_ecs WHERE elfe_zabbix_id=%s", [ecs["zabbixid"]]))
		if (len(last_consumption) == 0):
			last_consumption = 0
			print("no last consumption known")
		else: 
			last_consumption = last_consumption[0][0]
		duration_hour = last_consumption / ecs["power"] + 2#add two hours to be safe, to be put in a config file
		duration_step = duration_hour * 4 #WARNING, quick and dirty, couples the code to 15min simulation step. To be reworked
		duration_step = ceil(duration_step)
		ecs_curve = []
		for i in range(duration_step):
			ecs_curve.append(ecs["power"])
		possible_starts = [
			midnight_timestamp + ecs["start"] - 24 * 3600,
			midnight_timestamp + ecs["start"]
		]
		possible_ends = [
			midnight_timestamp + ecs["end"] - 24 * 3600,
			midnight_timestamp + ecs["end"]
		]
		consumer : ECSConsumer
		print(timestamp - possible_starts[0], timestamp - possible_ends[0])
		if (timestamp > possible_starts[0] and timestamp < possible_ends[0]):
			consumer = ECSConsumer(ecs["epmid"], ecs_curve, possible_starts[0], possible_ends[0], ecs["power"], ecs["volume"])
		else: 
			consumer = ECSConsumer(ecs["epmid"], ecs_curve, possible_starts[1], possible_ends[1], ecs["power"], ecs["volume"])
		consumer.consumer_machine_type = ecs["epmtype"]
		ecs_consumers.append(consumer)
	return (ecs_consumers)

def get_electric_vehicle(timestamp) -> List[VehicleConsumer]:
	vehicle_to_schedule_query = f"SELECT m.id, ve.pourcentage_charge_restant, ve.pourcentage_charge_finale_minimale_souhaitee, ve.timestamp_dispo_souhaitee, ve.puissance_de_charge, ve.capacite_de_batterie, m.equipement_pilote_ou_mesure_type_id\
		FROM {ELFE_database_names['ELFE_EquipementPilote']} AS m\
		INNER JOIN {ELFE_database_names['ELFE_VehiculeElectriqueGenerique']} AS ve ON ve.equipement_pilote_ou_mesure_id = m.id\
		WHERE m.equipement_pilote_ou_mesure_mode_id={MODE_PILOTE}"
	vehicle_to_schedule_query_result = fetch(db_credentials["ELFE"], vehicle_to_schedule_query)
	vehicle_not_to_schedule = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result WHERE first_valid_timestamp=%s AND decisions_0=1", [timestamp]))
	vehicle_not_to_schedule = [int(vehicle_not_to_schedule[0]) for vehicle_not_to_schedule in vehicle_not_to_schedule]
	vehicles : List[VehicleConsumer] = []
	if vehicle_to_schedule_query_result != None:
		for vehicle in vehicle_to_schedule_query_result:
			(Id, current_charge_pourc, target_charge_pourc, end_timestamp, power_watt, capacity_watt_hour, epmtype) = vehicle
			if Id not in vehicle_not_to_schedule:
				vehicle_consumer : VehicleConsumer = VehicleConsumer(Id, power_watt, capacity_watt_hour, current_charge_pourc, target_charge_pourc, timestamp, end_timestamp)
				vehicle_consumer.consumer_machine_type = epmtype
				vehicles.append(vehicle_consumer)
			else:
				print("electic vehicle not to schedule", Id)
	return vehicles

def get_sum_consumer(timestamp : int, calculationParams: CalculationParams) -> List[SumConsumer]:
	"""
	Sum consumers currently are only made of heaters on which we don't have access to the room's heat
	"""
	elfe_heater_query = f"SELECT heater.* \
		FROM {ELFE_database_names['ELFE_ChauffageNonAsservi']} AS heater\
		INNER JOIN {ELFE_database_names['ELFE_EquipementPilote']} AS epm ON epm.id = heater.equipement_pilote_ou_mesure_id\
		WHERE epm.equipement_pilote_ou_mesure_mode_id = {MODE_PILOTE}"	
	elfe_heater_result = fetch(db_credentials["ELFE"], elfe_heater_query)
	elfe_heater : List[ELFE_ChauffageNonAsservi] = [ELFE_ChauffageNonAsservi.create_from_select_output(result) for result in elfe_heater_result]
	starting_periods : List[datetime] = [get_midnight_date(timestamp - DAY_TIME_SECONDS), get_midnight_date(timestamp), get_midnight_date(timestamp + DAY_TIME_SECONDS)]
	for heater in elfe_heater:
		periods : List[Period] = []
		for start in starting_periods:
			if start.weekday() >= 5:
				if heater.prog_weekend_periode_1_confort_actif == True:
					periods.append(Period(int(start.timestamp()) + heater.prog_weekend_periode_1_confort_heure_debut, int(start.timestamp()) + heater.prog_weekend_periode_1_confort_heure_fin))
				if heater.prog_weekend_periode_2_confort_actif == True:
					periods.append(Period(int(start.timestamp()) + heater.prog_weekend_periode_2_confort_heure_debut, int(start.timestamp()) + heater.prog_weekend_periode_2_confort_heure_fin))
			else:
				if heater.prog_semaine_periode_1_confort_actif == True:
					periods.append(Period(int(start.timestamp()) + heater.prog_semaine_periode_1_confort_heure_debut, int(start.timestamp()) + heater.prog_semaine_periode_1_confort_heure_fin))
				if heater.prog_semaine_periode_2_confort_actif == True:
					periods.append(Period(int(start.timestamp()) + heater.prog_semaine_periode_2_confort_heure_debut, int(start.timestamp()) + heater.prog_semaine_periode_2_confort_heure_fin))
		for p in periods:
			p.snap_to(calculationParams.time_delta) #snaps period to the current time delta
		
		periods = sorted(periods, key=lambda x : x.start)
		print(periods)
		print([p - timestamp for p in periods])
		has_changed = True
		while (has_changed == True):
			periods, has_changed = get_merged_periods_and_has_changed(periods)
		periods : List[Period] = list(filter(lambda x : (x - timestamp).start > 0 and (x - timestamp).end > 0, periods))
		periods_from_timestamp = [p - timestamp for p in periods]
		if len(periods) == 0:
			print(f"no periods to schedule for heater {heater.equipement_pilote_ou_mesure_id}")
			continue
		heater_history_query = ("SELECT first_valid_timestamp, decisions_0 FROM result WHERE\
			   first_valid_timestamp > %s AND machine_id = %s",
			   [periods[0].start, heater.equipement_pilote_ou_mesure_id]
			   )
		heater_history_result = fetch(db_credentials["EMS"], heater_history_query)
		heater_history_result = sorted(heater_history_result, key= lambda x:x[0])
		print(periods, periods_from_timestamp, elfe_heater)
	#TODO reste
	#heater_last_schedules = fetch(db_credentials["EMS"], (f"SELECT machine_id FROM result WHERE first_valid_timestamp=%s AND decisions_0=1", [timestamp]))
	return []

if __name__ == "__main__":
	from datetime import datetime
	print(get_machines(int(datetime.now().timestamp())))

