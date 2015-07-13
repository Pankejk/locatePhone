from pymongo import MongoClient

def main():
    conn = MongoClient()

    while(True):
        msg = 'q - quit. All databases: ' + str(conn.database_names()) + '\n' + 'Choose database: '
        anw = raw_input(msg)
        if anw == 'q':
            conn.close()
            break
        db = conn[anw]
        msg = 'q - quit. All colletions: ' + str(db.collection_names()) + '\n' + 'Choose collection: '
        anw = raw_input(msg)
        if anw == 'q':
            conn.close()
            break

if __name__ == '__main__':
    main()
