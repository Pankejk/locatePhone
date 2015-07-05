from pymongo import MongoClient
import os
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
os.system('mongoimport --db fingerprint --collection kuznia1_DATASIZE:200_STEP:3_1_DEFAULT --file backup/kuznia1_DATASIZE\:200_STEP\:3_1_DEFAULT_fingerprint_2.07.15.json')
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

cursor = coll_kuznia.find({ 'Y' : 36})
for doc in cursor:
    coll_kuznia.delete_one({'_id' : doc['_id']})
print 'DOCYMENTS WITH Y 36 REMOVED -' +  str(coll_kuznia.count())


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