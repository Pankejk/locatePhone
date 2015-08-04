from pymongo import MongoClient

class CheckCollection(object):

    def __init__(self):
        self.conn = MongoClient()
        self.dbList = self.conn.database_names()

    def __del__(self):
        self.conn.close()

################################################################################
    """menu"""
    def menu(self):
        while(True):
            msg = 'q - quit. All databases: ' + str(self.dbList) + '\n' + 'Choose database(0-%s): ' %(len(self.dbList) - 1)
            anw = int(raw_input(msg))
            db = self.conn[self.dbList[anw]]
            collList = db.collection_names()
            msg = 'q - quit. All colletions: ' + str(collList) + '\n' + 'Choose collection(0-%s): ' % (len(collList) - 1)
            anw = int(raw_input(msg))
            coll = db[collList[anw]]
            msg = 'q - quit. enter query to find: '
            anw = raw_input(msg)
            if anw == 'q':
                break
            anw = anw.split(' ')
            cursor = coll.find({anw[0]: anw[1]})
            docs = [res for res in cursor]
            for doc in docs:
                print doc


################################################################################

if __name__ == '__main__':
    CheckCollection().menu()
