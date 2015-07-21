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
        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE",
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
            4 - count norm and statistic for norm - magnetic - finger/locate''')

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

if __name__ == '__main__':
    CleanDataKuznia().menu()
