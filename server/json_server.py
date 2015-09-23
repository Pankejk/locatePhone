import os
import json
from datetime import datetime
from SaveMongo import *

localDir = os.path.dirname(__file__)
absDir = os.path.join(os.getcwd(), localDir)
insertData = SaveMongo()
import cherrypy

class FileDemo(object):

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def index(self):
		data = cherrypy.request.json
		#print type(data)
		#print data
		#print len(data)
		#for i in  data:
		#	print i
		#	print type(i)
        #tmpFile = '/home/mike/Desktop/praca_magisterska/workspace/data_' + str(datetime.now()) + '.json'
        #tmpFile.replace(' ','_')
        #print tmpFile
        #fd = open(tmpFile, 'w')
        #fd.write(json.dumps(data))
        #fd.close()
		insertData.saveData(data)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def out (self):
        return {'key': 'value'}
    #index.exposed = True

tutconf = os.path.join(os.path.dirname(__file__), 'tutorial.conf')
cherrypy.config.update({'server.socket_host': '192.168.1.101',
                        'server.socket_port': 8080,
                                               })
if __name__ == '__main__':
    # CherryPy always starts with app.root when trying to map request URIs
    # to objects, so we need to mount a request handler root. A request
    # to '/' will be mapped to HelloWorld().index().
    cherrypy.quickstart(FileDemo(), config=tutconf)
else:
    # This branch is for the test suite; you can ignore it.
    cherrypy.tree.mount(FileDemo(), config=tutconf)
