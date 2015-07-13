import numpy as np
import matplotlib.pyplot as plt
import time
from pymongo import MongoClient
import sys

class Results(object):

    def __init__(self,collName):
        self.collname = collName
        self.conn = MongoClient()
        self.db = self.conn['result']
        self.coll = self.db[self.collname]
        self.distinctCp = self.coll.distinct('CHECKPOINT')
        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]

    def showSinglePoint(self, chooseAp, sd):
        cursor = self.coll.find({'CHECKPOINT' : chooseAp})
        docs = [res for res in cursor]
        for doc in docs:
            print doc['RESULT'][self.STATISTIC_NAME[sd]]
            #for key , value in doc.items():
            #    print key + ' ' + str(value)



def main():
    if len(sys.argv) != 2:
        sys.exit('Too small arguments! You gave: %s' % len(sys.argv))
    results = Results(sys.argv[1])
    msg = 'Options:\n q- exit\n 0- show single checkpoint\n'
    while(True):
        time.sleep(1)
        print msg
        anw = raw_input()
        if anw == 'q':
            break
        elif anw == '0':
            ap = raw_input('Choose checkpoint - %s - ' % str(results.distinctCp))
            sd = int(raw_input('Choose statistic data(0-9) - %s - ' % str(results.STATISTIC_NAME)))
            results.showSinglePoint(ap,sd)


if __name__ == '__main__':
    main()
