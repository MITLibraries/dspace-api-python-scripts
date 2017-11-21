import json
import requests
import secrets
import time
import csv
from collections import Counter

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

#login info kept in secrets.py file
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify

requests.packages.urllib3.disable_warnings()

#authentication
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'
startTime = time.time()

endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=headerAuth, verify=verify).json()

#create list of all item IDs
itemList = []
for i in range (0, len (communities)):
    communityID = communities[i]['id']
    communityName = communities[i]['name'].encode('utf-8')
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        collectionName = collections[j]['name'].encode('utf-8')
        fullName = communityName+' - '+collectionName
        if collectionID == 24:
            print 'Levy Collection - skipped'
        else:
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=headerAuth, verify=verify)
            while items.status_code != 200:
                time.sleep(5)
                print 'collection:', collectionID, '# of items:',len(items), 'fail'
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=headerAuth, verify=verify)
            items = items.json()
            print 'collection:', collectionID,', Number of items:',len(items)
            for i in range (0, len (items)):
                itemID = items[i]['id']
                itemList.append(itemID)

#retrieve metadata from all items
keyList = []
for itemID in itemList:
    print itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
    for i in range (0, len (metadata)):
        key = metadata[i]['key']
        if key not in keyList:
            keyList.append(key)

keyListHeader = ['collectionNameColumn']
keyList.sort()
keyListHeader = keyListHeader + keyList
f=csv.writer(open(filePath+'collectionsKeysMatrix.csv', 'wb'))
f.writerow(keyListHeader)

for i in range (0, len (communities)):
    communityID = communities[i]['id']
    communityName = communities[i]['name'].encode('utf-8')
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        if collectionID == 24:
            print 'Levy Collection - skipped'
        else:
            collectionItemList = []
            collectionName = collections[j]['name'].encode('utf-8')
            fullName = communityName+' - '+collectionName
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=headerAuth, verify=verify)
            while items.status_code != 200:
                time.sleep(5)
                print 'collection:', collectionID, '# of items:',len(items), 'fail'
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=5000', headers=headerAuth, verify=verify)
            items = items.json()
            for i in range (0, len (items)):
                itemID = items[i]['id']
                collectionItemList.append(itemID)

            collectionKeyCount = {}
            for key in keyList:
                collectionKeyCount[key] = 0
            for itemID in collectionItemList:
                print itemID
                metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth, verify=verify).json()
                for i in range (0, len (metadata)):
                    itemKey = metadata[i]['key']
                    for key in keyList:
                        if itemKey == key:
                            collectionKeyCount[key] = collectionKeyCount[key]+1

            collectionKeyCountList = []
            for k, v in collectionKeyCount.items():
                collectionKeyCountList.append(k+' '+str(v))
            collectionKeyCountList.sort()
            updatedCollectionKeyCountList = []
            for entry in collectionKeyCountList:
                count = entry[entry.index(' ')+1:]
                updatedCollectionKeyCountList.append(count)
            fullName = [fullName]
            updatedCollectionKeyCountList = fullName + updatedCollectionKeyCountList
            f.writerow(updatedCollectionKeyCountList)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth, verify=verify)
