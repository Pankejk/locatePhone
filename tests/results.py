# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import time
from pymongo import MongoClient
import sys

import csv
from datetime import datetime
import math

import scipy.stats

class Results(object):

    def __init__(self,collName, collFingerprintName, fileName):
        self.collname = collName
        self.collFingerprintName = collFingerprintName
        self.fileName = fileName

        self.conn = MongoClient()
        self.db = self.conn['result']
        self.db_fingerprint = self.conn['fingerprint']
        self.db_result_statistics = self.conn['result_statistics']
        self.coll = self.db[self.collname]
        self.coll_fingerprint = self.db_fingerprint[self.collFingerprintName]

        self.distinctCp = self.coll.distinct('CHECKPOINT')
        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.x_distinct.sort()
        self.y_distinct.sort()
        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.ERROR_STATISTICS = ['MAX','MIN', 'MEAN', 'MODE']
        self.map = ['MAGNETIC', 'RSSI']
        self.mac_ap_distinct = self.coll_fingerprint.distinct('MAC_AP')
        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.x_distinct.sort()
        self.y_distinct.sort()
        self.y_sample_stat = [0,20,40,60,80,100]

        self.checkPoints = {}

        self.loadCheckPoints()

    def __del__(self):
        self.conn.close()
###############################################################################
    """methods for menu"""

    """method shows localization and localizztion error"""
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

    """method shows localization of checkpoint and error on chart"""
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
                print drawDict['X']
                print drawDict['Y']
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
                print drawDict['X']
                print drawDict['Y']
            fig, ax = plt.subplots()
            anws = raw_input('Do you want errors on: only x(0), only y (1), x and y (2)')
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
            if choose == '1':
                plt.title('RSSI')
            elif choose == '0':
                plt.title('MAGNETIC')
            plt.xlim(0,max(self.x_distinct))
            plt.ylim(0,max(self.y_distinct))
            plt.xlabel('width [m]')
            plt.ylabel('length [m]')
            plt.show()

    """method show checkpoint located by algorithm and chosen points"""
    def showLocatedCheckpointAndPoints(self):
        while(True):
            anws = raw_input('quit(q)?')
            if anws == 'q':
                break
            checkpoint = raw_input('%s\nchoose checkpoint(0-%s): ' % (str(self.distinctCp),(len(self.distinctCp) - 1)))
            chosenStatistic = int(raw_input('%s\nchoose data statistic(0-%s): ' %(str(self.STATISTIC_NAME),(len(self.STATISTIC_NAME) - 1))))
            chosenStatistic = self.STATISTIC_NAME[chosenStatistic]
            anws = raw_input('magnetic(0) or rssi (1) or quit(q)')
            if anws == 'q':
                break
            cursor = None
            if anws == '0':
                cursor = self.coll.find({'CHECKPOINT': checkpoint, 'FINGERPRINT_MAP': 'MAGNETIC'})
            elif anws == '1':
                cursor = self.coll.find({'CHECKPOINT': checkpoint, 'FINGERPRINT_MAP': 'RSSI'})

            tmp = [res for res in cursor]
            doc = tmp[0]
            resultDict = doc['RESULTS'][chosenStatistic]
            chosenPoints = doc['CHOSEN_POINTS'][chosenStatistic]

            xList = []
            yList = []

            for item in chosenPoints:
                xList.append(item['X_FINGERPRINT'])
                yList.append(item['Y_FINGERPRINT'])
            xList.append(resultDict['X'])
            yList.append(resultDict['Y'])

            self.showCheckpointOnMap(xList,yList,checkpoint, anws)

    """method counts statistic of errors and effectiveness of use data statistic"""
    def countAlgorithmStatisticsError(self):
        self.countWhenSumErrorTheSmallest()
        self.countWhenCoordinatesErrorTheSmallest()
        self.countDataStatisticsError()
        print 'DATA SAVED TO CSV FILE'
        
    """method shows the best data statistc for localization"""
    def showTheSmallestErrorForCoordinates(self):

        cursor = self.db_result_statistics[self.collname].find({'DOCUMENT_TYPE': 'COUNTER_STATISTICS_COORDINATES'})
        tmp = [res for res in cursor]
        statisticCounterDoc = tmp[0]

        bestStatistic = {}
        bestStatistic['RSSI'] = {}
        bestStatistic['MAGNETIC'] = {}

        for map_name in self.map:
            tmpDic = {}
            tmpDic['VALUE'] = 0
            tmpDic['DATA_STATISTICS'] = ''
            bestStatistic[map_name]['X'] = tmpDic
            tmpDic = {}
            tmpDic['VALUE'] = 0
            tmpDic['DATA_STATISTICS'] = ''
            bestStatistic[map_name]['Y'] = tmpDic
            bestStatistic[map_name]['X']['DATA_STATISTICS'] = 'MAX'
            bestStatistic[map_name]['X']['VALUE'] = statisticCounterDoc[map_name]['X']['MAX']
            bestStatistic[map_name]['Y']['DATA_STATISTICS'] = 'MAX'
            bestStatistic[map_name]['Y']['VALUE'] = statisticCounterDoc[map_name]['Y']['MAX']

        for map_name in self.map:
            for dataStatistic in self.ERROR_STATISTICS[1:]:
                if bestStatistic[map_name]['X']['VALUE'] < statisticCounterDoc[map_name]['X'][dataStatistic]:
                    bestStatistic[map_name]['X']['VALUE'] = statisticCounterDoc[map_name]['X'][dataStatistic]
                    bestStatistic[map_name]['X']['DATA_STATISTICS'] = dataStatistic

                if bestStatistic[map_name]['Y']['VALUE'] < statisticCounterDoc[map_name]['Y'][dataStatistic]:
                    bestStatistic[map_name]['Y']['VALUE'] = statisticCounterDoc[map_name]['Y'][dataStatistic]
                    bestStatistic[map_name]['Y']['DATA_STATISTICS'] = dataStatistic

        cursor = self.db_result_statistics[self.collname].find({'DOCUMENT_TYPE': 'ERROR_STATISTICS'})
        tmp = [res for res in cursor]
        statisticsErrorDoc = tmp[0]

        statisticsMagneticX = bestStatistic['MAGNETIC']['X']['DATA_STATISTICS']
        statisticsMagneticY = bestStatistic['MAGNETIC']['Y']['DATA_STATISTICS']
        statisticsRssiX = bestStatistic['RSSI']['X']['DATA_STATISTICS']
        statisticsRssiY = bestStatistic['RSSI']['Y']['DATA_STATISTICS']
        statisticsErrorDoc['MAGNETIC'][statisticsMagneticX]
        statisticsErrorDoc['MAGNETIC'][statisticsMagneticY]
        statisticsErrorDoc['RSSI'][statisticsRssiX]
        statisticsErrorDoc['RSSI'][statisticsRssiY]

        tDic = {}
        tmpDic = {}
        tmpDic['X'] = statisticsErrorDoc['MAGNETIC'][statisticsMagneticX]
        tmpDic['Y'] = statisticsErrorDoc['MAGNETIC'][statisticsMagneticY]
        tDic['MAGNETIC'] = tmpDic
        tmpDic = {}
        tmpDic['X'] = statisticsErrorDoc['RSSI'][statisticsRssiX]
        tmpDic['Y'] = statisticsErrorDoc['RSSI'][statisticsRssiY]
        tDic['RSSI'] = tmpDic

        anwserDic = {}
        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        anwserDic['MAGNETIC'] = tmpDic
        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        anwserDic['RSSI'] = tmpDic

        for map_name in self.map:
            errorX = tDic[map_name]['X']['ERROR']['X']
            errorY = tDic[map_name]['Y']['ERROR']['Y']
            errorPercentX = tDic[map_name]['X']['ERROR_PERCENT']['X']
            errorPercentY = tDic[map_name]['Y']['ERROR_PERCENT']['Y']
            errorCoordinateX = tDic[map_name]['X']['ERROR_COORDINATE']['X']
            errorCoordinateY = tDic[map_name]['Y']['ERROR_COORDINATE']['Y']

            tmpErrorDicX = {}
            tmpErrorDicY = {}

            tmpErrorDicX['ERROR'] = errorX
            tmpErrorDicX['ERROR_PERCENT'] = errorPercentX
            tmpErrorDicX['ERROR_COORDINATE'] = errorCoordinateX

            tmpErrorDicY['ERROR'] = errorY
            tmpErrorDicY['ERROR_PERCENT'] = errorPercentY
            tmpErrorDicY['ERROR_COORDINATE'] = errorCoordinateY

            anwserDic[map_name]['X'] = tmpErrorDicX
            anwserDic[map_name]['Y'] = tmpErrorDicY

        for map_name in self.map:
            print map_name
            if map_name == 'MAGNETIC':
                print 'STATISTIC DATA X: ' + statisticsMagneticX
                print anwserDic[map_name]['X']
                print 'STATISTIC DATA Y: ' + statisticsMagneticY
                print anwserDic[map_name]['Y']
            elif map_name == 'RSSI':
                print 'STATISTIC DATA X: ' + statisticsRssiX
                print anwserDic[map_name]['X']
                print 'STATISTIC DATA Y: ' + statisticsRssiY
                print anwserDic[map_name]['Y']

    """method for certain data statistc shows error for x and y separetly"""
    def showErrorForCoordinatesFoStatistics(self):
        cursor = self.db_result_statistics[self.collname].find({'DOCUMENT_TYPE': 'ERROR_STATISTICS'})
        tmp = [res for res in cursor]
        statisticsErrorDoc = tmp[0]

        anws  = int(raw_input('%s\n Choose data statistic(0-%s)' % (str(self.STATISTIC_NAME), (len(self.STATISTIC_NAME) - 1))))

        errorDataMagnetic = statisticsErrorDoc['MAGNETIC'][self.STATISTIC_NAME[anws]]
        errorDataRssi = statisticsErrorDoc['RSSI'][self.STATISTIC_NAME[anws]]

        print self.STATISTIC_NAME[anws]
        print 'MAGNETIC'
        print 'X - ERROR'
        print errorDataMagnetic['ERROR']['X']
        print 'Y - ERROR'
        print errorDataMagnetic['ERROR']['Y']

        print 'X - ERROR_PERCENT'
        print errorDataMagnetic['ERROR_PERCENT']['X']
        print 'Y - ERROR_PERCENT'
        print errorDataMagnetic['ERROR_PERCENT']['Y']

        print 'X - ERROR_STATISTICS'
        print errorDataMagnetic['ERROR_COORDINATE']['X']
        print 'Y - ERROR_STATISTICS'
        print errorDataMagnetic['ERROR_COORDINATE']['Y']

        print 'RSSI'
        print 'X - ERROR'
        print errorDataRssi['ERROR']['X']
        print 'Y - ERROR'
        print errorDataRssi['ERROR']['Y']

        print 'X - ERROR_PERCENT'
        print errorDataRssi['ERROR_PERCENT']['X']
        print 'Y - ERROR_PERCENT'
        print errorDataRssi['ERROR_PERCENT']['Y']

        print 'X - ERROR_COORDINATE'
        print errorDataRssi['ERROR_COORDINATE']['X']
        print 'Y - ERROR_STATISTICS'
        print errorDataRssi['ERROR_COORDINATE']['Y']

    """method shows number of checkpoints which has x error and y error lower
       then given at start"""
    def showNumberOfCheckPointsBeloweError(self):
        while(True):
            anws = raw_input('quit(q)\nWhat error do you want to check?(x y): ')
            if anws == 'q':
                break
            anws = anws.split(' ')
            givenError = {}
            givenError['X'] = anws[0]
            givenError['Y'] = anws[1]
            
            anwserDict = self.countNumberOfCheckPointForGivenError(givenError)
            
            date = str(datetime.now()).replace(' ','_')
            date = date.replace(':','-')
            fileName = self.collname + '_CHECKPOINTS_BELOWE_ERROR_X_' + str(givenError['X']) + '_Y_' + str(givenError['Y']) + '_' + date
            
            linesList = []
            self.preapreLinesForCsvFileNumberOfCheckpointBeloweError(linesList,anwserDict)
            self.writeToCsvFile(fileName,linesList)
            print 'DATA SAVED TO CSV FILE'
            while(True):
                anws = int(raw_input('quit(100)\n%s\nchoose statistic data(0-%s)' % (str(self.STATISTIC_NAME), (len(self.STATISTIC_NAME) - 1))))
                if anws == 100:
                    break
                for map_name in self.map:
                    print map_name
                    print
                    print 'X'
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['X']['VALUE']
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['X']['PERCENT']
                    print 'checkpoints'
                    tString = ''
                    for doc in anwserDict[map_name][self.STATISTIC_NAME[anws]]['X']['CHECKPOINT_LIST']:
                        tString += doc['CHECKPOINT'] + ','
                    print tString
                    print

                    print 'Y'
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['Y']['VALUE']
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['Y']['PERCENT']
                    print 'checkpoints'
                    tString = ''
                    for doc in anwserDict[map_name][self.STATISTIC_NAME[anws]]['Y']['CHECKPOINT_LIST']:
                        tString += doc['CHECKPOINT'] + ','
                    print tString
                    print

                    print 'XY'
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['XY']['VALUE']
                    print anwserDict[map_name][self.STATISTIC_NAME[anws]]['XY']['PERCENT']
                    print 'checkpoints'
                    tString = ''
                    for doc in anwserDict[map_name][self.STATISTIC_NAME[anws]]['XY']['CHECKPOINT_LIST']:
                        tString += doc['CHECKPOINT'] + ','
                    print tString
#########################################################################################################
    def preapreLinesForCsvFileNumberOfCheckpointBeloweError(self, tList, counterDict):
        for map_name in self.map:
            firstLineFile = [self.collname + '_' + map_name]
            tList.append(firstLineFile)
            for dataStatistics in self.STATISTIC_NAME:
                tmpRow = [dataStatistics.replace(' ','')]
                tList.append(tmpRow)
                tmpRow = ['#;X;Y;XY']
                tList.append(tmpRow)
                tmpRow = ['LICZBA_PUNKTOW_ODNIESIENIA',counterDict[map_name][dataStatistics]['X']['VALUE'], counterDict[map_name][dataStatistics]['Y']['VALUE'], counterDict[map_name][dataStatistics]['XY']['VALUE']]
                tList.append(tmpRow)
                tmpRow = ['PROCENT_PUNKTOW_ODNIESIENIA',counterDict[map_name][dataStatistics]['X']['PERCENT'], counterDict[map_name][dataStatistics]['Y']['PERCENT'], counterDict[map_name][dataStatistics]['XY']['PERCENT']]
                tList.append(tmpRow)
                tmpCp = {}
                tmpCp['X'] = counterDict[map_name][dataStatistics]['X']['CHECKPOINT_LIST']
                tmpCp['Y'] = counterDict[map_name][dataStatistics]['Y']['CHECKPOINT_LIST']
                tmpCp['XY'] = counterDict[map_name][dataStatistics]['XY']['CHECKPOINT_LIST']
                for k in tmpCp.keys():
                    tmpCp[k +'_string'] = ''
                    tmpString = ''
                    for cp in tmpCp[k]:
                        tmpString += cp['CHECKPOINT'] + ','
                    tmpCp[k +'_string'] = tmpString
                
                tmpRow = ['LISTA_PUNKTOW_ODNIESIENIA',tmpCp['X_string'], tmpCp['Y_string'], tmpCp['XY_string']]
                tList.append(tmpRow)
                

########################################################################################################

    """method shows RSSI for certain AP and magnetic field for certain checkpoint
       and for certain position on map"""
       
    def showRssiAndMagneticCheckpointLocate(self):
        while(True):
            checkpoint = raw_input('q - quit\n%s\nChoose checkpoint: ' % (str(self.distinctCp)))
            if checkpoint == 'q':
                break
            coordinates = raw_input('X: %s\nY: %s\nChoose choordinates(x y): ' % (str(self.x_distinct),str(self.y_distinct)))
            coordinates = coordinates.split(' ')
            if len(coordinates) != 2:
                print 'Smth went wrong!'
                return
        
            coordinates[0] = int(coordinates[0])
            coordinates[1] = int(coordinates[1])
            dataStatistic = int(raw_input('''%s\nchoose statistic data(0,%s)''' % (str(self.STATISTIC_NAME),(len(self.STATISTIC_NAME) - 1))))
            dataStatistic = self.STATISTIC_NAME[dataStatistic]                          
            
            cursor = self.coll_fingerprint.find({'X': coordinates[0], 'Y': coordinates[1]})
            fingerprintDocs = [res for res in cursor]
            cursor = self.coll.find({'CHECKPOINT': checkpoint})
            locateDocs = [res for res in cursor]
        
            print 'FINGERPRINT - X: %s Y: %s' % (str(coordinates[0]), str(coordinates[1]))
            print
            for doc in fingerprintDocs:
                if 'RSSI_DATA' in doc.viewkeys():
                    print 'RSSI - %s ' % (doc['MAC_AP'])
                    print dataStatistic + ' - ' + str(doc['STATISTICS'][dataStatistic]) 
                elif 'MAGNETIC_DATA' in doc.viewkeys():
                    print 'MAGNETIC - X: %s, Y: %s' % (str(coordinates[0]), str(coordinates[1]))
                    print dataStatistic + ' - ' + str(doc['STATISTICS_NORM'][dataStatistic])
                
            checkpointDic = self.checkPoints[checkpoint]
            print
            print 'CHECKPOINT - %s - X: %s, Y: %s' % (checkpoint,str(checkpointDic['X']), str(checkpointDic['Y']))
            print
            for doc in fingerprintDocs:
                if 'RSSI_DATA' in doc.viewkeys():
                    print 'RSSI - ' + doc['MAC_AP']
                    print dataStatistic + ' - ' + str(doc['STATISTICS'][dataStatistic]) 
                elif 'MAGNETIC_DATA' in doc.viewkeys():
                    print 'MAGNETIC'
                    print dataStatistic + ' - ' + str(doc['STATISTICS_NORM'][dataStatistic])
    

###############################################################################
    """methods neede for showing effectiveness of certain algorithm """

    def countNumberOfCheckPointForGivenError(self,errorDict):
        resultDocs = {}
        self.loadDataResult(resultDocs)

        anwserDict = {}
        self.preapreAnwserDict(anwserDict)
        for map_name in self.map:
            for doc in resultDocs[map_name]:
                for dataStatistic in self.STATISTIC_NAME:
                    if doc['RESULTS'][dataStatistic]['ERROR']['X'] <= float(errorDict['X']):
                        anwserDict[map_name][dataStatistic]['X']['CHECKPOINT_LIST'].append(doc)
                        if doc['RESULTS'][dataStatistic]['ERROR']['Y'] <= float(errorDict['Y']):
                            anwserDict[map_name][dataStatistic]['Y']['CHECKPOINT_LIST'].append(doc)


        for map_name in self.map:
            for dataStatistic in self.STATISTIC_NAME:
                xList = anwserDict[map_name][dataStatistic]['X']['CHECKPOINT_LIST']
                yList = anwserDict[map_name][dataStatistic]['Y']['CHECKPOINT_LIST']

                for xDoc in xList:
                    for yDoc in yList:
                        if xDoc['CHECKPOINT'] == yDoc['CHECKPOINT']:
                            anwserDict[map_name][dataStatistic]['XY']['CHECKPOINT_LIST'].append(xDoc)

        numberOfCheckpoints = len(resultDocs['RSSI'])
        for map_name in self.map:
            for dataStatistic in self.STATISTIC_NAME:
                lenList = len(anwserDict[map_name][dataStatistic]['X']['CHECKPOINT_LIST'])
                anwserDict[map_name][dataStatistic]['X']['VALUE'] = str(lenList) + '/' + str(numberOfCheckpoints)
                anwserDict[map_name][dataStatistic]['X']['PERCENT'] = (lenList/float(numberOfCheckpoints)) * 100

                lenList = len(anwserDict[map_name][dataStatistic]['Y']['CHECKPOINT_LIST'])
                anwserDict[map_name][dataStatistic]['Y']['VALUE'] = str(lenList) + '/' + str(numberOfCheckpoints)
                anwserDict[map_name][dataStatistic]['Y']['PERCENT'] = (lenList/float(numberOfCheckpoints)) * 100

                lenList = len(anwserDict[map_name][dataStatistic]['XY']['CHECKPOINT_LIST'])
                anwserDict[map_name][dataStatistic]['XY']['VALUE'] = str(lenList) + '/' + str(numberOfCheckpoints)
                anwserDict[map_name][dataStatistic]['XY']['PERCENT'] = (lenList/float(numberOfCheckpoints)) * 100

        return anwserDict

    """method preapres anwser dict for number of checkpoints"""
    def preapreAnwserDict(self,tDict):
        tDict['RSSI'] = {}
        tDict['MAGNETIC'] = {}
        for dataStatistic in self.STATISTIC_NAME:
            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['RSSI'][dataStatistic] = {}
            tDict['RSSI'][dataStatistic]['X'] = tmpDict
            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['RSSI'][dataStatistic]['Y'] = tmpDict
            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['RSSI'][dataStatistic]['XY'] = tmpDict

            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['MAGNETIC'][dataStatistic] = {}
            tDict['MAGNETIC'][dataStatistic]['X'] = tmpDict
            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['MAGNETIC'][dataStatistic]['Y'] = tmpDict
            tmpDict ={}
            tmpDict['VALUE'] = ''
            tmpDict['PERCENT'] = 0
            tmpDict['CHECKPOINT_LIST'] = []
            tDict['MAGNETIC'][dataStatistic]['XY'] = tmpDict

###############################################################################
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
        

        resultStatistic['DOCUMENT_TYPE'] = 'ERROR_STATISTICS'
        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        fileName = self.collname + '_DATA_STATISTICS_' + date
        self.writeToCsvFile(fileName, fileList)
        self.db_result_statistics[self.collname].insert(resultStatistic)

    """method search all checkpoints and shows the best data statistic for
       localization. summing error of x and y - counting per document"""
    def countWhenSumErrorTheSmallest(self):
        resultAlgorithmDocs = {}
        self.loadDataResult(resultAlgorithmDocs)

        commonStatistics = {}
        self.preapreCounterErrorDictonary(commonStatistics)

        self.smallestErrorStatisticCounter(resultAlgorithmDocs, commonStatistics)

        fileList = []
        self.preapreLinesForCsvFileStatisticCounter(fileList, commonStatistics)

        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        firstLineFile = self.collname + '_DATA_STATISTICS_BEST_' + date
        self.writeToCsvFile(firstLineFile, fileList)
        self.db_result_statistics[self.collname].insert(commonStatistics)

    """method search all checkpoints and shows the best data statistic for
       localization - counting per document"""
    def countWhenCoordinatesErrorTheSmallest(self):
        resultAlgorithmDocs = {}
        self.loadDataResult(resultAlgorithmDocs)

        commonStatistics = {}
        self.preapreCounterErrorCoordinatesDictonary(commonStatistics)

        self.smallestErrorStatisticCoordinatesCounter(resultAlgorithmDocs, commonStatistics)

        fileList = []
        self.preapreLinesForCsvFileStatisticCounterCoordinates(fileList, commonStatistics)

        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        firstLineFile = self.collname + '_DATA_STATISTICS_COORDINATES_BEST_' + date
        self.writeToCsvFile(firstLineFile, fileList)
        self.db_result_statistics[self.collname].insert(commonStatistics)
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
            spamwriter.writerows(tList)
################################################################################
    """methods for showing chosen points with located checkpoint"""
    """method draws choosen ponts on map """

    def showCheckpointOnMap(self,xList, yList,checkpoint ,choose):
        tmpX = xList
        tmpY = yList
        colourList = [0] * len(tmpX)
        colourList[-1] = 1000
        colourList.append(100)
        tmpX.append(float(self.checkPoints[checkpoint]['X']))
        tmpY.append(float(self.checkPoints[checkpoint]['Y']))
        print tmpX
        print tmpY
        print colourList
        plt.scatter(tmpX, tmpY,c=colourList)
        plt.xlim(0,max(self.x_distinct))
        plt.ylim(0,max(self.y_distinct))
        for i in range(len(tmpX) - 2):
            tmplist = [tmpX[i],tmpY[i]]
            tmpTuple = tuple(tmplist)
            plt.annotate('RP',xy=tmpTuple)
        tmplist = [tmpX[-1],tmpY[-1]]
        tmpTuple = tuple(tmplist)
        plt.annotate('CP',xy=tmpTuple)
        tmplist = [tmpX[-2],tmpY[-2]]
        tmpTuple = tuple(tmplist)
        plt.annotate('LP',xy=tmpTuple)
        if choose == '0':
            plt.title('MAGNETIC - CHECKPOINT ' + checkpoint)
        elif choose == '1':
            plt.title('RSSI - CHECKPOINT ' + checkpoint)
        plt.xlabel('width [m]')
        plt.ylabel('length [m]')
        plt.show()

    '''reading checkpoints coordinates from text file '''
    def loadCheckPoints(self):
        with open(self.fileName,'r') as fd:
            lines = fd.readlines()

        for line in lines:
            line = line.replace('\n','')
            tmp = line.split(' ')
            tmpDict = {}
            tmpDict['X'] = tmp[1]
            tmpDict['Y'] = tmp[2]
            self.checkPoints[tmp[0]] = tmpDict
        print 'All checkpoints coordinates loaded'
################################################################################
    """methods for statistics counter - seprate cooridinates"""

    """method prepares dictoney for counting when data statistic has the smallest error
       coordinates separetly"""
    def preapreCounterErrorCoordinatesDictonary(self, counterDict):
        counterDict['DOCUMENT_TYPE'] = 'COUNTER_STATISTICS_COORDINATES'
        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        counterDict['MAGNETIC'] = tmpDic
        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        counterDict['RSSI'] = tmpDic

        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        counterDict['MAGNETIC']['LISTS'] = tmpDic
        tmpDic = {}
        tmpDic['X'] = {}
        tmpDic['Y'] = {}
        counterDict['RSSI']['LISTS'] = tmpDic

        """choosing the best data statistic for locating"""
        for map_name in self.map:
            for dataStatistics in self.STATISTIC_NAME:
                counterDict[map_name]['X'][dataStatistics] = 0
                counterDict[map_name]['Y'][dataStatistics] = 0
                counterDict[map_name]['LISTS']['X'][dataStatistics] = []
                counterDict[map_name]['LISTS']['Y'][dataStatistics] = []

    """method counts how many each data statistc is the best in localization
       per coordinate"""
    def smallestErrorStatisticCoordinatesCounter(self, resultAlgorithmDict, counterDict):
        for map_name in self.map:
            for doc in resultAlgorithmDict[map_name]:
                bestX = doc['RESULTS']['MEAN']['ERROR']['X']
                bestY = doc['RESULTS']['MEAN']['ERROR']['Y']
                anwserX = 'MEAN'
                anwserY = 'MEAN'

                for dataStatistics in self.STATISTIC_NAME[1:]:
                    nextX = doc['RESULTS'][dataStatistics]['ERROR']['X']
                    nextY = doc['RESULTS'][dataStatistics]['ERROR']['Y']
                    if bestY > nextY:
                        anwserY = dataStatistics
                        bestY = nextY
                    if bestX > nextX:
                        anwserX = dataStatistics
                        bestX = nextX
                counterDict[map_name]['X'][anwserX] += 1
                counterDict[map_name]['LISTS']['X'][anwserX].append(doc)
                counterDict[map_name]['Y'][anwserY] += 1
                counterDict[map_name]['LISTS']['Y'][anwserY].append(doc)

    """methods preapres lines to save statistc counter to csv file"""
    def preapreLinesForCsvFileStatisticCounterCoordinates(self, tList, counterDict):
        for map_name in self.map:
            firstLineFile = [self.collname + '_' + map_name]
            tList.append(firstLineFile)
            for dataStatistics in self.STATISTIC_NAME:
                tmpRow = [dataStatistics.replace(' ','')]
                tList.append(tmpRow)
                #tmpRow = [' ']
                #tList.append(tmpRow)
                tmpRow = ['X',  str(counterDict[map_name]['X'][dataStatistics])]
                tList.append(tmpRow)
                tmpRow = ['Y',  str(counterDict[map_name]['Y'][dataStatistics])]
                tList.append(tmpRow)

################################################################################
    """methods for statistic counter - summing error of x nad y"""

    """preparing dictonary for counting the best statistic data"""
    def preapreCounterErrorDictonary(self,counterDict):
        counterDict['DOCUMENT_TYPE'] = 'COUNTER_STATISTICS'
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
                    if errorSumBest > errorSumNext:
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
                
                tList.append(['#,ERROR,#,ERROR_PERCENT,#,ERROR_COORDINATE'])
                tList.append(['#,X,Y,X,Y,X,Y'])
                tmpRow = ['MIN', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MIN']), str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MIN']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MIN']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MIN']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MIN']),str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MIN'])]
                tList.append(tmpRow)
                tmpRow = ['MAX', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MAX']), str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MAX']),str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MAX']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MAX']),str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MAX']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MAX'])]
                tList.append(tmpRow)
                tmpRow = [u'SREDNIA', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MEAN']), str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MEAN']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MEAN']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MEAN']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MEAN']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MEAN'])]
                tList.append(tmpRow)
                tmpRow = ['MODA', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['MODE']), str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['MODE']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['MODE']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['MODE']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['MODE']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['MODE'])]
                tList.append(tmpRow)
                tmpRow = ['ODCHYLENIE_STANDARDOWE', str(statisticDict[map_name][dataStatistics]['ERROR']['X']['STANDARD_DEVIATION']), str(statisticDict[map_name][dataStatistics]['ERROR']['Y']['STANDARD_DEVIATION']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['X']['STANDARD_DEVIATION']), str(statisticDict[map_name][dataStatistics]['ERROR_PERCENT']['Y']['STANDARD_DEVIATION']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['X']['STANDARD_DEVIATION']), str(statisticDict[map_name][dataStatistics]['ERROR_COORDINATE']['Y']['STANDARD_DEVIATION'])]
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
        errorDic['DOCUMENT_TYPE'] = 'ERROR_STATISTICS'
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
    def saveAllCheckpointsErrorsToCsvFile(self):
        docs = {}
        docs['RSSI'] = []
        docs['MAGNETIC'] = []
        for map_name in self.map:
            cursor = self.coll.find({'FINGERPRINT_MAP': map_name})
            docs[map_name] = [res for res in cursor]
        linesFile = []
        self.preapreLinesForCheckpointErrorsCsvFile(linesFile, docs)
        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        fileName = self.collname + '_ALL_CHECKPOINTS_ERRORS_' + date
        self.writeToCsvFile(fileName, linesFile)
        print 'DATA WRITTEN TO CSV FILE'

    def preapreLinesForCheckpointErrorsCsvFile(self, tList, counterDic):
        for map_name in self.map:
            tmpRow = [map_name]
            tList.append(tmpRow)
            for dataStatistic in self.STATISTIC_NAME:
                tmpRow = [dataStatistic]
                tList.append(tmpRow)
                tmpRow = ['#,ERROR ERROR_PERCENT ERROR_COORDINATE']
                tList.append(tmpRow)
                tmpRow = ['#,X,Y,X,Y,X,Y']
                tList.append(tmpRow)
                for doc in counterDic[map_name]:
                    tmpRow = [doc['CHECKPOINT'], doc['RESULTS'][dataStatistic]['ERROR']['X'], doc['RESULTS'][dataStatistic]['ERROR']['Y'], doc['RESULTS'][dataStatistic]['ERROR_PERCENT']['X'], doc['RESULTS'][dataStatistic]['ERROR_PERCENT']['Y'], doc['RESULTS'][dataStatistic]['ERROR_COORDINATE']['X'], doc['RESULTS'][dataStatistic]['ERROR_COORDINATE']['Y']]
                    tList.append(tmpRow)
    
    def saveRangeApAndMagneticFingerprint(self):
                
        docs = {}
        docs['RSSI'] = {}
        for mac in self.mac_ap_distinct:
            docs['RSSI'][mac] = {'docs': [], 'values': {}, 'max': {}, 'min': {}, 'mean': {}, 'std': {}, 'mode': {}, 'mediana': {}, 'covrage': {}}
            for dataStatistic in self.STATISTIC_NAME:
                docs['RSSI'][mac]['values'][dataStatistic] = []
                docs['RSSI'][mac]['max'][dataStatistic] = 0
                docs['RSSI'][mac]['min'][dataStatistic] = 0
                docs['RSSI'][mac]['mean'][dataStatistic] = 0
                docs['RSSI'][mac]['std'][dataStatistic] = 0
                docs['RSSI'][mac]['mode'][dataStatistic] = {'value':0, 'accurance': 0}
                docs['RSSI'][mac]['mediana'][dataStatistic] = 0
                docs['RSSI'][mac]['covrage'][dataStatistic] = ''
            cursor = self.coll_fingerprint.find({'RSSI_DATA': {'$exists': True}, 'MAC_AP': mac})
            docs['RSSI'][mac]['docs'] = [res for res in cursor]
            
        
        docs['MAGNETIC'] = {'docs': [], 'values': {}, 'max': {}, 'min': {}, 'mean': {}, 'std': {}, 'mode': {}, 'mediana': {}, 'covrage': {}}
        for dataStatistic in self.STATISTIC_NAME:
            docs['MAGNETIC']['values'][dataStatistic] = []
            docs['MAGNETIC']['min'][dataStatistic] = 0
            docs['MAGNETIC']['max'][dataStatistic] = 0
            docs['MAGNETIC']['mean'][dataStatistic] = 0
            docs['MAGNETIC']['std'][dataStatistic] = 0
            docs['MAGNETIC']['mode'][dataStatistic] = {'value': 0, 'accurance': 0}
            docs['MAGNETIC']['mediana'][dataStatistic] = 0
            docs['MAGNETIC']['covrage'][dataStatistic] = ''
            
        cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}})
        docs['MAGNETIC']['docs'] = [res for res in cursor]
        
        
        
        for mac in self.mac_ap_distinct:
            for doc in docs['RSSI'][mac]['docs']:
                for dataStatistic in self.STATISTIC_NAME:
                    docs['RSSI'][mac]['values'][dataStatistic].append(doc['STATISTICS'][dataStatistic])
        
        for doc in docs['MAGNETIC']['docs']:
                for dataStatistic in self.STATISTIC_NAME:
                    docs['MAGNETIC']['values'][dataStatistic].append(doc['STATISTICS_NORM'][dataStatistic])
                    
                    
        for mac in self.mac_ap_distinct:
            for dataStatistic in self.STATISTIC_NAME:
                docs['RSSI'][mac]['max'][dataStatistic] = (max(docs['RSSI'][mac]['values'][dataStatistic]))
                docs['RSSI'][mac]['min'][dataStatistic] = (min(docs['RSSI'][mac]['values'][dataStatistic]))
                docs['RSSI'][mac]['mean'][dataStatistic] = (np.mean(docs['RSSI'][mac]['values'][dataStatistic]))
                docs['RSSI'][mac]['std'][dataStatistic] = (np.std(docs['RSSI'][mac]['values'][dataStatistic]))
                tmp = list(scipy.stats.mode(docs['RSSI'][mac]['values'][dataStatistic]))
                modeV = tmp[0].tolist()[0]
                acc = tmp[1].tolist()[0]
                docs['RSSI'][mac]['mode'][dataStatistic]['value'] = (modeV)
                docs['RSSI'][mac]['mode'][dataStatistic]['accurance'] = (acc)
                docs['RSSI'][mac]['mediana'][dataStatistic] = (np.median(docs['RSSI'][mac]['values'][dataStatistic]))
                tmpString = str(len(docs['RSSI'][mac]['values'][dataStatistic])) + '/' + str((len(self.x_distinct) * (len(self.y_distinct))))
                docs['RSSI'][mac]['covrage'][dataStatistic] = (tmpString)
        
        for dataStatistic in self.STATISTIC_NAME:
            docs['MAGNETIC']['max'][dataStatistic] = (max(docs['MAGNETIC']['values'][dataStatistic]))
            docs['MAGNETIC']['min'][dataStatistic] = (min(docs['MAGNETIC']['values'][dataStatistic]))
            docs['MAGNETIC']['mean'][dataStatistic] = (np.mean(docs['MAGNETIC']['values'][dataStatistic]))
            docs['MAGNETIC']['std'][dataStatistic] = (np.std(docs['MAGNETIC']['values'][dataStatistic]))
            tmp = list(scipy.stats.mode(docs['MAGNETIC']['values'][dataStatistic]))
            modeV = tmp[0].tolist()[0]
            acc = tmp[1].tolist()[0]
            docs['MAGNETIC']['mode'][dataStatistic]['value'] = (modeV)
            docs['MAGNETIC']['mode'][dataStatistic]['accurance'] = (acc)
            docs['MAGNETIC']['mediana'][dataStatistic] = (np.median(docs['MAGNETIC']['values'][dataStatistic]))
            tmpString = str(len(docs['MAGNETIC']['values'][dataStatistic])) + '/' + str((len(self.x_distinct) * (len(self.y_distinct))))
            docs['MAGNETIC']['covrage'][dataStatistic] = (tmpString)
        
        
        
        linesFile = []
        self.preapreLinesForApAndMagneticRangeCsvFile(linesFile, docs)
        date = str(datetime.now()).replace(' ','_')
        date = date.replace(':','-')
        fileName = self.collname + '_AP_MAGNETIC_RANGE_FINGERPRINT_' + date
        self.writeToCsvFile(fileName, linesFile)
        print 'DATA WRITTEN TO CSV FILE'
                    
    def preapreLinesForApAndMagneticRangeCsvFile(self,tList, counterDic):
        for map_name in self.map:
            tmpRow = [map_name]
            tList.append(tmpRow)
            for dataStatistic in self.STATISTIC_NAME:
                tmpRow = [dataStatistic.replace(' ','')]
                tList.append(tmpRow)
                if map_name == 'RSSI':
                    tmpRow = ['#,min,max,srednia,odchylenie_standardowe,moda-wartosc,moda-czestotliwosc,mediana,pokrycie_mapy']
                    tList.append(tmpRow)
                    for mac in self.mac_ap_distinct:
                        tmpRow = [mac,counterDic[map_name][mac]['min'][dataStatistic], counterDic[map_name][mac]['max'][dataStatistic], counterDic[map_name][mac]['mean'][dataStatistic], counterDic[map_name][mac]['std'][dataStatistic], counterDic[map_name][mac]['mode'][dataStatistic]['value'], counterDic[map_name][mac]['mode'][dataStatistic]['accurance'], counterDic[map_name][mac]['mediana'][dataStatistic], counterDic[map_name][mac]['covrage'][dataStatistic]]
                        tList.append(tmpRow)
                elif map_name == 'MAGNETIC':
                    tmpRow = ['min,max,srednia,odchylenie_standardowe,moda-wartosc,moda-czestotliwosc,mediana,pokrycie_mapy']
                    tList.append(tmpRow)
                    tmpRow = [counterDic[map_name]['min'][dataStatistic], counterDic[map_name]['max'][dataStatistic], counterDic[map_name]['mean'][dataStatistic], counterDic[map_name]['std'][dataStatistic], counterDic[map_name]['mode'][dataStatistic]['value'], counterDic[map_name]['mode'][dataStatistic]['accurance'], counterDic[map_name]['mediana'][dataStatistic], counterDic[map_name]['covrage'][dataStatistic]]
                    tList.append(tmpRow)
    
    def showLocalizationErrorChoosePoints(self):
        while(True):
            choose = raw_input('Magnetic map(0) or RSSI map(1) or quit(q)?')
            if choose == 'q':
                break
            dataStatistic = int(raw_input('All statistic - %s\n choose from 0 - %s' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))
            checkpointRange = raw_input('All checkpoints - %s\n choose 0-%s(a b ...)' % (str(self.distinctCp), len(self.distinctCp) - 1))
            checkpointRange = checkpointRange.split(' ')

            drawDict = {'NAME': [],'X': [], 'Y': [], 'X_ERROR': [], 'Y_ERROR': []}

            if choose == '0':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'MAGNETIC'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['X'].append(tmpDic['X'])
                        drawDict['Y'].append(tmpDic['Y'])
                        drawDict['X_ERROR'].append(tmpDic['ERROR']['X'])
                        drawDict['Y_ERROR'].append(tmpDic['ERROR']['Y'])
                        drawDict['NAME'].append(checkpoint)
                print drawDict['X']
                print drawDict['Y']
            elif choose == '1':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'RSSI'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['X'].append(tmpDic['X'])
                        drawDict['Y'].append(tmpDic['Y'])
                        drawDict['X_ERROR'].append(tmpDic['ERROR']['X'])
                        drawDict['Y_ERROR'].append(tmpDic['ERROR']['Y'])
                        drawDict['NAME'].append(checkpoint)
                print drawDict['X']
                print drawDict['Y']
            fig, ax = plt.subplots()
            anws = raw_input('Do you want errors on: only x(0), only y (1), x and y (2)')
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
            if choose == '1':
                plt.title('RSSI')
            elif choose == '0':
                plt.title(u'POLE MAGNETYCZNE')
            plt.xlim(-2,max(self.x_distinct)+ 2)
            plt.ylim(-15,max(self.y_distinct) + 8)
            plt.xlabel(u'szerokość [m]')
            plt.ylabel(u'długość [m]')
            plt.show()
            
    def showLocalizationErrorChoosePointsKopalnia(self):
        while(True):
            choose = raw_input('Magnetic map(0) or RSSI map(1) or quit(q)?')
            if choose == 'q':
                break
            dataStatistic = int(raw_input('All statistic - %s\n choose from 0 - %s' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))
            checkpointRange = raw_input('All checkpoints - %s\n choose 0-%s(a b ...)' % (str(self.distinctCp), len(self.distinctCp) - 1))
            checkpointRange = checkpointRange.split(' ')
            
            
            
            drawDict = {'NAME_WYZNACZONE': [], 'NAME_CHECKPOINT': [],'CHECKPOINT_WYZNACZONE': [], 'REAL_POSTION': []}

            if choose == '0':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'MAGNETIC'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['CHECKPOINT_WYZNACZONE'].append([tmpDic['X'],tmpDic['Y']])
                        drawDict['NAME_WYZNACZONE'].append(checkpoint + '-W')
                        drawDict['REAL_POSTION'].append([float(self.checkPoints[checkpoint]['X']),float(self.checkPoints[checkpoint]['Y'])])
                        drawDict['NAME_CHECKPOINT'].append(checkpoint + '-R')
            elif choose == '1':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'RSSI'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['CHECKPOINT_WYZNACZONE'].append([tmpDic['X'],tmpDic['Y']])
                        drawDict['NAME_WYZNACZONE'].append(checkpoint + '-W')
                        drawDict['REAL_POSTION'].append([float(self.checkPoints[checkpoint]['X']),float(self.checkPoints[checkpoint]['Y'])])
                        drawDict['NAME_CHECKPOINT'].append(checkpoint + '-R')
                        
            if choose == '1':
                plt.title('RSSI')
            elif choose == '0':
                plt.title(u'POLE MAGNETYCZNE')
            
            for i in range(len(drawDict['CHECKPOINT_WYZNACZONE'])):
                print drawDict['REAL_POSTION'][i]
                print drawDict['CHECKPOINT_WYZNACZONE'][i]
                x = [drawDict['REAL_POSTION'][i][0],drawDict['CHECKPOINT_WYZNACZONE'][i][0]]
                y = [drawDict['REAL_POSTION'][i][1],drawDict['CHECKPOINT_WYZNACZONE'][i][1]]
                plt.plot(x, y)
                tmpTuple = tuple(drawDict['REAL_POSTION'][i])
                plt.annotate(drawDict['NAME_CHECKPOINT'][i],xy=tmpTuple)
                tmpTuple = tuple(drawDict['CHECKPOINT_WYZNACZONE'][i])
                plt.annotate(drawDict['NAME_WYZNACZONE'][i],xy=tmpTuple)
            plt.xlim(0,max(self.x_distinct))
            plt.ylim(0,max(self.y_distinct))
            plt.xlabel(u'szerokość [m]')
            plt.ylabel(u'długość [m]')
            plt.show()        

    def showLocalizationErrorChoosePointsKuznia(self):
        while(True):
            choose = raw_input('Magnetic map(0) or RSSI map(1) or quit(q)?')
            if choose == 'q':
                break
            dataStatistic = int(raw_input('All statistic - %s\n choose from 0 - %s' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))
            checkpointRange = raw_input('All checkpoints - %s\n choose 0-%s(a b ...)' % (str(self.distinctCp), len(self.distinctCp) - 1))
            checkpointRange = checkpointRange.split(' ')
            
            
            
            drawDict = {'NAME_WYZNACZONE': [], 'NAME_CHECKPOINT': [],'CHECKPOINT_WYZNACZONE': [], 'REAL_POSTION': [], 'RADIUS':[]}

            if choose == '0':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'MAGNETIC'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['CHECKPOINT_WYZNACZONE'].append([tmpDic['X'],tmpDic['Y']])
                        drawDict['NAME_WYZNACZONE'].append(checkpoint + '-W')
                        drawDict['REAL_POSTION'].append([float(self.checkPoints[checkpoint]['X']),float(self.checkPoints[checkpoint]['Y'])])
                        drawDict['NAME_CHECKPOINT'].append(checkpoint + '-R')
                        drawDict['RADIUS'].append(math.sqrt((pow(tmpDic['ERROR']['X'],2) + pow(tmpDic['ERROR']['Y'],2))))
            elif choose == '1':
                for checkpoint in checkpointRange:
                    cursor = self.coll.find({'CHECKPOINT' : checkpoint, 'FINGERPRINT_MAP': 'RSSI'})
                    docs = [res for res in cursor]
                    for doc in docs:
                        tmpDic = doc['RESULTS'][self.STATISTIC_NAME[dataStatistic]]
                        drawDict['CHECKPOINT_WYZNACZONE'].append([tmpDic['X'],tmpDic['Y']])
                        drawDict['NAME_WYZNACZONE'].append(checkpoint + '-W')
                        drawDict['REAL_POSTION'].append([float(self.checkPoints[checkpoint]['X']),float(self.checkPoints[checkpoint]['Y'])])
                        drawDict['NAME_CHECKPOINT'].append(checkpoint + '-R')
                        drawDict['RADIUS'].append(math.sqrt((pow(tmpDic['ERROR']['X'],2) + pow(tmpDic['ERROR']['Y'],2))))
            if choose == '1':
                plt.title('RSSI')
            elif choose == '0':
                plt.title(u'POLE MAGNETYCZNE')
            
            for i in range(len(drawDict['CHECKPOINT_WYZNACZONE'])):
                print drawDict['REAL_POSTION'][i]
                print drawDict['CHECKPOINT_WYZNACZONE'][i]
                circle1=plt.Circle(tuple(drawDict['CHECKPOINT_WYZNACZONE'][i]),drawDict['RADIUS'][1],fill=False)
                fig = plt.gcf()
                fig.gca().add_artist(circle1)
                
                tmpTuple = tuple(drawDict['REAL_POSTION'][i])
                plt.annotate(drawDict['NAME_CHECKPOINT'][i],xy=tmpTuple)
                tmpTuple = tuple(drawDict['CHECKPOINT_WYZNACZONE'][i])
                plt.annotate(drawDict['NAME_WYZNACZONE'][i],xy=tmpTuple)
            plt.xlim(0,max(self.x_distinct) + 10)
            plt.ylim(0,max(self.y_distinct))
            plt.xlabel(u'szerokość [m]')
            plt.ylabel(u'długość [m]')
            plt.show()
            
    def drawChecpointsOnMap(self):
        drawDict = {'NAME': [], 'X': [],'Y': []}
        
        plt.title(u'CHODNIK KOPALNI')
        
        for checpoint in self.distinctCp:
            drawDict['NAME'].append(checpoint)
            drawDict['X'].append(float(self.checkPoints[checpoint]['X']))
            drawDict['Y'].append(float(self.checkPoints[checpoint]['Y']))
            
        for i in range(len(drawDict['NAME'])):
            plt.plot(drawDict['X'][i], drawDict['Y'][i])
            tmpTuple = tuple([drawDict['X'][i],drawDict['Y'][i]])
            plt.annotate(drawDict['NAME'][i],xy=tmpTuple)
        plt.xlim(0,max(self.x_distinct))
        plt.ylim(0,max(self.y_distinct))
        plt.xlabel(u'szerokość [m]')
        plt.ylabel(u'długość [m]')
        plt.show()


################################################################################
    """method which helps in analyze of statistics from error"""

def main():
    if len(sys.argv) != 4:
        sys.exit('Too small arguments! You gave: %s' % len(sys.argv))
    results = Results(sys.argv[1],sys.argv[2],sys.argv[3])
    msg = '''
    q - exit
    0 - show single checkpoint
    1 - show checkpoints localization error for certain data statistic
    2 - count data statistic error
    3 - show the smallest error per coordinate
    4 - show error od x and y for certain data statistics
    5 - show chosen points, acctual position of checkpoint and localization
    6 - show number of checkpoints belowe given x and y error
    7 - show RSSI value and magnetic field for ceratain refernce point and checkpoint
    8 - save checkpoints errors to csv file
    9 - save range of values of each AP and magnetic field
    10 - show localization error of checkpoint
    11 - show localization error of checkpoint - kopalnia
    12 - show localization error of checkpoint - kuznia
    13 - schowcheckpoints on map
    '''
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
        elif anw == '3':
            results.showTheSmallestErrorForCoordinates()
        elif anw == '4':
            results.showErrorForCoordinatesFoStatistics()
        elif anw == '5':
            results.showLocatedCheckpointAndPoints()
        elif anw == '6':
            results.showNumberOfCheckPointsBeloweError()
        elif anw == '7':
            results.showRssiAndMagneticCheckpointLocate()
        elif anw == '8':
            results.saveAllCheckpointsErrorsToCsvFile()
        elif anw == '9':
            results.saveRangeApAndMagneticFingerprint()
        elif anw == '10':
            results.showLocalizationErrorChoosePoints()
        elif anw == '11':
            results.showLocalizationErrorChoosePointsKopalnia()
        elif anw == '12':
            results.showLocalizationErrorChoosePointsKuznia()
        elif anw == '13':
            results.drawChecpointsOnMap()


if __name__ == '__main__':
    main()
