import numpy as np
import matplotlib.pyplot as plt
import time
from pymongo import MongoClient
import sys

import csv
from datetime import datetime

import scipy.stats

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
            if choose == '0':
                plt.title('RSSI')
            elif choose == '1':
                plt.title('MAGNETIC')
            plt.xlabel('width [m]')
            plt.ylabel('height [m]')
            plt.show()

    def countAlgorithmStatisticsError(self):

        self.countWhenDataStatisticIfTheBest()
        self.countDataStatisticsError()

    """method counts max. min. mode, mean of error per data statisitcs"""
    def countDataStatisticsError(self):
        """take all RSSI documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'RSSI'})
        rssiDocs = [res for res in cursor]

        """take all magnetic documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'MAGNETIC'})
        magneticDocs = [res for res in cursor]

        """counting the max,mean, mode, min error for data statistic"""
        commonStatistics = {}
        commonStatistics['MAGNETIC'] = {}
        commonStatistics['RSSI'] = {}

        for dataStatistics in self.STATISTIC_NAME:
            commonStatistics['RSSI'][dataStatistics] = {}
            tmpDic = {}
            tmpDic['ERROR'] = []
            tmpDic['ERROR_PERCENT'] = []
            tmpDic['ERROR_COORDINATE'] = []
            commonStatistics['RSSI'][dataStatistics] = tmpDic

            commonStatistics['MAGNETIC'][dataStatistics] = {}
            tmpDic = {}
            tmpC = {}
            tmpC['X'] = []
            tmpC['Y'] = []
            tmpDic['ERROR'] = tmpC

            tmpC = {}
            tmpC['X'] = []
            tmpC['Y'] = []
            tmpDic['ERROR_PERCENT'] = tmpC

            tmpC = {}
            tmpC['X'] = []
            tmpC['Y'] = []
            tmpDic['ERROR_COORDINATE'] = tmpC
            commonStatistics['MAGNETIC'][dataStatistics] = tmpDic

        for magneticDoc in magneticDocs:
            for dataStatistics in self.STATISTIC_NAME:
                tmpX = magneticDoc['RESULTS'][dataStatistics]['ERROR']['X']
                tmpY = magneticDoc['RESULTS'][dataStatistics]['ERROR']['Y']
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR']['X'].append(tmpX)
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR']['Y'].append(tmpY)

                tmpX = magneticDoc['RESULTS'][dataStatistics]['ERROR_PERCENT']['X']
                tmpY = magneticDoc['RESULTS'][dataStatistics]['ERROR_PERCENT']['Y']
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X'].append(tmpX)
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y'].append(tmpY)

                tmpX = magneticDoc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['X']
                tmpY = magneticDoc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['Y']
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X'].append(tmpX)
                commonStatistics['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y'].append(tmpY)

        for rssiDoc in rssiDocs:
            for dataStatistics in self.STATISTIC_NAME:
                tmpX = rssiDoc['RESULTS'][dataStatistics]['ERROR']['X']
                tmpY = rssiDoc['RESULTS'][dataStatistics]['ERROR']['Y']
                commonStatistics['RSSI'][dataStatistics]['ERROR']['X'].append(tmpX)
                commonStatistics['RSSI'][dataStatistics]['ERROR']['Y'].append(tmpY)

                tmpX = magneticDoc['RESULTS'][dataStatistics]['ERROR_PERCENT']['X']
                tmpY = magneticDoc['RESULTS'][dataStatistics]['ERROR_PERCENT']['Y']
                commonStatistics['RSSI'][dataStatistics]['ERROR_PERCENT']['X'].append(tmpX)
                commonStatistics['RSSI'][dataStatistics]['ERROR_PERCENT']['Y'].append(tmpY)

                tmpDic['X'] = magneticDoc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['X']
                tmpDic['Y'] = magneticDoc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['Y']
                commonStatistics['RSSI'][dataStatistics]['ERROR_COORDINATE']['X'].append(tmpX)
                commonStatistics['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y'].append(tmpY)

        resultStatistic = {}
        resultStatistic['MAGNETIC'] = {}
        resultStatistic['RSSI'] = {}
        for dataStatistics in self.STATISTIC_NAME:
                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultStatistic['MAGNETIC'][dataStatistics] = {}
                resultStatistic['MAGNETIC'][dataStatistics]['ERROR'] = tmp

                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultStatistic['MAGNETIC'][dataStatistics] = {}
                resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT'] = tmp

                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultStatistic['MAGNETIC'][dataStatistics] = {}
                resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE'] = tmp
                ################################################################

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic

                resultStatistic['RSSI'][dataStatistics] = {}
                resultStatistic['RSSI'][dataStatistics]['ERROR'] = tmp

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR_PERCENT']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic

                resultStatistic['RSSI'][dataStatistics] = {}
                resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT'] = tmp

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = commonStatistics['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmp = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmp[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic

                resultStatistic['RSSI'][dataStatistics] = {}
                resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE'] = tmp

        fileList = []
        firstLineFile = self.collname + '_MAGNETIC_DATA_STATISTICS_' + str(datetime.now()).replace(' ','_')
        fileList.append(firstLineFile)
        for dataStatistics in self.STATISTIC_NAME:
            fileList.append(dataStatistics)
            fileList.append('ERROR')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('ERROR_PERCENT')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('ERROR_COORDINATE')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_COORDINATE']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['MAGNETIC'][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION'])

        firstLineFile = self.collname + '_RSSI_DATA_STATISTICS_' + str(datetime.now()).replace(' ','_')
        fileList.append(firstLineFile)
        for dataStatistics in self.STATISTIC_NAME:
            fileList.append(dataStatistics)
            fileList.append('ERROR')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR']['Y']['STANDARD_DEVIATION'])

            fileList.append('ERROR_PERCENT')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION'])

            fileList.append('ERROR_COORDINATE')
            fileList.append('')
            fileList.append('X')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['X']['STANDARD_DEVIATION'])

            fileList.append('')
            fileList.append('Y')
            tmpRow = 'MIN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']['MIN'])
            tmpRow = 'MAX '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']['MAX'])
            tmpRow = 'MEAN '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']['MEAN'])
            tmpRow = 'MODE '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']['MODE'])
            tmpRow = 'STANDARD_DEVIATION '+ ' - ' + str(resultStatistic['RSSI'][dataStatistics]['ERROR_COORDINATE']['Y']['STANDARD_DEVIATION'])

        firstLineFile = self.collname + '_DATA_STATISTICS' + str(datetime.now()).replace(' ','_')
        self.writeToCsvFile(firstLineFile, fileList)

    """method search all checkpoints and shows the best data statistic for
       localization"""
    def countWhenDataStatisticIfTheBest(self):
        """take all RSSI documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'RSSI'})
        rssiDocs = [res for res in cursor]

        """take all magnetic documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'MAGNETIC'})
        magneticDocs = [res for res in cursor]

        commonStatistics = {}
        commonStatistics['MAGNETIC'] = {}
        commonStatistics['RSSI'] = {}

        commonStatistics['MAGNETIC']['LISTS'] = {}
        commonStatistics['RSSI']['LISTS'] = {}

        """choosing the best data statistic for locating"""
        for dataStatistics in self.STATISTIC_NAME:
            commonStatistics['MAGNETIC'][dataStatistics] = 0
            tmpDict = dict()
            tmpDict[dataStatistics] = list()
            commonStatistics['MAGNETIC']['LISTS'] = tmpDict

            commonStatistics['RSSI'][dataStatistics] = 0
            tmpDict = dict()
            tmpDict[dataStatistics] = list()
            commonStatistics['RSSI']['LISTS'] = tmpDict

        for magneticDoc in magneticDocs:
            bestX = magneticDoc['RESULTS']['MEAN']['ERROR']['X']
            bestY = magneticDoc['RESULTS']['MEAN']['ERROR']['Y']
            errorSumBest = bestX + bestY
            anwser = 'MEAN'
            for dataStatistics in self.STATISTIC_NAME[1:]:
                nextX = magneticDoc['RESULTS'][dataStatistics]['ERROR']['X']
                nextY = magneticDoc['RESULTS'][dataStatistics]['ERROR']['Y']
                errorSumNext = nextX + nextY
                if errorSumBest > nextY:
                    anwser = dataStatistics
            commonStatistics['MAGNETIC'][anwser] += 1
            commonStatistics['MAGNETIC']['LISTS'][anwser].append(magneticDoc)

        for rssiDoc in rssiDocs:
            bestX = rssiDoc['RESULTS']['MEAN']['ERROR']['X']
            bestY = rssiDoc['RESULTS']['MEAN']['ERROR']['Y']
            errorSumBest = bestX + bestY
            anwser = 'MEAN'
            for dataStatistics in self.STATISTIC_NAME[1:]:
                nextX = rssiDoc['RESULTS'][dataStatistics]['ERROR']['X']
                nextY = rssiDoc['RESULTS'][dataStatistics]['ERROR']['Y']
                errorSumNext = nextX + nextY
                if errorSumBest > nextY:
                    anwser = dataStatistics
            commonStatistics['RSSI'][anwser] += 1
            commonStatistics['RSSI']['LISTS'][anwser].append(magneticDoc)

        fileList = []
        firstLineFile = self.collname + '_RSSI_DATA_STATISTICS_' + str(datetime.now()).replace(' ','_')
        fileList.append(firstLineFile)
        for dataStatistics in self.STATISTIC_NAME:
            tmpRow = dataStatistics + ' - ' + str(commonStatistics['RSSI'][dataStatistics])
            fileList.append(tmpRow)

        firstLineFile = self.collname + '_MAGNETIC_DATA_STATISTICS_' + str(datetime.now()).replace(' ','_')
        fileList.append('')
        fileList.append(firstLineFile)
        for dataStatistics in self.STATISTIC_NAME:
            tmpRow = dataStatistics + ' - ' + str(commonStatistics['MAGNETIC'][dataStatistics])
            fileList.append(tmpRow)

        firstLineFile = self.collname + '_DATA_STATISTICS_BEST' + str(datetime.now()).replace(' ','_')
        self.writeToCsvFile(firstLineFile, fileList)

    def writeToCsvFile(self, fileName, tList):
        name = fileName + '_algorithms.csv'
        with open(name, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ')
            for row in tList:
                spamwriter.writerow(row)
def main():
    if len(sys.argv) != 2:
        sys.exit('Too small arguments! You gave: %s' % len(sys.argv))
    results = Results(sys.argv[1])
    msg = '''
    q - exit
    0 - show single checkpoint
    1 - show checkpoints localization error for certain data statistic
    2 - count data statistic error'''
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
        elif anw == '2':
            results.countAlgorithmStatisticsError()


if __name__ == '__main__':
    main()
