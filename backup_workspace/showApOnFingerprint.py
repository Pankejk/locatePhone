import numpy as np
import matplotlib.pyplot as plt
import time
from pymongo import MongoClient
import sys

class Draw(object):

    def __init__(self,collName):
        self.collname = collName
        self.conn = MongoClient()
        self.db = self.conn['fingerprint']
        self.coll = self.db[self.collname]
        self.distinctAp = self.coll.distinct('MAC_AP')
        self.distinctX = self.coll.distinct('X')
        self.distinctY = self.coll.distinct('Y')

    def drawAp(self, chooseAp):
        print 'AP: ' + self.distinctAp[chooseAp]
        cursor = self.coll.find({'MAC_AP' : self.distinctAp[chooseAp]})
        docs = [res for res in cursor]
        for y in self.distinctY:
            for x in self.distinctX:
                for doc in docs:
                    if doc['X'] == x and doc['Y'] == y:
                        print 'X: ' + str(x) + ' Y: ' + str(y) + ' - ' + str(doc['STATISTICS']['MEAN'])

    def drawMagnetic(self):
        print 'MAGNETIC FINGERPRINT'
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists' : True}})
        docs = [res for res in cursor]
        print len(docs)
        for y in self.distinctY:
            for x in self.distinctX:
                for doc in docs:
                    if doc['X'] == x and doc['Y'] == y:
                        print 'X: ' + str(x) + ' Y: ' + str(y) + ' - ' + str(doc['STATISTICS_NORM']['MEAN'])



def main():
    if len(sys.argv) != 2:
        sys.exit('Too small arguments! You gave: %s' % len(sys.argv))
    draw = Draw(sys.argv[1])
    msg = 'Options:\n q- exit\n 0- show RSSI AP on coordiantes\n 1- show magnetic field on coordiantes\n'
    while(True):
        time.sleep(1)
        print msg
        anw = raw_input()
        if anw == 'q':
            break
        elif anw == '0':
            size = len(draw.distinctAp) -1
            ap = raw_input('Choose ap from 0 to %s - ' % size )
            ap = int(ap)
            draw.drawAp(ap)
        elif anw == '1':
            draw.drawMagnetic()


if __name__ == '__main__':
    main()
