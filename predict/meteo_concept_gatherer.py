#this is a program designed to run at fixed time to gather meteo data from the api of Meteo concept <https://api.meteo-concept.com>
#this program should add/update the database accordingly
import requests
from database.EMS_db_types import InitialWheatherForecast, HistoricalInitialWheatherForecast
from database.query import fetch, execute_queries
from credentials.meteo_concept_credentials import meteo_concept_key
from credentials.db_credentials import db_credentials
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
BASE_API_URL = "https://api.meteo-concept.com/api/"
NEXT_HOURS_ROUTE = "forecast/nextHours"
PERIOD_FORECAST_ROUTE = "forecast/daily/periods"
def send_request(base_url, route, params):
	response = requests.get(base_url + route, params)
	return json.loads(response.text)

def get_formatted_data(data) -> InitialWheatherForecast:
	usefull_info = {}
	date = datetime.strptime(data["datetime"].split(':')[0], "%Y-%m-%dT%H")
	date += timedelta(hours=-int(data["datetime"].split("+")[1][:2]))
	usefull_info["date"] = int(date.timestamp())
	usefull_info["temperature"] = int(data["temp2m"]) + 273
	usefull_info["wind"] = int(data["wind10m"])
	usefull_info["gust"] = int(data["gust10m"])
	usefull_info["wind_angle"] = int(data["dirwind10m"])#info is in degrees
	forecast = InitialWheatherForecast(wheather_timestamp=usefull_info["date"], temperature=usefull_info["temperature"], sun_hours=None , wind_speed=usefull_info["wind"], gust_speed=usefull_info["gust"], wind_direction=usefull_info["wind_angle"])
	return forecast

if __name__ == '__main__':
	period_data = send_request(BASE_API_URL, PERIOD_FORECAST_ROUTE, 
	{
		'token': meteo_concept_key,
		'insee': 35236,
	})['forecast']
	period_data = [get_formatted_data(data) for daily_data in period_data for data in daily_data]
	forecast = {}
	for data in period_data:
		forecast[data.wheather_timestamp] = data
	next_hours_data = send_request(BASE_API_URL, NEXT_HOURS_ROUTE, 
	{
		'token': meteo_concept_key,
		'insee': 35236,
		'hourly': 'true'
	})['forecast']
	next_hours_data = [get_formatted_data(data) for data in next_hours_data]
	for data in next_hours_data:
		forecast[data.wheather_timestamp] = data # this is the minimal forecast, i'll historize it
	time_of_forecast = int(datetime.now().timestamp())
	#post data to historize the current state
	historize_queries = []
	for key in forecast.keys():
		fc : InitialWheatherForecast = forecast[key]
		forecast_to_historize_point = HistoricalInitialWheatherForecast(0, time_of_forecast, fc.wheather_timestamp, fc.temperature, fc.wind_speed, fc.gust_speed, fc.wind_direction, None)
		historize_queries.append(forecast_to_historize_point.get_append_in_table_str("historyinitialweather"))
	execute_queries(db_credentials["EMS"], historize_queries)
	#let's make the full forecast to be applied
	forecast_to_apply = []
	current_forecast : InitialWheatherForecast = forecast[list(sorted(forecast.keys()))[0]]
	for i in range(len(forecast.keys()) - 1):
		next_forecast : InitialWheatherForecast = forecast[list(sorted(forecast.keys()))[i + 1]]
		current_timestamp = current_forecast.wheather_timestamp
		while (current_timestamp < next_forecast.wheather_timestamp):
			cfc = current_forecast
			forecast_to_apply.append(current_forecast.get_clone_at_timestamp(current_timestamp))
			current_timestamp += 15 * 60
		current_forecast = next_forecast
	dates = [fc.wheather_timestamp for fc in forecast_to_apply]
	query = f"SELECT wheather_timestamp FROM initialweather WHERE wheather_timestamp in ({', '.join(['%s' for fc in forecast_to_apply])})"
	print("going to fetch")
	already_existing = fetch(credentials=db_credentials["EMS"], query=(query, dates))
	print(already_existing)
	queries = []
	for i in range(len(dates)):
		known = False
		if already_existing != None:
			for data in already_existing:
				if int(data[0]) == dates[i]:
					print("date already_existing ", dates[i])
					queries.append(forecast_to_apply[i].get_update_in_table_str("initialweather"))
					known = True
					break
		if (not known):
			queries.append(forecast_to_apply[i].get_append_in_table_str("initialweather"))
	execute_queries(db_credentials["EMS"], queries)