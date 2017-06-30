import json
import requests
import secrets
import csv
import time
from datetime import datetime

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

communityHandle = raw_input('Enter community handle: ')
key = raw_input('Enter key: ')

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
startTime = time.time()

endpoint = baseURL+'/rest/handle/'+communityHandle
community = requests.get(endpoint, headers=headerAuth, verify=verify).json()
communityID = community['id']
collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth, verify=verify).json()

itemList = []
for i in range (0, len (collections)):
    collectionID = collections[i]['id']
    collectionHandle = collections[i]['handle']
    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=headerAuth, verify=verify).json()
    for j in range (0, len (items)):
        itemID = items[j]['id']
        itemList.append(itemID)

f=csv.writer(open(filePath+'removeUnnecessarySpaces'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['replacedKey']+['replacedValue']+['delete']+['post'])
for itemID in itemList:
    itemMetadataProcessed = []
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    for i in range (0, len (metadata)):
        if metadata[i]['key'] == key:
            if '  ' in json.dumps(metadata[i]) or ' ,' in json.dumps(metadata[i]):
                updatedMetadataElement = json.loads(json.dumps(metadata[i]).replace('   ',' ').replace('  ',' ').replace(' ,',','))
                itemMetadataProcessed.append(updatedMetadataElement)
                f.writerow([itemID]+[metadata[i]['key']]+[metadata[i]['value']])
            else:
                itemMetadataProcessed.append(metadata[i])
        else:
            itemMetadataProcessed.append(metadata[i])
    if json.dumps(itemMetadataProcessed) != json.dumps(metadata):
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print 'updated', itemID
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify, data=itemMetadataProcessed)
        print post
    else:
        print 'not updated', itemID

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
