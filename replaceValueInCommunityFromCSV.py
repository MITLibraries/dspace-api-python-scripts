# -*- coding: utf-8 -*-
import json
import requests
import secrets
import csv
import time
import urllib3
import argparse
from datetime import datetime

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--handle', help='handle of the community. optional - if not provided, the script will ask for input')
parser.add_argument('-f', '--fileName', help='the CSV file of changes. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.fileName:
    fileName = filePath+args.fileName
else:
    fileName = filePath+raw_input('Enter the file name of the CSV of changes (including \'.csv\'): ')
if args.handle:
    handle = args.handle
else:
    handle = raw_input('Enter community handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'

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
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityID = community['uuid']
collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
collSels = ''
for j in range (0, len (collections)):
    collectionID = collections[j]['uuid']
    collSel = '&collSel[]=' + collectionID
    collSels = collSels + collSel

f=csv.writer(open(filePath+'replacedValues'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['handle']+['replacedValue']+['replacementValue'])
with open(fileName) as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        print row
        replacedValue = row['replacedValue'].decode('utf-8')
        replacementValue = row['replacementValue'].decode('utf-8')
        if replacedValue != replacementValue:
            print replacedValue
            offset = 0
            recordsEdited = 0
            items = ''
            while items != []:
                endpoint = baseURL+'/rest/filtered-items?query_field[]=*&query_op[]=equals&query_val[]='+replacedValue+collSels+'&limit=200&offset='+str(offset)
                print endpoint
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
                        if metadata[l]['value'] == replacedValue:
                            key = metadata[l]['key']
                            replacedElement = metadata[l]
                            updatedMetadataElement = {}
                            updatedMetadataElement['key'] = metadata[l]['key']
                            updatedMetadataElement['value'] = unicode(replacementValue)
                            updatedMetadataElement['language'] = languageValue
                            itemMetadataProcessed.append(updatedMetadataElement)
                            provNote = '\''+key+': '+replacedValue+'\' was replaced by \''+key+': '+replacementValue+'\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
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
                    f.writerow([itemLink]+[replacedValue.encode('utf-8')]+[replacementValue.encode('utf-8')]+[delete]+[post])
                offset = offset + 200

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
