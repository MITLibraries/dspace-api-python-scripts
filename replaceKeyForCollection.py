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

oldKey = raw_input('Enter old key: ')
newKey = raw_input('Enter new key: ')
handle = raw_input('Enter collection handle: ')

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
endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
collectionID = collection['uuid']
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

recordsEdited = 0
elementsEdited = 0
f=csv.writer(open(filePath+'replaceKey'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['replacedKey']+['replacedValue']+['delete']+['post'])
for number, itemID in enumerate(itemList):
    replacedElement = ''
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    for l in range (0, len (metadata)):
        if metadata[l]['key'] == oldKey:
            replacedElement = metadata[l]
            updatedMetadataElement = {}
            updatedMetadataElement['key'] = newKey
            updatedMetadataElement['value'] = unicode(replacedElement['value'])
            updatedMetadataElement['language'] = unicode(replacedElement['language'])
            print updatedMetadataElement
            itemMetadataProcessed.append(updatedMetadataElement)
            provNote = '\''+oldKey+'\' was replaced by \''+newKey+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = unicode(provNote)
            provNoteElement['language'] = 'en_US'
            itemMetadataProcessed.append(provNoteElement)
            elementsEdited = elementsEdited + 1
        else:
            if metadata[l] not in itemMetadataProcessed:
                itemMetadataProcessed.append(metadata[l])
    if replacedElement != '':
        recordsEdited = recordsEdited + 1
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print 'updated', itemID, recordsEdited, elementsEdited
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[replacedElement['key']]+[replacedElement['value'].encode('utf-8')]+[delete]+[post])
    else:
        print 'not updated', itemID

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
