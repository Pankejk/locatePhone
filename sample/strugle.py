#self.collection_received.insert(jsonFile)
		#jsonFile = self.collection_received.find({})
		#options = CodecOptions(document_class=jsonFile.OrderedDict)
		#jsonFile = json_util.loads(str(jsonFile))
		#bson.BSON.decode(jsonFile, codec_options=options)
		#for i in jsonFile:
			#print type(i)
			#print i
		#for j in jsonFile:
		#	print type(j)
		#	print j
		#dictonary = json.load(jsonFile)
		#for k in jsonFile[0]:
		#	print k
		#	tmp = jsonFile[0][k]
		#	k = unicodedata.normalize('NFKD', k).encode('ascii','ignore')
		#	if k == "_id":
		#		continue
		#	dictonary[k] = unicodedata.normalize('NFKD', tmp).encode('ascii','ignore')
		#self.collection_received.remove()
		#d = {}
		#for k,v in jsonFile.items():
		#	print k
		#	print v
		#	tmpK = ast.literal_eval(k)#json.loads(k)
		#	tmpV = json.loads(unicodedata.normalize('NFKD', v).encode('ascii','ignore'))
		#	d[tmpK] = tmpV
