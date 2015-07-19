"""class creates fake checkpoint form fingerprint map to check location alg."""

from pymongo import MongoClient

import time
import sys
import random

class FakeCheckpoints(object):

    def __init__(self, collName):
        self.collName = collName

        self.conn = MongoClient()
        db_fingerprint = self.conn['fingerprint']
        db_locate = self.conn['locate']
        self.coll_fingerprint = db_fingerprint[self.collname]
        self.coll_locate = db_locate['locate_fake_checkpoints_' + self.collName]

        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.x_max = max(self.x_distinct)
        self.y_max = max(self.y_distinct)
        self.x_min = min(self.x_distinct)
        self.y_min = min(self.y_distinct)

    def __del__(self):
        self.conn.close()

###############################################################################
    def createFakeCheckpoints(self, numberOfFakeCheckpoints):
        random_x = []
        random_y = []

        counter = 0
        while (True):
            x = random.randint(self.x_min,self.x_max)
            if not x in random_x:
                random_x.append(x)
                counter += 1
            if counter == numberOfFakeCheckpoints:
                break

        counter = 0
        while (True):
            y = random.randint(self.y_min,self.y_max)
            if not x in random_y:
                random_y.append(x)
                counter += 1
            if counter == numberOfFakeCheckpoints:
                break

        for x in random_x:
            for y in random_y:
                cursor = self.coll_fingerpritn({'X': x, 'Y': y})
###############################################################################

if __name__ == '__main__':
    if len(sys.argv) == 3:
        numberOfFakeCheckpoints = int(raw_input('How many FakeCheckpoints do you want?'))
        FakeCheckpoints(sys.argv[1]).createFakeCheckpoints(numberOfFakeCheckpoints)
    else:
        sys.exit('Too few arguments. Shold be 3. Given: %s' % len(sys.argv))
