#this is a program designed to run at fixed time to gather meteo data from the api of Meteo concept <https://api.meteo-concept.com>
#this program should add/update the database accordingly
import requests
from learning.database.EMS_db_types import InitialWheatherForecast
from learning.database.EMS_db_creator import fetch, execute_queries
from credentials.meteo_concept_credentials import meteo_concept_key
from credentials.db_credentials import db_credentials
from datetime import datetime, timedelta
import json
BASE_API_URL = "https://api.meteo-concept.com/api/"
NEXT_HOURS_ROUTE = "forecast/nextHours"

def send_request(base_url, route, params):
	response = requests.get(base_url + route, params)
	return json.loads(response.text)

if __name__ == '__main__':
	next_hours_data = send_request(BASE_API_URL, NEXT_HOURS_ROUTE, 
	{
		'token': meteo_concept_key,
		'insee': 35236,
		'hourly': 'true'
	})['forecast']
	forecasts = []
	for data in next_hours_data:
		usefull_info = {}
		date = datetime.strptime(data["datetime"].split(':')[0], "%Y-%m-%dT%H")
		date += timedelta(hours=-int(data["datetime"].split("+")[1][:2]))
		usefull_info["date"] = int(date.timestamp())
		usefull_info["temperature"] = int(data["temp2m"]) + 273
		usefull_info["wind"] = int(data["wind10m"])
		usefull_info["gust"] = int(data["gust10m"])
		usefull_info["wind_angle"] = int(data["dirwind10m"])#info is in degrees
		forecast = InitialWheatherForecast(wheather_timestamp=usefull_info["date"], temperature=usefull_info["temperature"], sun_hours=None , wind_speed=usefull_info["wind"], gust_speed=usefull_info["gust"], wind_direction=usefull_info["wind_angle"])
		forecasts.append(forecast)
	dates = [fc.wheather_timestamp for fc in forecasts]
	query = f"SELECT wheather_timestamp FROM initialweather WHERE wheather_timestamp in ({', '.join(['%s' for fc in forecasts])})"
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
					queries.append(forecasts[i].get_update_in_table_str("initialweather"))
					known = True
					break
		if (not known):
			queries.append(forecasts[i].get_append_in_table_str("initialweather"))
	execute_queries(db_credentials["EMS"], queries)
	pass
