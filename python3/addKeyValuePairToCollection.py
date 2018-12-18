import json
import requests
import secrets
import time
import csv
from datetime import datetime
import urllib3
import argparse

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be added. optional - if not provided, the script will ask for input')
parser.add_argument('-v', '--value', help='the value to be added. optional - if not provided, the script will ask for input')
parser.add_argument('-l', '--language', help='the language tag to be added. optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    addedKey = args.key
else:
    addedKey = input('Enter the key: ')
if args.value:
    addedValue = args.value
else:
    addedValue = input('Enter the value: ')
if args.language:
    addedLanguage = args.language
else:
    addedLanguage = input('Enter the language tag: ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter collection handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
print('authenticated')

itemList = []
endpoint = baseURL+'/rest/handle/'+collectionHandle
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
print('Item list creation time: ','%d:%02d:%02d' % (h, m, s))

recordsEdited = 0
f=csv.writer(open(filePath+'addKeyValuePair'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['itemID']+['addedKey']+['addedValue']+['delete']+['post'])
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    itemMetadataProcessed = []
    for l in range (0, len (metadata)):
        metadata[l].pop('schema', None)
        metadata[l].pop('element', None)
        metadata[l].pop('qualifier', None)
        itemMetadataProcessed.append(metadata[l])
    addedMetadataElement = {}
    addedMetadataElement['key'] = addedKey
    addedMetadataElement['value'] = addedValue
    addedMetadataElement['language'] = addedLanguage
    itemMetadataProcessed.append(addedMetadataElement)
    provNote = '\''+addedKey+': '+addedValue+'\' was added through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
    provNoteElement = {}
    provNoteElement['key'] = 'dc.description.provenance'
    provNoteElement['value'] = provNote
    provNoteElement['language'] = 'en_US'
    itemMetadataProcessed.append(provNoteElement)
    recordsEdited = recordsEdited + 1
    itemMetadataProcessed = json.dumps(itemMetadataProcessed)
    print('updated', itemID, recordsEdited)
    delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
    print(delete)
    post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
    print(post)
    f.writerow([itemID]+[addedKey]+[addedValue]+[delete]+[post])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
