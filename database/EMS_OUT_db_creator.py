
from credentials.db_credentials import db_credentials
from dataclasses import dataclass
import typing
from typing import Union
from database.query import execute_queries, fetch
from database.EMS_db_types import  EMSResult, EMSPowerCurveData
def create_tables(credentials):
	tables_queries = [
		EMSResult.get_create_table_str("result"),
		EMSPowerCurveData.get_create_table_str("p_c_with_flexible_consumption"),
		EMSPowerCurveData.get_create_table_str("p_c_without_flexible_consumption")
	]
	execute_queries(credentials, tables_queries)

			
if __name__ == '__main__':
	create_tables(db_credentials["EMS_SORTIE"])