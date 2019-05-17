import requests
import time
import csv
from datetime import datetime
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

itemHandle = input('Enter item handle: ')

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

bitstreamList = []
endpoint = baseURL + '/rest/handle/' + itemHandle
item = requests.get(endpoint, headers=header, cookies=cookies,
                    verify=verify).json()
itemID = item['uuid']
print('itemID = %s' % itemID)
bitstreams = ''
url = baseURL + '/rest/items/' + str(itemID) + '/bitstreams?expand=bitstreams'
bitstreams = requests.get(url, headers=header, cookies=cookies, verify=verify)
while bitstreams.status_code != 200:
    time.sleep(5)
    bitstreams = requests.get(url, headers=header, cookies=cookies,
                              verify=verify)
bitstreams = bitstreams.json()
print('found %d bitstreams' % len(bitstreams))
for k in range(0, len(bitstreams)):
    bitstreamID = bitstreams[k]['uuid']
    bitstreamList.append(bitstreamID)

dsFunc.elapsedTime(startTime, 'Bitstream list creation time')
print(bitstreamList)

f = csv.writer(open(filePath + 'deletedBitstreams'
               + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'w'))
f.writerow(['bitstreamID'] + ['delete'])
for number, bitstreamID in enumerate(bitstreamList):
    bitstreamsRemaining = len(bitstreamList) - number
    print('Bitstreams remaining: ', bitstreamsRemaining, 'bitstreamID: ',
          bitstreamID)
    delete = requests.delete(baseURL + '/rest/bitstreams/' + str(bitstreamID),
                             headers=header, cookies=cookies, verify=verify)
    print(delete)
    f.writerow([bitstreamID] + [delete])

logout = requests.post(baseURL + '/rest/logout', headers=header,
                       cookies=cookies, verify=verify)

# print script run time
dsFunc.elapsedTime(startTime, 'Script run time')
