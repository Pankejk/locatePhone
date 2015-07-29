'''class where are implemented algorithms for locating people'''

from pymongo import MongoClient
import sys
import operator

import time

import numpy as np
import matplotlib.pyplot as plt

class Algorithms (object):

    ''' Algorithm class '''

    def __init__(self, collectionName, collectionNameLocate, checkPointFile, numberNeighbours, algorithmDistance, algorithmChoosePoints, mode):

        '''constructor'''

        self.collName = collectionName
        self.collNameLocate = collectionNameLocate
        self.fileName = checkPointFile
        self.numberOfNeighbours = numberNeighbours
        self.choosenAlgorithmDistance = algorithmDistance
        self.choosenAlgorithmChoosePoints = algorithmChoosePoints
        self.mode = mode

        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE",
        "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50",
        "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.ALGORITHM_DISTANCE_NAME = ['EUCLEUDIAN_DISTANCE', '']
        self.ALGORITHM_CHOOSEPOINTS_NAME = ['_KNN_','']

        self.x_distinct = None
        self.y_distinct = None
        self.checkPoints = {}
        self.checkpointsLocate = []
        self.mac_fingerprint_distinct = []

        self.conn = MongoClient()

        dbFingerprint = self.conn['fingerprint']
        dbLocate = self.conn['locate']
        self.dbResult = self.conn['result']
        #dbResultBackup = self.conn['result_backup']
        self.collFingerprint = dbFingerprint[self.collName]
        self.collLocate = dbLocate[self.collNameLocate]
        #self.collResult = dbResult['result_' + self.collName]
        #self.collResultBackup = dbResultBackup[self.collName]


        '''data for all algorithms'''
        self.ipPhone = ''
        self.macPhone = ''
        self.place = ''
        self.currentCheckpoint = ''
        self.checkpointStatistic = []
        self.locateCheckpoint = {}
        self.sumDiff = {}
        self.sumDiffMac = {}
        self.allDiff = {}

        self.loadCheckPoints()
        self.distinctCoordinates()
        self.placeAndPhoneInfo()
        self.checkpointsLocate = self.collLocate.distinct('CHECKPOINT')
        self.mac_fingerprint_distinct = self.collFingerprint.distinct('MAC_AP')

    '''destructor closes connection to mongo database'''
    def __del__(self):

        '''destructor'''
        self.conn.close()

    '''method inserts result doc for a proper collection '''
    def insertResult(self,doc):
        name = self.collName + self.ALGORITHM_CHOOSEPOINTS_NAME[self.choosenAlgorithmChoosePoints] + str(self.numberOfNeighbours) + '_distanceAlgorithm_' +self.ALGORITHM_DISTANCE_NAME[self.choosenAlgorithmDistance]
        self.dbResult[name].insert(doc)

###############################################################################
    ''' PREPARING CLASS FOR LOCATING BY ANY ALGORITHM'''

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

    '''take distinct coordinates for chosen fingerprint map'''
    def distinctCoordinates(self):
        self.x_distinct = self.collFingerprint.distinct('X')
        self.y_distinct = self.collFingerprint.distinct('Y')
        #print self.x_distinct
        #self.x_distinct = self.x_distinct.sort()
        #self.y_distinct = self.y_distinct.sort()
        print 'All distinct coordinates found'

    '''method is finding place, ip_phone, mac_phone'''
    def placeAndPhoneInfo(self):
        ip = self.collLocate.distinct('IP_PHONE')
        mac = self.collLocate.distinct('MAC_PHONE')
        place = self.collLocate.distinct('PLACE')
        print 'LENGTH OF IP_PHONE TABLE: ' + str(len(ip))
        print 'LENGTH OF MAC_PHONE TABLE: ' + str(len(mac))
        print 'LENGTH OF IP_TABLE TABLE: ' + str(len(place))
        self.ipPhone = ip[0]
        self.macPhone = mac[0]
        self.place = place[0]

    '''method check if new point is already on list'''
    def checkList(self,locateList, doc):
        anws = False
        for locateDoc in locateList:
            if locateDoc['X_FINGERPRINT'] == doc['X_FINGERPRINT'] and locateDoc['Y_FINGERPRINT'] == doc['Y_FINGERPRINT']:
                anws = True
                break
        return anws

    '''Method gain information about how many AP was used to compare checkpoint in certain coordinates'''
    def prepareCheckpointStatistic(self):
        self.checkpointStatistic = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmpDict = {}
                tmpDict['X_FINGERPRINT'] = x
                tmpDict['Y_FINGERPRINT'] = y
                tmpDict['USED_AP'] = []
                self.checkpointStatistic.append(tmpDict)

    '''method is gaining mac addres of AP used in certain coordinate for certain checkpoint'''
    def assignCheckpointStatistics(self, x,y, mac):
        for item in self.checkpointStatistic:
            if item['X_FINGERPRINT'] == x and item['Y_FINGERPRINT'] == y:
                item['USED_AP'].append(mac)

    '''method for choosen points for certain statistic show used AP for locating'''
    def resultUsedAp(self, resultDict):
        for dataStatistic in self.STATISTIC_NAME:
            tList = resultDict['CHOSEN_POINTS'][dataStatistic]
            rList = []
            for fingerprintCoordinate in tList:
                rDic = {}
                x = fingerprintCoordinate['X_FINGERPRINT']
                y = fingerprintCoordinate['Y_FINGERPRINT']
                macList = []
                for checkpointStats in self.checkpointStatistic:
                    if checkpointStats['X_FINGERPRINT'] == x and checkpointStats['Y_FINGERPRINT'] == y:
                        macList = checkpointStats['USED_AP']
                        rDic['LIST_AP'] = macList
                        rDic['SIZE_OF_LIST'] = len(macList)
                        tmpDic = {'X': x,'Y': y}
                        rDic['FINGERPRINT_COORDINATES'] = tmpDic
                        rList.append(rDic)
                resultDict['USED_AP'][dataStatistic] = rList
                #!!!!!!!!!print resultDict


    '''method prepare result dictonary with choosen points fo certain statistic data'''
    def resultChosenPoints(self,resultDict, chosenPointsDict):
        for dataStatistic in self.STATISTIC_NAME:
            name = 'SUM_DIFF_' + dataStatistic
            #print chosenPointsDict['RSSI'][dataStatistic]
            tmpList = []

            for element in chosenPointsDict['RSSI'][dataStatistic]:
                tmpDic = {}
                tmpDic['X_FINGERPRINT'] = element['X_FINGERPRINT']
                tmpDic['Y_FINGERPRINT'] = element['Y_FINGERPRINT']
                tmpDic[name] = element[name]
                tmpList.append(tmpDic)
            resultDict['RSSI']['CHOSEN_POINTS'][dataStatistic] = tmpList

            tmpList = []

            for element in chosenPointsDict['MAGNETIC'][dataStatistic]:
                tmpDic = {}
                tmpDic['X_FINGERPRINT'] = element['X_FINGERPRINT']
                tmpDic['Y_FINGERPRINT'] = element['Y_FINGERPRINT']
                tmpDic[name] = element[name]
                tmpList.append(tmpDic)

            resultDict['MAGNETIC']['CHOSEN_POINTS'][dataStatistic] = tmpList


    ''' method preapres dictonary with results of any algorithm'''
    def resultDictonary(self, docDict):
        doc={}
        doc['IP_PHONE'] = self.ipPhone
        doc['MAC_PHONE'] = self.macPhone
        doc['PLACE'] = self.place
        doc['CHECKPOINT'] = self.currentCheckpoint
        coordinatesCheckpoint = {}
        coordinatesCheckpoint['X'] = float(self.checkPoints[self.currentCheckpoint]['X'])
        coordinatesCheckpoint['Y'] = float(self.checkPoints[self.currentCheckpoint]['Y'])
        doc['CHECKPOINT_COORDINATES'] = coordinatesCheckpoint
        doc['CHOSEN_POINTS'] ={}
        doc['RESULTS'] = {}
        doc['USED_AP'] = {}

        for dataStatistic in self.STATISTIC_NAME:
            doc['CHOSEN_POINTS'][dataStatistic] = []

            tmp = {}
            tmp['X'] = 0
            tmp['Y'] = 0
            tmp['ERROR'] = {'X': 0,'Y': 0}
            doc['RESULTS'][dataStatistic] = tmp

            #tmp = {}
            #tmp[dataStatistic] = {'LIST_AP' : [] , 'SIZE_OF_LIST': 0}
            doc['USED_AP'][dataStatistic] = []#{'FINGERPRINT_COORDINATES' : {'X':0,'Y': 0},'LIST_AP' : [] , 'SIZE_OF_LIST': 0}


        doc['FINGERPRINT_MAP'] = 'RSSI'
        docDict['RSSI'] = doc
        mDoc = dict(doc)
        del mDoc['USED_AP']
        mDoc['FINGERPRINT_MAP'] = 'MAGNETIC'
        docDict['MAGNETIC'] = mDoc

        self.resultChosenPoints(docDict, self.locateCheckpoint)
        self.resultUsedAp(docDict['RSSI'])

###############################################################################
    '''GENERAL LOCATING ALGORITHM SCHEMA '''

    ''' method preapres class for countings for next checkpoint'''
    def beforeLocate(self,checkpoint):
        self.currentCheckpoint = str(checkpoint)
        self.prepareCheckpointStatistic()
        self.beforeLocateEucledian()

    '''method counts diffrences beetween single checkpoint and all positions in fingerprint map
       method runs one of two algorithm to count diffrence
       method counts diffences in RSSI and magnetic fingerprint
       diffrences are counted for all statistic data
       other algorithm determine chooseCheckpoints and countLocationError'''
    def countDifference(self):
        self.eucledianDifference()

    ''' method is suming all diffrences in corelation with coordinates of rssi and magnetic map
        this method can implement diffrent algorithm'''
    def countSumStatisticalDiffrence(self):
        self.eucledianSumDifference()
        self.eucledianSumDifferenceMac()

    '''method is choosing points which has the smallest diffrence with points in fingerprintmap
       points are choosen accordingly to statistic data
       points are choosen parallelly from RSSI and magnetic data
       method can choose one of available methods for choosing points'''
    def choosePointsOnMap(self):
        self.choosePointsOnMapEucledian()


    '''method counts location at the RSSI and magnetic map
       method counts location for all statistic data
       method for each above possibilities counts error according to checkpoint coordinates'''
    def countLocationAndError(self):
        resultDic = {}
        self.resultDictonary(resultDic)
        for dataStatistic in self.STATISTIC_NAME:

            '''locating and counting error by RSSI map '''
            tmpList = resultDic['RSSI']['CHOSEN_POINTS'][dataStatistic]
            tmp = [0,0]
            for coordinates in tmpList:
                tmp[0] += coordinates['X_FINGERPRINT']
                tmp[1] += coordinates['Y_FINGERPRINT']

            print 'RSSI'
            print tmp
            resultDic['RSSI']['RESULTS'][dataStatistic]['X'] = tmp[0]/float(len(tmpList))
            resultDic['RSSI']['RESULTS'][dataStatistic]['Y'] = tmp[1]/float(len(tmpList))
            resultDic['RSSI']['RESULTS'][dataStatistic]['ERROR']['X'] = abs(resultDic['RSSI']['RESULTS'][dataStatistic]['X'] - resultDic['RSSI']['CHECKPOINT_COORDINATES']['X'])
            resultDic['RSSI']['RESULTS'][dataStatistic]['ERROR']['Y'] = abs(resultDic['RSSI']['RESULTS'][dataStatistic]['Y'] - resultDic['RSSI']['CHECKPOINT_COORDINATES']['Y'])

            '''locating and counting error by magnetic map '''
            tmpList = resultDic['MAGNETIC']['CHOSEN_POINTS'][dataStatistic]
            tmp = [0,0]
            for coordinates in tmpList:
                tmp[0] += coordinates['X_FINGERPRINT']
                tmp[1] += coordinates['Y_FINGERPRINT']
            print 'MAGNETIC'
            print tmp
            resultDic['MAGNETIC']['RESULTS'][dataStatistic]['X'] = tmp[0]/float(len(tmpList))
            resultDic['MAGNETIC']['RESULTS'][dataStatistic]['Y'] = tmp[1]/float(len(tmpList))
            resultDic['MAGNETIC']['RESULTS'][dataStatistic]['ERROR']['X'] = abs(resultDic['MAGNETIC']['RESULTS'][dataStatistic]['X'] - resultDic['MAGNETIC']['CHECKPOINT_COORDINATES']['X'])
            resultDic['MAGNETIC']['RESULTS'][dataStatistic]['ERROR']['Y'] = abs(resultDic['MAGNETIC']['RESULTS'][dataStatistic]['Y'] - resultDic['MAGNETIC']['CHECKPOINT_COORDINATES']['Y'])
        self.insertResult(resultDic['RSSI'])
        self.insertResult(resultDic['MAGNETIC'])
        #self.countLocationAndErrorEucledian()

###############################################################################
    '''eucledian implemetation'''

    ''' method preapre list to keep sum of all difference between certain CP
        for certain point at rssi map and magnetic map
        eventaully list can be sorted by diffrent statistics'''
    def preapreSumDiffEucledian(self):
        self.sumDiff = {}
        self.sumDiff['RSSI'] = []
        self.sumDiff['MAGNETIC'] = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmpDicAp = {}
                tmpDicAp['X_FINGERPRINT'] = x
                tmpDicAp['Y_FINGERPRINT'] = y

                tmpDicMagnetic = {}
                tmpDicMagnetic['X_FINGERPRINT'] = x
                tmpDicMagnetic['Y_FINGERPRINT'] = y
                for dataStatistic in self.STATISTIC_NAME:
                    name = 'SUM_DIFF_' + dataStatistic
                    tmpDicMagnetic[name] = 0
                    tmpDicAp[name] = 0
                self.sumDiff['RSSI'].append(tmpDicAp)
                self.sumDiff['MAGNETIC'].append(tmpDicMagnetic)


    ''' method preapre list to keep sum of all difference between certain CP
        for certain point at rssi(certain AP) map and magnetic map
        eventaully list can be sorted by diffrent statistics'''
    def preapreSumDiffMacEucledian(self):
        self.sumDiffMac = {}
        self.sumDiffMac['RSSI'] = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                for mac in self.mac_fingerprint_distinct:
                    tmpDicAp = {}
                    tmpDicAp['X_FINGERPRINT'] = x
                    tmpDicAp['Y_FINGERPRINT'] = y
                    tmpDicAp['MAC_AP'] = mac

                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        tmpDicAp[name] = 0
                    self.sumDiffMac['RSSI'].append(tmpDicAp)

    ''' method preapre list to keep all diffrence beerween CP and all points in magnetic and rssi map '''
    def prepareAllDiffEucledian(self):
        self.allDiff = {}
        self.allDiff['RSSI'] = []
        self.allDiff['MAGNETIC'] = []

    '''Prepares final dict with choosen points accordingly to statistics data'''
    def prepareLocateCheckpointEucledian(self):
        self.locateCheckpoint = {}
        self.locateCheckpoint['RSSI'] = {}
        self.locateCheckpoint['MAGNETIC'] = {}
        for dataStatistic in self.STATISTIC_NAME:
            self.locateCheckpoint['RSSI'][dataStatistic] = []
            self.locateCheckpoint['MAGNETIC'][dataStatistic] = []

    ''' method preapres class for coutings for next checkpoint'''
    def beforeLocateEucledian(self):
        self.preapreSumDiffMacEucledian()
        self.preapreSumDiffEucledian()
        self.prepareAllDiffEucledian()
        self.prepareLocateCheckpointEucledian()

    '''method counts diffrence beetween checkpoint gain data and each point of fingerprintmap as eucledian distance
       method counts it for RSSI map and magnetic map
       method counts diffrence beetween statistic data declared in STATISTIC_NAME'''
    def eucledianDifference(self):

        '''get rssi, magnetic fingerprintmap and all data for certain checkpoint'''
        magneticFingerprintDocs = self.collFingerprint.find({'MAGNETIC_DATA': {'$exists' : True}})
        rssiFingerprintDocs = self.collFingerprint.find({'RSSI_DATA': {'$exists' : True}})
        magneticLocateDocs = self.collLocate.find({'CHECKPOINT': self.currentCheckpoint, 'MAGNETIC_DATA': {'$exists' : True}})
        rssiLocateDocs = self.collLocate.find({'CHECKPOINT': self.currentCheckpoint, 'RSSI_DATA': {'$exists' : True}})

        '''parse cursor data to python dictonary'''
        magneticFingerprintDocs = [res for res in magneticFingerprintDocs]
        rssiFingerprintDocs = [res for res in rssiFingerprintDocs]
        magneticLocateDocs = [res for res in magneticLocateDocs]
        rssiLocateDocs = [res for res in rssiLocateDocs]

        '''counting diff for RSSI map'''
        for docLocate in rssiLocateDocs:
            for docFingerprint in rssiFingerprintDocs:
                #print docFingerprint
                #print ''
                #print docLocate
                if docLocate['MAC_AP'] == docFingerprint['MAC_AP']:
                    self.assignCheckpointStatistics(docFingerprint['X'],docFingerprint['Y'], docFingerprint['MAC_AP'])

                    diff = {}
                    diff['FINGERPRINT_MAP'] = 'RSSI'
                    diff['MAC_AP'] = docFingerprint['MAC_AP']
                    diff['X_FINGERPRINT'] = docFingerprint['X']
                    diff['Y_FINGERPRINT'] = docFingerprint['Y']
                    diff['STATISTICS_DIFF'] = {}

                    statisticsLocate = docLocate['STATISTICS']
                    statisticsFingerprint = docFingerprint['STATISTICS']
                    #statisticDict = {}
                    for dataStatistic in self.STATISTIC_NAME:
                        tmpDiff = abs(statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic])
                        diff[dataStatistic] = tmpDiff
                    #diff['STATISTICS_DIFF']
                    self.allDiff['RSSI'].append(diff)

        ''' counting diff for magnetic map'''
        for docLocate in magneticLocateDocs:
            for docFingerprint in magneticFingerprintDocs:
                diff = {}
                diff['FINGERPRINT_MAP'] = 'MAGNETIC'
                diff['X_FINGERPRINT'] = docFingerprint['X']
                diff['Y_FINGERPRINT'] = docFingerprint['Y']
                diff['STATISTICS_DIFF'] = {}

                statisticsLocate = docLocate['STATISTICS_NORM']
                statisticsFingerprint = docFingerprint['STATISTICS_NORM']
                #statisticDict = {}
                for dataStatistic in self.STATISTIC_NAME:
                    tmpDiff = abs(statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic])
                    diff[dataStatistic] = tmpDiff
                #diff['STATISTICS_DIFF']
                self.allDiff['MAGNETIC'].append(diff)

    '''method sums all diffrences accordingly to dataStatistic for each point on rssi(certain AP) and amgnetic map '''
    def eucledianSumDifferenceMac(self):
        ''' suming rssi data in certain points'''
        for doc in self.allDiff['RSSI']:
            for sumDoc in self.sumDiffMac['RSSI']:
                if doc['X_FINGERPRINT'] == sumDoc['X_FINGERPRINT'] and doc['Y_FINGERPRINT'] == sumDoc['Y_FINGERPRINT'] and doc['MAC_AP'] == sumDoc['MAC_AP']:
                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        #print doc
                        sumDoc[name] += doc[dataStatistic]
        print 'AFTER SUMING RSSI FINGERPRINT MAP'
        #print self.sumDiff['RSSI']

    '''method sums all diffrences accordingly to dataStatistic for each point on rssi and amgnetic map '''
    def eucledianSumDifference(self):
        ''' suming rssi data in certain points'''
        for doc in self.allDiff['RSSI']:
            for sumDoc in self.sumDiff['RSSI']:
                if doc['X_FINGERPRINT'] == sumDoc['X_FINGERPRINT'] and doc['Y_FINGERPRINT'] == sumDoc['Y_FINGERPRINT']:
                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        #print doc
                        sumDoc[name] += doc[dataStatistic]
        print 'AFTER SUMING RSSI FINGERPRINT MAP'

        ''' suming magnetic data in certain points'''
        for doc in self.allDiff['MAGNETIC']:
            for sumDoc in self.sumDiff['MAGNETIC']:
                if doc['X_FINGERPRINT'] == sumDoc['X_FINGERPRINT'] and doc['Y_FINGERPRINT'] == sumDoc['Y_FINGERPRINT']:
                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        sumDoc[name] += doc[dataStatistic]
        print 'AFTER SUMING MAGNETIC FINGERPRINT MAP'

    ''' method chooses points on rssi and magnetic map for eucledian distnace algorithm'''
    def choosePointsOnMapEucledian(self):

        '''choosing points on rssi map '''
        for doc in self.sumDiff['RSSI']:
            #print 'RSSI - SORT'
            self.sortEucledianSumDiffrence(self.locateCheckpoint['RSSI'],doc)

        '''choosing points on magnetic map '''
        for doc in self.sumDiff['MAGNETIC']:
            #print 'MAGNETIC - SORT'
            self.sortEucledianSumDiffrence(self.locateCheckpoint['MAGNETIC'],doc)

    '''method chooses position with the smallest diffrence on map and put it to list accordingly to statistic data '''
    def sortEucledianSumDiffrence(self, locateDic, doc):
        for dataStatistic in self.STATISTIC_NAME:
            if self.checkList(locateDic[dataStatistic],doc):
                continue
            name = 'SUM_DIFF_' + dataStatistic
            if len(locateDic[dataStatistic]) != self.numberOfNeighbours:
                    locateDic[dataStatistic].append(doc)
            else:
                locateDic[dataStatistic]= sorted(locateDic[dataStatistic], key=lambda x: x[name])
                #raw_input()
                #print name
                #print doc
                #print
                #print locateDic[dataStatistic]
                #raw_input()
                if locateDic[dataStatistic][-1][name] > doc[name]:
                    locateDic[dataStatistic][-1] = doc

        #    self.sumDiff['RSSI'] = sorted(self.sumDiff['RSSI'], key=lambda x: x[name])
        #    self.sumDiff['MAGNETIC'] = sorted(self.sumDiff['MAGNETIC'], key=lambda x: x[name])
        #    self.locateCheckpoint['RSSI'][dataStatistic] = self.sumDiff['RSSI'][0:3]
        #    self.locateCheckpoint['MAGNETIC'][dataStatistic] = self.sumDiff['MAGNETIC'][0:3]

    #def countLocationAndErrorEucledian(self):
###############################################################################
    """set of methods for debugging locating algorithm"""
    def menu(self):
        while(True):
            self.slowDownLoop()
            anws = raw_input('''
            q - quit
            0 - show checkpoint on acces point map
            1 - show checkpoint on magnetic field map
            2 - show list of diffrence
            3 - show list of sum diffrence
            4 - show list of sum diffence for certain mac''')
            if anws == 'q':
                break
            elif anws == '0':
                anws = int(raw_input('''This are all macs: %s. Choose(0,%s)''' % (str(self.mac_fingerprint_distinct), len(self.mac_fingerprint_distinct))))
                self.showCheckpointOnMapAp(anws)
            elif anws == '1':
                self.showCheckpointOnMapMagnetic()
            elif anws == '2':
                self.showTableOfDiffrence()
            elif anws == '3':
                self.showsSumAllDiff()
            elif anws == '4':
                anws = int(raw_input('%s\nChoose mac(0-%s): ' % (str(self.mac_fingerprint_distinct), len(self.mac_fingerprint_distinct))))
                self.showSumDiffMac(anws)

    """method chooses best points in map accordingly to AP and draw it on graph"""
    def showCheckpointOnMapAp(self,macChoice):
        macAp = self.mac_fingerprint_distinct[macChoice]

        diffApDocs = []
        for item in self.sumDiffMac['RSSI']:
            if item['MAC_AP'] == macAp:
                diffApDocs.append(item)

        locateCheckpoint = {}
        locateCheckpoint['RSSI'] = {}
        for dataStatistic in self.STATISTIC_NAME:
            locateCheckpoint['RSSI'][dataStatistic] = []

        for doc in diffApDocs:
            self.sortEucledianSumDiffrence(locateCheckpoint['RSSI'],doc)

        x_points = []
        y_points = []
        anws = int(raw_input('%s\n Which data statistic do you want to see?(0-%s)' % (str(self.STATISTIC_NAME),(len(self.STATISTIC_NAME) - 1))))
        statisticName = self.STATISTIC_NAME[anws]
        for point in locateCheckpoint['RSSI']['MEAN']:
            x_points.append(point['X_FINGERPRINT'])
            y_points.append(point["Y_FINGERPRINT"])

        self.showCheckpointOnMap(x_points,y_points)


    """method choose the best points on map and show it on map"""
    def showCheckpointOnMapMagnetic(self):
        x_points = []
        y_points = []
        anws = int(raw_input('%s\n Which data statistic do you want to see?(0-%s)' % (str(self.STATISTIC_NAME),(len(self.STATISTIC_NAME) - 1))))
        statisticName = self.STATISTIC_NAME[anws]
        for point in self.locateCheckpoint['MAGNETIC'][statisticName]:
            x_points.append(point['X_FINGERPRINT'])
            y_points.append(point['Y_FINGERPRINT'])
        self.showCheckpointOnMap(x_points,y_points)

    """method draws choosen ponts on map """
    def showCheckpointOnMap(self,xList, yList):
        tmpX = xList
        tmpY = yList
        colourList = [0] * len(tmpX)
        colourList.append(100)
        tmpX.append(int(self.checkPoints[self.currentCheckpoint]['X']))
        tmpY.append(int(self.checkPoints[self.currentCheckpoint]['Y']))
        plt.scatter(xList, yList,c=colourList)
        plt.xlim(0,max(self.x_distinct))
        plt.ylim(0,max(self.y_distinct))
        plt.show()

    """ method slows down work of loop"""
    def slowDownLoop(self):
        time.sleep(0.5)


###############################################################################
    """ method shows diff table for magnetic or certain AP """
    def showTableOfDiffrence(self):
        anws = int(raw_input('MAGNETIC(0) or RSSI(1)'))
        if anws == 1:
            anws  = raw_input('X - %s\nY - %s Choose coordinates(x y): ' % (str(self.x_distinct), str(self.y_distinct)))
            anws.replace('\n','')
            anws = anws.split(' ')
            anws[0] = int(anws[0])
            anws[1] = int(anws[1])
            for record in self.allDiff['RSSI']:
                if record['X_FINGERPRINT'] == anws[0] and record['Y_FINGERPRINT'] == anws[1]:
                    print record
        elif anws == 0:
            anws  = raw_input('X - %s\nY - %s Choose coordinates(x y): ' % (str(self.x_distinct), str(self.y_distinct)))
            anws.replace('\n','')
            anws = anws.split(' ')
            anws[0] = int(anws[0])
            anws[1] = int(anws[1])
            for record in self.allDiff['MAGNETIC']:
                if record['X_FINGERPRINT'] == anws[0] and record['Y_FINGERPRINT'] == anws[1]:
                    print record

    """method shows sumdiff table"""
    def showsSumAllDiff(self):
        anws = int(raw_input('MAGNETIC(0) or RSSI(1)'))
        if anws == 1:
            anws  = raw_input('X - %s\nY - %s Choose coordinates(x y): ' % (str(self.x_distinct), str(self.y_distinct)))
            anws.replace('\n','')
            anws = anws.split(' ')
            anws[0] = int(anws[0])
            anws[1] = int(anws[1])
            for record in self.sumDiff['RSSI']:
                if record['X_FINGERPRINT'] == anws[0] and record['Y_FINGERPRINT'] == anws[1]:
                    print record
        elif anws == 0:
            anws  = raw_input('X - %s\nY - %s Choose coordinates(x y): ' % (str(self.x_distinct), str(self.y_distinct)))
            anws.replace('\n','')
            anws = anws.split(' ')
            anws[0] = int(anws[0])
            anws[1] = int(anws[1])
            for record in self.sumDiff['MAGNETIC']:
                if record['X_FINGERPRINT'] == anws[0] and record['Y_FINGERPRINT'] == anws[1]:
                    print record

    """method shows sumdiffMac table"""
    def showSumDiffMac(self,mac):
        for record in self.sumDiffMac['RSSI']:
            if record['MAC_AP'] == self.mac_fingerprint_distinct[mac]:
                print record
################################################################################
    '''starts locating device on RSSI and magnetic map
       with defined algorithm in constructor'''
    def startLocate(self):
        for checkpoint in self.checkpointsLocate: #[0:5]:
            print 'BEFORE LOCATING CHECKPOINT - ' + checkpoint
            if self.mode == 'DEPLOY':
                self.beforeLocate(checkpoint)
                self.countDifference()
                self.countSumStatisticalDiffrence()
                self.choosePointsOnMap()
                self.countLocationAndError()
            elif self.mode == 'DEBUG':
                self.beforeLocate(checkpoint)
                anws = raw_input('DEBUG - after before locate smth(y/n/q)?')
                if anws == 'y':
                    self.menu()
                elif anws == 'q':
                    break
                self.countDifference()
                anws = raw_input('DEBUG - after count diffrence smth(y/n/q)?')
                if anws == 'y':
                    self.menu()
                elif anws == 'q':
                    break
                self.countSumStatisticalDiffrence()
                anws = raw_input('DEBUG - after summing diffrence smth(y/n/q)?')
                if anws == 'y':
                    self.menu()
                elif anws == 'q':
                    break
                self.choosePointsOnMap()
                anws = raw_input('DEBUG after choosing checkpoint smth(y/n/q)?')
                if anws == 'y':
                    self.menu()
                elif anws == 'q':
                    break
                self.countLocationAndError()
                anws = raw_input('DEBUG after counting location error smth(y/n/q)?')
                if anws == 'y':
                    self.menu()
                elif anws == 'q':
                    break
            print 'AFTER LOCATING CHECKPOINT - ' + checkpoint


def main():
    if len(sys.argv) != 8:
        sys.exit('Wrong number argument length : %s' % len(sys.argv))
    collName = sys.argv[1]
    collNameLocate = sys.argv[2]
    checkPointFile = sys.argv[3]
    numberOfNeighbours = int(sys.argv[4])
    algorithmDistance = int(sys.argv[5])
    algorithmChoosePoints = int(sys.argv[6])
    mode = sys.argv[7]
    Algorithms(collName, collNameLocate, checkPointFile, numberOfNeighbours, algorithmDistance, algorithmChoosePoints, mode).startLocate()


if __name__ == '__main__':
    main()
