"""class creates fake checkpoint form fingerprint map to check location alg."""

from pymongo import MongoClient

import time
import sys
import random
from datetime import datetime

class FakeCheckpoints(object):

    def __init__(self, collName):
        self.collName = collName
        self.collLocateName = 'locate_fake_checkpoints_' + self.collName
        self.conn = MongoClient()
        db_fingerprint = self.conn['fingerprint']
        db_locate = self.conn['locate']
        self.coll_fingerprint = db_fingerprint[self.collName]
        self.coll_locate = db_locate[self.collLocateName]
        if self.collLocateName in db_locate.collection_names():
            self.coll_locate.drop()

        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.x_max = max(self.x_distinct)
        self.y_max = max(self.y_distinct)
        self.x_min = min(self.x_distinct)
        self.y_min = min(self.y_distinct)

        date = str(datetime.now()).replace(' ', '.')
        date = date.replace(':','_')
        filename = 'fakecheckpoints_' + self.collName + '_' + date  + '.txt'
        self.fd = open(filename,'w')

    def __del__(self):
        self.conn.close()
        self.fd.close()

###############################################################################
    def createFakeCheckpoints(self, numberOfFakeCheckpoints):
        random_x = []
        random_y = []

        counter = 0
        while (True):
            x = random.randint(0,len(self.x_distinct) -1)
            if not x in random_x:
                random_x.append(self.x_distinct[x])
                counter += 1
            if counter == numberOfFakeCheckpoints:
                break

        counter = 0
        while (True):
            y = random.randint(0,len(self.y_distinct) - 1)
            if not y in random_y:
                random_y.append(self.y_distinct[y])
                counter += 1
            if counter == numberOfFakeCheckpoints:
                break

        randomCoordinates = []
        for i in range(0,numberOfFakeCheckpoints):
            randomCoordinates.append([random_x[i],random_y[i]])

        checkpointCounter = 0
        for tList in randomCoordinates:
            cursor = self.coll_fingerprint.find({'X': tList[0], 'Y': tList[1]})
            docs = [res for res in cursor]

            self.saveCheckpointsToFile(checkpointCounter, tList[0], tList[1])
            for doc in docs:
                doc['CHECKPOINT'] = str(checkpointCounter)
                doc['MODE'] = 'LOCATE_PHONE'
                del doc['X']
                del doc['Y']
                del doc['_id']
                self.coll_locate.save(doc)
            checkpointCounter += 1
###############################################################################
    """method for saving checkpoints"""
    def saveCheckpointsToFile(self, checkpointName, x, y):
        line = str(checkpointName) + ' ' + str(x) + ' ' + str(y) + '\n'
        self.fd.write(line)
###############################################################################
if __name__ == '__main__':
    if len(sys.argv) == 2:
        numberOfFakeCheckpoints = int(raw_input('How many FakeCheckpoints do you want?'))
        FakeCheckpoints(sys.argv[1]).createFakeCheckpoints(numberOfFakeCheckpoints)
    else:
        sys.exit('Too few arguments. Should be 2. Given: %s' % len(sys.argv))
