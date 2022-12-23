from dataclasses import dataclass
import typing
from typing import Union, List

class DBAnnotation():
	is_db_primary    : bool
	is_db_nullable   : bool
	is_db_list       : bool
	db_element_count : int
	def __init__(self) -> None:
		self.is_db_primary  = False
		self.is_db_nullable = False
		self.is_db_list     = False
		db_element_count    = 0


def create_DB_Annotation(*, is_primary = False, is_nullable = False, is_db_list = False, db_element_count = 0):
	class toReturn(DBAnnotation):
		pass
	toReturn.is_db_nullable   = is_nullable
	toReturn.is_db_primary    = is_primary
	toReturn.is_db_list       = is_db_list
	toReturn.db_element_count = db_element_count 
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
			if not dbannotation.is_db_list:
				if (base_type == PrimaryAutoInt):
					args.append(f"{key} SERIAL PRIMARY KEY")
				elif (base_type == int):
					args.append(f"{key} INTEGER {'PRIMARY KEY' if dbannotation.is_db_primary else ''} {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
				elif (base_type == bool):
					args.append(f"{key} BOOLEAN {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
				elif (base_type == str):
					args.append(f"{key} TEXT    {'PRIMARY KEY' if dbannotation.is_db_primary else ''} {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
				else:
					print(annotations[key])
			else:
				for i in range(dbannotation.db_element_count):
					if (base_type == int):
						args.append(f"{key}_{i} INTEGER {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
					elif (base_type == bool):
						args.append(f"{key}_{i} BOOLEAN {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
					elif (base_type == str):
						args.append(f"{key}_{i} TEXT    {'NOT NULL' if not dbannotation.is_db_nullable else ''}")
					else:
						print(annotations[key])
			
		return (f" CREATE TABLE IF NOT EXISTS {name} ({', '.join(args)});")

	def get_append_in_table_str(self, name):
		args = []
		values = []
		annotations = clas.__annotations__
		primary_key = None
		for key in annotations.keys():
			base_type = annotations[key]
			dbannotation = DBAnnotation()
			if type(base_type) == typing._UnionGenericAlias:
				dbannotation = base_type.__args__[1]
				base_type = base_type.__args__[0]
			if dbannotation.is_db_primary:
				primary_key = key
			if (base_type == PrimaryAutoInt):
				primary_key = key
				continue
			
			if (self.__getattribute__(key) is None):
				if (dbannotation.is_db_nullable):
					continue
				else:
					raise Exception(f"try to serialize not nullable with none ({key})")
			if not dbannotation.is_db_list:
				if (base_type == int):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				
				elif (base_type == str):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				elif (base_type == bool):
					args.append(f"{key}")
					values.append('1' if self.__getattribute__(key) == True else '0')
				else:
					print(annotations[key])
			else:
				for i in range(dbannotation.db_element_count):
					if (base_type == int):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					
					elif (base_type == str):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					elif (base_type == bool):
						args.append(f"{key}_{i}")
						values.append('1' if self.__getattribute__(key)[i] == True else '0')
					else:
						print(annotations[key])
		if primary_key is None:
			print("warning, no primary key registered")
			return (f"INSERT INTO {name} ({', '.join(args)}) VALUES ({', '.join(['%s' for s in args])});", values)
		return (f"INSERT INTO {name} ({', '.join(args)}) VALUES ({', '.join(['%s' for s in args])}) RETURNING {primary_key};", values)

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
			if (self.__getattribute__(key) is None):
				if (dbannotation.is_db_nullable):
					continue
				else:
					raise Exception(f"try to serialize not nullable with none ({key})")
			if not dbannotation.is_db_list:
				if (base_type == int):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				elif (base_type == str):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				elif (base_type == bool):
					args.append(f"{key}")
					values.append('1' if self.__getattribute__(key) == True else '0')
				else:
					print(annotations[key])
			else:
				for i in range(dbannotation.db_element_count):
					if (base_type == int):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					elif (base_type == str):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					elif (base_type == bool):
						args.append(f"{key}_{i}")
						values.append('1' if self.__getattribute__(key)[i] == True else '0')
					else:
						print(annotations[key])

		return (f"UPDATE {name} SET {', '.join([s + '=%s' for s in args])} WHERE {primary_key} = %s;", values + [primary_value])

	def get_create_or_update_in_table_str(self, name):
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
			if (self.__getattribute__(key) is None):
				if (dbannotation.is_db_nullable):
					continue
				else:
					raise Exception(f"try to serialize not nullable with none ({key})")
			if not dbannotation.is_db_list:
				if (base_type == int):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				elif (base_type == str):
					args.append(f"{key}")
					values.append(self.__getattribute__(key))
				elif (base_type == bool):
					args.append(f"{key}")
					values.append('1' if self.__getattribute__(key) == True else '0')
				else:
					print(annotations[key])
			else:
				for i in range(dbannotation.db_element_count):
					if (base_type == int):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					elif (base_type == str):
						args.append(f"{key}_{i}")
						values.append(self.__getattribute__(key)[i])
					elif (base_type == bool):
						args.append(f"{key}_{i}")
						values.append('1' if self.__getattribute__(key)[i] == True else '0')
					else:
						print(annotations[key])
		return (f"INSERT INTO {name} ({', '.join([primary_key] + args)}) VALUES ({', '.join(['%s' for s in [primary_key] + args])}) ON CONFLICT ({primary_key}) DO UPDATE SET {', '.join([s + '=%s' for s in args])};", [primary_value] + values + values)


	def create_from_select_output(output):
		obj = {}
		annotations = clas.__annotations__
		j = 0
		for i in range(len(list(annotations.keys()))):
			key = list(annotations.keys())[i]

			base_type = annotations[key]
			dbannotation = DBAnnotation()
			if type(base_type) == typing._UnionGenericAlias:
				dbannotation = base_type.__args__[1]
				base_type = base_type.__args__[0]
			if not dbannotation.is_db_list:
				if (base_type == int):
					obj[list(annotations.keys())[i]] = int(output[j])
				elif (base_type == bool):
					obj[list(annotations.keys())[i]] = bool(output[j])
				else:
					obj[list(annotations.keys())[i]] = output[j]
				j = j + 1
			else:
				obj[list(annotations.keys())[i]] = [0] * dbannotation.db_element_count
				for k in range(dbannotation.db_element_count):
					if (base_type == int):
						obj[list(annotations.keys())[i]][k] = int(output[j])
					elif (base_type == bool):
						obj[list(annotations.keys())[i]][k] = bool(output[j])
					else:
						obj[list(annotations.keys())[i]][k] = output[j]
					j = j + 1
		return clas(**obj)
	
	clas.get_update_in_table_str = get_update_in_table_str
	clas.get_append_in_table_str = get_append_in_table_str
	clas.get_create_table_str    = get_create_table_str
	clas.get_create_or_update_in_table_str = get_create_or_update_in_table_str
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

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSDeviceTemperatureData():
	Id_elfe                    : Union[int, create_DB_Annotation(is_primary=True)]
	data_timestamp             : int
	temperature                : int 

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSPowerCurveData():
	data_timestamp             : Union[int, create_DB_Annotation(is_primary=True)]
	power                      : int 

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class EMSResult():
	Id                        : PrimaryAutoInt
	first_valid_timestamp     : int
	machine_id                : int
	result_type               : int
	machine_type              : int
	decisions                 : Union[int, create_DB_Annotation(is_db_list=True, db_element_count=96), List[int]]
	 