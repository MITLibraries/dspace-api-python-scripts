import json
import requests
import secrets
import time
from datetime import datetime
import os

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
handlePrefix = secrets.handlePrefix
verify = secrets.verify
skippedCollections = secrets.skippedCollections

requests.packages.urllib3.disable_warnings()

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
print('authenticated')

endpoint = baseURL+'/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
backupDirectory = filePath+'backup'+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'
os.makedirs(backupDirectory)
for i in range (0, len (communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
    for j in range (0, len (collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            collectionHandle = collections[j]['handle'].replace(handlePrefix,'').replace('/','-')
            print('collectionID: ', collectionID)
            itemList = []
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=1000&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
                items = items.json()
                for k in range (0, len (items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 1000
            f=open(backupDirectory+collectionHandle+'.json', 'w')
            collectionMetadata = []
            for itemID in itemList:
                metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
                collectionMetadata.append(metadata)
            json.dump(collectionMetadata, f)

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))
