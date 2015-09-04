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
        plt.title('RSSI[dbm] - ' + self.mac_ap_distinct[chosenAp])
        plt.xlabel('width [m]')
        plt.ylabel('length [m]')
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
        plt.title('MAGNETIC[mikroT]')
        plt.xlabel('width [m]')
        plt.ylabel('length [m]')
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
        plt.title("Histogram - whole map magnetic")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
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
        plt.title("Histogram - whole map RSSI")
        plt.xlabel("Value")
        plt.ylabel("Frequency")
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
        plt.title("Cumulative distribution - whole map magnetic")
        plt.xlabel("Value")
        plt.ylabel("Probability")
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
        plt.title("Cumulative distribution - whole map RSSI")
        plt.xlabel("Value")
        plt.ylabel("Probability")
        #plt.ylim(0,5)
        plt.show()
        
        
    def drawHistogramPostionsMagnetic(self):
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
        
        valueList = np.asarray(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title("Histogram - x= %s,y= %s - magnetic" % (postions[0],postions[1]))
        plt.xlabel("Value")
        plt.ylabel("Frequency")
        plt.ylim(0,5)
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
        
        valueList = np.asarray(valueList)
        plt.hist(valueList, histtype='stepfilled')
        plt.title("Histogram - x= %s,y= %s - RSSI" % (postions[0],postions[1]))
        plt.xlabel("Value")
        plt.ylabel("Frequency")
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
        plt.title("Cumulative distribution - x= %s,y= %s - magnetic" % (postions[0],postions[1]))
        plt.xlabel("Value")
        plt.ylabel("Probability")
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
        plt.title("Cumulative distribution - x= %s,y= %s - RSSI")
        plt.xlabel("Value")
        plt.ylabel("Probability")
        #plt.ylim(0,5)
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
                pass
if __name__ == '__main__':
    if len(sys.argv)  == 2:
        collName = sys.argv[1]
        drawFingerprint = DrawFingerprint(collName)
    else:
        sys.exit('NOT GOOD NUMBER OF ARGS')
