import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import argparse
import dsFunc

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

parser = argparse.ArgumentParser()
parser.add_argument('-1', '--replacedKey', help='the key to be replaced. \
optional - if not provided, the script will ask for input')
parser.add_argument('-2', '--replacementKey', help='the replacement key. \
optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection to \
retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.replacedKey:
    replacedKey = args.replacedKey
else:
    replacedKey = input('Enter the key to be replaced: ')
if args.replacementKey:
    replacementKey = args.replacementKey
else:
    replacementKey = input('Enter the replacement key: ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter collection handle: ')

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

endpoint = baseURL + '/rest/handle/' + handle
collection = requests.get(endpoint, headers=header, cookies=cookies,
                          verify=verify).json()
collectionID = collection['uuid']
collSels = '&collSel[]=' + collectionID
date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
f = csv.writer(open(filePath + 'replaceKey' + date + '.csv', 'w'))
f.writerow(['itemID'] + ['replacedKey'] + ['replacedValue'] + ['delete']
           + ['post'])
offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL + '/rest/filtered-items?query_field[]='
    endpoint += replacedKey + '&query_op[]=exists&query_val[]='
    endpoint += collSels + '&limit=200&offset=' + str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies,
                            verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        itemLinks.append(itemLink)
    offset = offset + 200
    print(offset)
for itemLink in itemLinks:
    itemMetadataProcessed = []
    print(itemLink)
    metadata = requests.get(baseURL + itemLink + '/metadata', headers=header,
                            cookies=cookies, verify=verify).json()
    for l in range(0, len(metadata)):
        metadata[l].pop('schema', None)
        metadata[l].pop('element', None)
        metadata[l].pop('qualifier', None)
        if metadata[l]['key'] == replacedKey:
            replacedElement = metadata[l]
            updatedMetadataElement = {}
            updatedMetadataElement['key'] = replacementKey
            updatedMetadataElement['value'] = replacedElement['value']
            updatedMetadataElement['language'] = replacedElement['language']
            print(updatedMetadataElement)
            itemMetadataProcessed.append(updatedMetadataElement)
            provNote = '\'' + replacedKey + '\' was replaced by \''
            provNote += replacementKey
            provNote += '\' through a batch process on '
            date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.'
            provNote += date
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = provNote
            provNoteElement['language'] = 'en_US'
            itemMetadataProcessed.append(provNoteElement)
        else:
            if metadata[l] not in itemMetadataProcessed:
                itemMetadataProcessed.append(metadata[l])
    itemMetadataProcessed = json.dumps(itemMetadataProcessed)
    delete = requests.delete(baseURL + itemLink + '/metadata', headers=header,
                             cookies=cookies, verify=verify)
    print(delete)
    post = requests.put(baseURL + itemLink + '/metadata', headers=header,
                        cookies=cookies, verify=verify,
                        data=itemMetadataProcessed)
    print(post)
    f.writerow([itemLink] + [replacedElement['key']]
               + [replacedElement['value']] + [delete] + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
