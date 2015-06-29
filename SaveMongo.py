from pymongo import *
import statistics
import numpy as np
import json
import ast
import unicodedata
from bson.objectid import ObjectId
import bson
from bson.codec_options import CodecOptions
from bson import json_util

class SaveMongo(object):

	def __init__(self):
		self.FILTER_DOWN = 20
		self.FILTER_UP = 90
		self.con = MongoClient()
		self.db_map = self.con.fingerprint
		self.db_locate = self.con.locate
		self.db_gain_data = self.con.gain_data
		self.collection_map = self.db_map['fingerprint']
		self.collection_locate = self.db_locate['locate']
		self.collection_received = self.db_gain_data["received_data"]
		self.jsonKey = ["DATA_SIZE", "MODE", "STEP", "PLACE", "POSITIONS", "TIMESTAMP", "MAGNETIC_DATA", "MAGNETIC_AVG_TIME", "IP_PHONE", "MAC_PHONE"]
		self.jsonNewKey = {"FILTERED_RSSI_DATA" : "FILTERED_RSSI_DATA", "FILTERED_MAGNETIC_DATA" : "FILTERED_MAGNETIC_DATA"}
		self.checkPointsCoordinates = {"A" : [0,0], "B" : [0,0], "C" : [0,0], "D" : [0,0], "E" : [0,0], "F" : [0,0], "G" : [0,0], "H" : [0,0], "I" : [0,0], "J" : [0,0], "K" : [0,0], "L" :[0,0], "M" : [0,0], "N" : [0,0], "O" : [0,0], "P" : [0,0], "R" : [0,0], "S" : [0,0], "T" : [0,0], "U" : [0,0],"ERROR" : [-1,-1]};
		self.apCoordinates={}

	def saveData(self,jsonFile):
		#print type(jsonFile)
		#print jsonFile
		con = MongoClient()
		db = con.gain_data['received_data']
		collection = db
		collection.insert(jsonFile)
		anw = collection.find_one()
		lista = []
		print type(anw)
		for key in self.jsonKey:
			#print type(anw[key])
			lista.append(json.loads(anw[key]))
		print lista
		self.filterAndStatistics(jsonFile)
		if jsonFile["MODE"] ==  "FEED_MAP":
			self.collection_map.insert(dictonary)
		elif jsonFile["MODE"] ==  "LOCATE_PHONE":
			self.collection_locate.insert(dictonary)

	def __del__(self):
		self.con.disconnect()

	def filterData(self, jsonFile):
		#print jsonFile
		#uniqueKeys = [j[0] for i in jsonFile for j in i.iteritems()]
		for i in jsonFile:
			#print type(i)			
			#print i
			for j in i.items():
				print type(j)
				print j
				
		rawData = []
		if "RSSI_DATA" in uniqueKeys:
			rawData = json.loads(jsonFile["RSSI_DATA"])
		elif "MAGNETIC_DATA" in uniqueKeys:
			rawData = json.loads(jsonFile["MAGNETIC_DATA"])
		#print rawData
		array = np.array(rawData)
		percentile20 = np.percentile(array, self.FILTER_DOWN)
		percentile90 = np.percentile(array, self.FILTER_UP)
		filteredData = cleanNoise(percentile20, percentile90, rawdata)
		if "RSSI_DATA" in uniqueKeys:
			jsonFile[jsonNewKey["FILTERED_RSSI_DATA"]] = filteredData
		elif "MAGNETIC_DATA" in uniqueKeys:
			jsonFile[jsonNewKey["FILTERED_MAGNETIC_DATA"]] = filteredData
		

	def cleanNoise(self, per20, per90, data):
		for i in range(0,len(data)):
			if data[i] < per20 or data[i] > per90:
				del data[i]
		return data

	def countStatisticsData(self, jsonFile):
		uniqueKeys = [j[0] for i in jsonFile for j in i.items()]
		data = []
		if "FILTERED_RSSI_DATA" in uniqueKeys:
			data = jsonFile["FILTERED_RSSI_DATA"]
		elif "FILTERED_MAGNETIC_DATA" in uniqueKeys:
			data = jsonFile["FILTERED_MAGNETIC_DATA"]
		meanV = mean(data)
		standardDeviation = pstdev(data)
		maxV = max(data)
		minV = min(data)
		medianaV = median_grouped(data)
		modeV = mode(data)
		array = np.array(data)
		percentile10 = np.percentile(array, 10)
		percentile20 = np.percentile(array, 20)
		percentile50 = np.percentile(array, 50)
		percentile70 = np.percentile(array, 70)
		percentile90 = np.percentile(array, 90)
		statisticsDict = {"MEAN" : meanV,"STANDARD_DEVIATION" : standardDeviation, "MAX" : maxV, "MIN" : minV, "MEDIANA" : medianaV, "MODE" : modeV,  "PERCENTILE - 10" : percentile10,"PERCENTILE - 20" : percentile20,  "PERCENTILE - 50" : percentile50,  "PERCENTILE - 70" : percentile70,  "PERCENTILE - 90" : percentile90 }
		jsonFile["STATISTICS"] = statisticsDict

	def filterAndStatistics(self, jsonFile):
		self.filterData(jsonFile)
		self.countStatisticsData(jsonFile)



			
            
