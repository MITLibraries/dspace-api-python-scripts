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

fileName = filePath+raw_input('Enter fileName (including \'.csv\'): ')
addedKey = raw_input('Enter key: ')
startTime = time.time()

f=csv.writer(open(filePath+'addKeyValuePair'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['addedKey']+['addedValue']+['delete']+['post'])

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        addedValue = row['value'].decode('utf-8')
        handle = row['handle'].strip()
        addedMetadataElement = {}
        addedMetadataElement['key'] = addedKey
        addedMetadataElement['value'] = unicode(addedValue)
        addedMetadataElement['language'] = 'en_us'
        endpoint = baseURL+'/rest/handle/'+handle
        item = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
        itemID = item['uuid']
        itemMetadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
        itemMetadata.append(addedMetadataElement)
        itemMetadataProcessed = itemMetadata

        provNote = '\''+addedKey+': '+addedValue+'\' was added through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
        provNoteElement = {}
        provNoteElement['key'] = 'dc.description.provenance'
        provNoteElement['value'] = unicode(provNote)
        provNoteElement['language'] = 'en_US'
        itemMetadataProcessed.append(provNoteElement)

        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
        print delete
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemID]+[addedMetadataElement['key']]+[addedMetadataElement['value'].encode('utf-8')]+[delete]+[post])
