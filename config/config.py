from dataclasses import dataclass

HOUR_TIMESTAMP = 60*60

@dataclass(init= True, repr=True)
class Config():
	heater_eco_sliding_percentage : int
	heater_eco_sliding_period_s   : int
	heater_forced_eco_active      : bool
	heater_forced_eco_percentage  : int

def get_config() -> Config:
	return Config(
		heater_eco_sliding_percentage = 25,
		heater_eco_sliding_period_s   = HOUR_TIMESTAMP,
		heater_forced_eco_active      = True,
		heater_forced_eco_percentage  = 10,
	)