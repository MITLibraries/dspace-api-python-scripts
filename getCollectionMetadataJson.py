import json
import requests
import secrets
import time

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

handle = raw_input('Enter handle: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
startTime = time.time()

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=headerAuth).json()
collectionID = collection['id']
collectionTitle = requests.get(endpoint, headers=headerAuth).json()
endpoint = baseURL+'/rest/collections/'+str(collectionID)+'/items'
output = requests.get(endpoint, headers=headerAuth).json()

itemList = []
for i in range (0, len (output)):
    name = output[i]['name']
    itemID = output[i]['id']
    itemList.append(itemID)

f=open(filePath+handle.replace('/','-')+'.json', 'w')
metadataGroup = []
for itemID in itemList:
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth).json()
    metadataGroup.append(metadata)
json.dump(metadataGroup, f)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)
