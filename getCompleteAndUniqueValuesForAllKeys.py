import json
import requests
import secrets
import csv
import time
import os.path
from collections import Counter

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath

filePathComplete = filePath+'completeValueLists/'
filePathUnique = filePath+'/uniqueValueLists/'

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

itemList = []
endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=headerAuth).json()
for i in range (0, len (communities)):
    communityID = communities[i]['id']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        if collectionID != 24:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=headerAuth)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['id']
                    itemList.append(itemID)
                offset = offset + 1000
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Item list creation time: ','%d:%02d:%02d' % (h, m, s)

for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print 'Items remaining: ', itemsRemaining, 'ItemID: ', itemID
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth).json()
    for l in range (0, len (metadata)):
        if metadata[l]['key'] != 'dc.description.provenance':
            key = metadata[l]['key']
            value = metadata[l]['value'].encode('utf-8')
            if os.path.isfile(filePathComplete+key+'Values.csv') == False:
                f=csv.writer(open(filePathComplete+key+'Values.csv', 'wb'))
                f.writerow(['itemID']+['value'])
                f.writerow([itemID]+[value])
            else:
                f=csv.writer(open(filePathComplete+key+'Values.csv', 'a'))
                f.writerow([itemID]+[value])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Complete value list creation time: ','%d:%02d:%02d' % (h, m, s)

for fileName in os.listdir(filePathComplete):
    reader = csv.DictReader(open(filePathComplete+fileName))
    valueList = []
    for row in reader:
        valueList.append(row['value'])
    valueListCount = Counter(valueList)
    f=csv.writer(open(filePathUnique+fileName, 'wb'))
    f.writerow(['value']+['count'])
    for key, value in valueListCount.items():
        f.writerow([key]+[str(value).zfill(6)])

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
