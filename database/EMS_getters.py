from typing import List
from dataclasses import dataclass
from psycopg2 import sql
from database.query import fetch

def get_equipment_started_last_round(db_credentials, timestamp ,table_name) -> List[int]:
	query_formatted = sql.SQL("SELECT machine_id FROM {} WHERE first_valid_timestamp=%s AND decisions_0=1").format(sql.Identifier(table_name))
	result = fetch(db_credentials, (query_formatted, [timestamp]))
	return [int(i[0]) for i in result]


def get_cycle_filename_for_machine(credentials, cycle_name: str, zabbix_id: int) -> str:
	print(zabbix_id)
	csv_cycle = fetch(credentials, (f" SELECT cd.csv FROM machine AS m"
									+f" INNER JOIN cycle AS c ON c.id_machine = m.id_machine"
									+f" INNER JOIN cycledata AS cd ON cd.id_cycle_data = c.id_cycle_data "
									+f" WHERE m.id_machine_elfe=%s AND c.name=%s",
									[zabbix_id, cycle_name]))
	try: 
		csv_cycle = csv_cycle[0]
	except IndexError:
		csv_cycle = "default.csv"
		print("not found in database", zabbix_id)
	return csv_cycle