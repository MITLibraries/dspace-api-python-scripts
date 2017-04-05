import json
import requests
import secrets
import time
import csv
from datetime import datetime

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

key = raw_input('Enter key: ')

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=headerAuth).json()
for i in range (0, len (communities)):
    communityID = communities[i]['id']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        if collectionID != 24:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['id']
                    itemList.append(itemID)
                offset = offset + 1000
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Item list creation time: ','%d:%02d:%02d' % (h, m, s)

f=csv.writer(open(filePath+'languageTagUpdate'+key+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['key'])
for number, itemID in enumerate(itemList):
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth).json()
    for l in range (0, len (metadata)):
        if metadata[l]['key'] == key and metadata[l]['language'] == None:
            updatedMetadataElement = {}
            updatedMetadataElement['key'] = metadata[l]['key']
            updatedMetadataElement['value'] = metadata[l]['value']
            updatedMetadataElement['language'] = 'en_US'
            itemMetadataProcessed.append(updatedMetadataElement)
            provNote = 'The language tag for \''+metadata[l]['key']+': '+metadata[l]['value']+'\' was changed from \'null\' to \'en_US\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = unicode(provNote)
            provNoteElement['language'] = 'en_US'
            itemMetadataProcessed.append(provNoteElement)
        else:
            itemMetadataProcessed.append(metadata[l])
    if 'The language tag for \''+key in json.dumps(itemMetadataProcessed):
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print 'updated', itemID
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[key])
    else:
        print 'not updated', itemID

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
