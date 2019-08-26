import json
import requests
import time
import urllib3
import dsFunc

inst = input('To edit production server, enter the name of the secrets file: ')
secrets = dsFunc.instSelect(inst)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skipColl = secrets.skipColl

handle = input('Enter handle: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

startTime = time.time()
data = {'email': email, 'password': password}
header = {'content-type': 'application/json', 'accept': 'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header,
                        verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}


status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

endpoint = baseURL + '/rest/handle/' + handle
collection = requests.get(endpoint, headers=header, cookies=cookies,
                          verify=verify).json()
collectionID = collection['uuid']
collectionTitle = requests.get(endpoint, headers=header, cookies=cookies,
                               verify=verify).json()
endpoint = baseURL + '/rest/collections/' + str(collectionID) + '/items'
output = requests.get(endpoint, headers=header, cookies=cookies,
                      verify=verify).json()

itemList = []
for i in range(0, len(output)):
    name = output[i]['name']
    itemID = output[i]['uuid']
    itemList.append(itemID)

f = open(filePath + handle.replace('/', '-') + '.json', 'w')
metadataGroup = []
for itemID in itemList:
    metadata = requests.get(baseURL + '/rest/items/' + str(itemID)
                            + '/metadata', headers=header, cookies=cookies,
                            verify=verify).json()
    metadataGroup.append(metadata)
json.dump(metadataGroup, f)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
