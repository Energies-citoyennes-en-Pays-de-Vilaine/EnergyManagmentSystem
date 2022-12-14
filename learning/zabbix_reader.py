import requests
from learning.data_reader_interface import DataReaderInterface
from datetime import datetime
import json
import numpy as np
import re
import matplotlib.pyplot as plt
class ZabbixReader(DataReaderInterface):
	url : str
	username : str
	password : str
	token : str
	last_refresh : datetime

	def __init__(self, url, username, password) -> None:
		self.url = url
		self.username = username
		self.password = password
		self.last_refresh = None
	def send_request(self, method, params, has_token : bool = False, log : bool = False):
		toSendObject = {
			"jsonrpc": "2.0",
			"method": method,
			"params": params,
			"id": 42,
		}
		if (has_token):
			toSendObject["auth"] = self.get_token()
		data = requests.post(self.url, json=toSendObject, headers={'Content-type': 'application/json'})
		if (log):
			print(params, data)
		#TODO add error code management
		data = json.loads(data.content)
		return data
	def get_token(self):
		if (self.last_refresh == None or (datetime.now() - self.last_refresh).total_seconds() > 100):
			print("refreshing token")
			data = self.send_request("user.login", {
				"user": self.username,
				"password": self.password
			},
			False)
			token = data["result"]
			self.token = token
			self.last_refresh = datetime.now()
		return self.token
	def get_items(self):
		data = self.send_request("item.get", {}, True)["result"]
		items = {}
		for d in data:
			if (re.search("[ADF]{1}\\d{1,3}", d["name"][:4]) != None or re.search("Equi", d["name"][:4]) != None ):
				items[d["name"]] = int(d["itemid"])
		return items

	def get_items_by_tag(self, tag):
		data = self.send_request("item.get", {"tags": [{"tag" : "appareil", "value": tag}]}, True)["result"]
		items = {}
		for d in data:
			items[d["name"]] = d["itemid"]
		return items
	def get_last_data_for_items(self, items):
		data = self.send_request("item.get", {
			"itemids"   : items,
		}, True)
		to_return = []
		for item in data["result"]:
			to_return.append({
				"name": item["name"],
				"itemid" : int(item["itemid"]),
				"last_value" : float(item["lastvalue"]),
				"last_timestamp" : int(item["lastclock"]),
			})
		return to_return
	def readData(self, clientID, time_from, time_till) -> np.ndarray:
		data = self.send_request("history.get", {
			"itemids" : clientID,
			"history": 0,
			"time_from" : time_from,
			"time_till" : time_till,
			"sortfield" : "clock",
			"sortorder" : "ASC"
		}, True)
		toReturn = { 
			"timestamps"  : [],
			"values"      : []
			}
		for d in data["result"]:
			toReturn["timestamps"].append(int(d["clock"]))
			toReturn["values"].append(float(d["value"]))
		return toReturn
	def readAllData(self, clientID) -> np.ndarray:
		data = self.send_request("history.get", {
			"itemids" : clientID,
			"history": 0,
			"sortfield" : "clock",
			"sortorder" : "DESC",
			"limit" : 100_000,
		}, True, True)
		toReturn = { 
			"timestamps"  : [],
			"values"      : []
			}
		for d in data["result"]:
			toReturn["timestamps"].append(int(d["clock"]))
			toReturn["values"].append(float(d["value"]))
		return toReturn