from pymongo import MongoClient
import time
import sys

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
        self.coll_locate = self.db_fingerprint[self.collName]

        self.availableCollections = str(self.db_fingerprint.collection_names())
        self.x_distinct = self.coll.distinct('X')
        self.y_distinct = self.coll.distinct('Y')
        self.mac_ap_distinct = self.coll.distinct('MAC_AP')
        self.chceckpoints = self.coll
        self.step = self.coll.distinct('STEP')

        self.menu()

    ''' destructor '''
    def __del__(self):
        self.conn.close()
#############################################################################################################################################################
    ''' method to communicate with menu'''

    '''method returns msg for choosing ap'''
    def availableAp(self):
        return 'ALL AP -' + str(self.mac_ap_distinct) + '\nchoose from 0 to %s ' % str(len(self.mac_ap_distinct) -1)
##############################################################################################################################################################
    '''method draws fingerprint for certain AP'''
    def drawFingerprintAp(self,chosenAp):
        cursor = self.coll.find({'MAC_AP' : self.mac_ap_distinct[chosenAp]})
        docs = [res for res in cursor]
        drawList = {'X': [], 'Y': [],'RSSI': []}
        for doc in docs:
            #print 'X:' + str(doc['X']) + ' Y: ' + str(doc['Y'])
            #print 'STEP X: ' + str(self.step[0]) + 'STEP Y: ' + str(self.step[1])
            tmp1 = np.arange(doc['X'],doc['X'] + self.step[0],0.2).tolist()

            #drawList['X'].append(tmp1)
            tmp2 = np.arange(doc['Y'],doc['Y'] + self.step[1],0.3).tolist()
            #print tmp2
            #drawList['Y'].append(tmp2)
            size = len(tmp1)
            tmp1  = self.preapreBetterDrawing(tmp1,size,'X')
            tmp2 = self.preapreBetterDrawing(tmp2,size,'Y')
            print len(tmp1)
            print len(tmp2)
            tmp = [doc['STATISTICS']['MEAN']]* len(tmp1)
            print len(tmp)
            self.appendDrawList(tmp1,drawList['X'])
            self.appendDrawList(tmp2,drawList['Y'])
            self.appendDrawList(tmp,drawList['RSSI'])
            #drawList['RSSI'].append(tmp)
            #drawList['X']append(doc['X'])
            #drawList['Y']append(doc['Y'])
            #drawList['RSSU']append(doc['STATISTICS']['MEAN'])
        print 'X length: %s' % len(drawList['X'])
        print 'Y length: %s' % len(drawList['Y'])
        print 'RSSI length: %s'% len(drawList['RSSI'])
        #print drawList['X']
        #print drawList['Y']
        #print drawList['RSSI']
        plt.scatter(drawList['X'], drawList['Y'], c=drawList['RSSI'])
        plt.show()

    '''method draws magnetic fingerprint'''
    def drawFingerprintMagnetic(self):
        cursor = self.coll.find({'STATISTICS_NORM': {'$exists': True}})
        docs = [res for res in cursor]
        drawList = {'X': [], 'Y': [],'MAGNETIC': []}

        for doc in docs:
            tmp1 = np.arange(doc['X'],doc['X'] + self.step[0],0.2).tolist()
            tmp2 = np.arange(doc['Y'],doc['Y'] + self.step[1],0.3).tolist()
            size = len(tmp1)
            tmp1  = self.preapreBetterDrawing(tmp1,size,'X')
            tmp2 = self.preapreBetterDrawing(tmp2,size,'Y')
            tmp = [doc['STATISTICS_NORM']['MEAN']]* len(tmp1)
            #print len(tmp)
            self.appendDrawList(tmp1,drawList['X'])
            self.appendDrawList(tmp2,drawList['Y'])
            self.appendDrawList(tmp,drawList['MAGNETIC'])
        plt.scatter(drawList['X'], drawList['Y'], c=drawList['MAGNETIC'])
        plt.show()

    def showCpOnFingerpintAp(self, arg):
        pass

######################################################################################################################
    '''methods to preapre drawing fingerprint maps - RSSI MAGNETIC '''

    '''method append list for drawing'''
    def appendDrawList(self,tList,mainList):
        for t in tList:
            mainList.append(t)

    ''''method for preapring good drawing'''
    def preapreBetterDrawing(self,tList,length, choice):
        tmp = []
        if choice == 'X':
            for t in tList:
                for i in range(0,length):
                    tmp.append(t)
            #print tList
        elif choice == 'Y':
            for i in range(0,length):
                for t in tList:
                    tmp.append(t)
        return tmp
##########################################################################################################################
    def menu(self):

        while(True):
            time.sleep(1)
            msg = 'MAGNETIC(0) OR AP FINGERPRINT(1) or QUIT(q)'
            anws = raw_input(msg)

            if anws == 'q':
                sys.exit(0)
                break
            elif anws == '0':
                self.drawFingerprintMagnetic()
            elif anws == '1':
                anws = int(raw_input(self.availableAp()))
                self.drawFingerprintAp(anws)
if __name__ == '__main__':
    if len(sys.argv)  == 2:
        collName = sys.argv[1]
        drawFingerprint = DrawFingerprint(collName)
        drawFingerprint.menu()
    else:
        sys.exit('NOT GOOD NUMBER OF ARGS')
