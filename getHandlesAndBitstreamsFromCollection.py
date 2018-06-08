import json
import requests
import secrets
import time
import csv
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

handle = raw_input('Enter handle: ')

startTime = time.time()
data = {'email':email,'password':password}
header = {'content-type':'application/json','accept':'application/json'}
session = requests.post(baseURL+'/rest/login', headers=header, verify=verify, params=data).cookies['JSESSIONID']
cookies = {'JSESSIONID': session}
headerFileUpload = {'accept':'application/json'}
cookiesFileUpload = cookies
status = requests.get(baseURL+'/rest/status', headers=header, cookies=cookies, verify=verify).json()
userFullName = status['fullname']
print 'authenticated'

endpoint = baseURL+'/rest/handle/'+handle
collection = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
collectionID = collection['uuid']
collectionTitle = requests.get(endpoint, headers=header, cookies=cookies, verify=verify).json()
itemList = {}
offset = 0
items = ''
while items != []:
    items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
    while items.status_code != 200:
        time.sleep(5)
        items = requests.get(baseURL+'/rest/collections/'+str(collectionID)+'/items?limit=200&offset='+str(offset), headers=header, cookies=cookies, verify=verify)
    items = items.json()
    for k in range (0, len (items)):
        itemID = items[k]['uuid']
        itemID = '/rest/items/'+itemID
        itemHandle = items[k]['handle']
        itemList[itemID] = itemHandle
    offset = offset + 200
    print offset

handle = handle.replace('/','-')
f=csv.writer(open(filePath+handle+'handlesAndBitstreams.csv', 'wb'))
f.writerow(['bitstream']+['handle'])

for k,v in itemList.items():
    itemID = k
    itemHandle = v
    bitstreams = requests.get(baseURL+itemID+'/bitstreams', headers=header, cookies=cookies, verify=verify).json()
    for bitstream in bitstreams:
        print json.dumps(bitstream)
        fileName = bitstream['name']
        fileName.replace('.jpg','')
        f.writerow([fileName]+[itemHandle])

logout = requests.post(baseURL+'/rest/logout', headers=header, cookies=cookies, verify=verify)

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print 'Total script run time: ','%d:%02d:%02d' % (h, m, s)
