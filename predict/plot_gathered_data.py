from database.EMS_db_types import InitialWheatherForecast, HistoricalInitialWheatherForecast
from database.query import fetch, execute_queries
import matplotlib.pyplot as plt
from credentials.db_credentials import db_credentials
from datetime import datetime
current_timestamp = int(datetime.now().timestamp())
query = ("SELECT * from initialweather WHERE initialweather.wheather_timestamp > %s", [current_timestamp - 15*60])

labels = ["timestamp", "temperature", "sun_hours", "wind_speed", "gust_speed", "wind_angle"]
result = fetch(db_credentials["EMS"], query)
print(result[0])
splitted_data = [[] for i in result[0]]
for data in sorted(result, key=lambda x:int(x[0])):
	for i in range(len(data)):
		splitted_data[i].append(data[i])
plt.figure(labels[1])
plt.plot(splitted_data[0], splitted_data[1], '.-g')
for i in range(3,len(splitted_data)):
	plt.figure(labels[i])
	plt.plot(splitted_data[0], splitted_data[i], '.-g')
plt.show()
print(InitialWheatherForecast.create_from_select_output(result[0]))