# -*- coding: utf-8 -*-
import json
import requests
import csv
import time
import urllib3
from datetime import datetime
import ast
import argparse

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__(secrets)
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

parser = argparse.ArgumentParser()
parser.add_argument('-r', '--replacedKey', help='the key to be replaced. \
optional - if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of changes. \
optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.replacedKey:
    replacedKey = args.replacedKey
else:
    replacedKey = input('Enter the key to be replaced: ')
if args.fileName:
    fileName = filePath + args.fileName
else:
    fileName = filePath + input('Enter the file name of the CSV of changes \
    (including \'.csv\'): ')

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
print('authenticated')

recordsEdited = 0
elementsEdited = 0
f = csv.writer(open(filePath + 'splitFieldIntoMultipleFields'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['replacedKey'] + ['replacementValueList']
           + ['delete'] + ['post'])
replacedElement = ''
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        replacedValue = row['value']
        print(replacedValue)
        replacementValueList = ast.literal_eval(row['structuredList'])
        offset = 0
        items = ''
        itemLinks = []
        while items != []:
            endpoint = baseURL + '/rest/filtered-items?query_field[]='
            endpoint += replacedKey
            endpoint += '&query_op[]=equals&query_val[]='
            endpoint += replacedValue + '&limit=200&offset='
            endpoint += str(offset)
            response = requests.get(endpoint, headers=header, cookies=cookies,
                                    verify=verify).json()
            items = response['items']
            for item in items:
                itemLink = item['link']
                itemLinks.append(itemLink)
            offset = offset + 200
            print(offset)
        for itemLink in itemLinks:
            itemMetadataProcessed = []
            print(itemLink)
            metadata = requests.get(baseURL + itemLink + '/metadata',
                                    headers=header, cookies=cookies,
                                    verify=verify).json()
            for l in range(0, len(metadata)):
                metadata[l].pop('schema', None)
                metadata[l].pop('element', None)
                metadata[l].pop('qualifier', None)
                languageValue = metadata[l]['language']
                key = metadata[l]['key']
                value = metadata[l]['value']
                if key == replacedKey and value == replacedValue:
                    print('match')
                    replacedElement = metadata[l]
                    for replacementValue in replacementValueList:
                        updatedMetadataElement = {}
                        updatedMetadataElement['key'] = replacedKey
                        updatedMetadataElement['value'] = replacementValue
                        updatedMetadataElement['language'] = languageValue
                        itemMetadataProcessed.append(updatedMetadataElement)
                        currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        provNote = '\'' + replacedKey + ': ' + replacedValue
                        provNote += '\' split into \'' + replacedKey
                        provNote += ': ' + replacementValue
                        provNote += '\' through a batch process on '
                        provNote += currTime + '.'
                        provNoteElement = {}
                        provNoteElement['key'] = 'dc.description.provenance'
                        provNoteElement['value'] = provNote
                        provNoteElement['language'] = 'en_US'
                        itemMetadataProcessed.append(provNoteElement)
                        elementsEdited = elementsEdited + 1
                else:
                    if metadata[l] not in itemMetadataProcessed:
                        itemMetadataProcessed.append(metadata[l])
            recordsEdited = recordsEdited + 1
            itemMetadataProcessed = json.dumps(itemMetadataProcessed)
            print('updated', itemLink, recordsEdited, elementsEdited)
            delete = requests.delete(baseURL + itemLink + '/metadata',
                                     headers=header, cookies=cookies,
                                     verify=verify)
            print(delete)
            post = requests.put(baseURL + itemLink + '/metadata',
                                headers=header, cookies=cookies, verify=verify,
                                data=itemMetadataProcessed)
            print(post)
            f.writerow([itemLink] + [replacedKey] + [replacementValueList]
                       + [delete] + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
