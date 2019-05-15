# -*- coding: utf-8 -*-
import json
import requests
import csv
import time
import urllib3
import argparse
from datetime import datetime
import dsFunc

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--handle', help='handle of the community. optional \
- if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of changes. \
optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter the CSV of changes (including \'.csv\'): ')
if args.handle:
    handle = args.handle
else:
    handle = input('Enter community handle: ')

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
community = requests.get(endpoint, headers=header, cookies=cookies,
                         verify=verify).json()
communityID = community['uuid']
collections = requests.get(baseURL + '/rest/communities/' + str(communityID)
                           + '/collections', headers=header, cookies=cookies,
                           verify=verify).json()
collSels = ''
for j in range(0, len(collections)):
    collectionID = collections[j]['uuid']
    collSel = '&collSel[]=' + collectionID
    collSels = collSels + collSel

counter = 0
f = csv.writer(open(filePath + 'replacedValues'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['handle'] + ['replacedValue'] + ['replacementValue'])
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    rowCount = len(list(reader))
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        rowCount -= 1
        replacedValue = row['replacedValue']
        replacementValue = row['replacementValue']
        print('Rows remaining: ', rowCount)
        print(replacedValue, ' -- ', replacementValue)
        if replacedValue != replacementValue:
            print(replacedValue)
            offset = 0
            recordsEdited = 0
            items = ''
            itemLinks = []
            while items != []:
                endpoint = baseURL + '/rest/filtered-items?'
                endpoint += 'query_field[]=*&query_op[]=equals'
                endpoint += '&query_val[]=' + replacedValue
                endpoint += collSels + '&limit=200&offset='
                endpoint += str(offset)
                print(endpoint)
                response = requests.get(endpoint, headers=header,
                                        cookies=cookies, verify=verify)
                print(response)
                response = response.json()
                items = response['items']
                print(len(items), ' search results')
                for item in items:
                    itemLink = item['link']
                    itemLinks.append(itemLink)
                offset = offset + 200
                print(offset)
            for itemLink in itemLinks:
                itemMetadataProcessed = []
                metadata = requests.get(baseURL + itemLink + '/metadata',
                                        headers=header, cookies=cookies,
                                        verify=verify).json()
                counter += 1
                print(counter)
                for l in range(0, len(metadata)):
                    metadata[l].pop('schema', None)
                    metadata[l].pop('element', None)
                    metadata[l].pop('qualifier', None)
                    languageValue = metadata[l]['language']
                    if metadata[l]['value'] == replacedValue:
                        key = metadata[l]['key']
                        replacedElement = metadata[l]
                        updatedMetadataElement = {}
                        updatedMetadataElement['key'] = metadata[l]['key']
                        updatedMetadataElement['value'] = replacementValue
                        updatedMetadataElement['language'] = languageValue
                        itemMetadataProcessed.append(updatedMetadataElement)
                        provNote = '\'' + key + ': ' + replacedValue
                        provNote += '\' was replaced by \'' + key
                        provNote += ': ' + replacementValue
                        provNote += '\' through a batch process on '
                        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        provNote += currTime + '.'
                        provNoteElement = {}
                        provNoteElement['key'] = 'dc.description.provenance'
                        provNoteElement['value'] = provNote
                        provNoteElement['language'] = 'en_US'
                        itemMetadataProcessed.append(provNoteElement)
                        recordsEdited = recordsEdited + 1
                    else:
                        if metadata[l] not in itemMetadataProcessed:
                            itemMetadataProcessed.append(metadata[l])
                itemMetadataProcessed = json.dumps(itemMetadataProcessed)
                print('updated', itemLink, recordsEdited)
                delete = requests.delete(baseURL + itemLink + '/metadata',
                                         headers=header, cookies=cookies,
                                         verify=verify)
                print(delete)
                post = requests.put(baseURL + itemLink + '/metadata',
                                    headers=header, cookies=cookies,
                                    verify=verify, data=itemMetadataProcessed)
                print(post)
                f.writerow([itemLink] + [replacedValue] + [replacementValue]
                           + [delete] + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
