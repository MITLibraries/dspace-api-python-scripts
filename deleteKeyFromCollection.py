import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import argparse
import dsFunc

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    secrets = __import__('secrets')
    print('Editing Development')

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--deletedKey', help='the key to be deleted. \
optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection to \
retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.deletedKey:
    deletedKey = args.deletedKey
else:
    deletedKey = input('Enter the key to be deleted: ')

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

f = csv.writer(open(filePath + 'deletedValues'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['handle'] + ['deletedValue'] + ['delete'] + ['post'])
offset = 0
recordsEdited = 0
items = ''
itemLinks = []
while items != []:
    endpoint = baseURL + '/rest/filtered-items?query_field[]=' + deletedKey
    endpoint += '&query_op[]=exists&query_val[]=' + collSels
    endpoint += '&limit=200&offset=' + str(offset)
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
        languageValue = metadata[l]['language']
        if metadata[l]['key'] == deletedKey:
            provNote = '\'' + deletedKey
            provNote += '\' was deleted through a batch process on '
            provNote += datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            provNote += '.'
            provNoteElement = {}
            provNoteElement['key'] = 'dc.description.provenance'
            provNoteElement['value'] = provNote
            provNoteElement['language'] = 'en_US'
            itemMetadataProcessed.append(provNoteElement)
        else:
            itemMetadataProcessed.append(metadata[l])
    recordsEdited = recordsEdited + 1
    itemMetadataProcessed = json.dumps(itemMetadataProcessed)
    print('updated', itemLink, recordsEdited)
    delete = requests.delete(baseURL + itemLink + '/metadata', headers=header,
                             cookies=cookies, verify=verify)
    print(delete)
    post = requests.put(baseURL + itemLink + '/metadata', headers=header,
                        cookies=cookies, verify=verify,
                        data=itemMetadataProcessed)
    print(post)
    f.writerow([itemLink] + [deletedKey] + [delete] + [post])


logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
