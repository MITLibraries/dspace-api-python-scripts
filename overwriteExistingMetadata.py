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
parser.add_argument('-f', '--fileName', help='the name of the CSV with handles \
and file identifiers. optional - if not provided, the script will ask for \
input')
args = parser.parse_args()
if args.fileName:
    fileName = args.fileName
else:
    fileName = input('Enter file name: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

handleIdDict = {}
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        fileIdentifier = row['fileId']
        handle = row['handle']
        handleIdDict[fileIdentifier] = handle
print(handleIdDict)
id = input('test')

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

collectionMetadata = json.load(open('metadataOverwrite.json'))

f = csv.writer(open(filePath + 'metadataOverwrite'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['delete'] + ['post'])

for k, v in handleIdDict.items():
    for itemMetadata in collectionMetadata:
        updatedItemMetadata = {}
        updatedItemMetadataList = []
        for element in itemMetadata['metadata']:
            if element['key'] == 'fileIdentifier':
                fileIdentifier = element['value']
            else:
                updatedItemMetadataList.append(element)
        uriElement = {}
        uriElement['key'] = 'dc.identifier.uri'
        uriElement['value'] = 'http://jhir.library.jhu.edu/handle/' + v
        updatedItemMetadataList.append(uriElement)
        provNote = 'Item metadata updated through a batch process on ' \
            + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + '.'
        provNoteElement = {}
        provNoteElement['key'] = 'dc.description.provenance'
        provNoteElement['value'] = provNote
        provNoteElement['language'] = 'en_US'
        updatedItemMetadataList.append(provNoteElement)

        if fileIdentifier == k:
            print(fileIdentifier)
            endpoint = baseURL + '/rest/handle/' + v
            item = requests.get(endpoint, headers=header, cookies=cookies,
                                verify=verify).json()
            itemID = item['uuid']
            metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                    + '/metadata', headers=header,
                                    cookies=cookies, verify=verify).json()
            for l in range(0, len(metadata)):
                metadata[l].pop('schema', None)
                metadata[l].pop('element', None)
                metadata[l].pop('qualifier', None)
                if metadata[l]['key'] == 'dc.description.provenance':
                    updatedItemMetadataList.append(metadata[l])
                if metadata[l]['key'] == 'dc.date.available':
                    updatedItemMetadataList.append(metadata[l])
                if metadata[l]['key'] == 'dc.date.accessioned':
                    updatedItemMetadataList.append(metadata[l])
            updatedItemMetadata = json.dumps(updatedItemMetadataList)
            delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                     + '/metadata', headers=header,
                                     cookies=cookies, verify=verify)
            print(delete)
            post = requests.put(baseURL + '/rest/items/' + str(itemID)
                                + '/metadata', headers=header, cookies=cookies,
                                verify=verify, data=updatedItemMetadata)
            print(post)
            f.writerow([itemID] + [delete] + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
