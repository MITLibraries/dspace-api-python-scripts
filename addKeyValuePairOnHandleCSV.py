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

data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}

filename = filePath+raw_input('Enter filename (including \'.csv\'): ')
addedKey = raw_input('Enter key: ')
startTime = time.time()

f=csv.writer(open(filePath+'addKeyValuePair'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['addedKey']+['addedValue']+['delete']+['post'])

with open(filename) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        addedValue = row['value'].decode('utf-8')
        handle = row['handle'].strip()
        addedMetadataElement = {}
        addedMetadataElement['key'] = addedKey
        addedMetadataElement['value'] = unicode(addedValue)
        addedMetadataElement['language'] = 'en_us'
        endpoint = baseURL+'/rest/handle/'+handle
        item = requests.get(endpoint, headers=header).json()
        itemID = item['id']
        itemMetadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth).json()
        itemMetadata.append(addedMetadataElement)
        itemMetadataProcessed = itemMetadata

        provNote = '\''+addedKey+': '+addedValue+'\' was added through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
        provNoteElement = {}
        provNoteElement['key'] = 'dc.description.provenance'
        provNoteElement['value'] = unicode(provNote)
        provNoteElement['language'] = 'en_US'
        itemMetadataProcessed.append(provNoteElement)

        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[addedMetadataElement['key']]+[addedMetadataElement['value'].encode('utf-8')]+[delete]+[post])
