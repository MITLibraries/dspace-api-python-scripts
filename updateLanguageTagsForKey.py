import json
import requests
import secrets
import time
import csv
from datetime import datetime
import urllib3
import argparse

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be updated. optional - if not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = raw_input('Enter the key to be updated: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
print 'authenticated'

f=csv.writer(open(filePath+'languageTagUpdate'+key+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'wb'))
f.writerow(['itemID']+['key'])
offset = 0
recordsEdited = 0
items = ''
while items != []:
    endpoint = baseURL+'/rest/filtered-items?query_field[]='+key+'&query_op[]=exists&query_val[]=&limit=200&offset='+str(offset)
    print endpoint
    response = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        print itemLink
        metadata = requests.get(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify).json()
        for l in range (0, len (metadata)):
            if metadata[l]['key'] == key and metadata[l]['language'] == None:
                updatedMetadataElement = {}
                updatedMetadataElement['key'] = metadata[l]['key']
                updatedMetadataElement['value'] = metadata[l]['value']
                updatedMetadataElement['language'] = 'en_US'
                itemMetadataProcessed.append(updatedMetadataElement)
                provNote = 'The language tag for \''+metadata[l]['key']+': '+metadata[l]['value']+'\' was changed from \'null\' to \'en_US\' through a batch process on '+datetime.now().strftime('%Y-%m-%d %H:%M:%S')+'.'
                provNoteElement = {}
                provNoteElement['key'] = 'dc.description.provenance'
                provNoteElement['value'] = unicode(provNote)
                provNoteElement['language'] = 'en_US'
                itemMetadataProcessed.append(provNoteElement)
            else:
                itemMetadataProcessed.append(metadata[l])
            delete = requests.delete(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify)
            print delete
            post = requests.put(baseURL + itemLink + '/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
            print post
            f.writerow([itemLink]+[key])
        offset = offset + 200
        print offset

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
