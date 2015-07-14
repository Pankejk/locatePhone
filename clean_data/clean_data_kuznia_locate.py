from pymongo import MongoClient
import os
from math import sqrt
import numpy as np
import scipy.stats


def countStatisticsData(jsonFile):
		#uniqueKeys = [j[0] for i in jsonFile for j in i.items()]
        uniqueKeys = []
		#for key in jsonFile:
		#	uniqueKeys.append(key)
        data = []
		#if "RSSI_DATA" in uniqueKeys: # "FILTERED_RSSI_DATA"
		#	data = jsonFile["RSSI_DATA"] #"FILTERED_RSSI_DATA"
		#elif "MAGNETIC_DATA" in uniqueKeys: #"FILTERED_MAGNETIC_DATA"
        data = jsonFile['MAGNETIC_DATA_NORM'] #"FILTERED_MAGNETIC_DATA"
        array = np.array(data)
        #print data
        meanV = np.mean(data)
        standardDeviation = np.std(data)
        maxV = max(data)
        minV = min(data)
        medianaV = np.median(data)
        tmp = list(scipy.stats.mode(data))
        modeV = tmp[0].tolist()[0]

        percentile10 = np.percentile(array, 10)
        percentile20 = np.percentile(array, 20)
        percentile50 = np.percentile(array, 50)
        percentile70 = np.percentile(array, 70)
        percentile90 = np.percentile(array, 90)
        statisticsDict = {"MEAN" : meanV,"STANDARD_DEVIATION" : standardDeviation, "MAX" : maxV, "MIN" : minV, "MEDIANA" : medianaV, "MODE" : modeV,  "PERCENTILE - 10" : percentile10,"PERCENTILE - 20" : percentile20,  "PERCENTILE - 50" : percentile50,  "PERCENTILE - 70" : percentile70,  "PERCENTILE - 90" : percentile90 }
        jsonFile["STATISTICS_NORM"] = statisticsDict




os.system('mongoimport --db locate --collection kuznia1_DATASIZE_200_STEP_3_1_DEFAULT --file data-backup/kuznia1_DATASIZE:200_STEP:3_1_DEFAULT_locate_2.07.15.json')

conn = MongoClient()

db_locate = conn['locate']
distinctLocate = db_locate['kuznia1_DATASIZE_200_STEP_3_1_DEFAULT'].distinct('MAC_AP')
coll_kuznia = db_locate['kuznia1_DATASIZE_200_STEP_3_1_DEFAULT']
distinctCp = coll_kuznia.distinct('CHECKPOINT')

distinctCp.sort()

infoList = []
for cp in distinctCp:
    for ap in distinctLocate:
        cursor = coll_kuznia.find({'CHECKPOINT' : cp, 'MAC_AP' : ap})
        results = [res for res in cursor]
        tmp = [cp,ap,len(results)]
        infoList.append(tmp)
        if len(results) > 1:
            #print 'NICE'
            coll_kuznia.delete_one({'_id' : results[0]['_id']})

infoList = []

for cp in distinctCp:
        cursor = coll_kuznia.find({'CHECKPOINT' : cp})
        results = [res for res in cursor]
        counter = 0
        for doc in results:
            if 'MAGNETIC_DATA' in doc.viewkeys():
                counter += 1
                if counter > 1:
                    print 'CHECKPOINT:' + doc['CHECKPOINT'] + 'COUNTER: ' + str(counter)
                    coll_kuznia.delete_one({'_id' : doc['_id']})
#print "AFTER REMOVING DUPLICATION MAGNETIC DATA FOR CHECKPOINT: " + str(counter)
        #tmp = [cp,ap,len(results)]
        #infoList.append(tmp)
        #if len(results) > 1:
        #    print 'NICE'
        #    coll_kuznia.delete_one({'_id' : results[0]['_id']})

for doc in coll_kuznia.find({}):
    doc['STEP'] = [2,3]
    if  'MAGNETIC_DATA' in doc.viewkeys():
        tmp = doc['MAGNETIC_DATA']
        norm = []
        if len(tmp) > 600:
            tmp = tmp[0:600]
            doc['MAGNETIC_DATA'] = tmp
            print 'RAW DATA SIZE: ' +  str(len(tmp))
            print tmp
        for i in range(0,len(tmp),3):
            norm.append(sqrt(pow(tmp[i],2) + pow(tmp[i+1],2) + pow(tmp[i+2],2)))
        print 'DATA NORM SIZE: ' +  str(len(norm))
        doc['MAGNETIC_DATA_NORM'] = norm
        countStatisticsData(doc)
    coll_kuznia.save(doc)


print 'AFTER AP DUPLICATION REMOVED: ' + str(coll_kuznia.count({}))

for doc in coll_kuznia.find({}):
    if doc['CHECKPOINT'] == '0':
        coll_kuznia.delete_one({'_id' : doc['_id']})
print 'AFTER ) checkpoint removed: ' + str(coll_kuznia.count({}))

fd = open('kuznia_locate_repair.txt','w')
for item in infoList:
    if item[-1] > 1:
        fd.write(str(item) + '\n')
fd.close()
