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

filename = filePath+raw_input('Enter filename (including \'.csv\'): ')

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

recordsEdited = 0
elementsEdited = 0
f=csv.writer(open(filePath+'searchAndReplace'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['replacedKey']+['replacedValue']+['delete']+['post'])
for number, itemID in enumerate(itemList):
    replacedElement = ''
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            replacedKey = row['replacedKey']
            replacementKey = row['replacementKey']
            replacedValue = row['replacedValue']
            replacementValue = row['replacementValue']
            for l in range (0, len (metadata)):
                languageValue = metadata[l]['language']
                if metadata[l]['key'] == replacedKey and metadata[l]['value'] == replacedValue:
                    replacedElement = metadata[l]
                    updatedMetadataElement = {}
                    updatedMetadataElement['key'] = replacementKey
                    updatedMetadataElement['value'] = unicode(replacementValue)
                    updatedMetadataElement['language'] = languageValue
                    itemMetadataProcessed.append(updatedMetadataElement)
                    provNote = '\''+replacedKey+': '+replacedValue+'\' was replaced by \''+replacementKey+': '+replacementValue+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
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
        print replacedElement
        itemMetadataProcessed2 = []
        for m in range (0, len (itemMetadataProcessed)):
            if itemMetadataProcessed[m]['key'] == replacedElement['key'] and itemMetadataProcessed[m]['value'] == replacedElement['value']:
                pass
            else:
                itemMetadataProcessed2.append(itemMetadataProcessed[m])
        itemMetadataProcessed = itemMetadataProcessed2
        recordsEdited = recordsEdited + 1
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print 'updated', itemID, recordsEdited, elementsEdited
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[replacedElement['key']]+[replacedElement['value']]+[delete]+[post])
    else:
        print 'not updated', itemID

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
