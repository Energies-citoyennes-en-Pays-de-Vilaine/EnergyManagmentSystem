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
	
	def create_from_select_output(output):
		obj = {}
		annotations = clas.__annotations__
		for i in range(len(list(annotations.keys()))):
			obj[list(annotations.keys())[i]] = output[i]
		return clas(**obj)
	
	clas.get_update_in_table_str = get_update_in_table_str
	clas.get_append_in_table_str = get_append_in_table_str
	clas.get_create_table_str    = get_create_table_str
	clas.create_from_select_output = create_from_select_output
	return clas
@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSMachineData():
	Id_machine      : PrimaryAutoInt
	Id_machine_elfe : int
	threshold_begin : int
	threshold_end   : int
	period          : int
	period_count    : int
	Id_type         : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSCycle():
	Id_cycle      : PrimaryAutoInt
	Id_machine    : int
	Id_cycle_data : int
	name          : str

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSCycleData():
	Id_cycle_data   : PrimaryAutoInt
	start_time      : int
	csv             : str
	duree           : int
	moved_timestamp : int


@serializableThroughDatabase
@dataclass(init=True, repr=True)
class InitialWheatherForecast():
	wheather_timestamp : Union[int, create_DB_Annotation(is_primary=True)]
	temperature        : int
	wind_speed         : int
	gust_speed         : int
	wind_direction     : int
	sun_hours          : Union[int, create_DB_Annotation(is_nullable=True), None] = None
	def get_clone_at_timestamp(self, timestamp : int):
		return InitialWheatherForecast(timestamp, self.temperature, self.wind_speed, self.gust_speed, self.wind_direction, self.sun_hours)

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class HistoricalInitialWheatherForecast():
	Id_forecast_data   : PrimaryAutoInt
	forecast_timestamp : int
	wheather_timestamp : int
	temperature        : int
	wind_speed         : int
	gust_speed         : int
	wind_direction     : int
	sun_hours          : Union[int, create_DB_Annotation(is_nullable=True), None] = None