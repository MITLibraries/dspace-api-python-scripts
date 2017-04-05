import json
import requests
import secrets

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
headerAuthFileUpload = {'accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

#Post community
communityName = 'Test Community'
community = json.dumps({'name': communityName})
post = requests.post(baseURL+'/rest/communities', headers=headerAuth, data=community).json()
print post
communityID = post['link']
print communityID

# #Post collection
collectionName = 'Test Collection'
collection = json.dumps({'name': collectionName})
post = requests.post(baseURL+communityID+'/collections', headers=headerAuth, data=collection).json()
print post
collectionID = post['link']

#Post item
item = json.dumps({'metadata': [{'key': 'dc.title', 'language': 'en_US', 'value': 'testing123'}]})
post = requests.post(baseURL+collectionID+'/items', headers=headerAuth, data=item).json()
print post
itemID = post['link']

#Post bitstream
#bitstream = filePath+'test.txt'
bitstream = filePath+'testImage.jpg'
fileName = bitstream[bitstream.rfind('/')+1:]
files = {'file': open(bitstream, 'rb')}
data = json.dumps({'name': fileName, 'sequenceId': 1})
post = requests.post(baseURL+itemID+'/bitstreams', headers=headerAuthFileUpload, files=files).json()
print post
bitstreamID = '/rest/bitstreams/'+str(post['id'])
post = requests.put(baseURL+bitstreamID, headers=headerAuth, data=data)
print post

# print baseURL+itemID+'/metadata'
# item = json.dumps([{'key': 'dc.title', 'language': 'en_US', 'value': 'testing123'}])
# post = requests.post(baseURL+itemID+'/metadata', headers=headerAuth, data=item).json()
# print post

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)
