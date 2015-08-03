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
        self.map = ['MAGNETIC', 'RSSI']
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

        self.countWhenSumErrorTheSmallest()
        self.countDataStatisticsError()

    """method counts max. min. mode, mean of error per data statisitcs"""
    def countDataStatisticsError(self):

        resultAlgorithmDocs = {}
        self.loadDataResult(resultAlgorithmDocs)

        errorDictonary = {}
        self.preapreErrorDictonaryStatistics(errorDictonary)

        self.gainXAndYErrorStatistics(resultAlgorithmDocs,errorDictonary)

        resultStatistic = {}
        resultStatistic['MAGNETIC'] = {}
        resultStatistic['RSSI'] = {}
        self.countErrorStatistics(errorDictonary,resultStatistic)

        fileList = []
        self.prepareLinesForCsvFileStatistics(resultStatistic, fileList)

        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        fileName = self.collname + '_DATA_STATISTICS_' + date
        self.writeToCsvFile(fileName, fileList)

    """method search all checkpoints and shows the best data statistic for
       localization - counting per document"""
    def countWhenSumErrorTheSmallest(self):
        resultAlgorithmDocs = {}
        self.loadDataResult(resultAlgorithmDocs)

        commonStatistics = {}
        self.preapreCounterErrorDictonary(commonStatistics)

        self.smallestErrorStatisticCounter(resultAlgorithmDocs, commonStatistics)

        fileList = []
        self.preapreLinesForCsvFileStatisticCounter(fileList, commonStatistics)
        for line in fileList:
            print line
            raw_input()
        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        firstLineFile = self.collname + '_DATA_STATISTICS_BEST_' + date
        self.writeToCsvFile(firstLineFile, fileList)

################################################################################
    """method loads data from result databse to count statistics"""
    def loadDataResult(self, docDict):
        """take all RSSI documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'RSSI'})
        docDict['RSSI'] = [res for res in cursor]

        """take all magnetic documents from all checkpoints"""
        cursor = self.coll.find({'FINGERPRINT_MAP': 'MAGNETIC'})
        docDict['MAGNETIC'] = [res for res in cursor]


    """method save dataStatistic to file"""
    def writeToCsvFile(self, fileName, tList):
        name = fileName + '_algorithms.csv'
        with open(name, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=' ', dialect='excel', quoting=csv.QUOTE_NONE, escapechar=' ')
            for row in tList:
                print row
            spamwriter.writerows(tList)
################################################################################
    """methods for statistic counter"""

    """preparing dictonary for counting the best statistic data"""
    def preapreCounterErrorDictonary(self,counterDict):
        counterDict['MAGNETIC'] = {}
        counterDict['RSSI'] = {}

        counterDict['MAGNETIC']['LISTS'] = {}
        counterDict['RSSI']['LISTS'] = {}

        """choosing the best data statistic for locating"""
        for map_name in self.map:
            for dataStatistics in self.STATISTIC_NAME:
                counterDict[map_name][dataStatistics] = 0
                counterDict[map_name]['LISTS'][dataStatistics] = []

    """choosing data statistic with the smallest error in each document """
    def smallestErrorStatisticCounter(self, resultAlgorithmDict, counterDict):
        for map_name in self.map:
            for doc in resultAlgorithmDict[map_name]:
                bestX = doc['RESULTS']['MEAN']['ERROR']['X']
                bestY = doc['RESULTS']['MEAN']['ERROR']['Y']
                errorSumBest = bestX + bestY
                anwser = 'MEAN'
                for dataStatistics in self.STATISTIC_NAME[1:]:
                    nextX = doc['RESULTS'][dataStatistics]['ERROR']['X']
                    nextY = doc['RESULTS'][dataStatistics]['ERROR']['Y']
                    errorSumNext = nextX + nextY
                    if errorSumBest > nextY:
                        anwser = dataStatistics
                        errorSumBest = errorSumNext
                counterDict[map_name][anwser] += 1
                counterDict[map_name]['LISTS'][anwser].append(doc)

    def preapreLinesForCsvFileStatisticCounter(self, tList, counterDict):
        for map_name in self.map:
            firstLineFile = [self.collname + '_' + map_name]
            tList.append(firstLineFile)
            for dataStatistics in self.STATISTIC_NAME:
                tmpRow = [dataStatistics.replace(' ',''),  str(counterDict[map_name][dataStatistics])]
                tList.append(tmpRow)
################################################################################
    """defenition methods which helps counting statistics of errors"""

    def prepareLinesForCsvFileStatistics(self, statisticDict, tList):
        for map_name in self.map:
            tList.append([map_name])
            for dataStatistics in self.STATISTIC_NAME:
                tList.append([dataStatistics.replace(' ','')])
                tList.append(['ERROR'])
                tList.append([' '])
                tList.append(['X'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION'])]
                tList.append(tmpRow)

                tList.append([' '])
                tList.append(['Y'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION'])]
                tList.append(tmpRow)

                tList.append([' '])
                tList.append(['ERROR_PERCENT'])
                tList.append([' '])
                tList.append(['X'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['STANDARD_DEVIATION'])]
                tList.append(tmpRow)

                tList.append([' '])
                tList.append(['Y'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION'])]

                tList.append([' '])
                tList.append(['ERROR_COORDINATE'])
                tList.append([' '])
                tList.append(['X'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['STANDARD_DEVIATION'])]
                tList.append(tmpRow)

                tList.append([' '])
                tList.append(['Y'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MAX'])]
                tList.append(tmpRow)
                tmpRow = ['MEAN', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODE', str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['STANDARD_DEVIATION', str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION'])]
                tList.append(tmpRow)

    """method count max.min,mode, mean, standart deviation for magnetic rssi map
       for each cooridinate and each statistics"""
    def countErrorStatistics(self,errorStatisticDic, resultDic):

        for map_name in self.map:
            for dataStatistics in self.STATISTIC_NAME:
                resultDic[map_name][dataStatistics] = {}
                """ERROR"""
                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultDic[map_name][dataStatistics]['ERROR'] = tmp

                """ERROR_PERCENT"""
                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR_PERCENT']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR_PERCENT']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultDic[map_name][dataStatistics]['ERROR_PERCENT'] = tmp

                """ERROR_COORDINATE"""
                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR_COORDINATE']['X']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp = {}
                tmp['X'] = tmpDic

                tmpDic = {}
                data = errorStatisticDic[map_name][dataStatistics]['ERROR_COORDINATE']['Y']
                tmpDic['MIN'] = min(data)
                tmpDic['MAX'] = max(data)
                tmpList = list(scipy.stats.mode(data))
                tmpDic['MODE'] = tmpList[0].tolist()[0]
                tmpDic['MEAN'] = np.mean(data)
                tmpDic['STANDARD_DEVIATION'] = np.std(data)

                tmp['Y'] = tmpDic
                resultDic[map_name][dataStatistics]['ERROR_COORDINATE'] = tmp

    """gain x and y error"""
    def gainXAndYErrorStatistics(self, resultAlgorithmDict, errorDictonary):

        for map_name in self.map:
            for doc in resultAlgorithmDict[map_name]:
                for dataStatistics in self.STATISTIC_NAME:
                    tmpX = doc['RESULTS'][dataStatistics]['ERROR']['X']
                    tmpY = doc['RESULTS'][dataStatistics]['ERROR']['Y']
                    errorDictonary[map_name][dataStatistics]['ERROR']['X'].append(tmpX)
                    errorDictonary[map_name][dataStatistics]['ERROR']['Y'].append(tmpY)

                    tmpX = doc['RESULTS'][dataStatistics]['ERROR_PERCENT']['X']
                    tmpY = doc['RESULTS'][dataStatistics]['ERROR_PERCENT']['Y']
                    errorDictonary[map_name][dataStatistics]['ERROR_PERCENT']['X'].append(tmpX)
                    errorDictonary[map_name][dataStatistics]['ERROR_PERCENT']['Y'].append(tmpY)

                    tmpX = doc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['X']
                    tmpY = doc['RESULTS'][dataStatistics]['ERROR_COORDINATE']['Y']
                    errorDictonary[map_name][dataStatistics]['ERROR_COORDINATE']['X'].append(tmpX)
                    errorDictonary[map_name][dataStatistics]['ERROR_COORDINATE']['Y'].append(tmpY)

    """method preapres dictonry for getting all errors"""
    def preapreErrorDictonaryStatistics(self, errorDic):

        errorDic['MAGNETIC'] = {}
        errorDic['RSSI'] = {}

        for map_name in self.map:

            for dataStatistics in self.STATISTIC_NAME:

                errorDic[map_name][dataStatistics] = {}
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
                errorDic[map_name][dataStatistics] = tmpDic
################################################################################
    """method which helps in analyze of statistics from error"""

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
