import requests
import time
import csv
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    secrets = __import__('secrets')
    print('Editing Development')

# login info kept in secrets.py file
baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

# authentication
startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, verify=verify,
                        params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

endpoint = baseURL + '/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies,
                           verify=verify).json()

# create list of all item IDs
itemList = []
endpoint = baseURL + '/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies,
                           verify=verify).json()
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL + '/rest/communities/'
                               + str(communityID) + '/collections',
                               headers=header, cookies=cookies,
                               verify=verify).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        print(collectionID)
        if collectionID not in skippedCollections:
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL + '/rest/collections/'
                                     + str(collectionID)
                                     + '/items?limit=200&offset='
                                     + str(offset), headers=header,
                                     cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL + '/rest/collections/'
                                         + str(collectionID)
                                         + '/items?limit=200&offset='
                                         + str(offset), headers=header,
                                         cookies=cookies, verify=verify)
                items = items.json()
                for k in range(0, len(items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 200
                print(offset)
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Item list creation time: ', '%d:%02d:%02d' % (h, m, s))

# retrieve metadata from all items
keyList = []
for itemID in itemList:
    print(itemID)
    metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify).json()
    for i in range(0, len(metadata)):
        key = metadata[i]['key']
        if key not in keyList:
            keyList.append(key)

keyListHeader = ['collectionNameColumn']
keyList.sort()
keyListHeader = keyListHeader + keyList
f = csv.writer(open(filePath + 'collectionsKeysMatrix.csv', 'w'))
f.writerow(keyListHeader)

for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    communityName = communities[i]['name']
    collections = requests.get(baseURL + '/rest/communities/'
                               + str(communityID) + '/collections',
                               headers=header, cookies=cookies,
                               verify=verify).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skippedCollections:
            print('Collection skipped')
        else:
            collectionItemList = []
            collectionName = collections[j]['name']
            fullName = communityName + ' - ' + collectionName
            items = requests.get(baseURL + '/rest/collections/'
                                 + str(collectionID) + '/items?limit=5000',
                                 headers=header, cookies=cookies,
                                 verify=verify)
            while items.status_code != 200:
                time.sleep(5)
                items = requests.get(baseURL + '/rest/collections/'
                                     + str(collectionID) + '/items?limit=5000',
                                     headers=header, cookies=cookies,
                                     verify=verify)
            items = items.json()
            for i in range(0, len(items)):
                itemID = items[i]['uuid']
                collectionItemList.append(itemID)

            collectionKeyCount = {}
            for key in keyList:
                collectionKeyCount[key] = 0
            for itemID in collectionItemList:
                print(itemID)
                metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                        + '/metadata', headers=header,
                                        cookies=cookies, verify=verify).json()
                for i in range(0, len(metadata)):
                    itemKey = metadata[i]['key']
                    for key in keyList:
                        if itemKey == key:
                            collectionKeyCount[key] += 1

            collectionKeyCountList = []
            for k, v in collectionKeyCount.items():
                collectionKeyCountList.append(k + ' ' + str(v))
            collectionKeyCountList.sort()
            updatedCollKeyCountList = []
            for entry in collectionKeyCountList:
                count = entry[entry.index(' ') + 1:]
                updatedCollKeyCountList.append(count)
            fullName = [fullName]
            updatedCollKeyCountList = fullName + updatedCollKeyCountList
            f.writerow(updatedCollKeyCountList)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print("%d:%02d:%02d" % (h, m, s))

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)
