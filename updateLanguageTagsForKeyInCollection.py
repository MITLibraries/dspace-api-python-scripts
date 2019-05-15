import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import dsFunc

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

key = input('Enter key: ')
collectionHandle = input('Enter collection handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

itemList = []
endpoint = baseURL + '/rest/handle/' + collectionHandle
collection = requests.get(endpoint, headers=header, cookies=cookies,
                          verify=verify).json()
collectionID = collection['uuid']
offset = 0
items = ''
while items != []:
    items = requests.get(baseURL + '/rest/collections/' + str(collectionID)
                         + '/items?limit=200&offset=' + str(offset),
                         headers=header, cookies=cookies, verify=verify)
    while items.status_code != 200:
        time.sleep(5)
        items = requests.get(baseURL + '/rest/collections/' + str(collectionID)
                             + '/items?limit=200&offset=' + str(offset),
                             headers=header, cookies=cookies, verify=verify)
    items = items.json()
    for k in range(0, len(items)):
        itemID = items[k]['uuid']
        itemList.append(itemID)
    offset = offset + 200

dsFunc.elapsedTime(startTime, 'Item list creation time')

f = csv.writer(open(filePath + 'languageTagUpdate' + key
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['key'])
for number, itemID in enumerate(itemList):
    itemMetadataProcessed = []
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify).json()
    for l in range(0, len(metadata)):
        if metadata[l]['key'] == key and metadata[l]['language'] == '':
            updatedMetadataElement = {}
            updatedMetadataElement['key'] = metadata[l]['key']
            updatedMetadataElement['value'] = metadata[l]['value']
            updatedMetadataElement['language'] = 'en_US'
            itemMetadataProcessed.append(updatedMetadataElement)
            provNote = 'The language tag for \'' + metadata[l]['key'] + ': '
            provNote += metadata[l]['value']
            provNote += '\' was changed from \'null\' to \'en_US\' '
            provNote += 'through a batch process on '
            provNote += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            provNote += '.'
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = provNote
            provNoteElement['language'] = 'en_US'
            itemMetadataProcessed.append(provNoteElement)
        else:
            itemMetadataProcessed.append(metadata[l])
    if 'The language tag for \'' + key in json.dumps(itemMetadataProcessed):
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print('updated', itemID)
        delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                 + '/metadata', headers=header,
                                 cookies=cookies, verify=verify)
        print(delete)
        post = requests.put(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify, data=itemMetadataProcessed)
        print(post)
        f.writerow([itemID] + [key])
    else:
        print('not updated', itemID)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
