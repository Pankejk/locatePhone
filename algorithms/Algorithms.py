'''class where are implemented algorithms for locating people'''

from pymongo import MongoClient
import sys
import operator

class Algorithms (object):

    ''' Algorithm class '''

    def __init__(self, collectionName, checkPointFile, numberNeighbours):

        '''constructor'''

        self.collName = collectionName
        self.fileName = checkPointFile
        self.numberOfNeighbours = numberNeighbours

        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.x_distinct = None
        self.y_distinct = None
        self.checkPoints = {}
        self.checkPointsLocate = []

        self.ipPhone = ''
        self.macPhone = ''
        self.place = ''

        self.conn = MongoClient()

        dbFingerprint = self.conn['fingerprint']
        dbLocate = self.conn['locate']
        self.dbResult = self.conn['result']
        dbResultBackup = self.conn['result_backup']
        self.collFingerprint = dbFingerprint[self.collName]
        self.collLocate = dbLocate[self.collName]
        #self.collResult = dbResult['result_' + self.collName]
        self.collResultBackup = dbResultBackup[self.collName]


        self.loadCheckPoints()
        self.distinctCoordinates()
        self.placeAndPhoneInfo()
        self.checkPointsLocate = self.collLocate.distinct('CHECKPOINT')

        '''eucledian algorithm variables'''
        self.checkpointStatistic = []
        self.sortedDiff = {}
        self.allDiff = {}
        self.locateCheckpoint = {}



    '''destructor closes connection to mongo database'''
    def __del__(self):

        '''destructor'''
        self.conn.close()

##############################################################################################################################################
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
        self.x_distinct = self.x_distinct.sort()
        self.y_distinct = self.y_distinct.sort()
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

##############################################################################################################################################################################
    '''GENERAL LOCATING ALGORITHM SCHEMA '''

    ''' method preapres class for countings for next checkpoint'''
    def beforeLocate(self):
        self.beforeLocateEucledian()

    '''method counts diffrences beetween single checkpoint and all positions in fingerprint map
       method runs one of two algorithm to count diffrence
       method counts diffences in RSSI and magnetic fingerprint
       diffrences are counted for all statistic data
       other algorithm determine chooseCheckpoints and countLocationError'''
    def countDifference(self,checkPoint):
        self.eucledianDifference(checkPoint)

    ''' method is suming all diffrences in corelation with coordinates of rssi and magnetic map
        this method can implement diffrent algorithm'''
    def countSumStatisticalDiffrence(self):
        self.sumEucledianDifference()

    '''method can sort sum of diffrences in relation of statistic data and points in rssi and magnetic map
        method can implement diffrent sorting'''
    def sortSumStatisticalDiffrence(self):
        self.sortSumStatisticalDiffrence()

    '''method is choosing points which has the smallest diffrence with points in fingerprintmap
       points are choosen accordingly to statistic data
       points are choosen parallelly from RSSI and magnetic data
       method can choose one of available methods for choosing points'''
    def choosePointsOnMap(self,checkPoint):
        pass

    '''method check if new point is already on list'''
    def checkList(self):
        pass

    '''method counts location at the RSSI and magnetic map
       method counts location for all statistic data
       method for each above possibilities counts error according to checkpoint coordinates'''
    def countLocationAndError(self,checkPoint):
        pass
#########################################################################################################################################################################################################
    '''eucledian implemetation'''

    '''Method gain information about how many AP was used to compare checkpoint in certain coordinates'''
    def prepareCheckpointStatisticEucledian(self):
        self.checkpointStatistic = {}
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmpDict = {}
                tmpDict['X'] = x
                tmpDict['Y'] = y
                tmpDict['USED_AP'] = []
                self.checkpointStatistic.append(tmpDict)

    ''' method preapre list to keep sum of all difference between certain CP for certain point at rssi map and magnetic map
        eventaully list can be sorted by diffrent statistics'''
    def preapreSortedDiffEucledian(self):
        self.sortedDiff = {}
        self.sortedDiff['RSSI'] = []
        self.sortedDiff['MANETIC'] = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmpDic = {}
                tmpDic['X_FINGERPRINT'] = x
                tmpDic['Y_FINGERPRINT'] = y
                for dataStatistic in self.STATISTIC_NAME:
                    name = 'SUM_DIFF_' + dataStatistic
                    tmpDic[name] = 0
                self.sortedDiff['RSSI'].append(tmpDic)
                self.sortedDiff['MAGNETIC'].append(tmpDic)

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
        self.prepareCheckpointStatisticEucledian()
        self.preapreSortedDiffEucledian()
        self.prepareAllDiffEucledian()
        self.prepareLocateCheckpointEucledian()

    '''method counts diffrence beetween checkpoint gain data and each point of fingerprintmap as eucledian distance
       method counts it for RSSI map and magnetic map
       method counts diffrence beetween statistic data declared in STATISTIC_NAME'''
    def eucledianDifference(self,checkPoint):

        '''get rssi, magnetic fingerprintmap and all data for certain checkpoint'''
        magneticFingerprintDocs = self.collFingerprint.find({'RSSI_DATA': {'$exists' : True}})
        rssiFingerprintDocs = self.collFingerprint.find({'MAGNETIC_DATA': {'$exists' : True}})
        magneticLocateDocs = self.collLocate.find({'CHECKPOINT': checkPoint, 'MAGNETIC_DATA': {'$exists' : True}})
        rssiLocateDocs = self.collLocate.find({'CHECKPOINT': checkPoint, 'RSSI_DATA': {'$exists' : True}})

        '''parse cursor data to python dictonary'''
        magneticFingerprintDocs = [res for res in magneticFingerprintDocs]
        rssiFingerprintDocs = [res for res in rssiFingerprintDocs]
        allLocateDocs = [res for res in allLocateDocs]

        '''counting diff for RSSI map'''
        for docLocate in rssiLocateDocs:
            for docFingerprint in rssiFingerprintDocs:
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
                    statisticDict = {}
                    for dataStatistic in self.STATISTIC_NAME:
                        tmpDiff = abs(statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic])
                        statisticDict[dataStatistic] = tmpDiff
                    diff['STATISTICS_DIFF']
                    self.allDiff['RSSI'].apened(diff)

        ''' counting diff for magnetic map'''
        for docLocate in magneticLocateDocs:
            for docFingerprint in rssiLocateDocs:
                diff = {}
                diff['FINGERPRINT_MAP'] = 'MAGNETIC'
                diff['X_FINGERPRINT'] = docFingerprint['X']
                diff['Y_FINGERPRINT'] = docFingerprint['Y']
                diff['STATISTICS_DIFF'] = {}

                statisticsLocate = docLocate['STATISTICS_NORM']
                statisticsFingerprint = docFingerprint['STATISTICS_NORM']
                statisticDict = {}
                for dataStatistic in self.STATISTIC_NAME:
                    tmpDiff = abs(statisticsLocate[dataStatistic] - statisticsFingerprint[dataStatistic])
                    statisticDict[dataStatistic] = tmpDiff
                diff['STATISTICS_DIFF']
                self.allDiff['MAGNETIC'].apened(diff)

    '''method sums all diffrences accordingly to dataStatistic for each point on rssi and amgnetic map '''
    def eucledianSumDifference(self):
        ''' suming rssi data in certain points'''
        for doc in self.allDiff['RSSI']:
            for sortDoc in self.sortedDiff['RSSI']:
                if doc['X_FINGERPRINT'] == sortDoc['X_FINGERPRINT'] and doc['X_FINGERPRINT'] == sortDoc['X_FINGERPRINT']:
                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        sortDoc[name] += doc[dataStatistic]

        ''' suming magnetic data in certain points'''
        for doc in self.allDiff['MAGNETIC']:
            for sortDoc in self.sortedDiff['MAGNETIC']:
                if doc['X_FINGERPRINT'] == sortDoc['X_FINGERPRINT'] and doc['X_FINGERPRINT'] == sortDoc['X_FINGERPRINT']:
                    for dataStatistic in self.STATISTIC_NAME:
                        name = 'SUM_DIFF_' + dataStatistic
                        sortDoc[name] += doc[dataStatistic]

    '''method srots list by statistic data and preapre four points with the smallest diffrence '''
    def sortEucledianSumDiffrence(self):
        for dataStatistic in self.STATISTIC_NAME:
            name = 'SUM_DIFF_' + dataStatistic
            self.sortedDiff['RSSI'] = sorted(self.sortedDiff['RSSI'], key=lambda x: x[name])
            self.sortedDiff['MAGNETIC'] = sorted(self.sortedDiff['MAGNETIC'], key=lambda x: x[name])
            self.locateCheckpoint['RSSI'][dataStatistic] = self.sortedDiff['RSSI'][0:3]
            self.locateCheckpoint['MAGNETIC'][dataStatistic] = self.sortedDiff['MAGNETIC'][0:3]



    '''method is gaining mac addres of AP used in certain coordinate for certain checkpoint'''
    def assignCheckpointStatistics(self, x,y, mac):
        for item in self.checkpointStatistic:
            if item['X'] == x and item['Y'] == y:
                item['USED_AP'].append(mac)
##################################################################################################################################################################################
    '''starts locating device on RSSI and magnetic map
       with defined algorithm in constructor'''
    def startLocate(self):
        for checkPoint in self.checkPointsLocate[0:1]:
            self.beforeLocate()
            self.countDifference()
            self.choosePointsOnMap()
            self.countLocationAndError()


def main():
    if len(sys.argv) != 4:
        sys.exit('Wrong number argument length : %s' % len(sys.argv))
    collName = sys.argv[1]
    checkPointFile = sys.argv[2]
    numberOfNeighbours = int(sys.argv[3])
    Algorithms(collName, checkPointFile, numberOfNeighbours).startLocate()


if __name__ == '__main__':
    main()
