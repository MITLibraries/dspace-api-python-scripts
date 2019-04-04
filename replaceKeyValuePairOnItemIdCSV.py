import json
import requests
import time
import csv
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
print('authenticated')

fileName = filePath + input('Enter fileName (including \'.csv\'): ')
replacedKey = input('Enter key: ')
replacementKey = replacedKey

f = csv.writer(open(filePath + 'replacedKeyValuePair'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['itemID'] + ['replacedKey'] + ['replacedValue']
           + ['replacementValue'] + ['delete'] + ['post'])

with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        itemMetadataProcessed = []
        itemID = row['itemID']
        replacedValue = row['replacedValue']
        replacementValue = row['replacementValue']
        itemMetadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                    + '/metadata', headers=header,
                                    cookies=cookies, verify=verify).json()
        for element in itemMetadata:
            languageValue = element['language']
            key = element['key'] == replacedKey
            value = element['value']
            if key and value == replacedValue:
                updatedMetadataElement = {}
                updatedMetadataElement['key'] = replacementKey
                updatedMetadataElement['value'] = replacementValue
                updatedMetadataElement['language'] = languageValue
                itemMetadataProcessed.append(updatedMetadataElement)

                provNote = '\'' + replacedKey + ': ' + replacedValue
                provNote += '\' was replaced by \'' + replacementKey
                provNote += ': ' + replacementValue
                provNote += '\' through a batch process on '
                currTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                provNote += currTime + '.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = provNote
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
            else:
                itemMetadataProcessed.append(element)
        print(itemMetadata)
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)

        delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                 + '/metadata', headers=header,
                                 cookies=cookies, verify=verify)
        print(delete)
        post = requests.put(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify, data=itemMetadataProcessed)
        print(post)
        f.writerow([itemID] + [replacedKey] + [replacedValue]
                   + [replacementValue] + [delete] + [post])
