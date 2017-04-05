import json
import requests
import secrets
import time
from datetime import datetime
import os

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
handlePrefix = secrets.handlePrefix

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, data=data).content
headerAuth = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=headerAuth).json()
backupDirectory = filePath+'backup'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'
os.makedirs(backupDirectory)
for i in range (0, len (communities)):
    communityID = communities[i]['id']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=headerAuth).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['id']
        if collectionID != 24:
            collectionHandle = collections[j]['handle'].replace(handlePrefix,'').replace('/','-')
            print 'collectionID: ', collectionID
            itemList = []
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
            f=open(backupDirectory+collectionHandle+'.json', 'w')
            collectionMetadata = []
            for itemID in itemList:
                metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=headerAuth).json()
                collectionMetadata.append(metadata)
            json.dump(collectionMetadata, f)

logout = requests.post(baseURL+'/rest/logout', headers=headerAuth)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print "%d:%02d:%02d" % (h, m, s)
