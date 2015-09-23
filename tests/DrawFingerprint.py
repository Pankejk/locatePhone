# -*- coding: utf-8 -*-

from pymongo import MongoClient
import time
import sys

from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import numpy as np
import matplotlib.pyplot as plt

import scipy.stats as stats

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
        self.map_name = ['MAGNETIC', 'RSSI']

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
        plt.title('RSSI [dBm] - ' + self.mac_ap_distinct[chosenAp])
        plt.xlabel(u'szerokość [m]')
        plt.ylabel(u'długość [m]')
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
        plt.title(u'POLE MAGNETYCZNE [μT]')
        plt.xlabel(u'szerokość [m]')
        plt.ylabel(u'długość [m]')
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
    def drawHistogramWholeMapMagnetic(self):
        
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['MAGNETIC_DATA_NORM']:
                valueList.append(value)
        
        valueList = np.asarray(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title(u"Histogram - cała mapa POLA MAGNETYCZNEGO")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Częstotliwość")
        #plt.ylim(0,5)
        plt.show()
        
    def drawHistogramWholeMapRssi(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))

        mac = self.mac_ap_distinct[macIndex]
        
        cursor = self.coll.find({'RSSI_DATA' : {'$exists': True}, 'MAC_AP': mac})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['RSSI_DATA']:
                valueList.append(value)
        
        valueList = np.asarray(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title(u"Histogram - cała mapa RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Częstotliwość")
        #plt.ylim(0,5)
        plt.show()
        
    def drawCumuLativeDistributionWholeMapMagnetic(self):
        
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['MAGNETIC_DATA_NORM']:
                valueList.append(value)
        
        #valueList = np.asarray(valueList)
            
        valueList=np.sort( valueList )
        yvals=np.arange(len(valueList))/float(len(valueList))
        print valueList
        print yvals
        plt.plot( valueList, yvals )
        plt.title(u"Dystrybuanta - cała mapa POLA MAGNETYCZNEGO")
        plt.xlabel(u"Wartosć [μT]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
            
            
            
    def drawCumuLativeDistributionWholeMapRssi(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))
        
        mac = self.mac_ap_distinct[macIndex]
        
        cursor = self.coll.find({'RSSI_DATA' : {'$exists': True}, 'MAC_AP': mac})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['RSSI_DATA']:
                valueList.append(value)
        
        valueList=np.sort( valueList )
        yvals=np.arange(len(valueList))/float(len(valueList))
        print valueList
        print yvals
        plt.plot( valueList, yvals )
        plt.title(u"Dystrybuanta - cała mapa RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        
    def drawHistogramPostionsMagnetic(self):
        postions = raw_input('''X - %s\n Y - %s\n choose postions (x y)''' % (str(self.x_distinct),str(self.y_distinct)))
        postions = postions.split(' ')
        postions[0] = int(postions[0])
        postions[1] = int(postions[1])
        #print postions
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}, 'X': postions[0], 'Y': postions[1]})
        docs = [res for res in cursor]
        
        print len(docs)
        print len(docs[0]['MAGNETIC_DATA'])
        valueList = []
        for doc in docs:
            for value in doc['MAGNETIC_DATA_NORM']:
                valueList.append(value)
        
        valueList = np.asarray(valueList)
        print len(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title("Histogram - x= %s,y= %s - POLE MAGNETYCZNE" % (postions[0],postions[1]))
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Częstotliwość")
        plt.ylim(0,280)
        plt.show()
        
        
    def drawHistogramPositionsRssi(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))
        postions = raw_input('''X - %s\n Y - %s\n choose postions (x y)''' % (str(self.x_distinct),str(self.y_distinct)))
        postions = postions.split(' ')
        postions[0] = int(postions[0])
        postions[1] = int(postions[1])
        
        mac = self.mac_ap_distinct[macIndex]
        
        cursor = self.coll.find({'RSSI_DATA' : {'$exists': True}, 'MAC_AP': mac, 'X': postions[0], 'Y': postions[1]})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['RSSI_DATA']:
                valueList.append(value)
        print valueList
        valueList = np.asarray(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title("Histogram - x= %s,y= %s - RSSI - %s" % (postions[0],postions[1], mac))
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Częstotliwość")
        #plt.ylim(0,5)
        plt.show()
        
        
    def drawCumuLativeDistributionPositionsMagnetic(self):
        postions = raw_input('''X - %s\n Y - %s\n choose postions (x y)''' % (str(self.x_distinct),str(self.y_distinct)))
        postions = postions.split(' ')
        postions[0] = int(postions[0])
        postions[1] = int(postions[1])
        
        cursor = self.coll.find({'MAGNETIC_DATA' : {'$exists': True}, 'X': postions[0], 'Y': postions[1]})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['MAGNETIC_DATA_NORM']:
                valueList.append(value)
        
        #valueList = np.asarray(valueList)
            
        valueList=np.sort( valueList )
        yvals=np.arange(len(valueList))/float(len(valueList))
        print valueList
        print yvals
        plt.plot( valueList, yvals )
        plt.title("Dystrybuanta - x= %s,y= %s - POLE MAGNETYCZNE" % (postions[0],postions[1]))
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
    def drawCumuLativeDistributionPositionsRssi(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))
        postions = raw_input('''X - %s\n Y - %s\n choose postions (x y)''' % (str(self.x_distinct),str(self.y_distinct)))
        postions = postions.split(' ')
        postions[0] = int(postions[0])
        postions[1] = int(postions[1])
        
        mac = self.mac_ap_distinct[macIndex]
        
        cursor = self.coll.find({'RSSI_DATA' : {'$exists': True}, 'MAC_AP': mac, 'X': postions[0], 'Y': postions[1]})
        docs = [res for res in cursor]
        
        valueList = []
        for doc in docs:
            for value in doc['RSSI_DATA']:
                valueList.append(value)
        
        valueList=np.sort( valueList )
        yvals=np.arange(len(valueList))/float(len(valueList))
        print valueList
        print yvals
        plt.plot( valueList, yvals )
        plt.title("DYSTRYBUANATA - x= %s,y= %s - RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
    def drawHistogramSideMagneticKopalnia(self):
        docsX1 = []
        docsX2 = []
        docsX3 = []

        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 1})
        docsX1 = [res for res in cursor]
        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 2})
        docsX2 = [res for res in cursor]
        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 3})
        docsX3 = [res for res in cursor]
        
        valueListX1 = []
        valueListX2 = []
        valueListX3 = []
        
        for doc in docsX1:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX1.append(value)
        
        for doc in docsX2:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX2.append(value)
        
        for doc in docsX3:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX3.append(value)
                
        valueListX1 = np.asarray(valueListX1)
        valueListX2 = np.asarray(valueListX2)
        valueListX3 = np.asarray(valueListX3)
        
        plt.hist(valueListX1)
        plt.title("Histogram - POLE MAGNETYCNE - kopalnia - x = 1")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
        plt.hist(valueListX2)
        plt.title("Histogram - POLE MAGNETYCZNE - kopalnia - x = 2")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
        plt.hist(valueListX3)
        plt.title("Histogram - POLE MAGNETYCZNE - kopalnia - x = 3")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
    def drawHistogramSideRssiKopalnia(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))
        mac = self.mac_ap_distinct[macIndex]
        
        docsX1 = []
        docsX2 = []
        docsX3 = []

        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 1, 'MAC_AP': mac})
        docsX1 = [res for res in cursor]
        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 2, 'MAC_AP': mac})
        docsX2 = [res for res in cursor]
        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 3, 'MAC_AP': mac})
        docsX3 = [res for res in cursor]
        
        valueListX1 = []
        valueListX2 = []
        valueListX3 = []
        
        for doc in docsX1:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX1.append(value)
        
        for doc in docsX2:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX2.append(value)
        
        for doc in docsX3:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX3.append(value)
                
        valueListX1 = np.asarray(valueListX1)
        valueListX2 = np.asarray(valueListX2)
        valueListX3 = np.asarray(valueListX3)
        
        plt.hist(valueListX1)
        plt.title("Histogram - RSSI - kopalnia - x = 1 - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
        plt.hist(valueListX2)
        plt.title("Histogram - RSSI - kopalnia - x = 2 - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
        plt.hist(valueListX3)
        plt.title("Histogram - RSSI - kopalnia - x = 3 - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Częstotliwość")
        plt.show()
        
    def drawCumulativeDistributionSideMagneticKopalnia(self):
        docsX1 = []
        docsX2 = []
        docsX3 = []

        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 1})
        docsX1 = [res for res in cursor]
        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 2})
        docsX2 = [res for res in cursor]
        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}, 'X': 3})
        docsX3 = [res for res in cursor]
        
        valueListX1 = []
        valueListX2 = []
        valueListX3 = []
        
        for doc in docsX1:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX1.append(value)
        
        for doc in docsX2:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX2.append(value)
        
        for doc in docsX3:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                valueListX3.append(value)
                
        valueListX1 = np.sort(valueListX1)
        yvalsX1=np.arange(len(valueListX1))/float(len(valueListX1))
        valueListX2 = np.sort(valueListX2)
        yvalsX2=np.arange(len(valueListX2))/float(len(valueListX2))
        valueListX3 = np.sort(valueListX3)
        yvalsX3=np.arange(len(valueListX3))/float(len(valueListX3))
        
        
        plt.plot( valueListX1, yvalsX1 )
        plt.title("Dystrybuanta - x = 1 - POLE MAGNETYCZNE")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        plt.plot( valueListX2, yvalsX2 )
        plt.title("Dystrybuanta - x = 2 - POLE MAGNETYCZNE")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        plt.plot( valueListX3, yvalsX3 )
        plt.title("Dystrybuanta - x = 3 - POLE MAGNETYCZNE")
        plt.xlabel(u"Wartość [μT]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        
    def drawCumulativeDistributionSideRssiKopalnia(self):
        macIndex = int(raw_input('''%s\nChoose mac address(0-%s)''' % (str(self.mac_ap_distinct),len(self.mac_ap_distinct) - 1)))
        mac = self.mac_ap_distinct[macIndex]
        
        docsX1 = []
        docsX2 = []
        docsX3 = []

        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 1, 'MAC_AP': mac})
        docsX1 = [res for res in cursor]
        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 2, 'MAC_AP': mac})
        docsX2 = [res for res in cursor]
        cursor = self.coll.find({'RSSI_DATA': {'$exists': True}, 'X': 3, 'MAC_AP': mac})
        docsX3 = [res for res in cursor]
        
        valueListX1 = []
        valueListX2 = []
        valueListX3 = []
        
        for doc in docsX1:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX1.append(value)
        
        for doc in docsX2:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX2.append(value)
        
        for doc in docsX3:
            tmpList = doc['RSSI_DATA']
            for value in tmpList:
                valueListX3.append(value)
                
        valueListX1 = np.sort(valueListX1)
        yvalsX1=np.arange(len(valueListX1))/float(len(valueListX1))
        valueListX2 = np.sort(valueListX2)
        yvalsX2=np.arange(len(valueListX2))/float(len(valueListX2))
        valueListX3 = np.sort(valueListX3)
        yvalsX3=np.arange(len(valueListX3))/float(len(valueListX3))
        
        
        plt.plot( valueListX1, yvalsX1 )
        plt.title(u"Dystrybuanta - x = 1 - RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        plt.plot( valueListX2, yvalsX2 )
        plt.title(u"Dystrybuanta - x = 2 - RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
        plt.plot( valueListX3, yvalsX3 )
        plt.title(u"Dystrybuanta - x = 3 - RSSI - " + mac)
        plt.xlabel(u"Wartość [dBm]")
        plt.ylabel(u"Prawdopodobieństwo")
        #plt.ylim(0,5)
        plt.show()
        
    def testIfDataFitNormalDistribution(self):
        cursor = self.coll.find({'MAGNETIC_DATA': {'$exists': True}})
        allMagneticDocs = [res for res in cursor]
        
        positionMagneticAnws = []
        allMagneticAnws = {'value': [],'statistic': 0, 'pvalue': 0}
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmpDic = {}
                tmpDic['X'] = x
                tmpDic['Y'] = y
                tmpDic['TEST_ANWS'] = {'value': [],'statistic': 0, 'pvalue': 0}
                positionMagneticAnws.append(tmpDic)
                
        for doc in allMagneticDocs:
            tmpList = doc['MAGNETIC_DATA_NORM']
            for value in tmpList:
                allMagneticAnws['value'].append(value)
            
            for dic in positionMagneticAnws:
                if dic['X'] == doc['X'] and dic['Y'] == doc['Y']:
                    dic['TEST_ANWS']['value'] = tmpList
                    
        allMagneticAnws['statistic'], allMagneticAnws['pvalue'] = stats.normaltest(allMagneticAnws['value'])
        
        for dic in positionMagneticAnws:
            if dic['TEST_ANWS']['value'] == []:
                print dic['X']
                print dic['Y']
                print dic['TEST_ANWS']['value']
                continue
            dic['TEST_ANWS']['statistic'], dic['TEST_ANWS']['pvalue'] = stats.normaltest(dic['TEST_ANWS']['value'])
            
        print 'MAGNETIC NORM TEST FOR DATA FOR WHOLE MAP'
        print 'statistic: ' + str(allMagneticAnws['statistic'])
        print 'pvalue: ' + str(allMagneticAnws['pvalue'])
        
        print
        print 'MAGNETIC NORM TEST FOR EACH REFERENCE POINT ON MAP'
        print
        
        for dic in positionMagneticAnws:
            print 'X: ' + str(dic['X']) + ', Y: ' + str(dic['Y']) + ' - statistic: ' + str(dic['TEST_ANWS']['statistic']) + ', pvalue: ' + str(dic['TEST_ANWS']['pvalue'])
            print

        
###############################################################################
    def menu(self):

        while(True):
            time.sleep(1)
            anws = raw_input('''
            q - quit
            0 - show magnetic fingerprint
            1 - show rssi fingerprint
            2 - draw heatmap rssi
            3 - draw heatmap magnetic
            4 - draw histogram - whole map - rssi
            5 - draw histogram - whole map - magnetic
            6 - draw distribution - whole map - rssi
            7 - draw distribution - whole map - magnetic
            8 - draw histogram - choose positions - rssi
            9 - draw histogram - choose positions - magnetic
            10 - draw distribution - choose positions - rssi
            11 - draw distribution - choose positions - magnetic
            12 - test if data fits normal distribution
            13 - draw side histogram - magnetic - kopalnia
            14 - draw side histogram - RSSI - kopalnia
            15 - draw side cumulative distribution - magnetic - kopalnia
            16 - draw side cumulative distribution - RSSI - kopalnia
            ''')

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
            elif anws == '4':
                self.drawHistogramWholeMapRssi()
            elif anws == '5':
                self.drawHistogramWholeMapMagnetic()
            elif anws == '6':
                self.drawCumuLativeDistributionWholeMapRssi()
            elif anws == '7':
                self.drawCumuLativeDistributionWholeMapMagnetic()
            elif anws == '8':
                self.drawHistogramPositionsRssi()
            elif anws == '9':
                self.drawHistogramPostionsMagnetic()
            elif anws == '10':
                self.drawCumuLativeDistributionPositionsRssi()
            elif anws == '11':
                self.drawCumuLativeDistributionPositionsMagnetic()
            elif anws == '12':
                self.testIfDataFitNormalDistribution()
            elif anws == '13':
                self.drawHistogramSideMagneticKopalnia()
            elif anws == '14':
                self.drawHistogramSideRssiKopalnia()
            elif anws == '15':
                self.drawCumulativeDistributionSideMagneticKopalnia()
            elif anws == '16':
                self.drawCumulativeDistributionSideRssiKopalnia()
if __name__ == '__main__':
    if len(sys.argv)  == 2:
        collName = sys.argv[1]
        drawFingerprint = DrawFingerprint(collName)
    else:
        sys.exit('NOT GOOD NUMBER OF ARGS')
