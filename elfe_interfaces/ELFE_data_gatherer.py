from database.ELFE_db_types import ELFE_BallonECS, ELFE_BallonECSHeuresCreuses, ELFE_ChauffageAsservi, ELFE_ChauffageAsserviModeleThermique, ELFE_ChauffageNonAsservi, ELFE_EquipementPilote, ELFE_MachineGenerique, ELFE_MachineGeneriqueCycle, ELFE_VehiculeElectriqueGenerique
from database.ELFE_db_types import ELFE_database_names
from database.EMS_db_types import EMSCycle, EMSCycleData, EMSDeviceTemperatureData, EMSMachineData, EMSPowerCurveData, InitialWheatherForecast, EMS_Modele_Thermique
from database.query import execute_queries, fetch
from credentials.db_credentials import db_credentials
from typing import List, Tuple
from solution.ConsumerTypes.HeaterConsumer import HeaterConsumer
from solution.ConsumerTypes.SumConsumer import SumConsumer, SumPeriod
from solution.ConsumerTypes.MachineConsumer import MachineConsumer
from solution.ConsumerTypes.ECSConsumer import ECSConsumer
from solution.ConsumerTypes.VehicleConsumer import VehicleConsumer
from solution.Calculation_Params import CalculationParams
from utils.time.period import Period, get_merged_periods
from utils.time.midnight import get_midnight_date, get_midnight_timestamp
from utils.time.timestamp import get_timestamp, get_round_timestamp
from math import ceil
from datetime import datetime
import numpy as np
from config.config import Config, get_config

config : Config = get_config()
MODE_PILOTE = 30
DAY_TIME_SECONDS = 24 * 60 * 60
DELTA_SIMULATION = config.delta_time_simulation_s

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
			midnight_timestamp + ecs["start"],
			midnight_timestamp + ecs["start"] + 24 * 3600,
		]
		possible_ends = [
			midnight_timestamp + ecs["end"] - 24 * 3600,
			midnight_timestamp + ecs["end"],
			midnight_timestamp + ecs["end"] + 24 * 3600
		]
		consumer : ECSConsumer
		print(timestamp - possible_starts[0], timestamp - possible_ends[0])
		if (timestamp > possible_starts[0] and timestamp < possible_ends[0]):
			consumer = ECSConsumer(ecs["epmid"], ecs_curve, possible_starts[0], possible_ends[0], ecs["power"], ecs["volume"])
		elif (timestamp <= possible_starts[0] or (timestamp > possible_starts[1] and timestamp < possible_ends[1])): 
			consumer = ECSConsumer(ecs["epmid"], ecs_curve, possible_starts[1], possible_ends[1], ecs["power"], ecs["volume"])
		else:
			consumer = ECSConsumer(ecs["epmid"], ecs_curve, possible_starts[2], possible_ends[2], ecs["power"], ecs["volume"])
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
	sum_consumers : List[SumConsumer] = []
	for heater in elfe_heater:
		periods : List[Period] = []
		for start in starting_periods:
			periods += heater.get_periods(start)
		for p in periods:
			p.snap_to(calculationParams.time_delta) #snaps period to the current time delta
		periods = get_merged_periods(periods)
		periods = list(filter(lambda x : (x - timestamp).end > 0, periods))
		periods = sorted(periods, key=lambda x : x.start)
		if len(periods) == 0:
			print(f"no periods to schedule for heater {heater.equipement_pilote_ou_mesure_id}")
			continue
		first_period : Period = periods[0].deep_copy()
		first_period_cutted : Period = first_period.deep_copy()
		first_period_cutted.cut(calculationParams.begin, calculationParams.end)
		for p in periods:
			p.cut(calculationParams.begin , calculationParams.end)
		period_filtered : List[Period] = list(filter(lambda x : x.end - x.start > 0), periods)
		if len(periods) == 0:
			print(f"no periods left to schedule for heater {heater.equipement_pilote_ou_mesure_id} after cutting on the simulation params")
			continue
		count : int = 0
		summ : int = 0
		if (first_period_cutted in period_filtered):
			heater_history_query = ("SELECT COUNT(*) as c, SUM(decisions[0]) as s FROM result WHERE\
			   first_valid_timestamp > %s AND machine_id = %s GROUP BY machine_id",
			   [first_period.start, heater.equipement_pilote_ou_mesure_id]
			   )
			heater_history_result = fetch(db_credentials["EMS"], heater_history_query)
			count = heater_history_result[0][0]
			summ  = heater_history_result[0][1]
		sum_periods : List[SumPeriod] = []
		for p in periods:
			expected_sum : int = round((100.0 - heater.pourcentage_eco_force) / 100.0 * (count + (p.end - p .start) / calculationParams.step_size))
			expected_sum_left : int = expected_sum - summ
			steps_left : int = round((p.end - p .start) / calculationParams.step_size)
			if (expected_sum_left > steps_left):
				print(f"something went wrong with heater {heater.equipement_pilote_ou_mesure_id} period({p}), reducing expected sum left")
				expected_sum_left = steps_left
			sliding_period_steps : int = round(config.heater_eco_sliding_period_s / calculationParams.step_size)
			sliding_period_count : int = steps_left // sliding_period_steps
			sliding_period_consumption_denied : int = ceil(sliding_period_steps * config.heater_eco_sliding_percentage / 100.0)
			sliding_period_min : int = max(0, sliding_period_steps - sliding_period_consumption_denied)
			sliding_period_max : int = sliding_period_steps
			for i in range(sliding_period_count):
				start_time : int = i * calculationParams.step_size
				sum_period : SumPeriod = SumPeriod(p.start + start_time, p.end + start_time, sliding_period_min, sliding_period_max)
				sum_periods.append(sum_period)
			
			sum_periods.append(SumPeriod(p.start, p.end, expected_sum_left, steps_left))
			count = 0
			summ = 0
		sum_consumer : SumConsumer = SumConsumer(heater.equipement_pilote_ou_mesure_id, heater.puissance_moyenne_eco, heater.puissance_moyenne_confort, sum_periods)
		sum_consumers.append(sum_consumer)
		print(periods)
		print([p - timestamp for p in periods])
		print(elfe_heater)
	return sum_consumers

def get_temperature_forecast(timestamp_start : int, timestamp_end : int, timestamp_list : List[int]) -> np.ndarray:
	temperature_query = ("SELECT wheather_timestamp, temperature FROM initialweather WHERE wheather_timestamp >= %s AND wheather_timestamp <= %s ORDER BY wheather_timestamp ASC", timestamp_start, timestamp_end)
	temperature_list : List[Tuple[int, int]]= fetch(db_credentials["EMS"], temperature_query)
	forecast : List[int] = []
	for t in timestamp_list:
		current_temperature = 283 # 10 C, default value if no forecast is availible
		distance = 0
		real_point = False
		for timestamp, temperature in temperature_list:
			if real_point == False:
				real_point = True
				current_temperature = temperature
				distance = abs(timestamp - t)
				continue
			if (abs(timestamp - t) < distance):
				current_temperature = temperature
				distance = abs(timestamp - t)
				if (distance == 0):
					break
		forecast.append(current_temperature)
	return forecast

def get_heater_consumer(timestamp : int, calculationParams: CalculationParams) -> List[HeaterConsumer]:
	elfe_heater_query = f"SELECT heater.* \
		FROM {ELFE_database_names['ELFE_ChauffageAsservi']} AS heater\
		INNER JOIN {ELFE_database_names['ELFE_EquipementPilote']} AS epm ON epm.id = heater.equipement_pilote_ou_mesure_id\
		WHERE epm.equipement_pilote_ou_mesure_mode_id = {MODE_PILOTE}"	
	elfe_heater_result = fetch(db_credentials["ELFE"], elfe_heater_query)
	elfe_heater : List[ELFE_ChauffageAsservi] = [ELFE_ChauffageAsservi.create_from_select_output(result) for result in elfe_heater_result]
	starting_periods : List[datetime] = [get_midnight_date(timestamp - DAY_TIME_SECONDS), get_midnight_date(timestamp), get_midnight_date(timestamp + DAY_TIME_SECONDS)]
	heater_consumers : List[SumConsumer] = []
	for heater in elfe_heater:
		periods : List[Period] = []
		for start in starting_periods:
			periods += heater.get_periods(start)
		for p in periods:
			p.snap_to(calculationParams.time_delta) #snaps period to the current time delta
			p.cut(calculationParams.begin, calculationParams.end)
		periods = list(filter(lambda x : x.end - x.start > 0, periods))
		periods = list(filter(lambda x : x.end > calculationParams.begin , periods))
		periods = list(filter(lambda x : x.start < calculationParams.end , periods))
		simulation_timestamps : List[int] = calculationParams.get_time_array()
		in_periods : List[bool]  = [False for i in simulation_timestamps]
		target_temperature_low : List[float] = [0.0 for i in simulation_timestamp]
		target_temperature_high : List[float] = [0.0 for i in simulation_timestamp]
		t_low_eco      : int = (heater.temperature_eco - heater.delta_temp_maximale_temp_demandee) / 100 # data is in centiKelvin in the database
		t_high_eco     : int = (heater.temperature_eco + heater.delta_temp_maximale_temp_demandee) / 100 # data is in centiKelvin in the database
		t_low_comfort  : int = (heater.temperature_confort - heater.delta_temp_maximale_temp_demandee) / 100 # data is in centiKelvin in the database
		t_high_comfort : int = (heater.temperature_confort + heater.delta_temp_maximale_temp_demandee) / 100 # data is in centiKelvin in the database
		for i, simulation_timestamp in enumerate(simulation_timestamps):#there might be an optimisation possible
			for p in periods:
				if simulation_timestamp >= p.start and simulation_timestamp < p.end:
					in_periods[i] = True
		for i, in_period in enumerate(in_periods):
			target_temperature_low[i]  = t_low_eco
			target_temperature_high[i] = t_high_eco
			if (in_period):
				target_temperature_low[i]  = t_low_comfort
				target_temperature_high[i] = t_high_comfort
		t_init = 0.0
		initial_state = False
		m_th_query = fetch(db_credentials["EMS"], ("SELECT * FROM ems_modele_thermique where id=%s", [heater.modele_thermique_id]))
		m_th : EMS_Modele_Thermique = EMS_Modele_Thermique.create_from_select_output(m_th_query[0]) 
		T_ext_response = fetch(db_credentials["EMS"], ("SELECT wheather_timestamp, temperature FROM initialwheather WHERE wheather_timestamp >= %s",[get_round_timestamp()]))
		T_ext = np.array([T_ext_response[0][i] for i in range(len(calculationParams.get_time_array))])
		heater_consumer : HeaterConsumer = HeaterConsumer(heater.id, t_init, initial_state, T_ext, target_temperature_low, target_temperature_high, m_th.R_th, m_th.C_th, heater.puissance)
		heater_consumers.append(heater_consumer)
	return heater_consumers

def get_simulation_datas() -> List[int]:
	config = get_config()
	round_start_timestamp = get_round_timestamp()
	expected_power = fetch(db_credentials["EMS"], ("SELECT * FROM prediction WHERE data_timestamp >= %s ;", [round_start_timestamp]))
	expected_power = sorted(expected_power, key=lambda x : int(x[0]))
	simulation_datas = expected_power[:config.step_count]
	return simulation_datas

def get_calculation_params(simulation_datas = None) -> CalculationParams:
	timestamp = get_timestamp()
	round_start_timestamp = get_round_timestamp()
	if (simulation_datas == None):
		simulation_datas = get_simulation_datas()
	sim_params = CalculationParams(round_start_timestamp, timestamp + config.step_count * config.delta_time_simulation_s, config.delta_time_simulation_s, config.delta_time_simulation_s, [[-int(simulation_datas[i][1]) for i in range(config.step_count)]])
	return sim_params

if __name__ == "__main__":
	from datetime import datetime
	print(get_machines(int(datetime.now().timestamp())))

