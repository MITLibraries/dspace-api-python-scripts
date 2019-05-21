import json
import requests
import time
import csv
from datetime import datetime
import urllib3
import argparse
import dsFunc

inst = input('To edit production server, enter the name of the secrets file: ')
secrets = dsFunc.instSelect(inst)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skipColl = secrets.skipColl

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fileName', help='the CSV file of changes. '
                    'optional - if not provided, the script will ask for '
                    'input')
args = parser.parse_args()

if args.fileName:
    fileName = filePath + args.fileName
else:
    fileName = filePath + input('Enter the CSV of changes '
                                '(including \'.csv\'): ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}


status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

f = csv.writer(open(filePath + 'searchAndReplace'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['replacedKey'] + ['replacedValue'] + ['delete']
           + ['post'])
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        replacedKey = row['replacedKey']
        replacementKey = row['replacementKey']
        replacedValue = row['replacedValue']
        replacementValue = row['replacementValue']
        offset = 0
        recordsEdited = 0
        items = ''
        itemLinks = []
        while items != []:
            endpoint = baseURL + '/rest/filtered-items?query_field[]='
            endpoint += replacedKey
            endpoint += '&query_op[]=equals&query_val[]='
            endpoint += replacedValue + '&limit=200&offset='
            endpoint += str(offset)
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
                    replacedElement = metadata[l]
                    updatedMetadataElement = {}
                    updatedMetadataElement['key'] = replacementKey
                    updatedMetadataElement['value'] = replacementValue
                    updatedMetadataElement['language'] = languageValue
                    itemMetadataProcessed.append(updatedMetadataElement)
                    provNote = '\'' + replacedKey + ': ' + replacedValue
                    provNote += '\' was replaced by \''
                    provNote += replacementKey + ': '
                    provNote += replacementValue
                    provNote += '\' through a batch process on '
                    currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    provNote += currTime + '.'
                    provNoteElement = {}
                    provNoteElement['key'] = 'dc.description.provenance'
                    provNoteElement['value'] = provNote
                    provNoteElement['language'] = 'en_US'
                    itemMetadataProcessed.append(provNoteElement)
                else:
                    if metadata[l] not in itemMetadataProcessed:
                        itemMetadataProcessed.append(metadata[l])
            itemMetadataProcessed = json.dumps(itemMetadataProcessed)
            delete = requests.delete(baseURL + itemLink + '/metadata',
                                     headers=header, cookies=cookies,
                                     verify=verify)
            print(delete)
            post = requests.put(baseURL + itemLink + '/metadata',
                                headers=header, cookies=cookies, verify=verify,
                                data=itemMetadataProcessed)
            print(post)
            f.writerow([itemLink] + [replacedElement['key']]
                       + [replacedElement['value']] + [delete] + [post])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
