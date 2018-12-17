import json
import requests
import secrets
import time
import csv
from datetime import datetime
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

secretsVersion = raw_input('To edit production server, enter the name of the secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print 'Editing Production'
    except ImportError:
        print 'Editing Stage'
else:
    print 'Editing Stage'

baseURL = secrets.baseURL
email = secrets.email
password = secrets.password
filePath = secrets.filePath
verify = secrets.verify
skippedCollections = secrets.skippedCollections

itemHandle = raw_input('Enter item handle: ')

startTime = time.time()
data = json.dumps({'email':email,'password':password})
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL + '/rest/login', headers=header, cookies=cookies, verify=verify, data=data).content
header = {'content-type':'application/json','accept':'application/json', 'rest-dspace-token':session}
print 'authenticated'

bitstreamList = []
endpoint = baseURL + '/rest/handle/' + itemHandle
item = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
itemID = item['uuid']
print 'itemID = %s' % itemID
bitstreams = ''
url = baseURL + '/rest/items/' + str(itemID) + '/bitstreams?expand=bitstreams'
bitstreams = requests.get(url, headers=header, cookies=cookies, verify=verify)
while bitstreams.status_code != 200:
    time.sleep(5)
    bitstreams = requests.get(url, headers=header, cookies=cookies, verify=verify)
bitstreams = bitstreams.json()
print 'found %d bitstreams' % len(bitstreams)
for k in range(0, len(bitstreams)):
    bitstreamID = bitstreams[k]['uuid']
    bitstreamList.append(bitstreamID)
elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Bitstreams list creation time: ', '%d:%02d:%02d' % (h, m, s)
print(bitstreamList)

f=csv.writer(open(filePath + 'deletedBitstreams' + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.csv', 'wb'))
f.writerow(['bitstreamID'] + ['delete'])
for number, bitstreamID in enumerate(bitstreamList):
    bitstreamsRemaining = len(bitstreamList) - number
    print 'Bitstreams remaining: ', bitstreamsRemaining, 'bitstreamID: ', bitstreamID
    delete = requests.delete(baseURL + '/rest/bitstreams/' + str(bitstreamID), headers=header, cookies=cookies, verify=verify)
    print delete
    f.writerow([bitstreamID] + [delete])

logout = requests.post(baseURL + '/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ', '%d:%02d:%02d' % (h, m, s)
