from pymongo import MongoClient
import sys

class CleanData(object):

    def __init__(self,collName):
        self.collName = collName

        self.conn = MongoClient()
        self.db_fingerprint = self.conn['fingerprint']
        self.db_locate = self.conn['locate']
        self.coll_fingerprint = self.db_fingerprint[self.collName]
        self.coll_locate = self.db_locate[self.collName]

        '''distinct values'''
        self.x_distinct = self.coll_fingerprint.distinct('X')
        self.y_distinct = self.coll_fingerprint.distinct('Y')
        self.locationCp_distinct = self.coll_locate.distinct('CHECKPOINT')
        self.macAp_fingerprint_distinct = self.coll_fingerprint.distinct('MAC_AP')
        self.macAp_locate_distinct = self.coll_locate.distinct('MAC_AP')

    def __del__(self):
        self.conn.close()

    """method shows information about data in fingerprint map and in checkpoint data"""
    def printInfoAboutData(self):
        print 'DISCTINCT X COORDINATES: ' + str(self.x_distinct) + ' Length: ' + str(len(self.x_distinct))
        print 'DISCTINCT Y COORDINATES: ' + str(self.y_distinct) + ' Length: ' + str(len(self.y_distinct))
        print 'DISTINCT CHECKPOINTS: ' + str(self.locationCp_distinct) + ' Length: ' + str(len(self.locationCp_distinct))
        print 'DISTINCT APs MAC in fingerprint: ' + str(self.macAp_fingerprint_distinct) + ' Length: ' + str(len(self.macAp_fingerprint_distinct))
        print 'DISTINCT APs MAC in locate: ' + str(self.macAp_locate_distinct) + ' Length: ' + str(len(self.macAp_locate_distinct))
        print ''
##############################################################################
    '''methods that check if necessary is removing doubuled data
    or some magnetic documents are missing'''
###############################################################################
    '''methods for fingerprint db'''

    ''' method shows missing magnetic documents in fingerprint map'''
    def isMagneticMissingFingerprint(self):
        cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}})
        docs = [res for res in cursor]
        size = len(self.x_distinct)*len(self.y_distinct)
        #print self.x_distinct
        #print self.y_distinct
        msg = 'Found %s MAGNETIC DOCUMENTS. SHOULD BE: %s' % (len(docs),size)
        print msg

        counterList = []
        self.preapreListDictonaryCoordinatesMagneticFingerprint(counterList)
        for doc in docs:
            for counterDic in counterList:
                if doc['X'] == counterDic['X'] and doc['Y'] == counterDic['Y']:
                    counterDic['COUNTER'] += 1
        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        for dic in counterList:
            if dic['COUNTER'] == 0:
                print 'X: ' + str(dic['X']) + ' Y: ' + str(dic['Y']) + 'NUMBER OF DUCUMENTS: ' + str(dic['COUNTER'])

    ''' method shows dubled magnetic documents in fingerprint map'''
    def isMagneticDoubledFingerprint(self):
        cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}})
        docs = [res for res in cursor]
        #print len(self.x_distinct)
        #print ''
        print len(self.x_distinct)
        print ''
        print len(self.y_distinct)
        print 'Found %s MAGNETIC DOCUMENTS. SHOULD BE: %s' % (len(docs),len(self.x_distinct)*len(self.y_distinct))

        counterList = []
        self.preapreListDictonaryCoordinatesMagneticFingerprint(counterList)
        for doc in docs:
            for counterDic in counterList:
                if doc['X'] == counterDic['X'] and doc['Y'] == counterDic['Y']:
                    counterDic['COUNTER'] += 1
        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        counter = 0
        deleteCoordinates = []
        for dic in counterList:
            if dic['COUNTER'] > 1:
                print 'X: ' + str(dic['X']) + ' Y: ' + str(dic['Y']) + 'NUMBER OF DUCUMENTS: ' + str(dic['COUNTER'])
                deleteCoordinates.append(dic)
                counter += 1

        anws = raw_input('Found %s dubled magnetic documents. Do you want to delete unnecessary documents from positons?(y/n)' % counter)

        if anws == 'y':
            for dic in deleteCoordinates:
                cursor = self.coll_fingerprint.find({'MAGNETIC_DATA': {'$exists': True}, 'X': dic['X'], 'Y': dic['Y']})
                docs = [res for res in cursor]
                print len(docs)
                self.coll_fingerprint.delete_one({'_id': docs[0]['_id']})
        elif anws == 'n':
            pass


    ''' method shows dubled RSSI documents in fingerprint map'''
    def isRssiDoubledFingerprint(self):

        counterList = []
        self.preapreListDictonaryCoordinatesRssiFingerprint(counterList)
        for mac_distinct in self.macAp_fingerprint_distinct[0:1]:
            cursor = self.coll_fingerprint.find({'RSSI_DATA': {'$exists': True}, 'MAC_AP': mac_distinct})
            docs = [res for res in cursor]
            print len(docs)
            for doc in docs:
                for dic in counterList:
                    if dic['MAC_AP'] == doc['MAC_AP'] and dic['X'] == doc['X'] and dic['Y'] == doc['Y']:
                        dic['COUNTER'] += 1

        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        counter = 0
        deleteCoordinates = []
        for dic in counterList:
            if dic['COUNTER'] > 1:
                print 'MAC_AP: ' + dic['MAC_AP'] + ' X: ' + str(dic['X']) + ' Y: ' + str(dic['Y']) + 'NUMBER OF DUCUMENTS: ' + str(dic['COUNTER'])
                deleteCoordinates.append(dic)
                counter += 1
        anws = raw_input('Found %s dubled rssi documents. Do you want to delete unnecessary documents from positons?(y/n)' % counter)

        if anws == 'y':
            for dic in deleteCoordinates:
                cursor = self.coll_fingerprint.find({'RSSI_DATA': {'$exists': True}, 'MAC_AP': dic['MAC_AP'], 'X': dic['X'], 'Y': dic['Y']})
                docs = [res for res in cursor]
                self.coll_fingerprint.delete_one({'_id': docs[0]['_id']})
        elif anws == 'n':
            pass
#################################################################################################################################################################
    '''methods for locate db '''

    ''' method shows missing magnetic documents in fingerprint map'''
    def isMagneticMissingLocate(self):

        counterList = []
        self.preapreListDictonaryCoordinatesMagneticLocate(counterList)
        for cp in self.locationCp_distinct:
            cursor = self.coll_locate.find({'MAGNETIC_DATA': {'$exists': True},'CHECKPOINT': cp})
            docs = [res for res in cursor]
            msg = 'For checkpoint: %s found %s MAGNETIC DOCUMENTS. SHOULD BE: %s' % (cp,len(docs),1)
            print msg
            for doc in docs:
                for counterDic in counterList:
                    if doc['CHECKPOINT'] == counterDic['CHECKPOINT']:
                        counterDic['COUNTER'] += 1

            for dic in counterList:
                if dic['COUNTER'] == 0:
                    print 'CHECKPOINT MISSING MAGNETIC: ' + cp + ' NUMBER OF DUCUMENTS: ' + str(dic['COUNTER'])

    ''' method shows dubled magnetic documents in fingerprint map'''
    def isMagneticDoubledLocate(self):
        counterList = []
        self.preapreListDictonaryCoordinatesMagneticLocate(counterList)
        for cp in self.locationCp_distinct:
            cursor = self.coll_locate.find({'MAGNETIC_DATA': {'$exists': True},'CHECKPOINT': cp})
            docs = [res for res in cursor]
            print 'For checkpoint: %s found %s MAGNETIC DOCUMENTS. SHOULD BE: %s' % (cp,len(docs),1)
            for doc in docs:
                for counterDic in counterList:
                    if doc['CHECKPOINT'] == counterDic['CHECKPOINT']:
                        counterDic['COUNTER'] += 1
        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        counter = 0
        deleteCoordinates = []
        for dic in counterList:
            if dic['COUNTER'] > 1:
                print 'For checkpoint:' + dic['CHECKPOINT'] +  ' found duplicated documents: ' + str(dic['COUNTER'])
                deleteCoordinates.append(dic)
                counter += 1

        anws = raw_input('Found %s dubled magnetic documents in locate. Do you want to delete unnecessary documents from checkpoints?(y/n)' % counter)

        if anws == 'y':
            for dic in deleteCoordinates:
                cursor = self.coll_locate.find({'MAGNETIC_DATA': {'$exists': True}, 'CHECKPOINT': dic['CHECKPOINT']})
                docs = [res for res in cursor]
                self.coll_fingerprint.delete_one({'_id': docs[0]['_id']})
        elif anws == 'n':
            pass


    ''' method shows dubled RSSI documents in fingerprint map'''
    def isRssiDoubledLocate(self):

        counterList = []
        self.preapreListDictonaryCoordinatesRssiLocate(counterList)
        for cp in self.locationCp_distinct:

            for mac_distinct in self.macAp_locate_distinct:
                cursor = self.coll_fingerprint.find({'RSSI_DATA': {'$exists': True}, 'MAC_AP': mac_distinct, 'CHECKPOINT': cp})
                docs = [res for res in cursor]
            for doc in docs:
                for dic in counterList:
                    if dic['MAC_AP'] == doc['MAC_AP'] and dic['CHECKPOINT'] == doc['CHECKPOINT']:
                        dic['CUNTER'] += 1

        print 'FOR EACH POSITION FOUND NUMBER OF DOCUMENTS:'

        counter = 0
        deleteCoordinates = []
        for dic in counterList:
            if dic['COUNTER'] > 1:
                print 'CHECKPOINT: ' + cp + 'MAC_AP: ' + dic['MAC_AP'] + ' DUBLED NUMBER OF DUCUMENTS: ' + str(dic['COUNTER'])
                deleteCoordinates.append(dic)
                counter += 1

#        showNumberOfDcumentsOnCoordinates self documents in locate. Do you want to delete unnecessary documents from positons?(y/n)' % counter)
#'MAGNETIcursor = self.coll_fingerprint.find({})
#        docs = [res for res in cursor]
#        print len(docs)
#
#        counterList = []
#        for x in self.x_distinct:
#            for y in self.y_distinct:
#                tmpDict = {}
#                tmpDict['X'] = x
#                tmpDict['Y'] = y
#                tmpDict['COUNTER'] = 0
#                counterList.append(tmpDict)
#
#        for doc in docs:
#            for dic in counterList:
#                if doc['X'] == dic['X'] and doc['Y'] == dic['Y']:
#                    dic['COUNTER'] += 1
#        for dic in countery_distinct:
#                    print dic
#                    tmpDict['Y'] = y
#                    tmpDict['COUNTER'] = 0
#                counterList.append(tmpDict)

#        for doc in docs:
#            for dic in counterList:
#                if doc['X'] == dic['X'] and doc['Y'] == dic['Y']:
#                    dic['COUNTER'] += 1
#        for dic in counterList:
#            if dic['COUNTER'] > 4:
#                print dic
################################################################################
    ''' preparing list for fingerprint db'''

    '''method which prepares list of dict coordiantes - magnetic'''
    def preapreListDictonaryCoordinatesMagneticFingerprint(self,tList):
        for x in self.x_distinct:
            for y in self.y_distinct:
                tmp = {}
                tmp['X'] = x
                tmp['Y'] = y
                tmp['COUNTER'] = 0
                tList.append(tmp)

    '''method which prepares list of dict coordiantes - RSSI'''
    def preapreListDictonaryCoordinatesRssiFingerprint(self, counterList):
        for mac in self.macAp_fingerprint_distinct:
            for x in self.x_distinct:
                for y in self.y_distinct:
                    tmp = {}
                    tmp['MAC_AP'] = mac
                    tmp['X'] = x
                    tmp['Y'] = y
                    tmp['COUNTER'] = 0
                    counterList.append(tmp)
###############################################################################
    ''' preparing lists for locate db'''
###############################################################################
    '''method which prepares list of dict coordiantes - magnetic'''
    def preapreListDictonaryCoordinatesMagneticLocate(self,tList):
        for cp in self.locationCp_distinct:
            tmp = {}
            tmp['CHECKPOINT'] = cp
            tmp['COUNTER'] = 0
            tList.append(tmp)

    '''method which prepares list of dict coordiantes - RSSI'''
    def preapreListDictonaryCoordinatesRssiLocate(self, counterList):
        for cp in self.locationCp_distinct:
            for mac in self.macAp_fingerprint_distinct:
                tmp = {}
                tmp['CHECKPOINT'] = cp
                tmp['MAC_AP'] = mac
                tmp['COUNTER'] = 0
                counterList.append(tmp)
###############################################################################

    '''method which implements menu for script'''
    def menu(self):
        msg = '''
        quit -q,
        0 - check if magnetic data is missing - fingerprint,
        1 - if magnetic data is doubled - fingerprint,
        2 - if rssi is doubled - fingerprint
        3 - check if magnetic data is missing - locate,
        4 - if magnetic data is doubled - locate,
        5 - if rssi is doubled -locate
        6 - show number of documents per coordinate in fingerprint map'''
        while(True):
            anws = raw_input(msg)
            if anws == 'q':
                break
            elif anws == '0':
                self.isMagneticMissingFingerprint()
            elif anws == '1':
                self.isMagneticDoubledFingerprint()
            elif anws == '2':
                self.isRssiDoubledFingerprint()
            elif anws == '3':
                self.isMagneticMissingLocate()
            elif anws == '4':
                self.isMagneticDoubledLocate()
            elif anws == '5':
                self.isRssiDoubledLocate()
            elif anws == '6':
                pass#self.showNumberOfDcumentsOnCoordinates()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        collName = sys.argv[1]
        cleanData = CleanData(collName)
        cleanData.menu()
    else:
        sys.exit('Script requires 2 args, given: %s' % len(sys.argv))
