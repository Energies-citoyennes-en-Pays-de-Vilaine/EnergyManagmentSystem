import psycopg2
from credentials.db_credentials import db_credentials
from dataclasses import dataclass
import typing
from typing import Union
from learning.database.EMS_db_types import EMSMachineData, EMSCycle, EMSCycleData ,InitialWheatherForecast, HistoricalInitialWheatherForecast
def create_tables(credentials):
	tables_queries = [
		EMSCycle.get_create_table_str("cycle"),
		EMSCycleData.get_create_table_str("cycledata"),
		EMSMachineData.get_create_table_str("machine"),
		InitialWheatherForecast.get_create_table_str("initialweather"),
		HistoricalInitialWheatherForecast.get_create_table_str("historyinitialweather")
	]
	execute_queries(credentials, tables_queries)

def execute_queries(credentials, queries):
	cred = credentials
	try:
		connection = psycopg2.connect(host = cred["host"], database = cred["database"], user = cred["user"], password = cred["password"])
		cursor = connection.cursor()
		# create table one by one
		for query in queries:
			if (isinstance(query, str)):
				cursor.execute(query)
			else:
				cursor.execute(query[0], query[1])
		# close communication with the PostgreSQL database server
		cursor.close()
		# commit the changes
		connection.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if connection is not None:
			connection.close()
def fetch(credentials, query):
	cred = credentials
	result = None
	try:
		connection = psycopg2.connect(host = cred["host"], database = cred["database"], user = cred["user"], password = cred["password"])
		cursor = connection.cursor()
		if (isinstance(query, str)):
			cursor.execute(query)
		else:
			cursor.execute(query[0], query[1])
		result = cursor.fetchall()
		cursor.close()
		# commit the changes
		connection.commit()
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	finally:
		if connection is not None:
			connection.close()	
	return result		
			
if __name__ == '__main__':
	create_tables(db_credentials["EMS"])