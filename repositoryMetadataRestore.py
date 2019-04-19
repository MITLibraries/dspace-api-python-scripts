import json
import requests
import os
import time

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

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
handlePrefix = secrets.handlePrefix
verify = secrets.verify
skippedCollections = secrets.skippedCollections

requests.packages.urllib3.disable_warnings()

directory = filePath + input('Enter directory name: ')

startTime = time.time()

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

for fileName in os.listdir(directory):
    print(fileName)
    metadataGroup = json.load(open(directory + '/' + fileName))
    for i in range(0, len(metadataGroup)):
        metadata = metadataGroup[i]
        itemMetadata = json.dumps(metadata)
        for j in range(0, len(metadata)):
            key = metadata[j]['key']
            value = metadata[j]['value']
            if key == 'dc.identifier.uri' and value.startswith(handlePrefix):
                handle = metadata[j]['value'].replace(handlePrefix, '')
                print(handle)
                endpoint = baseURL + '/rest/handle/' + handle
                item = requests.get(endpoint, headers=header, cookies=cookies,
                                    verify=verify).json()
                itemID = item['uuid']
                print(fileName, itemID)
                delete = requests.delete(baseURL + '/rest/items/' + str(itemID)
                                         + '/metadata', headers=header,
                                         cookies=cookies, verify=verify)
                print(delete)
                post = requests.put(baseURL + '/rest/items/' + str(itemID)
                                    + '/metadata', headers=header,
                                    cookies=cookies, verify=verify,
                                    data=itemMetadata)
                print(post)
logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
