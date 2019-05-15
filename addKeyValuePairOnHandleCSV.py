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
session = requests.post(baseURL + '/rest/login', headers=header,
                        verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

fileName = filePath + input('Enter fileName (including \'.csv\'): ')
addedKey = input('Enter key: ')
startTime = time.time()

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open(filePath + 'addKeyValuePair' + date + '.csv', 'w'))
f.writerow(['itemID'] + ['addedKey'] + ['addedValue'] + ['delete'] + ['post'])

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        addedValue = row['value']
        handle = row['handle'].strip()
        addedMetadataElement = {}
        addedMetadataElement['key'] = addedKey
        addedMetadataElement['value'] = addedValue
        addedMetadataElement['language'] = 'en_us'
        endpoint = baseURL + '/rest/handle/' + handle
        item = requests.get(endpoint, headers=header, cookies=cookies,
                            verify=verify).json()
        itemID = item['uuid']
        itemMetadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                    + '/metadata', headers=header,
                                    cookies=cookies, verify=verify).json()
        itemMetadata.append(addedMetadataElement)
        itemMetadataProcessed = itemMetadata

        date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        provNote = '\'' + addedKey + ': ' + addedValue
        provNote += '\' was added through a batch process on '
        provNote += date + '.'
        provNoteElement = {}
        provNoteElement['key'] = 'dc.description.provenance'
        provNoteElement['value'] = provNote
        provNoteElement['language'] = 'en_US'
        itemMetadataProcessed.append(provNoteElement)

        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                 + '/metadata', headers=header,
                                 cookies=cookies, verify=verify)
        print(delete)
        post = requests.put(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify, data=itemMetadataProcessed)
        print(post)
        f.writerow([itemID] + [addedMetadataElement['key']]
                   + [addedMetadataElement['value']] + [delete] + [post])

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
