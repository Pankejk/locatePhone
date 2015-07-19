"""script changes x to be in set x[1,3] for intger.
Then it copies all data wich are statistic for left and right side data."""

from pymongo import MongoClient
import os
import time

class CleanDataKopalniaFingerprint(object):

    """class is used  for  reaprinfd broken fingerprint map - rssi, magnetic"""
    def __init__(self):

        self.conn = MongoClient()
        db = self.conn['fingerprint']
        self.coll = db['kopalnia_DATASIZE_200']
        self.coll_side_stats = db['kopalnia_DATASIZE_200_side_stats']
        self.STATISTIC_NAME = ["MEAN", "STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.mac_distinct = self.coll.distinct('MAC_AP')

    def __del__(self):
        self.conn.close()

    """change x coordinate to integer set [1,3] """
    def repairXCoordiante(self):
        cursor = self.coll.find({})
        docs = [res for res in cursor]

        print self.coll.distinct('X')
        print 'before changing x to be in integer set [1,3]. All documents number: %s' % self.coll.count()
        for doc in docs:
            if doc['X'] > 3:
                doc['X'] = doc['X'] % 3
                if doc['X'] == 0:
                    doc['X'] = 3
                self.coll.save(doc)
        print 'after changing x to be in in integer set [1,3]. All documents number: %s' % self.coll.count()
        print self.coll.distinct('X')

    '''copy side statistic docs to diffrent collection '''
    def copyDataSideStatistic(self):
        cursor = self.coll.find({'X': 2})
        docs = [res for res in cursor]

        print 'before before copying documents. All documents number: %s' % self.coll.count()

        for doc in docs:
            cursor = self.coll.find({'X': 1, 'Y': doc['Y']})
            doc1 = [res for res in cursor]
            cursor = self.coll.find({'X': 3, 'Y': doc['Y']})
            doc3 = [res for res in cursor]

            if len(doc3) == 4 and len(doc1) == 4:
                self.coll_side_stats.save(doc)
                for d in doc1:
                    self.coll_side_stats.save(d)
                for d in doc3:
                    self.coll_side_stats.save(d)
        print 'after compying documents. All documents: %s' % self.coll.count()

    """drop side statis data collection"""
    def dropSideStatistic(self):
        self.coll_side_stats.drop()

    """drop fingerprint data and load it again """
    def dropKopalniaFingerprint(self):
        self.coll.drop()
        os.system('mongoimport --db fingerprint --collection kopalnia_DATASIZE_200 --file ../data-backup/kopalnia_DATASIZE_200_16_07_15.json')

    """method creates new documents in fingerprint map """
    def createMissingDocumentsInMap(self):
        print 'Number of documents in fingeprint collecton before adding new documents: ' + str(self.coll.find({}).count())
        #cursor = self.coll.find({'X': 1})
        #docX1 = [res for res in cursor]
        #cursor = self.coll.find({'X': 2})
        #docX2 = [res for res in cursor]
        #cursor = self.coll.find({'X': 3})
        #docX3 = [res for res in cursor]

        #print 'Number of documnet for X = 1: ' + str(len(docX1))
        #print 'Number of documnet for X = 2: ' + str(len(docX2))
        #print 'Number of documnet for X = 3: ' + str(len(docX3))
        y_side_stat = [0,20,40,60,80,100]
        x_stat = [1,2,3]
        x_stat_border = [1,3]
        docs = {}
        for y in y_side_stat:
            docs[y] = {}
            for x in x_stat:
                docs[y][x] = []
                cursor = self.coll.find({'Y': y, 'X': x})
                tmpDocs = [res for res in cursor]
                print 'For Y = ' + str(y) + ' and X = ' + str(x) + ' Found number of documents: ' + str(len(tmpDocs))
                docs[y][x] = tmpDocs

        docList = {}
        for y in y_side_stat:
            docList[y] = []
            for x in x_stat:
                docList[y].append(docs[y][x])
            #for docDic in docs[y]:
            #    for x in x_stat:
            #        print docDic
            #        docList[y].append(docDic[x])

        statisticResult = {}
        for y in y_side_stat:
            statisticResult[y] = {}
            tList = docList[y]
            tmpX = {}
            tmpX['X1'] = {}
            tmpX['X3'] = {}

            for docX1 in tList[0]:

                for docX2 in tList[1]:
                    if 'RSSI_DATA' in docX1.viewkeys() and 'RSSI_DATA' in docX2.viewkeys():
                        if docX1['MAC_AP'] == docX2['MAC_AP']:
                            tmpAp = {}
                            tmpAp['STATISTICS_DIFFERENCE'] = {}
                            for dataStatistic in self.STATISTIC_NAME:
                                tmpAp['STATISTICS_DIFFERENCE'][dataStatistic] = abs(docX1['STATISTICS'][dataStatistic] - docX2['STATISTICS'][dataStatistic])
                            tmpX['X1'][docX1['MAC_AP']] = tmpAp

                    if 'MAGNETIC_DATA' in docX1.viewkeys() and 'MAGNETIC_DATA' in docX2.viewkeys():
                        tmpMagnetic = {}
                        tmpMagnetic['MAGNETIC'] = 'MAGNETIC'
                        tmpMagnetic['STATISTICS_DIFFERENCE'] = {}
                        for dataStatistic in self.STATISTIC_NAME:
                            tmpMagnetic['STATISTICS_DIFFERENCE'][dataStatistic] = abs(docX1['STATISTICS_NORM'][dataStatistic] - docX2['STATISTICS_NORM'][dataStatistic])
                        tmpX['X1']['MAGNETIC'] = tmpMagnetic

            for docX3 in tList[2]:

                for docX2 in tList[1]:
                    if 'RSSI_DATA' in docX3.viewkeys() and 'RSSI_DATA' in docX2.viewkeys():
                        if docX3['MAC_AP'] == docX2['MAC_AP']:
                            tmpAp = {}
                            tmpAp['STATISTICS_DIFFERENCE'] = {}
                            for dataStatistic in self.STATISTIC_NAME:
                                tmpAp['STATISTICS_DIFFERENCE'][dataStatistic] = abs(docX3['STATISTICS'][dataStatistic] - docX2['STATISTICS'][dataStatistic])
                            tmpX['X3'][docX3['MAC_AP']] = tmpAp

                    if 'MAGNETIC_DATA' in docX3.viewkeys() and 'MAGNETIC_DATA' in docX2.viewkeys():
                        tmpMagnetic = {}
                        tmpMagnetic['MAGNETIC'] = 'MAGNETIC'
                        tmpMagnetic['STATISTICS_DIFFERENCE'] = {}
                        for dataStatistic in self.STATISTIC_NAME:
                            tmpMagnetic['STATISTICS_DIFFERENCE'][dataStatistic] = abs(docX3['STATISTICS_NORM'][dataStatistic] - docX2['STATISTICS_NORM'][dataStatistic])
                        tmpX['X3']['MAGNETIC'] = tmpMagnetic
            statisticResult[y]['X1'] = tmpX['X1']
            statisticResult[y]['X3'] = tmpX['X3']

        msg = 'Which data statistic do ypu want to see?\n' + str(self.STATISTIC_NAME)
        while(True):
            time.sleep(1)
            anws  = int(raw_input(msg))
            if anws == 'q':
                break
            for y in y_side_stat:
                for x in x_stat_border:
                    dataType = ''
                    tX = 'X' + str(x)
                    #print str(statisticResult[y][tX])
                    print 'Y: ' + str(y) + ' X: ' + str(x) + ' DOCTYPE: ' + 'MAGNETIC - diff = ' + str(statisticResult[y][tX]['MAGNETIC']['STATISTICS_DIFFERENCE'][self.STATISTIC_NAME[anws]])
                    for mac in self.mac_distinct:
                        print 'Y: ' + str(y) + ' X: ' + str(x) + ' AP: ' + mac + ' - diff = ' + str(statisticResult[y][tX][mac]['STATISTICS_DIFFERENCE'][self.STATISTIC_NAME[anws]])
###############################################################################

    def menu(self):
        msq = """
        quit(q)
        repair x coordinates(0)
        copy side cordinates(1)
        drop sideStatistic(2)
        drop and load again data(3)
        create missing docs in fingerprint(4)"""
        while(True):
            time.sleep(1)
            anws = raw_input(msq)
            if anws == 'q':
                break
            elif anws == '0':
                self.repairXCoordiante()
            elif anws == '1':
                self.copyDataSideStatistic()
            elif anws == '2':
                self.dropSideStatistic()
            elif anws == '3':
                self.dropKopalniaFingerprint()
            elif anws == '4':
                self.createMissingDocumentsInMap()

if __name__ == '__main__':
    CleanDataKopalniaFingerprint().menu()
