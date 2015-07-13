from pymongo import *

dict = {
        "x": 1,
        "y": 2,
        "table" : ["string",1,5,4 ]
        }

con = Connection()
db = con.gain_data
collection = db['received_data1']
collection.insert(dict)
anw = collection.find_one()
print type(anw)

print anw["table"][-1]
