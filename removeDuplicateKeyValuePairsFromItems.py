import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import dsFunc

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

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
endpoint = baseURL + '/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies,
                           verify=verify).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL + '/rest/communities/'
                               + str(communityID) + '/collections',
                               headers=header, cookies=cookies,
                               verify=verify).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skipColl:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL + '/rest/collections/'
                                     + str(collectionID)
                                     + '/items?limit=200&offset='
                                     + str(offset), headers=header,
                                     cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL + '/rest/collections/'
                                         + str(collectionID)
                                         + '/items?limit=200&offset='
                                         + str(offset), headers=header,
                                         cookies=cookies, verify=verify)
                items = items.json()
                for k in range(0, len(items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 200

dsFunc.elapsedTime(startTime, 'Item list creation time')

f = csv.writer(open(filePath + 'DuplicateKeysRemoved'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['key:value'])
for number, itemID in enumerate(itemList):
    itemMetadataProcessed = []
    keyValueList = []
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify).json()
    changeRecord = False
    for metadataElement in metadata:
        metadataElement.pop('schema', None)
        metadataElement.pop('element', None)
        metadataElement.pop('qualifier', None)
        key = metadataElement['key']
        try:
            value = metadataElement['value']
        except ValueError:
            value = ''
        if key != 'dc.description.provenance':
            keyValue = {'key': key, 'value': value}
            if keyValue not in keyValueList:
                itemMetadataProcessed.append(metadataElement)
                keyValueList.append(keyValue)
            else:
                f.writerow([itemID] + [keyValue])
                currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                provNote = 'A duplicate element, \'' + key + ': ' + value
                provNote += ',\' was removed through a batch process'
                provNote += 'on ' + currTime + '.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = provNote
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
                changeRecord = True
    if changeRecord is True:
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print(itemID)
        delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                 + '/metadata', headers=header,
                                 cookies=cookies, verify=verify)
        print(delete)
        post = requests.put(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify, data=itemMetadataProcessed)
        print(post)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
