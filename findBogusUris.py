import requests
import csv
import time
import urllib3
import dsFunc
import argparse

inst = input('To edit production server, enter the name of the secrets file: ')
secrets = dsFunc.instSelect(inst)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skipColl = secrets.skipColl

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
session = requests.post(baseURL + '/rest/login', headers=header,
                        verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept': 'application/json'}

status = requests.get(baseURL + '/rest/status', headers=header,
                      cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print('authenticated', userFullName)

f = csv.writer(open(filePath + 'bogusUris.csv', 'w'))
f.writerow(['itemID'] + ['uri'])
offset = 0
recordsEdited = 0
items = ''
while items != []:
    endpoint = baseURL + '/rest/filtered-items?query_field[]='
    endpoint += 'dc.identifier.uri&query_op[]=doesnt_contain'
    endpoint += '&query_val[]=' + handlePrefix
    endpoint += '&limit=200&offset=' + str(offset)
    print(endpoint)
    response = requests.get(endpoint, headers=header, cookies=cookies,
                            verify=verify).json()
    items = response['items']
    for item in items:
        itemMetadataProcessed = []
        itemLink = item['link']
        metadata = requests.get(baseURL + itemLink + '/metadata',
                                headers=header, cookies=cookies,
                                verify=verify).json()
        for l in range(0, len(metadata)):
            if metadata[l]['key'] == 'dc.identifier.uri':
                uri = str(metadata[l]['value'])
                if uri.startswith(handlePrefix) is False:
                    f.writerow([itemLink] + [uri])
    offset = offset + 200
    print(offset)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
