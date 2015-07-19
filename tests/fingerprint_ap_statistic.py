"""class which shwos statistics for whole map"""

import time
from pymongo import MongoClient
import sys

import scipy.stats
import numpy as np

from math import floor

class FingerprintStatistics(object):

    def __init__(self,collName):
        self.collname = collName

        self.STATISTIC_CHOOSE = ["MEAN", "STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]

        self.conn = MongoClient()
        self.db = self.conn['fingerprint']
        self.coll = self.db[self.collname]

        self.mac_distinct = self.coll.distinct('MAC_AP')
        self.x_distinct = self.coll.distinct('X')
        self.y_distinct = self.coll.distinct('Y')
        self.allFingeprintPoints = len(self.x_distinct) * len(self.y_distinct)

    def accespointStatistics(self, chooseAp):
        cursor = self.coll.find({'MAC_AP' : self.mac_distinct[chooseAp]})
        docs = [res for res in cursor]
        anws =  int(raw_input('Count statistic on map by: %s' % str(self.STATISTIC_CHOOSE)))

        statisticList = []
        for doc in docs:
            statisticList.append(doc['STATISTICS'][self.STATISTIC_CHOOSE[anws]])

        statisticDic = self.countStatistics(statisticList)

        statisticDic['MAC_AP'] = self.mac_distinct[chooseAp]

        print 'RSSI statistics for ap: .'+ self.mac_distinct[chooseAp] + ' Number of points in fingerprint map: ' + str(self.allFingeprintPoints)
        for key, value in statisticDic.items():
            print key + ' - ' + str(value)
        print 'ALL values of AP on fingerprint map:'
        print str(statisticList)
        print 'coverage of ap on fingerprint map in %: ' + str(float(len(docs))/self.allFingeprintPoints * 100)
        print 'number of accurance mean on fingerprint map in %: ' + str(statisticList.count(floor(statisticDic['MEAN']))/float(self.allFingeprintPoints) * 100)
        print 'number of accurance mediana on fingerprint map in %: ' + str(statisticList.count(statisticDic['MEDIANA'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance max on fingerprint map in %: ' + str(statisticList.count(statisticDic['MAX'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance min on fingerprint map in %: ' + str(statisticList.count(statisticDic['MIN'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance mode on fingerprint map in %: ' + str(statisticDic['MODE_ACCURANCE']/self.allFingeprintPoints * 100)

    def magneticStatistics(self):
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}})
        docs = [res for res in cursor]
        anws =  int(raw_input('Count statistic on map by: %s' % str(self.STATISTIC_CHOOSE)))

        statisticList = []
        for doc in docs:
            statisticList.append(doc['STATISTICS_NORM'][self.STATISTIC_CHOOSE[anws]])

        statisticDic = self.countStatistics(statisticList)

        print 'MAGNETIC STATISTICS. Number of points in fingerprint map: ' + str(self.allFingeprintPoints)
        for key, value in statisticDic.items():
            print key + ' - ' + str(value)
        print 'ALL values of AP on fingerprint map:'
        print str(statisticList)
        print 'coverage of magnrtic field on fingerprint map in %: ' + str(float(len(docs))/self.allFingeprintPoints * 100)
        print 'number of accurance mean on fingerprint map in %: ' + str(statisticList.count(statisticDic['MEAN'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance mediana on fingerprint map in %: ' + str(statisticList.count(statisticDic['MEDIANA'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance max on fingerprint map in %: ' + str(statisticList.count(statisticDic['MAX'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance min on fingerprint map in %: ' + str(statisticList.count(statisticDic['MIN'])/float(self.allFingeprintPoints) * 100)
        print 'number of accurance mode on fingerprint map in %: ' + str(statisticDic['MODE_ACCURANCE']/self.allFingeprintPoints * 100)
###############################################################################
    def countStatistics(self,tList):
        meanV = np.mean(tList)
        standardDeviation = np.std(tList)
        maxV = max(tList)
        minV = min(tList)
        medianaV = np.median(tList)
        tmp = list(scipy.stats.mode(tList))
        print tmp
        modeV = tmp[0].tolist()[0]
        modeAccurance = tmp[1].tolist()[0]

        return {"MEAN": meanV, "STANDARD_DEVIATION": standardDeviation, "MAX": maxV, "MIN": minV , "MEDIANA": medianaV, "MODE": modeV, 'MODE_ACCURANCE': modeAccurance}
###############################################################################
    def menu(self):
        msg = '''
        q - quit
        0 - showStatistics for certain AP
        1 - show statistics for magnetic filed '''

        while(True):
            time.sleep(1)
            anws = raw_input(msg)

            if anws == 'q':
                break
            elif anws == '0':
                anws = int(raw_input('Avaiable AP: %s Choose AP(0,%s)' % (str(self.mac_distinct),len(self.mac_distinct) - 1)))
                self.accespointStatistics(anws)
            elif anws == '1':
                self.magneticStatistics()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        FingerprintStatistics(sys.argv[1]).menu()
    else:
        sys.exit('Too few arguments. Shoudle be 2. Given: %s' % len(sys.argv))
