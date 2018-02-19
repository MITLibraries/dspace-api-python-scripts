import json
import requests
import secrets
import time
import csv
from datetime import datetime

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

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=headerAuth, verify=verify).json()
for i in range (0, len (communities)):
    communityID = communities[i]['id']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        if collectionID != 24:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth, verify=verify)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['id']
                    itemList.append(itemID)
                offset = offset + 1000
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Item list creation time: ','%d:%02d:%02d' % (h, m, s)

f=csv.writer(open(filePath+'DuplicatesRecordsDiffLangTags'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['key:value'])
for number, itemID in enumerate(itemList):
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    for metadataElement in metadata:
        key = metadataElement['key']
        value = metadataElement['value']
        keyValue = key+':'+value
        if key+':'+value not in itemMetadataProcessed:
            itemMetadataProcessed.append(keyValue)
        else:
            f.writerow([itemID]+[keyValue])

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
