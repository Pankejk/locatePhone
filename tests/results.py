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
            if doc['FINGERPRINT_MAP'] == 'RSSI':
                print 'RSSI_MAP'
                print doc['RESULTS'][self.STATISTIC_NAME[sd]]
            elif doc['FINGERPRINT_MAP'] == 'MAGNETIC':
                print 'MAGNETIC_MAP'
                print doc['RESULTS'][self.STATISTIC_NAME[sd]]
    def showLocationErrorAllPoints(self):
        while(True):
            choose = raw_input('Magnetic map(0) or RSSI map(1) or quit(q)?')
            if choose == 'q':
                break
            dataStatistic = int(raw_input('All statistic - %s\n choose from 0 - %s' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))
            checkpointRange = raw_input('All checkpoints - %s\n choose 0-%s' % (str(self.distinctCp), len(self.distinctCp) - 1))
            checkpointRange = checkpointRange.split(' ')
            start = int(checkpointRange[0])
            stop = int(checkpointRange[1])
            drawDict = {'NAME': [],'X': [], 'Y': [], 'X_ERROR': [], 'Y_ERROR': []}

            if choose == '0':
                for checkpoint in self.distinctCp[start:stop]:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'MAGNETIC'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['X'].append(tmpDic['X'])
                        drawDict['Y'].append(tmpDic['Y'])
                        drawDict['X_ERROR'].append(tmpDic['ERROR']['X'])
                        drawDict['Y_ERROR'].append(tmpDic['ERROR']['Y'])
                        drawDict['NAME'].append(checkpoint)
            elif choose == '1':
                for checkpoint in self.distinctCp[start:stop]:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'RSSI'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['X'].append(tmpDic['X'])
                        drawDict['Y'].append(tmpDic['Y'])
                        drawDict['X_ERROR'].append(tmpDic['ERROR']['X'])
                        drawDict['Y_ERROR'].append(tmpDic['ERROR']['Y'])
                        drawDict['NAME'].append(checkpoint)
            fig, ax = plt.subplots()
            anws = raw_input('Do you want errors on: only x(0), only y (1), z and y (2)')
            if anws == '0':
                ax.errorbar(drawDict['X'], drawDict['Y'], xerr=drawDict['X_ERROR'], fmt='o')
            elif anws == '1':
                ax.errorbar(drawDict['X'], drawDict['Y'], yerr = drawDict['Y_ERROR'], fmt='o')
            elif anws == '2':
                ax.errorbar(drawDict['X'], drawDict['Y'], xerr=drawDict['X_ERROR'], yerr = drawDict['Y_ERROR'], fmt='o')
            for i in range(len(drawDict['X'])):
                print drawDict['NAME'][i]
                tmplist = [drawDict['X'][i],drawDict['Y'][i]]
                tmpTuple = tuple(tmplist)
                plt.annotate(drawDict['NAME'][i],xy=tmpTuple)
            plt.show()






def main():
    if len(sys.argv) != 2:
        sys.exit('Too small arguments! You gave: %s' % len(sys.argv))
    results = Results(sys.argv[1])
    msg = '''
    q- exit
    0- show single checkpoint
    1 - show checkpoints localization error for certain data statistic'''
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
        elif anw == '1':
            results.showLocationErrorAllPoints()


if __name__ == '__main__':
    main()
