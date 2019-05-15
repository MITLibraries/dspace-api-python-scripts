import json
import requests
import time
from datetime import datetime
import urllib3
import os
import dsFunc
import argparse

baseURL, email, password, filePath, verify, skipColl, sec = dsFunc.instSelect()

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--handlePrefix', help='Enter the handle prefix')
args = parser.parse_args()

if args.handlePrefix:
    handlePrefix = args.handlePrefix
else:
    handlePrefix = input('Enter the handle prefix: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

date = datetime.now().strftime('%Y-%m-%d %H.%M.%S')
endpoint = baseURL + '/rest/communities'
communities = requests.get(endpoint, headers=header, cookies=cookies,
                           verify=verify).json()
backupDirectory = filePath + 'backup' + date + '/'
os.makedirs(backupDirectory)
for i in range(0, len(communities)):
    communityID = communities[i]['uuid']
    collections = requests.get(baseURL + '/rest/communities/'
                               + str(communityID) + '/collections',
                               headers=header, cookies=cookies,
                               verify=verify).json()
    for j in range(0, len(collections)):
        collectionID = collections[j]['uuid']
        if collectionID not in skipColl:
            collectionHandle = collections[j]['handle']
            collectionHandle = collectionHandle.replace(handlePrefix, '')
            collectionHandle = collectionHandle.replace('/', '-')
            print('collectionID: ', collectionID)
            itemList = []
            offset = 0
            items = ''
            while items != []:
                items = requests.get(baseURL + '/rest/collections/'
                                     + str(collectionID)
                                     + '/items?limit=1000&offset='
                                     + str(offset), headers=header,
                                     cookies=cookies, verify=verify)
                while items.status_code != 200:
                    time.sleep(5)
                    items = requests.get(baseURL + '/rest/collections/'
                                         + str(collectionID)
                                         + '/items?limit=1000&offset='
                                         + str(offset), headers=header,
                                         cookies=cookies, verify=verify)
                items = items.json()
                for k in range(0, len(items)):
                    itemID = items[k]['uuid']
                    itemList.append(itemID)
                offset = offset + 1000
            f = open(backupDirectory + collectionHandle + '.json', 'w')
            collectionMetadata = []
            for itemID in itemList:
                metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                                        + '/metadata', headers=header,
                                        cookies=cookies, verify=verify).json()
                collectionMetadata.append(metadata)
            json.dump(collectionMetadata, f)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
