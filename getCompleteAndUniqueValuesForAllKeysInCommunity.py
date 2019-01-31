import json
import requests
import secrets
import csv
import time
import os.path
from collections import Counter
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

handle = input('Enter community handle: ')

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}

status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated')

itemList = []
endpoint = baseURL+'/rest/handle/'+handle
community = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
communityName = community['name'].replace(' ','')
communityID = community['uuid']

filePathComplete = filePath+'completeValueLists'+communityName+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'
filePathUnique = filePath+'uniqueValueLists'+communityName+datetime.now().strftime('%Y-%m-%d %H.%M.%S')+'/'

collections = requests.get(baseURL+'/rest/communities/'+str(communityID)+'/collections', headers=header, cookies=cookies, verify=verify).json()
for j in range (0, len (collections)):
    collectionID = collections[j]['uuid']
    if collectionID not in skippedCollections:
        offset = 0
        items = ''
        while items != []:
            items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=100&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=100&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
            items = items.json()
            for k in range (0, len (items)):
                itemID = items[k]['uuid']
                itemList.append(itemID)
            offset = offset + 100
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ','%d:%02d:%02d' % (h, m, s))

os.mkdir(filePathComplete)
os.mkdir(filePathUnique)
for number, itemID in enumerate(itemList):
    itemsRemaining = len(itemList) - number
    print('Items remaining: ', itemsRemaining, 'ItemID: ', itemID)
    metadata = requests.get(baseURL+'/rest/items/'+str(itemID)+'/metadata', headers=header, cookies=cookies, verify=verify).json()
    for l in range (0, len (metadata)):
        if metadata[l]['key'] != 'dc.description.provenance':
            key = metadata[l]['key']
            try:
                value = metadata[l]['value']
            except:
                value = ''
            if os.path.isfile(filePathComplete+key+'ValuesComplete.csv') == False:
                f=csv.writer(open(filePathComplete+key+'ValuesComplete.csv', 'w'))
                f.writerow(['itemID']+['value'])
                f.writerow([itemID]+[value])
            else:
                f=csv.writer(open(filePathComplete+key+'ValuesComplete.csv', 'a'))
                f.writerow([itemID]+[value])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Complete value list creation time: ','%d:%02d:%02d' % (h, m, s))

for fileName in os.listdir(filePathComplete):
    reader = csv.DictReader(open(filePathComplete+fileName))
    fileName = fileName.replace('Complete', 'Unique')
    valueList = []
    for row in reader:
        valueList.append(row['value'])
    valueListCount = Counter(valueList)
    f=csv.writer(open(filePathUnique+fileName, 'w'))
    f.writerow(['value']+['count'])
    for key, value in valueListCount.items():
        f.writerow([key]+[str(value).zfill(6)])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
