import json
import requests
import secrets
import csv
import time
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        print('Editing Stage')
else:
    print('Editing Stage')

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

communityHandle = input('Enter community handle: ')
key = input('Enter key: ')

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}

status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
print('authenticated')

endpoint = baseURL+'/rest/handle/'+communityHandle
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityID = community['uuid']
collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()

itemList = []
for i in range (0, len (collections)):
    collectionID = collections[i]['uuid']
    collectionHandle = collections[i]['handle']
    while items != []:
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
        while items.status_code != 200:
            time.sleep(5)
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
        items = items.json()
        for j in range (0, len (items)):
            itemID = items[j]['uuid']
            itemList.append(itemID)
            offset = offset + 200
            print(offset)

f=csv.writer(open(filePath+'removeUnnecessarySpaces'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'.csv', 'w'))
f.writerow(['itemID']+['replacedKey']+['replacedValue']+['delete']+['post'])
for itemID in itemList:
    itemMetadataProcessed = []
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    for i in range (0, len (metadata)):
        if metadata[i]['key'] == key:
            if '  ' in json.dumps(metadata[i]) or ' ,' in json.dumps(metadata[i]):
                updatedMetadataElement = json.loads(json.dumps(metadata[i]).replace('   ',' ').replace('  ',' ').replace(' ,',','))
                itemMetadataProcessed.append(updatedMetadataElement)
                f.writerow([itemID]+[metadata[i]['key']]+[metadata[i]['value']])
            else:
                itemMetadataProcessed.append(metadata[i])
        else:
            itemMetadataProcessed.append(metadata[i])
    if json.dumps(itemMetadataProcessed) != json.dumps(metadata):
        itemMetadataProcessed = json.dumps(itemMetadataProcessed)
        print('updated', itemID)
        delete = requests.delete(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify)
        print(delete)
        post = requests.put(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify, data=itemMetadataProcessed)
        print(post)
    else:
        print('not updated', itemID)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
