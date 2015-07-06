from pymongo import MongoClient
import sys

class Algorithms(object):
    
    def __init__(self, collectionName, checkPointFile):
        self.STATISTIC_NAME = ["MEAN" ,"STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        
        self.collName = collectionName
        self.fileName = checkPointFile
        self.conn = MongoClient()
        dbFingerprint = self.conn['fingerprint']
        dbLocate = self.conn['locate']
        dbResult = self.conn['result']
        self.collFingerprint = dbFingerprint[self.collName]
        self.collLocate = dbLocate[self.collName]
        self.collResult = dbResult['result_' + self.collName]
        self.checkPoints = {}
        self.checkPointsLocate = []
        self.loadCheckPoints()
    
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
                        print docFingerPrint
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
        self.collResult.insert(diffDictonary)
                        
    def kNn(self):
        pass
    
    #start all locating algorithms
    def startLocate(self):
        self.findAnwser()
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        sys.exit('Wrong number argument length : %s' % len(sys.argv))
    collName = sys.argv[1]
    checkPointFile = sys.argv[2]
    Algorithms(collName, checkPointFile).startLocate()
