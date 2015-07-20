"""script changes x to be in set x[1,3] for intger.
Then it copies all data wich are statistic for left and right side data."""

from pymongo import MongoClient
import os
import time

import matplotlib.pyplot as plt
from numpy.random import normal

class CleanDataKopalniaFingerprint(object):

    """class is used  for  reaprinfd broken fingerprint map - rssi, magnetic"""
    def __init__(self):

        self.conn = MongoClient()
        db = self.conn['fingerprint']
        self.coll = db['kopalnia_DATASIZE_200']

        self.STATISTIC_NAME = ["MEAN", "STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE", "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50", "PERCENTILE - 70",  "PERCENTILE - 90"]
        self.mac_distinct = self.coll.distinct('MAC_AP')
        self.y_side_stat = [0,20,40,60,80,100]
        self.x_stat = [1,2,3]
        self.x_stat_border = [1,3]

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
        docs = {}
        for y in self.y_side_stat:
            docs[y] = {}
            for x in self.x_stat:
                docs[y][x] = []
                cursor = self.coll.find({'Y': y, 'X': x})
                tmpDocs = [res for res in cursor]
                print 'For Y = ' + str(y) + ' and X = ' + str(x) + ' Found number of documents: ' + str(len(tmpDocs))
                docs[y][x] = tmpDocs

        docList = {}
        for y in self.y_side_stat:
            docList[y] = []
            for x in self.x_stat:
                docList[y].append(docs[y][x])

        statisticResult = {}
        for y in self.y_side_stat:
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
            for y in self.y_side_stat:
                for x in self.x_stat_border:
                    dataType = ''
                    tX = 'X' + str(x)
                    #print str(statisticResult[y][tX])
                    print 'Y: ' + str(y) + ' X: ' + str(x) + ' DOCTYPE: ' + 'MAGNETIC - diff = ' + str(statisticResult[y][tX]['MAGNETIC']['STATISTICS_DIFFERENCE'][self.STATISTIC_NAME[anws]])
                    for mac in self.mac_distinct:
                        print 'Y: ' + str(y) + ' X: ' + str(x) + ' AP: ' + mac + ' - diff = ' + str(statisticResult[y][tX][mac]['STATISTICS_DIFFERENCE'][self.STATISTIC_NAME[anws]])

    """method draws hostogram for certain x and y anf for certain AP and magnetic data"""
    def drawHistogramForSideStatistics(self, chooseY):

        docsX1 = []
        docsX2 = []
        docsX3 = []

        cursor = self.coll.find({'Y': chooseY, 'X': 1})
        docsX1 = [res for res in cursor]
        cursor = self.coll.find({'Y': chooseY, 'X': 2})
        docsX2 = [res for res in cursor]
        cursor = self.coll.find({'Y': chooseY, 'X': 3})
        docsX3 = [res for res in cursor]

        dicX1 = {}
        for doc in docsX1:
            if 'RSSI_DATA' in doc.viewkeys():
                dicX1[doc['MAC_AP']] = doc['RSSI_DATA']
            elif 'MAGNETIC_DATA_NORM' in doc.viewkeys():
                dicX1['MAGNETIC'] = doc['MAGNETIC_DATA_NORM']
        dicX2 = {}
        for doc in docsX2:
            if 'RSSI_DATA' in doc.viewkeys():
                dicX2[doc['MAC_AP']] = doc['RSSI_DATA']
            elif 'MAGNETIC_DATA_NORM' in doc.viewkeys():
                dicX2['MAGNETIC'] = doc['MAGNETIC_DATA_NORM']
        dicX3 = {}
        for doc in docsX3:
            if 'RSSI_DATA' in doc.viewkeys():
                dicX3[doc['MAC_AP']] = doc['RSSI_DATA']
            elif 'MAGNETIC_DATA_NORM' in doc.viewkeys():
                dicX3['MAGNETIC'] = doc['MAGNETIC_DATA_NORM']
        while(True):
            time.sleep(1)
            anwsMac = ''
            anwsX = raw_input('Avaiable x=%s\nWhich x do you want?' % self.x_stat)
            anws = raw_input('Magnetic(0) or RSSI(1)?')
            dataChosen = []
            if anws == '1':
                anwsMac = int(raw_input('Avaiable RSSI - %s\nWhich do you want(0-%s)?'%(str(self.mac_distinct),len(self.mac_distinct) - 1)))
            if anwsX == 'q':
                break
            elif anwsX == '1':
                if anws == '0':
                    dataChosen = dicX1['MAGNETIC']
                elif anws == '1':
                    dataChosen = dicX1[self.mac_distinct[anwsMac]]
            elif anwsX == '2':
                if anws == '0':
                    dataChosen = dicX2['MAGNETIC']
                elif anws == '1':
                    dataChosen = dicX2[self.mac_distinct[anwsMac]]
            elif anwsX == '3':
                if anws == '0':
                    dataChosen = dicX3['MAGNETIC']
                elif anws == '1':
                    dataChosen = dicX3[self.mac_distinct[anwsMac]]
            plt.hist(dataChosen)
            plt.title("Histogram")
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.show()

    def drawHistogramForAllYCoordinates(self):
        #dataDocs = {}

        histogramData = {}
        self.preapreDictForHistogram(histogramData)
        for x in self.x_stat:
            for y in self.y_side_stat:
                cursor = self.coll.find({'Y': y, 'X': x})
                docs = [res for res in cursor]
                for doc in docs:
                    if 'RSSI_DATA' in doc.viewkeys():
                        self.appendData(histogramData[x][doc['MAC_AP']], doc['RSSI_DATA'])
                    elif 'MAGNETIC_DATA_NORM' in doc.viewkeys():
                        self.appendData(histogramData[x]['MAGNETIC'], doc['MAGNETIC_DATA_NORM'])
        while(True):
            time.sleep(1)
            anwsMac = ''
            anwsX = raw_input('Avaiable x=%s\nWhich x do you want?' % self.x_stat)
            anws = raw_input('Magnetic(0) or RSSI(1)?')
            dataChosen = []
            if anws == '1':
                anwsMac = int(raw_input('Avaiable RSSI - %s\nWhich do you want(0-%s)?'%(str(self.mac_distinct),len(self.mac_distinct) - 1)))
            if anwsX == 'q':
                break
            elif anwsX == '1':
                if anws == '0':
                    dataChosen = histogramData[1]['MAGNETIC']
                elif anws == '1':
                    dataChosen = histogramData[1][self.mac_distinct[anwsMac]]
            elif anwsX == '2':
                if anws == '0':
                    dataChosen = histogramData[2]['MAGNETIC']
                elif anws == '1':
                    dataChosen = histogramData[2][self.mac_distinct[anwsMac]]
            elif anwsX == '3':
                if anws == '0':
                    dataChosen = histogramData[3]['MAGNETIC']
                elif anws == '1':
                    dataChosen = histogramData[3][self.mac_distinct[anwsMac]]
            plt.hist(dataChosen)
            plt.title("Histogram")
            plt.xlabel("Value")
            plt.ylabel("Frequency")
            plt.show()

###############################################################################
    """method prepares dictonary with data for Histogram for whole y coordinate"""
    def preapreDictForHistogram(self, tDic):
        for x in self.x_stat:
            tDic[x] = {}
            tDic[x]['MAGNETIC'] = []
            for mac in self.mac_distinct:
                tDic[x][mac] = []
    """append data list"""
    def appendData(self,tList, cList):
        for item in cList:
            tList.append(item)
###############################################################################

    def menu(self):
        msq = """
        quit(q)
        repair x coordinates(0)
        copy side cordinates(1)
        drop sideStatistic(2)
        drop and load again data(3)
        create missing docs in fingerprint(4)
        create histograms for side(5)
        draw histogram for all y coordinates(6)"""
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
            elif anws == '5':
                anws = int(raw_input('Y to choose - %s\nChoose y(0,%s)'% ( str(self.y_side_stat),len(self.y_side_stat,)-1)))
                self.drawHistogramForSideStatistics(anws)
            elif anws == '6':
                self.drawHistogramForAllYCoordinates()

if __name__ == '__main__':
    CleanDataKopalniaFingerprint().menu()
