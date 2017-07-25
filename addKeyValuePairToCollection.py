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

collectionHandle = raw_input('Enter collection handle: ')
addedKey = raw_input('Enter key: ')
addedValue = raw_input('Enter value: ')
addedLanguage = raw_input('Enter language: ')
confirm = raw_input('Hit enter to proceed')

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

itemList = []
endpoint = baseURL+'/rest/handle/'+collectionHandle
collection = requests.get(endpoint, headers=header, verify=verify).json()
collectionID = collection['id']
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

recordsEdited = 0
f=csv.writer(open(filePath+'addKeyValuePair'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['addedKey']+['addedValue']+['delete']+['post'])
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    itemMetadataProcessed = metadata
    addedMetadataElement = {}
    addedMetadataElement['key'] = addedKey
    addedMetadataElement['value'] = unicode(addedValue)
    addedMetadataElement['language'] = unicode(addedLanguage)
    itemMetadataProcessed.append(addedMetadataElement)
    provNote = '\''+addedKey+': '+addedValue+'\' was added through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
    provNoteElement = {}
    provNoteElement['key'] = 'dc.description.provenance'
    provNoteElement['value'] = unicode(provNote)
    provNoteElement['language'] = 'en_US'
    itemMetadataProcessed.append(provNoteElement)
    recordsEdited = recordsEdited + 1
    itemMetadataProcessed = json.dumps(itemMetadataProcessed)
    print 'updated', itemID, recordsEdited
    delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify)
    print delete
    post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify, data=itemMetadataProcessed)
    print post
    f.writerow([itemID]+[addedKey]+[addedValue]+[delete]+[post])

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
