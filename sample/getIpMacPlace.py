from pymongo import MongoClient

coll_name = 'kuznia1_DATASIZE_200_STEP_3_1_DEFAULT'

conn = MongoClient()
db = conn['fingerprint']
coll = db[coll_name]
ip = coll.distinct('IP_PHONE')
print ip
