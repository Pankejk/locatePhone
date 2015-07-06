from pymongo import MongoClient
import os
from math import sqrt
import numpy as np
import scipy.stats

conn = MongoClient()

db_fingerprint = conn['fingerprint']
#ap_fingerprint = db_fingerprint['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].distinct('MAC_AP')
coll_kuznia = db_fingerprint['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT']
#db_locate = conn['locate']
#ap_locate = db_locate['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].distinct('MAC_AP')

#yList = [y * 3 for y in range(0, 13)]
#xList = [x * 2 for x in range(0, 8)]



#apList = {}
#for x in xList:
#    for y in yList:
#        for uAp in doc_fingerprint:
#            db_fingerprint['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].find({})
#coll_kuznia.remove()

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




os.system('mongoimport --db fingerprint --collection kuznia1_DATASIZE:200_STEP:3_1_DEFAULT --file backup/kuznia1_DATASIZE:200_STEP:3_1_DEFAULT_fingerprint_2.07.15.json')
count = 0
docList=[]
for document in coll_kuznia.find({}):
    pos = document['POSITIONS']
    document.update({'X' : pos[0]})
    document.update({'Y' : pos[1]})
    document['STEP'] = [2,3]
    coll_kuznia.save(document)
    count += 1
print 'MODIFIED: ' + str(count)

#coll_kuznia.update({'POSITIONS' : {'$exsists' : 'true'}}, {'$unset' : {'POSITIONS' : 'true'}}, {'multi' : 'true'})
#for doc in docList:
#    coll_kuznia.update({'_id':doc['id']}, {'$set': 'x'})
#    coll_kuznia.update({'_id':doc['id']}, {'$set': 'y'})
coll_kuznia.update({}, {'$unset': {'POSITIONS':1}}, multi=True)
x_distinct = coll_kuznia.distinct('X')
y_distinct = coll_kuznia.distinct('Y')
distinct_fingerprint = coll_kuznia.distinct('MAC_AP')

infoList = []
for x in x_distinct:
    for y in y_distinct:
        for uAp in distinct_fingerprint:
            cursor = coll_kuznia.find({ 'X': x, 'Y' : y, 'MAC_AP': uAp})
            results = [res for res in cursor]
            tmp = [x,y,uAp,len(results)]
            if len(results) == 2:
                result = coll_kuznia.delete_one({'_id' : results[0]['_id']})
                #print result.deleted_count
            #infoList.append(tmp)
print 'DUPLICATED AP REMOVED -' +  str(coll_kuznia.count())

infoList = []
for x in x_distinct:
    for y in y_distinct:
        cursor = coll_kuznia.find({ 'X': x, 'Y' : y, 'MAC_AP': uAp})
        results = [res for res in cursor]
        counter = 0
        for doc in results:
            if 'MAGNETIC_DATA' in doc.viewkeys():
                counter += 1
                if counter > 1:
                    print 'REMOVED FROM: X: ' + doc['X'] + 'Y: ' + doc['Y']
                    coll_kuznia.delete_one({'_id' : doc['_id']})

print 'DUPLICATED MAGNETIC REMOVED -' +  str(coll_kuznia.count())

cursor = coll_kuznia.find({ 'Y' : 39})
for doc in cursor:
    coll_kuznia.delete_one({'_id' : doc['_id']})

for doc in coll_kuznia.find({}):
    doc['STEP'] = [2,3]
    if  'MAGNETIC_DATA' in doc.viewkeys():
        tmp = doc['MAGNETIC_DATA']
        norm = []
        print 'RAW DATA SIZE: ' +  str(len(tmp))
        for i in range(0,len(tmp),3):
            norm.append(sqrt(pow(tmp[i],2) + pow(tmp[i+1],2) + pow(tmp[i+2],2)))
        print 'DATA NORM SIZE: ' +  str(len(norm))
        doc['MAGNETIC_DATA_NORM'] = norm
        countStatisticsData(doc)
    coll_kuznia.save(doc)

print 'DOCYMENTS WITH Y 39 REMOVED -' +  str(coll_kuznia.count())


#infoList = []
#for x in x_distinct:
#    for y in y_distinct:
#        for uAp in distinct_fingerprint:
#            cursor = coll_kuznia.find({ 'X': x, 'Y' : y, 'MAC_AP': uAp})
#            results = [res for res in cursor]
#            tmp = [x,y,uAp,len(results)]
#            infoList.append(tmp)


#fd = open('db_kuznia_fingerprint_repair.txt','w')
#for item in infoList:
#    if item[-1] > 1:
#        fd.write(str(item) + '\n')
#fd.close()