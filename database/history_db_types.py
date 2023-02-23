from database.annotations import DBAnnotation, serializableThroughDatabase, PrimaryAutoInt
from dataclasses import dataclass

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class history_Prediction():
	_id                  : PrimaryAutoInt
	model_id             : int
	curve_id             : int
	run_timestamp        : int
	prediction_timestamp : int
	value                : int

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class history_Model():
	_id  : PrimaryAutoInt
	name : str

@serializableThroughDatabase
@dataclass(init=True, repr=True)
class history_Curve():
	_id  : PrimaryAutoInt
	name : str

