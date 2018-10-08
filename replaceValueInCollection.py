import json
import requests
import secrets
import csv
import time
import urllib3
import argparse
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be searched. optional - if not provided, the script will ask for input')
parser.add_argument('-1', '--replacedValue', help='the value to be replaced. optional - if not provided, the script will ask for input')
parser.add_argument('-2', '--replacementValue', help='the replacement value. optional - if not provided, the script will ask for input')
parser.add_argument('-i', '--handle', help='handle of the collection to retreive. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = raw_input('Enter the key: ')
if args.replacedValue:
    replacedValue = args.replacedValue
else:
    replacedValue = raw_input('Enter the value to be replaced: ')
if args.replacementValue:
    replacementValue = args.replacementValue
else:
    replacementValue = raw_input('Enter the replacement value: ')
if args.handle:
    handle = args.handle
else:
    handle = raw_input('Enter collection handle: ')

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

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
collectionID = collection['uuid']
collSels = '&collSel[]=' + collectionID

f=csv.writer(open(filePath+'replacedValues'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['handle']+['replacedValue']+['replacementValue'])
offset = 0
recordsEdited = 0
items = ''
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=equals&query_val[]='+replacedValue+collSels+'&limit=200&offset='+str(offset)
    print endpoint
    replacedKey = key
    replacementKey = key
    response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify).json()
        for l in range (0, len (metadata)):
            metadata[l].pop('schema', None)
            metadata[l].pop('element', None)
            metadata[l].pop('qualifier', None)
            languageValue = metadata[l]['language']
            if metadata[l]['key'] == replacedKey and metadata[l]['value'].encode('utf-8') == replacedValue:
                replacedElement = metadata[l]
                updatedMetadataElement = {}
                updatedMetadataElement['key'] = replacementKey
                updatedMetadataElement['value'] = unicode(replacementValue)
                updatedMetadataElement['language'] = languageValue
                itemMetadataProcessed.append(updatedMetadataElement)
                provNote = '\''+replacedKey+': '+replacedValue+'\' was replaced by \''+replacementKey+': '+replacementValue+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = unicode(provNote)
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
                recordsEdited = recordsEdited + 1
            else:
                if metadata[l] not in itemMetadataProcessed:
                    itemMetadataProcessed.append(metadata[l])
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print 'updated', itemLink, recordsEdited
        delete = requests.delete(baseURL+itemLink+'/metadata', headers=header, cookies=cookies, verify=verify)
        print delete
        post = requests.put(baseURL+itemLink+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
        print post
        f.writerow([itemLink]+[updatedMetadataElement['key']]+[updatedMetadataElement['value']]+[delete]+[post])
    offset = offset + 200
    print offset

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
