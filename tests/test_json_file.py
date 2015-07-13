import json
from requests import Request, Session
data = {u'temperature':u'24.3'}
data['list'] = [0,3,1,4,1,7.890]
data_json = json.dumps(data)
#r = requests.post('http://192.168.1.21/index', data=data_json)
s = Session()
r= Request('POST','http://192.168.1.15:8080', data=data_json, headers={'content-type' : 'application/json'})
prepped = s.prepare_request(r)
#prepped.headers = 'application/json'
#prepped.data=data_json
resp = s.send(prepped)
#print resp.content
#print resp.headers
