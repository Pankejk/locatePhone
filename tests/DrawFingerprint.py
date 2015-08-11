from pymongo import MongoClient
import time
import sys

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt

class DrawFingerprint(object):

    ''' constructor'''
    def __init__(self,collName):
        self.collName = collName

        self.conn = MongoClient()
        self.db_fingerprint = self.conn['fingerprint']
        self.db_locate = self.conn['locate']
        self.coll = self.db_fingerprint[self.collName]
        self.coll_locate = self.db_locate[self.collName]

        self.availableCollections = str(self.db_fingerprint.collection_names())
        self.x_distinct = self.coll.distinct('X')
        if self.collName == 'kopalnia_DATASIZE_200':
            self.x_distinct.append(1)
            self.x_distinct.append(3)
        self.y_distinct = self.coll.distinct('Y')
        self.x_distinct.sort()
        self.y_distinct.sort()
        self.mac_ap_distinct = self.coll.distinct('MAC_AP')
        self.chceckpoints = self.coll_locate.distinct('CHECKPOINT')
        self.step = self.coll.distinct('STEP')
        self.STATISTIC_NAME = ["MEAN" , "MAX", "MIN", "MEDIANA", "MODE",
        "PERCENTILE - 10", "PERCENTILE - 20", "PERCENTILE - 50",
        "PERCENTILE - 70",  "PERCENTILE - 90"]

        self.menu()

    ''' destructor '''
    def __del__(self):
        self.conn.close()
###############################################################################
    ''' method to communicate with menu'''

    '''method returns msg for choosing ap'''
    def availableAp(self):
        return 'ALL AP -' + str(self.mac_ap_distinct) + '\nchoose from 0 to %s ' % str(len(self.mac_ap_distinct) -1)
###############################################################################
    '''method draws fingerprint for certain AP - plot_surface'''
    def drawFingerprintAp(self,chosenAp):
        anws  = int(raw_input('''%s\nChoose data statistics(0-%s)''' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))

        drawArray = {'X': 0, 'Y': 0,'RSSI': 0}
        drawArray['X'] = np.asarray(self.x_distinct)
        drawArray['Y'] = np.asarray(self.y_distinct)
        drawArray['X'], drawArray['Y'] = np.meshgrid(drawArray['X'],drawArray['Y'])

        rssiList = []
        for y in self.y_distinct:
            for x in self.x_distinct:
                cursor = self.coll.find({'MAC_AP' : self.mac_ap_distinct[chosenAp], 'X': x, 'Y': y})
                docs = [res for res in cursor]
                if len(docs) == 0:
                    rssiList.append(-100)
                elif len(docs) == 1:
                    rssiList.append(docs[0]['STATISTICS'][self.STATISTIC_NAME[anws]])
        
        if self.collName == 'kopalnia_DATASIZE_200':
            for i in range(0,len(rssiList),len(self.x_distinct)):
                if rssiList[i] == -100:
                    rssiList[i] = rssiList[i+1]
                    rssiList[i + len(self.x_distinct) - 1] = rssiList[i+1]
                    
        finalList = []
        for i in range(0,len(rssiList),len(self.x_distinct)):
            finalList.append(rssiList[i:i+len(self.x_distinct)])

        drawArray['RSSI'] = np.asarray(finalList)
        drawArray['RSSI'] = drawArray['RSSI'].reshape(drawArray['X'].shape)

        print drawArray['X']
        print drawArray['Y']
        print drawArray['RSSI']
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        surf = ax.plot_surface(drawArray['X'], drawArray['Y'], drawArray['RSSI'],rstride=1, cstride=1, alpha=1,cmap=cm.jet,  linewidth=0)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.show()

    '''method draws magnetic fingerprint - plot_surface'''
    def drawFingerprintMagnetic(self):
        anws  = int(raw_input('''%s\nChoose data statistics(0-%s)''' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))

        drawArray = {'X': 0, 'Y': 0,'MAGNETIC': 0}
        drawArray['X'] = np.asarray(self.x_distinct)
        drawArray['Y'] = np.asarray(self.y_distinct)
        drawArray['X'], drawArray['Y'] = np.meshgrid(drawArray['X'],drawArray['Y'])

        rssiList = []
        for y in self.y_distinct:
            for x in self.x_distinct:
                cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}, 'X': x, 'Y': y})
                docs = [res for res in cursor]
                if len(docs) == 0:
                    rssiList.append(0)
                elif len(docs) == 1:
                    rssiList.append(docs[0]['STATISTICS_NORM'][self.STATISTIC_NAME[anws]])
        
        if self.collName == 'kopalnia_DATASIZE_200':
            for i in range(0,len(rssiList),len(self.x_distinct)):
                if rssiList[i] == 0:
                    rssiList[i] = rssiList[i+1]
                    rssiList[i + len(self.x_distinct) - 1] = rssiList[i+1]
        
        finalList = []
        for i in range(0,len(rssiList),len(self.x_distinct)):
            finalList.append(rssiList[i:i+len(self.x_distinct)])
        
        drawArray['MAGNETIC'] = np.asarray(finalList)

        print drawArray['X']
        print drawArray['Y']
        print drawArray['MAGNETIC']
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        surf = ax.plot_surface(drawArray['X'], drawArray['Y'], drawArray['MAGNETIC'],rstride=1, cstride=1, alpha=1,cmap=cm.jet,  linewidth=0)
        fig.colorbar(surf, shrink=0.5, aspect=5)
        plt.show()

    """method draws heat map for certain AP"""
    def drawHeatmapAp(self,chosenAp):
        anws  = int(raw_input('''%s\nChoose data statistics(0-%s)''' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))

        drawArray = {'RSSI': 0}

        rssiList = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                cursor = self.coll.find({'MAC_AP' : self.mac_ap_distinct[chosenAp], 'X': x, 'Y': y})
                docs = [res for res in cursor]
                if len(docs) == 0:
                    rssiList.append(0)
                elif len(docs) == 1:
                    rssiList.append(docs[0]['STATISTICS'][self.STATISTIC_NAME[anws]])
        finalList = []
        for i in range(0,len(rssiList),len(self.x_distinct)):
            finalList.append(rssiList[i:i+len(self.x_distinct)])

        drawArray['RSSI'] = np.asarray(finalList)

        x = []
        y = []
        for tx in self.x_distinct:
            x.append(str(tx))
        for ty in self.y_distinct:
            y.append(str(ty))

        plt.pcolor(drawArray['RSSI'])
        plt.yticks(np.arange(0,len(self.y_distinct)),y)
        plt.xticks(np.arange(0,len(self.x_distinct)),x)
        plt.show()

    """method draws heat map for magnetic field"""
    def drawHeatmapMagnetic(self):
        anws  = int(raw_input('''%s\nChoose data statistics(0-%s)''' % (str(self.STATISTIC_NAME),len(self.STATISTIC_NAME) - 1)))

        drawArray = {'MAGNETIC': 0}

        rssiList = []
        for x in self.x_distinct:
            for y in self.y_distinct:
                cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}, 'X': x, 'Y': y})
                docs = [res for res in cursor]
                if len(docs) == 0:
                    rssiList.append(0)
                elif len(docs) == 1:
                    rssiList.append(docs[0]['STATISTICS_NORM'][self.STATISTIC_NAME[anws]])
        finalList = []
        for i in range(0,len(rssiList),len(self.x_distinct)):
            finalList.append(rssiList[i:i+len(self.x_distinct)])

        drawArray['MAGNETIC'] = np.asarray(finalList)

        x = []
        y = []
        for tx in self.x_distinct:
            x.append(str(tx))
        for ty in self.y_distinct:
            y.append(str(ty))

        plt.pcolor(drawArray['MAGNETIC'])
        plt.yticks(np.arange(0,len(self.y_distinct)),y)
        plt.xticks(np.arange(0,len(self.x_distinct)),x)
        plt.show()

###############################################################################
    def menu(self):

        while(True):
            time.sleep(1)
            anws = raw_input('''
            q - quit
            0 - show magnetic fingerprint
            1 - show rssi fingerprint
            2 - draw heatmap rssi
            3 - draw heatmap magnetic''')

            if anws == 'q':
                break
            elif anws == '0':
                self.drawFingerprintMagnetic()
            elif anws == '1':
                anws = int(raw_input(self.availableAp()))
                self.drawFingerprintAp(anws)
            elif anws == '2':
                anws = int(raw_input(self.availableAp()))
                self.drawHeatmapAp(anws)
            elif anws == '3':
                self.drawHeatmapMagnetic()
if __name__ == '__main__':
    if len(sys.argv)  == 2:
        collName = sys.argv[1]
        drawFingerprint = DrawFingerprint(collName)
        drawFingerprint.menu()
    else:
        sys.exit('NOT GOOD NUMBER OF ARGS')
