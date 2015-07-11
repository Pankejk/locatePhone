'''class where are implemented algorithms for locating people'''

from pymongo import MongoClient
import sys
import operator


class Algorithms(object):

    ''' Algorithm class '''

    def __init__(self, collectionName, checkPointFile, numberNeighbours):

        '''constructor'''

        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.x_distinct = None
        self.y_distinct = None
        self.collName = collectionName
        self.fileName = checkPointFile
        self.numberOfNeighbours = numberNeighbours
        self.conn = MongoClient()
        dbFingerprint = self.conn['fingerprint']
        dbLocate = self.conn['locate']
        self.dbResult = self.conn['result']
        dbResultBackup = self.conn['result_backup']
        self.collFingerprint = dbFingerprint[self.collName]
        self.collLocate = dbLocate[self.collName]
        #self.collResult = dbResult['result_' + self.collName]
        self.collResultBackup = dbResultBackup[self.collName]
        self.checkPoints = {}
        self.checkPointsLocate = []
        self.loadCheckPoints()

        self.x_distinct = self.collFingerprint.distinct('X')
        self.y_distinct = self.collFingerprint.distinct('Y')

    def loadCheckPoints(self):
        with open(self.fileName,'r') as fd:
            lines = fd.readlines()
        #print lines
        #fd.close()
        #with open(self.fileName,'r') as fd:
        for line in lines:
            line = line.replace('\n','')
            tmp = line.split(' ')
            tmpDict = {}
            tmpDict['X'] = tmp[1]
            tmpDict['Y'] = tmp[2]
            tmpDict['RSSI_COUNTER'] = 0
            tmpDict['USED_AP'] = []
            self.checkPoints[tmp[0]] = tmpDict
        self.checkPointsLocate = self.collLocate.distinct('CHECKPOINT')
        #print self.checkPointsLocate

    def countStatisticalDifference(self):
        allFingerprintDocs = self.collFingerprint.find({})
        allFingerprintDocs = [res for res in allFingerprintDocs]
        resultDict = self.checkPoints

        for checkPoint in self.checkPointsLocate[0:1]:
            print 'CHECKPOINT START: ' + checkPoint
            #if checkPoint.isdigit():
            #    continue
            allLocateDocs = self.collLocate.find({'CHECKPOINT' : checkPoint})
            allLocateDocs = [res for res in allLocateDocs]

            macApInCheckpoint = []
            for doc in allLocateDocs:
                if 'MAC_AP' in doc.viewkeys():
                    if not doc['MAC_AP'] in macApInCheckpoint:
                        macApInCheckpoint.append(doc['MAC_AP'])
            checkPointDict = {}
            checkPointDict['CHECKPOINT'] = checkPoint
            diffList = []
            #print len(allLocateDocs)
            countLocateDocument = 0
            for docLocate in allLocateDocs:
                #print docLocate
                countFingerprintDocument = 0
                for docFingerPrint in allFingerprintDocs:
                    #print docLocate.viewkeys()
                    if 'RSSI_DATA' in docLocate.viewkeys() and 'RSSI_DATA' in docFingerPrint.viewkeys():
                        print 'RSSI'
                        #print docLocate
                        #print docFingerPrint
                        if docLocate['MAC_AP'] == docFingerPrint['MAC_AP']:
                            diff = {}
                            diff['FINGERPRINT_MAP'] = 'RSSI'
                            diff['MAC_AP'] = docFingerPrint['MAC_AP']
                            diff['X_FINGERPRINT'] = docFingerPrint['X']
                            diff['Y_FINGERPRINT'] = docFingerPrint['Y']
                            diff['IP_PHONE'] = docFingerPrint['IP_PHONE']
                            diff['PLACE'] = docFingerPrint['PLACE']
                            diff['MAC_PHONE'] = docFingerPrint['MAC_PHONE']
                            diff['STATISTICS_DIFF'] = {}
                            diff['CHECKPOINT'] = checkPoint
                            diff['CHECKPOINT_CORDINATES'] = [self.checkPoints[checkPoint]['X'],self.checkPoints[checkPoint]['Y']]
                            statisticsLocate = docLocate['STATISTICS']
                            statisticsFingerprint = docFingerPrint['STATISTICS']

                            statisticDict = {}
                            for dataStatistic in self.STATISTIC_NAME:
                                tmpDiff = statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic]
                                statisticDict[dataStatistic] = tmpDiff
                            diff['STATISTICS_DIFF'] = statisticDict
                            diffList.append(diff)
                            self.checkPoints[checkPoint]['RSSI_COUNTER'] += 1
                            self.checkPoints[checkPoint]['USED_AP'].append(docLocate['MAC_AP'])
                            #print diffList
                    elif 'MAGNETIC_DATA' in docLocate.viewkeys() and 'MAGNETIC_DATA' in docFingerPrint.viewkeys():
                        print 'MAGNETIC'
                        #print docFingerPrint
                        statisticsLocate = docLocate['STATISTICS_NORM']
                        statisticsFingerprint = docFingerPrint['STATISTICS_NORM']
                        diff =  {}
                        diff['FINGERPRINT_MAP'] = 'MAGNETIC'
                        diff['X_FINGERPRINT'] = docFingerPrint['X']
                        diff['Y_FINGERPRINT'] = docFingerPrint['Y']
                        diff['IP_PHONE'] = docFingerPrint['IP_PHONE']
                        diff['PLACE'] = docFingerPrint['PLACE']
                        diff['CHECKPOINT'] = checkPoint
                        diff['CHECKPOINT_CORDINATES'] = [self.checkPoints[checkPoint]['X'],self.checkPoints[checkPoint]['Y']]
                        diff['MAC_PHONE'] = docFingerPrint['MAC_PHONE']
                        diff['STATISTICS_DIFF'] = {}

                        statisticDict = {}
                        for dataStatistic in self.STATISTIC_NAME:
                            tmpDiff = statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic]
                            statisticDict[dataStatistic] = tmpDiff
                        diff['STATISTICS_DIFF'] = statisticDict
                        diffList.append(diff)
                        #print diffList
                    countFingerprintDocument += 1
                    print 'FINGERPRINT DOCUMENT COMPARE NR: ' + str(countFingerprintDocument) + '/'  + str(len(allFingerprintDocs))
                countLocateDocument +=1
                print 'LOCATE DOCUMENT NR: ' + str(countLocateDocument) + '/'  + str(len(allLocateDocs))
            #checkPointDict['DIFF_LIST'] = diffList
            tmpDict = resultDict[checkPoint]
            tmpDict['DIFF_LIST'] = diffList
            resultDict[checkPoint] = tmpDict
            print 'CHECKPOINT STOP: ' + checkPoint

        return resultDict

    def findAnwser(self):
        diffDictonary = self.countStatisticalDifference()
        
        self.collResultBackup.insert(diffDictonary)

        bestDictonary = []
        for key, value in self.checkPoints.items():
            tmp = {}
            tmp1 = {}

            for x in self.x_distinct:
                for y in self.y_distinct:

                    tmp['CHECKPOINT'] = key
                    tmp['CHECKPOINT_COORDINATE'] = value
                    tmp1['CHECKPOINT'] = key
                    tmp1['CHECKPOINT_COORDINATE'] = value

                    tmp['X_FINGERPRINT'] = x
                    tmp['Y_FINGERPRINT'] = y
                    tmp['FINGERPRINT_MAP'] = 'RSSI'
                    tmp1['X_FINGERPRINT'] = x
                    tmp1['Y_FINGERPRINT'] = y
                    tmp1['FINGERPRINT_MAP'] = 'MAGNETIC'

                for statisticData in self.STATISTIC_NAME:
                    fieldName = 'DIFFRENCE_'+ statisticData
                    tmp[fieldName] = 0
                    bestDictonary.append(tmp)
                    tmp1[fieldName] = 0
                    bestDictonary.append(tmp1)
                print 'JSON PREPARED'

        #complete search count sum of diff for all x,y cooridinates
        for dictonary in diffDictonary:
            if dictonary == '_id':
                continue
            if 'DIFF_LIST' in diffDictonary[dictonary].viewkeys():
                diffList = diffDictonary[dictonary]['DIFF_LIST']

                #fourBest = [0]

                diffCounter = 0
                for diffDict in diffList:
                    for d in bestDictonary:
                        if d['X'] == diffDict['X'] and d['Y'] == diffDict['Y'] and d['FINGERPRINT_MAP'] == diffDict['FINGERPRINT_MAP'] and d['CHECKPOINT'] == diffDict['CHECKPOINT']:
                            for statisticData in self.STATISTIC_NAME:
                                fieldName = 'DIFFRENCE_'+ statisticData
                                d[fieldName] = d[fieldName] + abs(diffDict['STATISTICS_DIFF'][statisticData])
                                print 'PROGRESS: ' + str(diffCounter) + '/' + str(len(diffDict))
                        diffCounter += 1
                print 'COUNT DIFF AFTER'


        locateRssi = []
        locateMagnetic  = []
        for key , value in self.checkPoints.items():
            tmp = {}
            tmp['CHECKPOINT'] = key
            cordiantes = {}
            cooridnates['X'] = value['X']
            cooridnates['Y'] = value['Y']
            tmp['CHECKPOINT_COORDINATES'] = cooridnates
            tmp['FINGERPRINT_MAP'] = 'RSSI'
            tmp['RSSI_COUNTER'] = value['RSSI_COUNTER']
            tmp['USED_AP'] = value['USED_AP']
            
            tmp['RESULT'] = {}
            tmp['CHOSEN_POINTS'] = {}
            for statisticData in self.STATISTIC_NAME:
                dic = {}
                dic['X'] = 0
                dic['Y'] = 0
                dic['ERROR'] = {'X': 0, 'Y' : 0}
                tmp['RESULT'][statisticData] = dic
                tmp['CHOSEN_POINTS'][statisticData] = []
            locateRssi.append(tmp)
        
        for key, value in self.checkPoints.items():
            tmp = {}
            tmp['CHECKPOINT'] = key
            coordinates = {}
            coordinates['X'] = value['X']
            coordinates['Y'] = value['Y']
            tmp['CHECKPOINT_COORDINATES'] = coordinates
            tmp['FINGERPRINT_MAP'] = 'MAGNETIC'
            
            tmp['RESULT'] = {}
            tmp['CHOSEN_POINTS'] = {}
            for statisticData in self.STATISTIC_NAME:
                dic = {}
                dic['X'] = 0
                dic['Y'] = 0
                dic['ERROR'] = {'X': 0, 'Y' : 0}
                tmp['RESULT'][statisticData] = dic
                tmp['CHOSEN_POINTS'][statisticData] = []
            locateMagnetic.append(tmp)
        
        print 'Final json prepared!' 
        
        for finalDoc in locateRssi:
            for best in bestDictonary:
                if finalDoc['CHECKPOINT'] == best['CHECKPOINT']:
                    if finalDoc['FINGERPRINT_MAP'] == 'RSSI':
                        self.kNn(best, finalDoc['CHOSEN_POINTS'])
                        bestDictonary.remove(best)
        
        for finalDoc in locateMagnetic:
            for best in bestDictonary:
                if finalDoc['CHECKPOINT'] == best['CHECKPOINT']:
                    if finalDoc['FINGERPRINT_MAP'] == 'MAGNETIC':
                        self.kNn(best, finalDoc['CHOSEN_POINTS'])
        
        for doc in locateRssi:
            for statisticData in self.STATISTIC_NAME:
                tmp = doc['CHOSEN_POINTS'][statisticData]
                coordinatesList = [0,0]
                for dic in tmp:
                    coordinatesList[0] += dic['X']
                    coordinatesList[0] += dic['Y']
                coordinateList[0] = coordinateList[0]/float(len(tmp))
                coordinateList[1] = coordinateList[1]/float(len(tmp))
                doc['RESULT'][statisticData]['X'] = coordinateList[0]
                doc['RESULT'][statisticData]['Y'] = coordinateList[1]
                doc['RESULT'][statisticData]['ERROR']['X'] = doc['CHECKPOINT_COORDINATES']['X'] - doc['RESULT'][statisticData]['X']
                doc['RESULT'][statisticData]['ERROR']['Y'] = doc['CHECKPOINT_COORDINATES']['Y'] - doc['RESULT'][statisticData]['Y']
        
        for doc in locateMagnetic:
            for statisticData in self.STATISTIC_NAME:
                tmp = doc['CHOSEN_POINTS'][statisticData]
                coordinatesList = [0,0]
                for dic in tmp:
                    coordinatesList[0] += dic['X']
                    coordinatesList[0] += dic['Y']
                coordinateList[0] = coordinateList[0]/float(len(tmp))
                coordinateList[1] = coordinateList[1]/float(len(tmp))
                doc['RESULT'][statisticData]['X'] = coordinateList[0]
                doc['RESULT'][statisticData]['Y'] = coordinateList[1]
                doc['RESULT'][statisticData]['ERROR']['X'] = doc['CHECKPOINT_COORDINATES']['X'] - doc['RESULT'][statisticData]['X']
                doc['RESULT'][statisticData]['ERROR']['Y'] = doc['CHECKPOINT_COORDINATES']['Y'] - doc['RESULT'][statisticData]['Y']
        
        collName = self.collName+'_KNN:' +str(self.numberOfNeighbours)
        for doc in locateRssi:
            coll = self.dbResult[collName]
            coll.insert(doc)
        

    def kNn(self, doc, dic):
        for statisticData in self.STATISTIC_NAME:
            if len(dic[statisticData]) != self.numberOfNeighbours:
                dic[statisticData].append(doc)
            else:
                dic[statisticData] = sorted(dic[statisticData], key=lambda x: x)
                if maX[statisticData][-1] > doc[fieldName]:
                    maX[statisticData][-1] = doc

    #start all locating algorithms
    def startLocate(self):
        self.findAnwser()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        sys.exit('Wrong number argument length : %s' % len(sys.argv))
    collName = sys.argv[1]
    checkPointFile = sys.argv[2]
    numberOfNeighbours = sys.argv[3]
    Algorithms(collName, checkPointFile, numberOfNeighbours).startLocate()
