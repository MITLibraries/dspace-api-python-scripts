import json
import requests
import secrets
import time
import csv
from collections import Counter
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

#login info kept in secrets.py file
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

#authentication
startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}

status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')

f=csv.writer(open(filePath+'collectionStats.csv', 'w'))
f.writerow(['Name']+['collectionID']+['collectionHandle']+['numberOfItems'])

itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
for i in range (0, len (communities)):
    communityID = communities[i]['uuid']
    communityName = communities[i]['name']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['uuid']
        collectionID = collections[j]['uuid']
        numberItems = collections[j]['numberItems']
        collectionName = collections[j]['name']
        collectionHandle = collections[j]['handle']
        fullName = communityName+' - '+collectionName
        print(collectionID)
        if collectionID not in skippedCollections:
            offset = 0
            items = ''
            while items != []:
                f.writerow([fullName]+[collectionID]+[collectionHandle]+[str(numberItems).zfill(6)])
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['uuid']
                    concat = str(communityID)+':'+str(collectionID)+'|'+str(itemID)
                    itemList.append(concat)
                offset = offset + 200
                print(offset)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ','%d:%02d:%02d' % (h, m, s))

#retrieve metadata from all items
keyList = []
dcTypeList = []
keyCount = []
f=csv.writer(open(filePath+'dspaceIDs.csv', 'w'))
f.writerow(['communityID']+['collectionID']+['itemID'])
for concat in itemList:
    communityID = concat[:concat.find(':')]
    collectionID = concat[concat.find(':')+1:concat.find('|')]
    itemID = concat[concat.find('|')+1:]
    f.writerow([communityID]+[collectionID]+[itemID])
    concat = concat[:concat.find('|')]
    print(itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    for i in range (0, len (metadata)):
        key = metadata[i]['key']
        keyCount.append(key)
        keyConcat = concat+'|'+ metadata[i]['key']
        if keyConcat not in keyList:
            keyList.append(keyConcat)
        if metadata[i]['key'] == 'dc.type':
            dcType = metadata[i]['value']
            if dcType not in dcTypeList:
                dcTypeList.append(dcType)

print('writing types')
f=csv.writer(open(filePath+'dspaceTypes.csv', 'w'))
f.writerow(['type'])
for dcType in dcTypeList:
    f.writerow([dcType])

print('writing global key counts')
f=csv.writer(open(filePath+'keyCount.csv', 'w'))
f.writerow(['key']+['count'])
countDict = Counter(keyCount)
for key, value in countDict.items():
    f.writerow([key]+[str(value).zfill(6)])

print('writing collection metadata keys')
f=csv.writer(open(filePath+'collectionMetadataKeys.csv', 'w'))
f.writerow(['fullName']+['collectionID']+['collectionHandle']+['key'])
for concat in keyList:
    communityID = concat[:concat.find(':')]
    collectionID = concat[concat.find(':')+1:concat.find('|')]
    key = concat[concat.rfind('|')+1:]
    additionalDataCommunity = requests.get(baseURL+'/rest/communities/'+str(communityID), headers=header, cookies=cookies, verify=verify).json()
    communityName = additionalDataCommunity['name']
    additionalDataCollection = requests.get(baseURL+'/rest/collections/'+str(collectionID), headers=header, cookies=cookies, verify=verify).json()
    collectionName = additionalDataCollection['name']
    collectionHandle = additionalDataCollection['handle']
    fullName = communityName+' - '+collectionName
    f.writerow([fullName]+[collectionID]+[collectionHandle]+[key])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)
