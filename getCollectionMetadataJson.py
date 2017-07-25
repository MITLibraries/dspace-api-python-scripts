import json
import requests
import secrets
import time

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'
    
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

handle = raw_input('Enter handle: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
startTime = time.time()

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=headerAuth, verify=verify).json()
collectionID = collection['id']
collectionTitle = requests.get(endpoint, headers=headerAuth, verify=verify).json()
endpoint = baseURL+'/rest/collections/'+str(collectionID)+'/items'
output = requests.get(endpoint, headers=headerAuth, verify=verify).json()

itemList = []
for i in range (0, len (output)):
    name = output[i]['name']
    itemID = output[i]['id']
    itemList.append(itemID)

f=open(filePath+handle.replace('/','-')+'.json', 'w')
metadataGroup = []
for itemID in itemList:
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    metadataGroup.append(metadata)
json.dump(metadataGroup, f)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)
