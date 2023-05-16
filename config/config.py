from dataclasses import dataclass

HOUR_TIMESTAMP = 60*60

@dataclass(init= True, repr=True)
class Config():
	delta_time_simulation_s       : int
	step_count                    : int
	max_time_to_solve_s           : int
	heater_eco_sliding_percentage : int
	heater_eco_sliding_period_s   : int
	heater_forced_eco_active      : bool
	log_problem_settings_active   : bool
	log_problem_settings_path     : str


def get_config() -> Config:
	return Config(
		delta_time_simulation_s       = 60 * 15,#15 mins
		step_count                    = 96, #number of steps for a day at 15mins/steps
		max_time_to_solve_s           = 60*10, #ten minutes to solve, 5 minutes for the interactions with the database
		heater_eco_sliding_percentage = 25,
		heater_eco_sliding_period_s   = HOUR_TIMESTAMP,
		heater_forced_eco_active      = True,
		log_problem_settings_active   = True,
		log_problem_settings_path     = "data/run_conditions"
	)