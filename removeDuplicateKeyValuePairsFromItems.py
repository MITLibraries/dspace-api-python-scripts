import json
import requests
import secrets
import time
import csv
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
print 'authenticated'

itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
for i in range (0, len (communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['uuid']
        if collectionID != '4dccec82-4cfb-4583-a728-2cb823b15ef0':
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 200
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Item list creation time: ','%d:%02d:%02d' % (h, m, s)

f=csv.writer(open(filePath+'removeDuplicatesRecordsEdited'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID'])
for number, itemID in enumerate(itemList):
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    for l in range (0, len (metadata)):
        if metadata[l] not in itemMetadataProcessed:
            itemMetadataProcessed.append(metadata[l])
        else:
            if metadata[l]['key'] == 'dc.description.provenance':
                itemMetadataProcessed.append(metadata[l])
            else:
                provNote = 'A duplicate element, \''+metadata[l]['key']+': '+metadata[l]['value']+',\' was removed through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = unicode(provNote)
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
    if itemMetadataProcessed != metadata:
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemID])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
