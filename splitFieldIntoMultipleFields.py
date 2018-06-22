import json
import requests
import secrets
import csv
import time
import urllib3
from datetime import datetime
import ast

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

fileName = filePath+raw_input('Enter fileName (including \'.csv\'): ')
replacedKey = raw_input('Enter key: ')

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print 'authenticated'

recordsEdited = 0
elementsEdited = 0
f=csv.writer(open(filePath+'splitFieldIntoMultipleFields'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['replacedKey']+['replacementValueList']+['delete']+['post'])
replacedElement = ''
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        replacedValue = row['originalSubject']
        print replacedValue
        replacementValueList = ast.literal_eval(row['listOfSubject'])
        print type(replacementValueList)
        offset = 0
        items = ''
        while items != []:
            endpoint = baseURL+'/rest/filtered-items?query_field[]='+replacedKey+'&query_op[]=equals&query_val[]='+replacedValue+'&limit=200&offset='+str(offset)
            response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
            items = response['items']
            for item in items:
                itemLink = item['link']
                itemMetadataProcessed = []
                metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify).json()
                for l in range (0, len (metadata)):
                    metadata[l].pop('schema', None)
                    metadata[l].pop('element', None)
                    metadata[l].pop('qualifier', None)
                    languageValue = metadata[l]['language']
                    if metadata[l]['key'] == replacedKey and metadata[l]['value'] == replacedValue:
                        replacedElement = metadata[l]
                        for replacementValue in replacementValueList:
                            updatedMetadataElement = {}
                            updatedMetadataElement['key'] = replacedKey
                            updatedMetadataElement['value'] = unicode(replacementValue)
                            updatedMetadataElement['language'] = languageValue
                            itemMetadataProcessed.append(updatedMetadataElement)
                            provNote = '\''+replacedKey+': '+replacedValue+'\' split into \''+replacedKey+': '+replacementValue+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                            provNoteElement = {}
                            provNoteElement['key'] = 'dc.description.provenance'
                            provNoteElement['value'] = unicode(provNote)
                            provNoteElement['language'] = 'en_US'
                            itemMetadataProcessed.append(provNoteElement)
                            elementsEdited = elementsEdited + 1
                    else:
                        if metadata[l] not in itemMetadataProcessed:
                            itemMetadataProcessed.append(metadata[l])
                recordsEdited = recordsEdited + 1
                itemMetadataProcessed = json.dumps(itemMetadataProcessed)
                print itemMetadataProcessed
                print 'updated', itemLink, recordsEdited, elementsEdited
                delete = requests.delete(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify)
                print delete
                post = requests.put(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
                print post
                f.writerow([itemLink]+[replacedKey]+[replacementValueList]+[delete]+[post])
            offset = offset + 200
            print offset
logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
