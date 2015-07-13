from pymongo import *
from bson.objectid import ObjectId
import json
import ast

con = MongoClient()
db = con.fingerprint
collection = db['fingerprint']

anw = collection.find_one()
print type(anw)

print anw

print "################################################################################################################################################"

#l = json.loads(anw['RSSI_AVG_TIME'])

print type(anw)
try:
    print anw["RSSI_DATA"][]
except:
    print type(json.loads(anw["RSSI_DATA"]))
        

#print l[0] 

#t = ast.literal_eval(anw['POSITIONS'])

#print type(t)
#print t
