from pymongo import *
import scipy.stats#import statistics
import numpy as np
from datetime import datetime
from math import sqrt

class SaveMongo(object):

	def __init__(self):
		self.FILTER_DOWN = 20
		self.FILTER_UP = 90
		self.con = MongoClient()
		self.db_map = self.con.fingerprint
		self.db_locate = self.con.locate
		#self.collection_map = self.db_map['fingerprint']
		#self.collection_locate = self.db_locate['locate']
		self.jsonKey = ["DATA_SIZE", "MODE", "STEP", "PLACE", "POSITIONS", "TIMESTAMP", "MAGNETIC_DATA", "MAGNETIC_AVG_TIME", "IP_PHONE", "MAC_PHONE"]
		self.jsonNewKey = {"FILTERED_RSSI_DATA" : "FILTERED_RSSI_DATA", "FILTERED_MAGNETIC_DATA" : "FILTERED_MAGNETIC_DATA"}
		self.checkPointsCoordinates = {"A" : [0,0], "B" : [0,0], "C" : [0,0], "D" : [0,0], "E" : [0,0], "F" : [0,0], "G" : [0,0], "H" : [0,0], "I" : [0,0], "J" : [0,0], "K" : [0,0], "L" :[0,0], "M" : [0,0], "N" : [0,0], "O" : [0,0], "P" : [0,0], "R" : [0,0], "S" : [0,0], "T" : [0,0], "U" : [0,0],"ERROR" : [-1,-1]};
		self.apCoordinates={}

	def saveData(self,jsonFile):
		#j = simplejson.loads(jsonFile['RSSI_DATA'])
		#print jsonFile
		#for dictonary in jsonFile:
		#	j = simplejson.loads(dictonary)
		#	print type(json)
		#	print json
		#self.filterAndStatistics(jsonFile)
		#print jsonFile
		collecton_name = jsonFile['PLACE'] + '_DATASIZE_' +str(jsonFile['DATA_SIZE'])
		self.countStatisticsData(jsonFile)
		if jsonFile["MODE"] ==  "FEED_MAP":
			self.db_map[collecton_name].insert(jsonFile)
		elif jsonFile["MODE"] ==  "LOCATE_PHONE":
			self.db_locate[collecton_name].insert(jsonFile)

	def __del__(self):
		self.con.disconnect()

	def filterData(self, jsonFile):
		#uniqueKeys = [j[0] for i in jsonFile for j in i.items()]
		uniqueKeys = []
		for key in jsonFile:
			uniqueKeys.append(key)

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
		#uniqueKeys = [j[0] for i in jsonFile for j in i.items()]
		uniqueKeys = []
		for key in jsonFile:
			uniqueKeys.append(key)
		data = []
		if 'POSITIONS' in uniqueKeys:
			tmpP = jsonFile['POSITIONS']
			jsonFile['X'] = tmpP[0]
			jsonFile['Y'] = tmpP[1]
			del jsonFile['POSITIONS']
		if "RSSI_DATA" in uniqueKeys: # "FILTERED_RSSI_DATA"
			data = jsonFile["RSSI_DATA"] #"FILTERED_RSSI_DATA"
		elif "MAGNETIC_DATA" in uniqueKeys: #"FILTERED_MAGNETIC_DATA"
			data = jsonFile["MAGNETIC_DATA"] #"FILTERED_MAGNETIC_DATA"
		meanV = np.mean(data)
		standardDeviation = np.std(data)
		maxV = max(data)
		minV = min(data)
		medianaV = np.median(data)
		tmp = list(scipy.stats.mode(data))
		modeV = tmp[0].tolist()[0]
		array = np.array(data)
		percentile10 = np.percentile(array, 10)
		percentile20 = np.percentile(array, 20)
		percentile50 = np.percentile(array, 50)
		percentile70 = np.percentile(array, 70)
		percentile90 = np.percentile(array, 90)
		statisticsDict = {"MEAN" : meanV,"STANDARD_DEVIATION" : standardDeviation, "MAX" : maxV, "MIN" : minV, "MEDIANA" : medianaV, "MODE" : modeV,  "PERCENTILE - 10" : percentile10,"PERCENTILE - 20" : percentile20,  "PERCENTILE - 50" : percentile50,  "PERCENTILE - 70" : percentile70,  "PERCENTILE - 90" : percentile90 }
		jsonFile["STATISTICS"] = statisticsDict

		if "MAGNETIC_DATA" in uniqueKeys:
			norm = []
			print 'RAW DATA SIZE: ' +  str(len(data))
			for i in range(0,len(data),3):
				norm.append(sqrt(pow(data[i],2) + pow(data[i+1],2) + pow(data[i+2],2)))
			jsonFile['MAGNETIC_DATA_NORM'] = norm
			meanV = np.mean(norm)
			standardDeviation = np.std(norm)
			maxV = max(norm)
			minV = min(norm)
			medianaV = np.median(norm)
			tmp = list(scipy.stats.mode(norm))
			modeV = tmp[0].tolist()[0]
			array = np.array(norm)
			percentile10 = np.percentile(array, 10)
			percentile20 = np.percentile(array, 20)
			percentile50 = np.percentile(array, 50)
			percentile70 = np.percentile(array, 70)
			percentile90 = np.percentile(array, 90)
			statisticsDict = {"MEAN" : meanV,"STANDARD_DEVIATION" : standardDeviation, "MAX" : maxV, "MIN" : minV, "MEDIANA" : medianaV, "MODE" : modeV,  "PERCENTILE - 10" : percentile10,"PERCENTILE - 20" : percentile20,  "PERCENTILE - 50" : percentile50,  "PERCENTILE - 70" : percentile70,  "PERCENTILE - 90" : percentile90 }
			jsonFile["STATISTICS_NORM"] = statisticsDict

	def filterAndStatistics(self, jsonFile):
		self.filterData(jsonFile)
		self.countStatisticsData(jsonFile)
