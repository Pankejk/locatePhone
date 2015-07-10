'''class where are implemented algorithms for locating people'''

from pymongo import MongoClient
import sys


class Algorithms(object):

    ''' Algorithm class '''

    def __init__(self, collectionName, checkPointFile, numberNeighbours):

        '''constructor'''

        self.STATISTIC_NAME = ["MEAN" ,"STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.x_distinct = None
        self.y_distinct = None
        self.collName = collectionName
        self.fileName = checkPointFile
        self.numberofNeighbours = numberNeighbours
        self.conn = MongoClient()
        dbFingerprint = self.conn['fingerprint']
        dbLocate = self.conn['locate']
        dbResult = self.conn['result']
        dbResultBackup = self.conn['result_backup']
        self.collFingerprint = dbFingerprint[self.collName]
        self.collLocate = dbLocate[self.collName]
        self.collResult = dbResult['result_' + self.collName]
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
                            diff['FINGERPRINT_MAP'] = 'AP'
                            diff['MAC_AP'] = docFingerPrint['MAC_AP']
                            diff['X_FINGERPRINT'] = docFingerPrint['X']
                            diff['Y_FINGERPRINT'] = docFingerPrint['Y']
                            diff['IP_PHONE'] = docFingerPrint['IP_PHONE']
                            diff['PLACE'] = docFingerPrint['PLACE']
                            diff['HASH'] = docFingerPrint['HASH']
                            diff['MAC_PHONE'] = docFingerPrint['MAC_PHONE']
                            diff['STATISTICS_DIFF'] = {}
                            statisticsLocate = docLocate['STATISTICS']
                            statisticsFingerprint = docFingerPrint['STATISTICS']

                            statisticDict = {}
                            for dataStatistic in self.STATISTIC_NAME:
                                tmpDiff = statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic]
                                statisticDict[dataStatistic] = tmpDiff
                            diff['STATISTICS_DIFF'] = statisticDict
                            diffList.append(diff)
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
                        diff['HASH'] = docFingerPrint['HASH']
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
        #load to diffrent db - this is before choosing x and y
        self.collResultBackup.insert(diffDictonary)

        maX = {}#bestDictonary[0]
        for statisticData in self.STATISTIC_NAME:
            tmp = {}
            tmp['CHOSEN_POINTS'] = []
            tmp['COUNTED_PONT'] = []
            tmp['CHECKPOINT'] = ''
            tmp['CHECKPOINT_COORDINATES'] = []
            tmp['LOCATION_ERROR'] = []
            tmp['FINGERPRINT_MAP'] = ''

            maX[statisticData] = []
            maX[statisticData].append(tmp)

            tmp = {}
            tmp['MAX'] = 0
            tmp['MIN'] = 0
            tmp['AVG'] = 0
            maX['CONCLUSION_RSSI'] = tmp

            tmp = {}
            tmp['MAX'] = 0
            tmp['MIN'] = 0
            tmp['AVG'] = 0
            maX['CONCLUSION_MAGNETIC'] = tmp

        for dictonary in diffDictonary:
            if dictonary == '_id':
                continue
            if 'DIFF_LIST' in diffDictonary[dictonary].viewkeys():
                diffList = diffDictonary[dictonary]['DIFF_LIST']

                #fourBest = [0]
                bestDictonary = []
                for x in self.x_distinct:
                    #print type(x)
                    for y in self.y_distinct:

                        tmp = {}
                        tmp['X'] = x
                        tmp['Y'] = y
                        tmp['FINGERPRINT_MAP'] = 'AP'

                        tmp1 = {}
                        tmp1['X'] = x
                        tmp1['Y'] = y
                        tmp1['FINGERPRINT_MAP'] = 'MAGNETIC'

                        for statisticData in self.STATISTIC_NAME:
                            fieldName = 'DIFFRENCE_'+ statisticData
                            tmp[fieldName] = 0
                            bestDictonary.append(tmp)
                            tmp1[fieldName] = 0
                            bestDictonary.append(tmp1)
                        print 'JSON PREPARED'
                for diffDict in diffList:
                    if 'FINGERPRINT_MAP' in diffDict:
                        for d in bestDictonary:
                            if d['X'] == diffDict['X'] and d['Y'] == diffDict['Y'] and d['FINGERPRINT_MAP'] == diffDict['FINGERPRINT_MAP']:
                                for statisticData in self.STATISTIC_NAME:
                                    fieldName = 'DIFFRENCE_'+ statisticData
                                    d[fieldName] = d[fieldName] + abs(diffDict['STATISTICS_DIFF'][statisticData])
                print 'COUNT DIFF AFTER'


                for statisticData in self.STATISTIC_NAME:
                    choose = []
                    tmp = maX[statisticData][0]
                    tmp['']
                    for best in bestDictonary:


                #maX = d
                #print maX
                    #tmp = diffDict['STATISTICS_DIFF']['MEAN']
                    #best = bestDictonary['STATISTICS_DIFF']['MEAN']
                    #anwser  = min(tmp,best)
                    #if (anwser != best):
                    #bestDictonary = tmp

                    #if tmp >
                    #mBest = max(tBest)
                    #if tmp >
    def kNn(self):
        pass

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
