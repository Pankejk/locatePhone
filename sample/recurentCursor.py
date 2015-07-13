from pymongo import MongoClient

conn = MongoClient()
db = conn['fingerprint']
coll = db['kuznia1_DATASIZE_200_STEP_3_1_DEFAULT']
c = coll.find({})
d = c.find({'RSSI_DATA': {'$exists' : True}})
l = [res for res in d]

count = 0
for doc in l:
    count += 1
print count


conn.close()
