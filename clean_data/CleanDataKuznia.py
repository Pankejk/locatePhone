from pymongo import MongoClient
import os
from math import sqrt
import numpy as np
import scipy.stats


class CleanDataKuznia(object):

    def __init__(self):

        self.conn = MongoClient()
        db_fingerprint = self.conn['fingerprint']
        db_locate = self.conn['locate']
        self.coll_fingerprint = db_fingerprint['kuznia1']
        self.coll_locate = db_locate['kuznia1']

        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.mac_ap_fingerprint_distinct = self.coll_fingerprint.distinct('MAC_AP')
        self.mac_ap_locate_distinct = self.coll_locate.distinct('MAC_AP')
        self.checkpoints_distinct = self.coll_locate.distinct('CHECKPOINT')
        self.STATISTIC_NAME = ["MEAN" , "STANDARD_DEVIATION", "MAX", "MIN", "MEDIANA", "MODE",
        "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50",
        "PERCENTILE - 70",  "PERCENTILE - 90"]

    def __del__(self):
        self.conn.close()

###############################################################################
    """methods which are usefull for the rest of function"""
    def countStatisticsData(self, tList):
        array = np.array(tList)
        meanV = np.mean(tList)
        standardDeviation = np.std(tList)
        maxV = max(tList)
        minV = min(tList)
        medianaV = np.median(tList)
        tmp = list(scipy.stats.mode(tList))
        modeV = tmp[0].tolist()[0]

        percentile10 = np.percentile(array, 10)
        percentile20 = np.percentile(array, 20)
        percentile50 = np.percentile(array, 50)
        percentile70 = np.percentile(array, 70)
        percentile90 = np.percentile(array, 90)
        statisticsDict = {"MEAN" : meanV,"STANDARD_DEVIATION" : standardDeviation,
        "MAX" : maxV, "MIN" : minV, "MEDIANA" : medianaV, "MODE" : modeV,
        "PERCENTILE - 10" : percentile10,"PERCENTILE - 20" : percentile20,
        "PERCENTILE - 50" : percentile50,  "PERCENTILE - 70" : percentile70,
        "PERCENTILE - 90" : percentile90 }

        return statisticsDict

    '''method which prepares list of dict coordiantes - magnetic'''
    def preapreListDictonaryCoordinatesMagneticFingerprint(self,tList):
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmp = {}
                tmp['X'] = x
                tmp['Y'] = y
                tmp['COUNTER'] = 0
                tList.append(tmp)

    """method preapres dictonry to gain documents for recover missing documents"""
    def preapreListDictonaryForRecoverMissingDocuments(self,tList):
        for dic in tList:
            dic['RECOVER_DOCUMENTS'] = []

    #""" method creates json documents to save in fingerprint map magnetic"""
    #def preapreJsonDocuments(self, tList, size):
    #    for i in range(size):
    #        tmpDic = {}
    #        tmpDic['STATISTICS'] = {'PERCENTILE - 90': 0, "PERCENTILE - 20" : 0,
    #        "MIN" : 0, "PERCENTILE - 10" : 0, "STANDARD_DEVIATION" : 0,
    #        "PERCENTILE - 70" : 0, "PERCENTILE - 50" : 0, "MODE" : 0,
    #        "MAX" : 0, "MEDIANA" : 0, "MEAN" : 0}
#
#            tmpDic["MAGNETIC_AVG_TIME"] = "25484"
#
#            tmpDic["STATISTICS_NORM"] = { "PERCENTILE - 90" : 0, "MIN" : 0,
#              "STANDARD_DEVIATION" : 0, "PERCENTILE - 20" : 0,
#              "PERCENTILE - 10" : 0, "MAX" : 0, "PERCENTILE - 70" : 0,
#              "PERCENTILE - 50" : 0, "MODE" : 0, "MEDIANA" : 0, "MEAN" : 0}
#
#            tmpDic["MAC_PHONE"] = "e8:99:c4:8e:97:36"
#            tmpDic["STEP"] = [2,3]
#            tmpDic["PLACE"] = "kuznia1"
#            tmpDic["MODE"] = "FEED_MAP"
#            tmpDic["IP_PHONE"] = "192.168.1.100"
#            tmpDic["TIMESTAMP"] = "2015-07-02:14-20-09.540"
#            tmpDic["Y"] = 0
#            tmpDic["X"] = 0
#            tmpDic["MAGNETIC_DATA_NORM"] = []
#            tmpDic["MAGNETIC_DATA"] = []
#            tmpDic["DATA_SIZE"] = 200
#            tmpDic["HASH"] = "DEFAULT"

#            tList.append(tmpDic)

    #"""method creates ditonary for keeping data statistics for recoverd documents"""
    #def preapreDictonaryStatistic(self, tDict):
    #    tDict = {}
    #    for dataStatistics in self.STATISTIC_NAME:
    #        tDict[]
###############################################################################
    """method changes filed POSITIONS to seperate x and y. changes step to
    true value"""
    def chnageFiledPositionToXAndY(self):
        count = 0
        docList=[]
        for document in self.coll_fingerprint.find({}):
            pos = document['POSITIONS']
            document.update({'X' : pos[0]})
            document.update({'Y' : pos[1]})
            document['STEP'] = [2,3]
            self.coll_fingerprint.save(document)
            count += 1
        print 'MODIFIED: ' + str(count)
        self.coll_fingerprint.update({}, {'$unset': {'POSITIONS':1}}, multi=True)

        for document in self.coll_locate.find({}):
            document['STEP'] = [2,3]
            self.coll_locate.save(document)

    """method deletes invalid y coordinate = 39"""
    def deleteInvalidYCoordinate(self):
        cursor = self.coll_fingerprint.find({ 'Y' : 39})
        for doc in cursor:
            self.coll_fingerprint.delete_one({'_id' : doc['_id']})
        print 'DOCUMENTS WITH Y 39 REMOVED -' +  str(self.coll_fingerprint.count())

    """method counts norm and statistic for norm"""
    def countNormAndStatistics(self):
        for doc in self.coll_fingerprint.find({}):
            if  'MAGNETIC_DATA' in doc.viewkeys():
                tmp = doc['MAGNETIC_DATA']
                norm = []
                print 'RAW DATA SIZE: ' +  str(len(tmp))
                for i in range(0,len(tmp),3):
                    norm.append(sqrt(pow(tmp[i],2) + pow(tmp[i+1],2) + pow(tmp[i+2],2)))
                    print 'DATA NORM SIZE: ' +  str(len(norm))
                    doc['MAGNETIC_DATA_NORM'] = norm
                dataStatistics = self.countStatisticsData(doc['MAGNETIC_DATA_NORM'])
                doc['STATISTICS_NORM'] = dataStatistics
                self.coll_fingerprint.save(doc)

        for doc in self.coll_locate.find({}):
            if  'MAGNETIC_DATA' in doc.viewkeys():
                tmp = doc['MAGNETIC_DATA']
                norm = []
                print 'RAW DATA SIZE: ' +  str(len(tmp))
                for i in range(0,len(tmp),3):
                    norm.append(sqrt(pow(tmp[i],2) + pow(tmp[i+1],2) + pow(tmp[i+2],2)))
                    print 'DATA NORM SIZE: ' +  str(len(norm))
                    doc['MAGNETIC_DATA_NORM'] = norm
                dataStatistics = self.countStatisticsData(doc['MAGNETIC_DATA_NORM'])
                doc['STATISTICS_NORM'] = dataStatistics
                self.coll_locate.save(doc)

    """method create missing magnetic doc files in magnetic fingerprint"""
    def createMissingMagneticDocuments(self):
        cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}})
        docs = [res for res in cursor]
        size = len(self.x_distinct)*len(self.y_distinct)

        msg = 'Found %s MAGNETIC DOCUMENTS. SHOULD BE: %s' % (len(docs),size)
        print msg

        missingMagneticDocuments = []
        self.preapreListDictonaryCoordinatesMagneticFingerprint(missingMagneticDocuments)
        for doc in docs:
            for counterDic in missingMagneticDocuments:
                if doc['X'] == counterDic['X'] and doc['Y'] == counterDic['Y']:
                    counterDic['COUNTER'] += 1
        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        missingMagneticDocuments = [dic for dic in missingMagneticDocuments if dic['COUNTER'] == 0]
        print 'Number of missing documents: ' + str(len(missingMagneticDocuments))

        self.preapreListDictonaryForRecoverMissingDocuments(missingMagneticDocuments)
        for dic in missingMagneticDocuments:
            xBefore = dic['X'] - 2
            xAfter = dic['X'] + 2
            yBefore = dic['Y'] - 3
            yAfter = dic['Y'] + 3
            docs = []
            cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}, 'X': xBefore, 'Y': dic['Y']})
            tmpDocs = [res for res in cursor]
            for doc in tmpDocs:
                docs.append(doc)
            cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}, 'X': xAfter, 'Y': dic['Y']})
            tmpDocs = [res for res in cursor]
            for doc in tmpDocs:
                docs.append(doc)
            cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}, 'X': dic['X'], 'Y': yBefore})
            tmpDocs = [res for res in cursor]
            for doc in tmpDocs:
                docs.append(doc)
            cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}, 'X': dic['X'], 'Y': yAfter})
            tmpDocs = [res for res in cursor]
            for doc in tmpDocs:
                docs.append(doc)
            dic['RECOVER_DOCUMENTS'] = docs

        for doc in missingMagneticDocuments:
            print 'X: ' +  str(doc['X'])
            print 'Y: ' +  str(doc['Y'])
            print len(doc['RECOVER_DOCUMENTS'])
            raw_input()

        recoverdDocuments = []
        for dic in missingMagneticDocuments:
            tmplist = dic['RECOVER_DOCUMENTS']

            tmpDic = {}
            tmpDic['STATISTICS'] = {'PERCENTILE - 90': 0, "PERCENTILE - 20" : 0,
            "MIN" : 0, "PERCENTILE - 10" : 0, "STANDARD_DEVIATION" : 0,
            "PERCENTILE - 70" : 0, "PERCENTILE - 50" : 0, "MODE" : 0,
            "MAX" : 0, "MEDIANA" : 0, "MEAN" : 0}

            tmpDic["MAGNETIC_AVG_TIME"] = "25484"

            tmpDic["STATISTICS_NORM"] = { "PERCENTILE - 90" : 0, "MIN" : 0,
              "STANDARD_DEVIATION" : 0, "PERCENTILE - 20" : 0,
              "PERCENTILE - 10" : 0, "MAX" : 0, "PERCENTILE - 70" : 0,
              "PERCENTILE - 50" : 0, "MODE" : 0, "MEDIANA" : 0, "MEAN" : 0}

            tmpDic["MAC_PHONE"] = "e8:99:c4:8e:97:36"
            tmpDic["STEP"] = [2,3]
            tmpDic["PLACE"] = "kuznia1"
            tmpDic["MODE"] = "FEED_MAP"
            tmpDic["IP_PHONE"] = "192.168.1.100"
            tmpDic["TIMESTAMP"] = "2015-07-02:14-20-09.540"
            tmpDic["Y"] = dic['Y']
            tmpDic["X"] = dic['X']
            tmpDic["MAGNETIC_DATA_NORM"] = []
            tmpDic["MAGNETIC_DATA"] = []
            tmpDic["DATA_SIZE"] = 200
            tmpDic["HASH"] = "DEFAULT"

            for recoverDoc in tmplist:
                for dataStatistics in self.STATISTIC_NAME:
                    tmpDic['STATISTICS'][dataStatistics] += recoverDoc['STATISTICS'][dataStatistics]
                    tmpDic["STATISTICS_NORM"][dataStatistics] += recoverDoc["STATISTICS_NORM"][dataStatistics]

            for dataStatistics in self.STATISTIC_NAME:
                tmpDic['STATISTICS'][dataStatistics] /= float(len(tmplist))
                tmpDic["STATISTICS_NORM"][dataStatistics] /= float(len(tmplist))
            recoverdDocuments.append(tmpDic)

        print 'BEFORE INSERTING MISSING DOCUMENTS: ' + str(self.coll_fingerprint.count())
        for recoverDoc in recoverdDocuments:
            self.coll_fingerprint.save(recoverDoc)
        print 'AFTER INSERTING MISSING DOCUMENTS: ' + str(self.coll_fingerprint.count())

###############################################################################
    """method drops fingeprint collection and load raw data again"""
    def dropAndLoadDataFingerprint(self):
        self.coll_fingerprint.drop()
        os.system('mongoimport --db fingerprint --collection kuznia1 --file ../data-backup/kuznia1_DATASIZE_200_STEP_3_1_DEFAULT_fingerprint_2.07.15.json')

    """method drops locate collection and load raw data again"""
    def dropAndLoadDatalocate(self):
        self.coll_locate.drop()
        os.system('mongoimport --db locate --collection kuznia1 --file ../data-backup/kuznia1_DATASIZE_200_STEP_3_1_DEFAULT_locate_2.07.15.json')
###############################################################################

    def menu(self):

        while(True):
            anws = raw_input('''
            q - quit
            0 - drop and load data fingeprint - kuznia
            1 - drop and load data locate - kuznia
            2 - change filed POSITINS to X and Y and (STEP to [2,3] - finger/locate)
            3 - delete invalid y = 39 coordinate
            4 - count norm and statistic for norm - magnetic - finger/locate
            5 - add mising documnets to magnetic fingerprint map''')

            if anws == 'q':
                break
            elif anws == '0':
                self.dropAndLoadDataFingerprint()
            elif anws == '1':
                self.dropAndLoadDatalocate()
            elif anws == '2':
                self.chnageFiledPositionToXAndY()
            elif anws == '3':
                self.deleteInvalidYCoordinate()
            elif anws == '4':
                self.countNormAndStatistics()
            elif anws == '5':
                self.createMissingMagneticDocuments()

if __name__ == '__main__':
    CleanDataKuznia().menu()
