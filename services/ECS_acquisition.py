from learning.zabbix_reader import ZabbixReader
from credentials.zabbix_credentials import zabbix_credentials
from credentials.db_credentials import db_credentials
from datetime import datetime
from database.EMS_db_types import EMS_ECS
from database.query import execute_queries
DELTA_TIME = 24 * 3600 # 24H
DELTA_TIME_24H = 24 * 3600 # 24H

current_time = int(datetime.now().timestamp())
zr = ZabbixReader(zabbix_credentials["url"], zabbix_credentials["username"], zabbix_credentials["password"])
zr.get_token()
items = zr.get_items_by_tag("ECS")
items_energie = []
items_puissance = []
for item in items:
    try:
        item = item.replace("_", " ")
        if item.split(" ")[1] == "energie":
            items_energie.append(item.split(" ")[0])
        elif item.split(" ")[1] == "puissance":
            items_puissance.append(item.split(" ")[0])  
    except IndexError as err:
        print(err, item)
queries = []
for i in items_puissance:
    if i in items_energie:
        allData = zr.readData(items[f"{i} energie"], current_time - DELTA_TIME, current_time)["values"]
        if len(allData) < 2:
            allData = [0,0]
            print("creating 0 consumption because no data is availible for item", i)
        energie_conso =  allData[-1] - allData[0]
        if zr.get_unit(items[f"{i} energie"]).upper().startswith("KWH"):
            energie_conso *= 1000
        if (energie_conso < 0):
            energie_conso = 0
        queries.append(EMS_ECS(items[f"{i} puissance"], energie_conso).get_create_or_update_in_table_str("ems_ecs"))
execute_queries(db_credentials["EMS"], queries)