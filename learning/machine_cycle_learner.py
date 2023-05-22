
from learning.zabbix_reader import ZabbixReader
from credentials.zabbix_credentials import zabbix_credentials
from credentials.db_credentials import db_credentials
from database.EMS_db_types import EMSCycle, EMSCycleData, EMSMachineData
from database.query import fetch, execute_queries
from learning.curve import Curve, make_curves
from datetime import datetime
from config.config import MachineLearnerConfig
import shutil
import matplotlib.pyplot as plt
zr = ZabbixReader("http://mqtt.projet-elfe.fr/api_jsonrpc.php", zabbix_credentials["username"], zabbix_credentials["password"])
zr.get_token()
tags = ["LV", "LL", "SL"]
items = {}
for tag in tags:
	items = {**items, **zr.get_items_by_tag(tag)}
power_items = {}
config : MachineLearnerConfig = MachineLearnerConfig()
DEFAULT_THRESH_BEGIN = config.default_thresh_begin
DEFAULT_THRESH_END   = config.default_thresh_end
DEFAULT_PERIOD       = config.default_period
DEFAULT_PERIOD_COUNT = config.default_period_count
DELTA_TIME_ACQUISITION = config.delta_time_acquisition
MACHINE_TABLE_NAME = config.machine_table_name
MACHINE_CYCLE_NAME = config.machine_cycle_name
MACHINE_CYCLE_DATA_NAME = config.machine_cycle_data_name
known_machines = fetch(db_credentials["EMS"], "SELECT * FROM machine")
known_machines = [EMSMachineData.create_from_select_output(machine) for machine in known_machines]
for item in items:
	if item.split(" ")[1] == "puissance":
		power_items[item] = items[item]
i = 0

for item in power_items:
	#power_items[item] is the id
	
	current_machine = None
	is_already_known = False
	for machine in known_machines:
		if int(machine.Id_machine_elfe) == int(power_items[item]):
			is_already_known = True
			current_machine = machine
			break
	if not is_already_known:
		current_machine = EMSMachineData(0, int(power_items[item]), DEFAULT_THRESH_BEGIN, DEFAULT_THRESH_END, DEFAULT_PERIOD, DEFAULT_PERIOD_COUNT, 0)
		#creates the machine
		execute_queries(db_credentials["EMS"], [current_machine.get_append_in_table_str(MACHINE_TABLE_NAME)])
		#gets the id of the newly created machine
		created_id = int(fetch(db_credentials["EMS"], (f"SELECT id_machine FROM {MACHINE_TABLE_NAME} WHERE {MACHINE_TABLE_NAME}.id_machine_elfe = %s", [int(power_items[item])]))[0][0])
		current_machine.Id_machine = created_id
		#creates the default cycle, pointing it to the default cycle data
		default_cycle = EMSCycle(0, created_id, 0, f"default_cycle_for_machine({power_items[item]})")
		execute_queries(db_credentials["EMS"], [default_cycle.get_append_in_table_str(MACHINE_CYCLE_NAME)])
	cycles = fetch(db_credentials["EMS"], (f"SELECT * FROM {MACHINE_CYCLE_NAME} WHERE id_machine = %s", [current_machine.Id_machine]))
	#TODO add mecanism to support different cycles here, to replace selected_cylce
	selected_cycle : EMSCycle = EMSCycle.create_from_select_output(cycles[0])
	cycle_data = fetch(db_credentials["EMS"], (f"SELECT * FROM {MACHINE_CYCLE_DATA_NAME} WHERE id_cycle_data = %s", [selected_cycle.Id_cycle_data]))
	selected_cycle_data : EMSCycleData = EMSCycleData.create_from_select_output(cycle_data[0])
	#gathers data :
	current_timestamp = int(datetime.now().timestamp())
	data = zr.readData(power_items[item], current_timestamp - DELTA_TIME_ACQUISITION, current_timestamp)
	curves = make_curves([int(d) for d in data["timestamps"]], data["values"], current_machine.threshold_begin, current_machine.threshold_end, current_machine.period, current_machine.period_count)
	if (len(curves) < 1):
		continue
	current_curve = curves[-1]
	current_curve_points = current_curve.points
	if (selected_cycle_data.csv == "default.csv" or selected_cycle_data.start_time < current_curve.timestamp):
		print("update in", item, power_items[item])
		out_file_name = f"{selected_cycle.Id_machine}_{selected_cycle.Id_cycle}_{current_curve.timestamp}.csv"
		out_file_path = f"data/in_use/{out_file_name}"
		with open(out_file_path, 'w') as out_file:
			print(", ".join([str(point) for point in current_curve_points]), file=out_file)
		shutil.copy(f"data/in_use/{selected_cycle_data.csv}", f"data/old/{selected_cycle_data.csv}")
		toCreate : EMSCycleData = EMSCycleData(0, current_curve.timestamp, out_file_name, current_curve.delta_T * len(current_curve.points), 0)
		selected_cycle_data.moved_timestamp = current_timestamp
		execute_queries(db_credentials["EMS"], [
			toCreate.get_append_in_table_str(MACHINE_CYCLE_DATA_NAME),
			selected_cycle_data.get_update_in_table_str(MACHINE_CYCLE_DATA_NAME)
		])
		created_id = int(fetch(db_credentials["EMS"], (f"SELECT id_cycle_data FROM {MACHINE_CYCLE_DATA_NAME} where csv=%s", [out_file_name]))[0][0])
		selected_cycle.Id_cycle_data = created_id
		execute_queries(db_credentials["EMS"], [
			selected_cycle.get_update_in_table_str(MACHINE_CYCLE_NAME)
		])
#else:
	#	print(item, power_items[item], 'is known')
	#first let's append the new machines
"""
for item in power_items:
	print(i, item, power_items[item])
	current_timestamp = int(datetime.now().timestamp())
	data = zr.readData(power_items[item], current_timestamp - 3 * 24*60*60, current_timestamp)
	curves = make_curves([int(d) for d in data["timestamps"]], data["values"], THRESH_BEGIN, THRESH_END, 15*60, 1)
	#plt.figure(1 + i * 2)
	#plt.plot([int(d) for d in data["timestamps"]], data["values"])
	if len(curves) >= 1:
		plt.figure(1 + i * 2)
		plt.plot([int(d) for d in data["timestamps"]], data["values"])
		plt.plot([int(data["timestamps"][0]), int(data["timestamps"][-1])], [THRESH_BEGIN, THRESH_BEGIN])
		plt.plot([int(data["timestamps"][0]), int(data["timestamps"][-1])], [THRESH_END,   THRESH_END])
		fig = plt.figure(2 + i * 2)
		(plots) = fig.subplots(len(curves))
		if (len(curves) ==  1):
			plots = [plots]
		for current_curve_index in range(len(curves)):
			curve = curves[current_curve_index]
			delta = curve.delta_T 
			out_times = [[i * delta, (i + 1) * delta] for i in range(len(curve.points))]
			out_merged = []
			for out in out_times:
				out_merged += out
			points = []
			for point in curve.points:
				points.append(point)
				points.append(point)
			plots[current_curve_index].plot(out_merged, points)
			plots[current_curve_index].plot([i - curve.timestamp for i in curve.origin_timestamp], curve.origin_points)
	i = i + 1	
plt.show()
"""