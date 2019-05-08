import json
import requests
import time
import csv
import urllib3
import argparse
import dsFunc

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

parser = argparse.ArgumentParser()
parser.add_argument('-k', '--key', help='the key to be searched. optional - if \
not provided, the script will ask for input')
args = parser.parse_args()

if args.key:
    key = args.key
else:
    key = input('Enter the key: ')

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

searchString = "\"" + key + "\""

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

f = csv.writer(open(filePath + 'recordsWithDuplicate-' + key + '.csv', 'w'))
f.writerow(['itemID'])
offset = 0
recordsEdited = 0
items = ''
while items != []:
    endpoint = baseURL + '/rest/filtered-items?query_field[]=' + key
    endpoint += '&query_op[]=exists&query_val[]=&limit=200&offset='
    endpoint += str(offset)
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
        metadata = json.dumps(metadata)
        if metadata.find(searchString) != metadata.rfind(searchString):
            f.writerow([itemLink])
    offset = offset + 200
    print(offset)

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
