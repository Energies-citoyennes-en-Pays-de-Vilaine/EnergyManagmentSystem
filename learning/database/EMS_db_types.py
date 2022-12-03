from dataclasses import dataclass
import typing
from typing import Union

class DBAnnotation():
	is_db_primary : bool
	is_db_nullable : bool
	def __init__(self) -> None:
		self.is_db_primary = False
		self.is_db_nullable = False


def create_DB_Annotation(*, is_primary = False, is_nullable = False):
	class toReturn(DBAnnotation):
		pass
	toReturn.is_db_nullable = is_nullable
	toReturn.is_db_primary = is_primary
	return toReturn
class PrimaryAutoInt(int):
	pass
def make_primary(clas):
	clas.is_db_primary = True
	return clas
def make_nullable(clas):
	clas.is_nullable = True
	return clas

def serializableThroughDatabase(clas):
	def get_create_table_str(name):
		args = []
		annotations = clas.__annotations__
		for key in annotations.keys():
			base_type = annotations[key]
			dbannotation = DBAnnotation()
			if type(base_type) == typing._UnionGenericAlias:
				dbannotation = base_type.__args__[1]
				base_type = base_type.__args__[0]
			if (base_type == PrimaryAutoInt):
				args.append(f"{key} SERIAL PRIMARY KEY")
			elif (base_type == int):
				args.append(f"{key} INTEGER {'PRIMARY KEY' if dbannotation.is_db_primary else ''} {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
			elif (base_type == str):
				args.append(f"{key} TEXT    {'PRIMARY KEY' if dbannotation.is_db_primary else ''} {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
			else:
				print(annotations[key])
			
		return (f" CREATE TABLE IF NOT EXISTS {name} ({', '.join(args)});")

	def get_append_in_table_str(self, name):
		args = []
		values = []
		annotations = clas.__annotations__
		for key in annotations.keys():
			base_type = annotations[key]
			dbannotation = DBAnnotation()
			if type(base_type) == typing._UnionGenericAlias:
				dbannotation = base_type.__args__[1]
				base_type = base_type.__args__[0]
			if (base_type == PrimaryAutoInt):
				continue
			
			if (self.__getattribute__(key) == None):
				if (dbannotation.is_db_nullable):
					continue
				else:
					raise Exception(f"try to serialize not nullable with none ({key})")
			
			if (base_type == int):
				args.append(f"{key}")
				values.append(self.__getattribute__(key))
			
			elif (base_type == str):
				args.append(f"{key}")
				values.append(self.__getattribute__(key))
			else:
				print(annotations[key])
		return (f"INSERT INTO {name} ({', '.join(args)}) VALUES ({', '.join(['%s' for s in args])});", values)

	def get_update_in_table_str(self, name):
		args = []
		values = []
		annotations = clas.__annotations__
		primary_key   = ""
		primary_value = -1
		for key in annotations.keys():
			base_type = annotations[key]
			dbannotation = DBAnnotation()
			if type(base_type) == typing._UnionGenericAlias:
				dbannotation = base_type.__args__[1]
				base_type = base_type.__args__[0]
			if (base_type == PrimaryAutoInt or dbannotation.is_db_primary):
				primary_key = key
				primary_value = self.__getattribute__(key)
				continue
			if (self.__getattribute__(key) == None):
				if (dbannotation.is_db_nullable):
					continue
				else:
					raise Exception(f"try to serialize not nullable with none ({key})")
			if (base_type == int):
				args.append(f"{key}")
				values.append(self.__getattribute__(key))
			elif (base_type == str):
				args.append(f"{key}")
				values.append(self.__getattribute__(key))
			else:
				print(annotations[key])
		return (f"UPDATE {name} SET {', '.join([s + '=%s' for s in args])} WHERE {primary_key} = %s;", values + [primary_value])
	clas.get_update_in_table_str = get_update_in_table_str
	clas.get_append_in_table_str = get_append_in_table_str
	clas.get_create_table_str    = get_create_table_str
	return clas
@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSMachineData():
	Id_machine      : PrimaryAutoInt
	Id_zabbix       : int
	Id_viriya       : int
	threshold_begin : int
	threshold_end   : int
	period          : int
	period_count    : int
	Id_type         : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSCycle():
	Id_cycle   : PrimaryAutoInt
	Id_machine : int
	csv_file   : str
	name       : str
	duree      : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class InitialWheatherForecast():
	wheather_timestamp : Union[int, create_DB_Annotation(is_primary=True)]
	temperature        : int
	wind_speed         : int
	gust_speed         : int
	wind_direction     : int
	sun_hours          : Union[int, create_DB_Annotation(is_nullable=True), None] = None