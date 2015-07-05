from pymongo import MongoClient
import os

os.system('mongoimport --db locate --collection kuznia1_DATASIZE:200_STEP:3_1_DEFAULT --file backup/kuznia1_DATASIZE:200_STEP:3_1_DEFAULT_locate_2.07.15.json')

conn = MongoClient()

db_locate = conn['locate']
distinctLocate = db_locate['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].distinct('MAC_AP')
coll_kuznia = db_locate['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT']
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
            print 'NICE'
            coll_kuznia.delete_one({'_id' : results[0]['_id']})

for doc in coll_kuznia.find({}):
    doc['STEP'] = [2,3]
    coll_kuznia.save(doc)

print 'AFTER AP DUPLICATION REMOVED: ' + str(coll_kuznia.count({}))

fd = open('kuznia_locate_repair.txt','w')
for item in infoList:
    if item[-1] > 1:
        fd.write(str(item) + '\n')
fd.close()