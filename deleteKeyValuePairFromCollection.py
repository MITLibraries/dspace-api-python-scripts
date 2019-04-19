import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import argparse

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
parser.add_argument('-v', '--deletedValue', help='the value to be deleted. \
optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the community to \
retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.deletedKey:
    deletedKey = args.deletedKey
else:
    deletedKey = input('Enter the key to be deleted: ')
if args.deletedValue:
    deletedValue = args.deletedValue
else:
    deletedValue = input('Enter the value to be deleted: ')
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

f = csv.writer(open(filePath + 'deletedKey'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['deletedKey'] + ['deletedValue'] + ['delete']
           + ['post'])
recordsEdited = 0
offset = 0
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
        key = metadata[l]['key']
        value = metadata[l]['value']
        if key == deletedKey and value == deletedValue:
            provNote = '\'' + deletedKey + ':' + deletedValue
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
    if itemMetadataProcessed != metadata:
        recordsEdited = recordsEdited + 1
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print('updated', itemLink, recordsEdited)
        delete = requests.delete(baseURL + itemLink + '/metadata',
                                 headers=header, cookies=cookies,
                                 verify=verify)
        print(delete)
        post = requests.put(baseURL + itemLink + '/metadata', headers=header,
                            cookies=cookies, verify=verify,
                            data=itemMetadataProcessed)
        print(post)
        f.writerow([itemLink] + [deletedKey] + [deletedValue] + [delete]
                   + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
