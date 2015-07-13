from pymongo import MongoClient

conn = MongoClient()

db_fingerprint = conn['fingerprint']
doc_fingerprint = db_fingerprint['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].distinct('MAC_AP')

db_locate = conn['locate']
doc_locate = db_locate['kuznia1_DATASIZE:200_STEP:3_1_DEFAULT'].distinct('MAC_AP')

theSame_fingerprint = []
theSame_locate = []
diffrent_fingerprint = []
diffrent_locate = []

for item in doc_fingerprint:
    if item in doc_locate:
        theSame_fingerprint.append(item)

for item in doc_locate:
    if item in doc_fingerprint:
        theSame_locate.append(item)

count = 0
diffrent_fingerprint = list(doc_fingerprint)
for item in diffrent_fingerprint:
    if item in theSame_fingerprint:
        #print item 
        diffrent_fingerprint.remove(item)
        #count += 1
        #print count
diffrent_fingerprint = list(doc_fingerprint)
for item in diffrent_fingerprint:
    if item in theSame_fingerprint:
        #print item 
        diffrent_fingerprint.remove(item)
        #count += 1
        #print count


diffrent_locate = list(doc_locate)
for item in diffrent_locate:
    if item in theSame_locate:
        diffrent_locate.remove(item)
            
        
print 'FINGERPRINT DISTINCT AP: ' + str(len(doc_fingerprint))
print 'LOCATE DISTINCT AP: ' + str(len(doc_locate))
print 'THE SAME AP IN FINGERPRINT - SIZE:' + str(len(theSame_fingerprint))
print 'THE SAME AP IN LOCATE - SIZE:' + str(len(theSame_locate))

print 'DIFFRENT AP IN FINGERPRINT - SIZE:' + str(len(diffrent_fingerprint))
print 'DIFFRENT AP IN LOCATE - SIZE:' + str(len(diffrent_locate))

#fd = open('ap.txt', 'w')

#fd.write('AP - FINGERPRINT - ALL \n\n')
#for item in doc_fingerprint:
#    fd.write(item + '\n')

#fd.write('\n\n AP - FINGERPRINT - THE SAME\n\n')
#for item in theSame_fingerprint:
#    fd.write(item + '\n')

#fd.write('\n\n AP - FINGERPRINT - DIFFRENT\n\n')
#for item in diffrent_fingerprint:
#    fd.write(item + '\n')
    
#fd.close()


#print 'DIFFRENT AP LOCATE - SIZE:' + str(len(diffrent1))
#for item in diffrent:
#    print item